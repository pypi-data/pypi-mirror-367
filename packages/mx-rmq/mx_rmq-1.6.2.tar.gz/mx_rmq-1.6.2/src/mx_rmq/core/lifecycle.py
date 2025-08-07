"""
消息生命周期管理服务模块
"""

import json
import time

from loguru import logger
from ..constants import GlobalKeys, TopicKeys
from ..message import Message
from .context import QueueContext


class MessageLifecycleService:
    """消息生命周期管理类"""

    def __init__(self, context: QueueContext) -> None:
        self.context = context

    async def complete_message(self, message_id: str, topic: str) -> None:
        """完成消息处理"""
        try:
            await self.context.lua_scripts["complete_message"](
                keys=[
                    self.context.get_global_key(GlobalKeys.PAYLOAD_MAP),
                    self.context.get_global_topic_key(topic, TopicKeys.PROCESSING),
                    self.context.get_global_key(GlobalKeys.EXPIRE_MONITOR),
                ],
                args=[message_id],
            )
        except Exception as e:
            logger.exception(
                f"完成消息处理失败, message_id={message_id}, topic={topic}"
            )
            raise

    async def handle_message_failure(self, message: Message, error: Exception) -> None:
        """处理消息失败"""
        try:
            message.mark_retry(str(error))

            # 根据重试能力采用不同处理策略
            if message.can_retry():
                await self._handle_retryable_failure(message, error)
            else:
                await self._handle_final_failure(message, error)
        except Exception as e:
            logger.exception(f"处理消息失败时出错, message_id={message.id}")

    async def _handle_retryable_failure(
        self, message: Message, error: Exception
    ) -> None:
        """处理可重试的失败消息"""
        await self.retry_message(message, message.topic)
        logger.info(
            f"消息重试调度, message_id={message.id}, topic={message.topic}, retry_count={message.meta.retry_count}, max_retries={message.meta.max_retries}, error={str(error)}"
        )

    async def _handle_final_failure(self, message: Message, error: Exception) -> None:
        """处理最终失败的消息"""
        await self.move_to_dead_letter_queue(message)
        logger.info(
            f"消息移入死信队列, message_id={message.id}, topic={message.topic}, retry_count={message.meta.retry_count}, error={str(error)}"
        )

    async def handle_expired_message(self, message: Message, queue_name: str) -> None:
        """处理过期消息"""
        try:
            # 根据重试能力选择处理方式
            if message.can_retry():
                await self._handle_expired_retry(message, queue_name)
            else:
                await self._handle_expired_final(message, queue_name)
        except Exception as e:
            logger.exception(f"处理过期消息失败, message_id={message.id}")

    async def _handle_expired_retry(self, message: Message, queue_name: str) -> None:
        """处理可重试的过期消息"""
        await self.retry_message(message, queue_name)
        logger.info(
            f"过期消息重试, message_id={message.id}, queue_name={queue_name}, retry_count={message.meta.retry_count}"
        )

    async def _handle_expired_final(self, message: Message, queue_name: str) -> None:
        """处理最终过期的消息"""
        await self.move_to_dead_letter_queue(message)
        logger.info(
            f"过期消息移入死信队列, message_id={message.id}, queue_name={queue_name}"
        )

    async def handle_stuck_message(
        self, msg_id: str, topic: str, processing_key: str
    ) -> None:
        """处理卡死的消息"""
        try:
            # 第一层验证：检查消息是否存在
            payload_json = await self.context.redis.hget(
                self.context.get_global_key(GlobalKeys.PAYLOAD_MAP), msg_id
            )  # type: ignore
            if not payload_json:
                logger.warning(
                    f"卡死消息不存在，从processing队列移除, message_id={msg_id}"
                )
                await self.context.redis.lrem(processing_key, 1, msg_id)  # type: ignore
                return

            # 第二层验证：解析消息数据
            try:
                message = Message.model_validate_json(payload_json)
            except (json.JSONDecodeError, ValueError) as parse_error:
                logger.exception(f"卡死消息格式错误, message_id={msg_id}")
                await self.context.redis.lrem(processing_key, 1, msg_id)  # type: ignore
                return

            # 第三层验证：检查消息是否在processing队列中
            removed_count = await self.context.redis.lrem(processing_key, 1, msg_id)  # type: ignore
            if removed_count == 0:
                logger.warning(f"卡死消息不在processing队列中, message_id={msg_id}")
                return

            # 核心业务逻辑：处理卡死消息
            await self._process_stuck_message(message, msg_id, topic)

        except Exception as e:
            # 异常处理：确保问题消息被清理
            await self._cleanup_stuck_message(msg_id, processing_key, e)

    async def _process_stuck_message(
        self, message: Message, msg_id: str, topic: str
    ) -> None:
        """处理卡死消息的核心逻辑"""
        # 更新消息状态
        message.mark_stuck("detected_by_processing_monitor")

        # 根据重试能力选择处理方式
        if message.can_retry():
            await self.retry_message(message, topic)
            logger.info(
                f"卡死消息重新调度, message_id={msg_id}, topic={topic}, retry_count={message.meta.retry_count}, reason=stuck_timeout"
            )
        else:
            await self.move_to_dead_letter_queue(message)
            logger.info(
                f"卡死消息移入死信队列, message_id={msg_id}, topic={topic}, reason=stuck_timeout"
            )

        # 从过期监控中移除
        await self.context.redis.zrem(
            self.context.get_global_key(GlobalKeys.EXPIRE_MONITOR), msg_id
        )  # type: ignore

    async def _cleanup_stuck_message(
        self, msg_id: str, processing_key: str, error: Exception
    ) -> None:
        """清理卡死消息的异常处理"""
        logger.exception(f"处理卡死消息失败, message_id={msg_id}")
        try:
            await self.context.redis.lrem(processing_key, 1, msg_id)  # type: ignore
            logger.info(f"已从processing队列移除问题消息, message_id={msg_id}")
        except Exception as cleanup_error:
            logger.exception(f"清理卡死消息失败, message_id={msg_id}")

    async def retry_message(self, message: Message, topic: str) -> None:
        """重试消息"""
        try:
            retry_delay = message.get_retry_delay()
            current_time = int(time.time())

            # 更新过期时间（使用秒级时间戳）
            new_expire_time = (
                current_time * 1000
                + retry_delay * 1000
                + self.context.config.message_ttl
            )
            message.meta.expire_at = new_expire_time

            # 使用Lua脚本重新调度
            await self.context.lua_scripts["retry_message"](
                keys=[
                    self.context.get_global_key(GlobalKeys.PAYLOAD_MAP),
                    self.context.get_global_key(GlobalKeys.DELAY_TASKS),
                    self.context.get_global_key(GlobalKeys.EXPIRE_MONITOR),
                    self.context.get_global_topic_key(
                        topic, TopicKeys.PROCESSING
                    ),  # 新增：processing队列
                ],
                args=[
                    message.id,
                    message.model_dump_json(
                        by_alias=True, exclude_none=True
                    ),  # 新的 message 消息体
                    retry_delay,
                    topic,  # 新增：topic参数
                ],
            )
        except Exception as e:
            logger.exception(f"重试消息失败, message_id={message.id}")
            raise

    async def move_to_dead_letter_queue(self, message: Message) -> None:
        """移入死信队列"""
        try:
            message.mark_dead_letter("max_retries_exceeded")

            await self.context.lua_scripts["move_to_dlq"](
                keys=[
                    self.context.get_global_key(GlobalKeys.DLQ_PAYLOAD_MAP),
                    self.context.get_global_key(GlobalKeys.DLQ_QUEUE),
                    self.context.get_global_key(GlobalKeys.EXPIRE_MONITOR),
                    self.context.get_global_key(GlobalKeys.PAYLOAD_MAP),
                    self.context.get_global_topic_key(
                        message.topic, TopicKeys.PROCESSING
                    ),  # 新增：processing队列
                ],
                args=[
                    message.id,
                    message.model_dump_json(by_alias=True, exclude_none=True),
                    message.topic,  # 新增：topic参数
                ],
            )
        except Exception:
            logger.exception(f"移入死信队列失败, message_id={message.id}")
            raise
