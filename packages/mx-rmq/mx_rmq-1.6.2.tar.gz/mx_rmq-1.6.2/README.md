# MX-RMQ 使用指南

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Redis](https://img.shields.io/badge/redis-5.0+-red.svg)](https://redis.io/)

MX-RMQ 是一个高性能、可靠的基于Redis的分布式消息队列系统，支持普通消息、延时消息、优先级消息，具备完善的监控和重试机制。

> 目前已基本生产可用。

## 目录

- [特性概览](#特性概览)
- [快速开始](#快速开始)
- [安装](#安装)
- [基本使用](#基本使用)
- [高级功能](#高级功能)
- [配置参考](#配置参考)
- [API 参考](#api-参考)
- [监控和管理](#监控和管理)
- [部署指南](#部署指南)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 特性概览

- 🚀 **高性能**: 基于Redis的内存存储，支持10,000+消息/秒的吞吐量
- 🔄 **可靠性**: 原子性Lua脚本操作，保证消息不丢失
- ⏰ **延时消息**: 支持任意时间延迟的消息调度
- 🏷️ **优先级**: 支持高、中、低优先级消息处理
- 🔁 **自动重试**: 可配置的重试机制和指数退避
- 💀 **死信队列**: 失败消息自动进入死信队列，支持人工干预
- 📊 **监控指标**: 实时监控队列状态、处理时间、吞吐率等
- 🛑 **优雅停机**: 支持优雅停机，确保消息处理完成
- 🔧 **易于使用**: 简洁的API设计，开箱即用

## 设计限制

- ❌ **不支持消费者组**: 每个topic只能被单一消费者组负载均衡消费，如需多组消费同一消息，请创建多个topic并投递多次消息

## 快速开始

启动 redis
```shell
docker run -d --name redis8 -p 6379:6379 redis:8 redis-server
```
### 30秒快速体验

```python
import asyncio
from mx_rmq import MQConfig, RedisMessageQueue

async def handle_order(payload: dict) -> None:
    """处理订单消息"""
    print(f"处理订单: {payload['order_id']}")
    # 你的业务逻辑
    await asyncio.sleep(1)

async def main():
    # 创建消息队列
    mq = RedisMessageQueue()
    
    # 注册消息处理器
    mq.register_handler("order_created", handle_order)
    
    # 生产消息
    await mq.produce("order_created", {
        "order_id": "ORD_123",
        "user_id": 456,
        "amount": 99.99
    })
    
    # 非阻塞启动（推荐）
    await mq.start_background()
    
    # 等待消息处理
    await asyncio.sleep(2)
    
    # 优雅停止
    await mq.stop()
if __name__ == "__main__":
    asyncio.run(main())
```

## 安装

### 使用 uv (推荐)

```bash
# 添加到现有项目
uv add mx-rmq

# 或者从源码安装
git clone https://github.com/CodingOX/mx-rmq.git
cd mx-rmq
uv sync
```

### 使用 pip

```bash
pip install mx-rmq

# 或从源码安装
pip install git+https://github.com/CodingOX/mx-rmq.git
```

### 系统要求

- Python 3.12+
- Redis 5.0+ 【推荐 Redis 7.4+】

## 基本使用

### 1. 创建消息队列

```python
from mx_rmq import MQConfig, RedisMessageQueue

# 使用默认配置
mq = RedisMessageQueue()

# 或自定义配置
config = MQConfig(
    redis_host="redis://localhost:6379",
    max_workers=10,
    task_queue_size=20
)
mq = RedisMessageQueue(config)
```

### 2. 注册消息处理器

```python
# 方式1: 使用装饰器
@mq.register_handler("user_registration")
async def handle_user_registration(payload: dict) -> None:
    user_id = payload['user_id']
    email = payload['email']
    print(f"欢迎新用户: {user_id} ({email})")

# 方式2: 直接注册
async def handle_payment(payload: dict) -> None:
    print(f"处理支付: {payload}")

mq.register_handler("payment_completed", handle_payment)
```

### 3. 生产消息

```python
# 生产普通消息
message_id = await mq.produce("user_registration", {
    "user_id": 12345,
    "email": "user@example.com",
    "timestamp": "2024-01-01T00:00:00Z"
})

print(f"消息已发送: {message_id}")
```

### 4. 启动消费者

MX-RMQ 提供多种方式启动消费者，以适应不同使用场景：

#### 方式1: 非阻塞启动（推荐）

```python
# 非阻塞启动，立即返回控制权
background_task = await mq.start_background()

# 可以继续执行其他操作
await mq.produce("test_topic", {"message": "Hello World"})

# 等待一段时间或执行其他任务
await asyncio.sleep(10)

# 优雅停止
await mq.stop()
```

#### 方式2: 阻塞式启动（传统方式）

```python
# 启动消费者（会阻塞，直到收到停机信号）
await mq.start()
```

#### 方式3: 异步上下文管理器

```
# 使用异步上下文管理器自动管理资源
async with RedisMessageQueue() as mq:
    mq.register_handler("test_topic", handle_message)
    await mq.start_background()
    await mq.produce("test_topic", {"message": "Hello World"})
    await asyncio.sleep(5)
    # 自动停止和清理资源
```

#### 方式4: 同步运行（简单场景）

```
# 同步运行指定时长
mq = RedisMessageQueue()
mq.register_handler("test_topic", handle_message)
mq.run(duration=10.0)  # 运行10秒后自动停止
```

## 高级功能

### 延时消息

```python
# 5分钟后发送提醒
await mq.produce(
    topic="send_reminder",
    payload={"user_id": 123, "type": "payment_due"},
    delay=300  # 300秒后执行
)

# 1小时后发送邮件
await mq.produce(
    topic="send_email",
    payload={
        "to": "user@example.com",
        "subject": "订单确认",
        "body": "感谢您的订单..."
    },
    delay=3600  # 1小时后执行
)
```

### 优先级消息

```python
from mx_rmq import MessagePriority

# 高优先级消息（优先处理）
await mq.produce(
    topic="system_alert",
    payload={"level": "critical", "message": "系统告警"},
    priority=MessagePriority.HIGH
)

# 普通优先级（默认）
await mq.produce(
    topic="user_activity",
    payload={"user_id": 123, "action": "login"},
    priority=MessagePriority.NORMAL
)

# 低优先级消息（最后处理）
await mq.produce(
    topic="analytics_data",
    payload={"event": "page_view", "page": "/home"},
    priority=MessagePriority.LOW
)
```

### 自定义重试配置

```python
config = MQConfig(
    redis_url="redis://localhost:6379",
    max_retries=5,  # 最大重试5次
    retry_delays=[30, 60, 300, 900, 1800],  # 重试间隔：30s, 1m, 5m, 15m, 30m
    processing_timeout=300,  # 5分钟处理超时
)

mq = RedisMessageQueue(config)
```

### 消息生存时间(TTL)

```python
# 设置消息1小时后过期
await mq.produce(
    topic="temp_notification",
    payload={"message": "临时通知"},
    ttl=3600  # 1小时后过期
)
```

### 批量生产消息

```
# 批量发送多个消息
messages = [
    {"topic": "order_created", "payload": {"order_id": f"ORD_{i}"}}
    for i in range(100)
]

for msg in messages:
    await mq.produce(msg["topic"], msg["payload"])
```

## 配置参考

### MQConfig 完整参数

```
from mx_rmq import MQConfig

config = MQConfig(
    # Redis 连接配置
    redis_host="redis://localhost:6379",      # Redis连接URL
    redis_db=0,                              # Redis数据库编号 (0-15)
    redis_password=None,                     # Redis密码
    queue_prefix="",                         # 队列前缀，用于多环境隔离
    connection_pool_size=20,                 # 连接池大小
    
    # 消费者配置
    max_workers=5,                           # 最大工作协程数
    task_queue_size=8,                       # 本地任务队列大小
    
    # 消息生命周期配置
    message_ttl=86400,                       # 消息TTL（秒），默认24小时
    processing_timeout=180,                  # 消息处理超时（秒），默认3分钟
    
    # 重试配置
    max_retries=3,                           # 最大重试次数
    retry_delays=[60, 300, 1800],           # 重试延迟间隔（秒）
    
    # 死信队列配置
    enable_dead_letter=True,                 # 是否启用死信队列
    
    # 监控配置
    monitor_interval=30,                     # 监控检查间隔（秒）
    expired_check_interval=10,               # 过期消息检查间隔（秒）
    processing_monitor_interval=30,          # Processing队列监控间隔（秒）
    batch_size=100,                          # 批处理大小
)
```

### 环境变量配置

支持通过环境变量配置：

```bash
export REDIS_URL="redis://localhost:6379"
export REDIS_PASSWORD="your_password"
export MQ_MAX_WORKERS=10
export MQ_TASK_QUEUE_SIZE=20
export MQ_MESSAGE_TTL=86400
```

```python
import os
from mx_rmq import MQConfig

config = MQConfig(
    redis_host=os.getenv("REDIS_URL", "localhost"),
    redis_port=os.getenv("REDIS_PORT","6379"),
    redis_password=os.getenv("REDIS_PASSWORD"),
    max_workers=int(os.getenv("MQ_MAX_WORKERS", "5")),
    task_queue_size=int(os.getenv("MQ_TASK_QUEUE_SIZE", "8")),
    message_ttl=int(os.getenv("MQ_MESSAGE_TTL", "86400")),
)
```

## API 参考

### RedisMessageQueue 类

#### 初始化

```python
def __init__(self, config: MQConfig | None = None) -> None:
    """
    初始化消息队列
    
    Args:
        config: 消息队列配置，如为None则使用默认配置
    """
```

#### 核心方法

```python
async def produce(
    self,
    topic: str,
    payload: dict[str, Any],
    delay: int = 0,
    priority: MessagePriority = MessagePriority.NORMAL,
    ttl: int | None = None,
    message_id: str | None = None,
) -> str:
    """
    生产消息
    
    Args:
        topic: 主题名称
        payload: 消息负载（必须是可JSON序列化的字典）
        delay: 延迟执行时间（秒），0表示立即执行
        priority: 消息优先级
        ttl: 消息生存时间（秒），None使用配置默认值
        message_id: 消息ID，None则自动生成UUID
        
    Returns:
        消息ID（字符串）
        
    Raises:
        ValueError: 参数验证失败
        RedisError: Redis操作失败
    """

def register_handler(self, topic: str, handler: Callable) -> None:
    """
    注册消息处理器
    
    Args:
        topic: 主题名称
        handler: 处理函数，必须是async函数，接受一个dict参数
        
    Raises:
        ValueError: 处理器不是可调用对象
    """

async def start(self) -> None:
    """
    启动消息分发和消费（阻塞式）
    
    此方法会阻塞，直到收到停机信号(SIGINT/SIGTERM)
    
    Raises:
        RuntimeError: 系统未正确初始化
        RedisError: Redis连接错误
    """

async def start_background(self) -> Task:
    """
    启动消息分发和消费（非阻塞式）
    
    此方法不会阻塞，立即返回一个Task对象
    
    Returns:
        Task: 后台任务对象
        
    Raises:
        RuntimeError: 系统未正确初始化
        RedisError: Redis连接错误
    """

async def stop(self) -> None:
    """
    停止消息队列处理
    
    优雅地停止所有后台任务并清理资源
    """

async def initialize(self) -> None:
    """
    手动初始化消息队列
    
    通常在start/start_background之前自动调用
    """

async def cleanup(self) -> None:
    """
    清理资源，关闭Redis连接池
    """

def run(self, duration: float | None = None) -> None:
    """
    同步运行消息队列
    
    Args:
        duration: 运行时长（秒），None表示无限运行直到收到信号
    """

async def health_check(self) -> dict[str, Any]:
    """
    执行健康检查
    
    Returns:
        dict: 包含健康状态信息的字典
    """
```

#### 属性

```python
@property
def status(self) -> dict[str, Any]:
    """
    获取队列状态信息
    
    Returns:
        dict: 包含运行状态、初始化状态、活跃任务数等信息
    """

@property
def is_running(self) -> bool:
    """
    检查队列是否正在运行
    
    Returns:
        bool: 队列运行状态
    """
```

### Message 类

```python
@dataclass
class Message:
    """消息数据类"""
    id: str                    # 消息唯一ID
    version: str               # 消息格式版本
    topic: str                 # 主题名称  
    payload: dict[str, Any]    # 消息负载
    priority: MessagePriority  # 消息优先级
    created_at: int           # 创建时间戳（毫秒）
    meta: MessageMeta         # 消息元数据

@dataclass  
class MessageMeta:
    """消息元数据"""
    status: MessageStatus      # 消息状态
    retry_count: int          # 重试次数
    max_retries: int          # 最大重试次数
    retry_delays: list[int]   # 重试延迟配置
    last_error: str | None    # 最后一次错误信息
    expire_at: int            # 过期时间戳
    # ... 其他元数据字段
```

### 枚举类型

```python
class MessagePriority(str, Enum):
    """消息优先级"""
    HIGH = "high"      # 高优先级
    NORMAL = "normal"  # 普通优先级
    LOW = "low"        # 低优先级

class MessageStatus(str, Enum):
    """消息状态"""
    PENDING = "pending"        # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 已完成
    RETRYING = "retrying"      # 重试中
    DEAD_LETTER = "dead_letter" # 死信
```

## 监控和管理

### 指标收集

```python
from mx_rmq import MetricsCollector

# 创建指标收集器
collector = MetricsCollector(redis=mq.redis, queue_prefix=config.queue_prefix)

# 收集所有指标
metrics = await collector.collect_all_metrics(["order_created", "user_registration"])

# 打印关键指标
print(f"待处理消息: {metrics['queue.order_created.pending']}")
print(f"处理中消息: {metrics['queue.order_created.processing']}")
print(f"总吞吐量: {metrics['throughput.messages_per_minute']}")
print(f"死信队列: {metrics['queue.dlq.count']}")
```

### 队列监控

```python
# 监控单个队列
queue_metrics = await collector.collect_queue_metrics(["order_created"])
print(f"订单队列状态: {queue_metrics}")

# 监控处理性能
processing_metrics = await collector.collect_processing_metrics(["order_created"])
print(f"平均处理时间: {processing_metrics['order_created.avg_processing_time']}ms")
```

### 死信队列管理

```python
# 查看死信队列
dlq_count = await mq.redis.llen("dlq:queue")
print(f"死信队列消息数: {dlq_count}")

# 获取死信消息列表
dlq_messages = await mq.redis.lrange("dlq:queue", 0, 9)  # 获取前10条
for msg_id in dlq_messages:
    payload = await mq.redis.hget("dlq:payload:map", msg_id)
    print(f"死信消息: {msg_id} - {payload}")

# 手动重试死信消息（需要自定义实现）
async def retry_dead_message(message_id: str):
    # 从死信队列获取消息
    payload_json = await mq.redis.hget("dlq:payload:map", message_id)
    if payload_json:
        # 解析消息并重新生产
        message = json.loads(payload_json)
        await mq.produce(message["topic"], message["payload"])
        # 从死信队列移除
        await mq.redis.lrem("dlq:queue", 1, message_id)
        await mq.redis.hdel("dlq:payload:map", message_id)
```

### 实时监控脚本

```python
import asyncio
import time

async def monitor_loop():
    """实时监控循环"""
    collector = MetricsCollector(redis=mq.redis)
    
    while True:
        try:
            # 收集指标
            metrics = await collector.collect_all_metrics(["order_created"])
            
            # 输出关键指标
            print(f"[{time.strftime('%H:%M:%S')}] 队列状态:")
            print(f"  待处理: {metrics.get('queue.order_created.pending', 0)}")
            print(f"  处理中: {metrics.get('queue.order_created.processing', 0)}")
            print(f"  死信队列: {metrics.get('queue.dlq.count', 0)}")
            
            # 检查告警条件
            pending = metrics.get('queue.order_created.pending', 0)
            if pending > 100:
                print(f"⚠️  告警: 待处理消息积压 ({pending})")
                
            dlq_count = metrics.get('queue.dlq.count', 0)
            if dlq_count > 10:
                print(f"🚨 告警: 死信队列消息过多 ({dlq_count})")
                
        except Exception as e:
            print(f"监控错误: {e}")
            
        await asyncio.sleep(10)  # 每10秒检查一次

# 启动监控
asyncio.create_task(monitor_loop())
```

## 部署指南

### 高可用部署

**Redis Sentinel 配置:**
```python
import redis.sentinel

# 配置Sentinel
sentinels = [
    ('sentinel1', 26379),
    ('sentinel2', 26379), 
    ('sentinel3', 26379),
]

sentinel = redis.sentinel.Sentinel(sentinels, socket_timeout=0.1)

# 发现主节点
redis_master = sentinel.master_for('mymaster', socket_timeout=0.1)

# 自定义Redis连接
config = MQConfig(redis_url="")  # 留空，使用自定义连接
mq = RedisMessageQueue(config)
mq.redis = redis_master  # 使用Sentinel管理的连接
```

### 监控和告警

**Prometheus 指标暴露:**
```python
from prometheus_client import start_http_server, Gauge, Counter

# 定义指标
queue_size = Gauge('mq_queue_size', 'Queue size', ['topic', 'status'])
messages_processed = Counter('mq_messages_processed_total', 'Messages processed', ['topic', 'status'])

async def export_metrics():
    """导出Prometheus指标"""
    collector = MetricsCollector(redis=mq.redis)
    
    while True:
        metrics = await collector.collect_all_metrics(['order_created'])
        
        # 更新Prometheus指标
        queue_size.labels(topic='order_created', status='pending').set(
            metrics.get('queue.order_created.pending', 0)
        )
        queue_size.labels(topic='order_created', status='processing').set(
            metrics.get('queue.order_created.processing', 0)
        )
        
        await asyncio.sleep(30)

# 启动Prometheus HTTP服务器
start_http_server(8000)
asyncio.create_task(export_metrics())
```

## 最佳实践

### 1. 消息设计

**✅ 推荐做法:**
```python
# 消息结构清晰，包含必要的上下文信息
await mq.produce("order_created", {
    "order_id": "ORD_123456",
    "user_id": 789,
    "total_amount": 99.99,
    "currency": "USD",
    "timestamp": "2024-01-01T12:00:00Z",
    "metadata": {
        "source": "web",
        "version": "v1.0"
    }
})
```

**❌ 避免做法:**
```python
# 消息过于简单，缺少上下文
await mq.produce("process", {"id": 123})

# 消息过于复杂，包含大量数据
await mq.produce("user_update", {
    "user": {...},  # 包含用户的所有信息
    "history": [...],  # 包含完整历史记录
    "related_data": {...}  # 包含大量关联数据
})
```

### 2. 错误处理

**✅ 推荐做法:**
```python
async def handle_payment(payload: dict) -> None:
    try:
        order_id = payload["order_id"]
        amount = payload["amount"]
        
        # 参数验证
        if not order_id or amount <= 0:
            raise ValueError(f"无效的订单参数: {payload}")
            
        # 业务逻辑
        result = await process_payment(order_id, amount)
        
        # 记录成功日志
        logger.info("支付处理成功", order_id=order_id, amount=amount)
        
    except ValueError as e:
        # 参数错误，不重试
        logger.error("支付参数错误", error=str(e), payload=payload)
        raise  # 重新抛出，进入死信队列
        
    except PaymentGatewayError as e:
        # 外部服务错误，可重试
        logger.warning("支付网关错误", error=str(e), order_id=order_id)
        raise  # 重新抛出，触发重试
        
    except Exception as e:
        # 未知错误
        logger.error("支付处理失败", error=str(e), order_id=order_id)
        raise
```

### 3. 幂等性处理

```python
async def handle_order_created(payload: dict) -> None:
    order_id = payload["order_id"]
    
    # 检查是否已处理（幂等性保护）
    if await is_order_processed(order_id):
        logger.info("订单已处理，跳过", order_id=order_id)
        return
        
    try:
        # 处理订单
        await process_order(order_id)
        
        # 标记为已处理
        await mark_order_processed(order_id)
        
    except Exception as e:
        logger.error("订单处理失败", order_id=order_id, error=str(e))
        raise
```

### 4. 性能优化

**工作协程数调优:**
```python
import os
import multiprocessing

# 根据CPU核心数和IO特性调整工作协程数
cpu_count = multiprocessing.cpu_count()

config = MQConfig(
    # CPU密集型任务：工作协程数 = CPU核心数
    max_workers=cpu_count if is_cpu_intensive else cpu_count * 2,
    
    # IO密集型任务：工作协程数 = CPU核心数 * 2-4
    # max_workers=cpu_count * 3,
    
    # 任务队列大小应该大于工作协程数
    task_queue_size=max_workers * 2,
)
```

**批量处理优化:**
```python
async def handle_batch_emails(payload: dict) -> None:
    """批量处理邮件发送"""
    email_list = payload["emails"]
    
    # 分批处理，避免内存占用过大
    batch_size = 10
    for i in range(0, len(email_list), batch_size):
        batch = email_list[i:i + batch_size]
        
        # 并发发送邮件
        tasks = [send_email(email) for email in batch]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 避免过快的请求
        await asyncio.sleep(0.1)
```

### 5. API使用建议

#### 推荐使用非阻塞API

```python
# 推荐：使用非阻塞启动
async def recommended_usage():
    mq = RedisMessageQueue()
    mq.register_handler("topic", message_handler)
    
    # 非阻塞启动
    task = await mq.start_background()
    
    # 可以继续执行其他操作
    await do_other_work()
    
    # 优雅停止
    await mq.stop()

# 不推荐：使用阻塞式启动（除非有特殊需求）
async def legacy_usage():
    mq = RedisMessageQueue()
    mq.register_handler("topic", message_handler)
    
    # 会阻塞直到收到信号
    await mq.start()
```

#### 使用异步上下文管理器自动管理资源

```
# 推荐：使用异步上下文管理器
async def context_manager_usage():
    async with RedisMessageQueue() as mq:
        mq.register_handler("topic", message_handler)
        await mq.start_background()
        await mq.produce("topic", {"data": "example"})
        await asyncio.sleep(5)
        # 自动清理资源
```

#### 合理使用同步API

```
# 适用于简单场景的同步API
def simple_usage():
    mq = RedisMessageQueue()
    mq.register_handler("topic", message_handler)
    # 运行10秒后自动停止
    mq.run(duration=10.0)
```

### 6. 多组消费的实现方案

由于系统不支持消费者组功能，如需实现多组消费同一消息，建议采用以下方案：

**✅ 推荐做法:**
```python
# 方案1：创建多个topic，发送多次消息
async def send_order_created(order_data: dict):
    """发送订单创建消息到多个处理组"""
    # 发送到不同的处理组
    await mq.produce("order_created_payment", order_data)    # 支付处理组
    await mq.produce("order_created_inventory", order_data)  # 库存处理组
    await mq.produce("order_created_analytics", order_data)  # 分析处理组
    await mq.produce("order_created_notification", order_data) # 通知处理组

# 注册不同的处理器
@mq.register_handler("order_created_payment")
async def handle_payment_processing(payload: dict):
    """处理支付相关逻辑"""
    await process_payment(payload)

@mq.register_handler("order_created_inventory")
async def handle_inventory_processing(payload: dict):
    """处理库存相关逻辑"""
    await update_inventory(payload)

@mq.register_handler("order_created_analytics")
async def handle_analytics_processing(payload: dict):
    """处理分析相关逻辑"""
    await update_analytics(payload)

@mq.register_handler("order_created_notification")
async def handle_notification_processing(payload: dict):
    """处理通知相关逻辑"""
    await send_notifications(payload)
```

**方案2：使用统一的分发器**
```python
# 创建一个分发器topic
@mq.register_handler("order_created")
async def order_dispatcher(payload: dict):
    """订单消息分发器"""
    order_id = payload["order_id"]
    
    # 并发分发到各个处理组
    tasks = [
        mq.produce("order_payment", payload),
        mq.produce("order_inventory", payload),
        mq.produce("order_analytics", payload),
        mq.produce("order_notification", payload),
    ]
    
    try:
        await asyncio.gather(*tasks)
        logger.info("订单消息分发成功", order_id=order_id)
    except Exception as e:
        logger.error("订单消息分发失败", order_id=order_id, error=str(e))
        raise
```

**方案3：使用topic命名规范**
```python
# 使用统一的命名规范
TOPIC_PATTERNS = {
    "order_created": [
        "order_created.payment",
        "order_created.inventory", 
        "order_created.analytics",
        "order_created.notification"
    ]
}

async def broadcast_message(base_topic: str, payload: dict):
    """广播消息到多个相关topic"""
    topics = TOPIC_PATTERNS.get(base_topic, [base_topic])
    
    tasks = [mq.produce(topic, payload) for topic in topics]
    await asyncio.gather(*tasks)
    
    logger.info("消息广播完成", base_topic=base_topic, target_topics=topics)

# 使用示例
await broadcast_message("order_created", order_data)
```

### 6. 监控和告警

```python
async def setup_monitoring():
    """设置监控和告警"""
    collector = MetricsCollector(redis=mq.redis)
    
    while True:
        try:
            metrics = await collector.collect_all_metrics(["order_created"])
            
            # 队列积压告警
            pending = metrics.get('queue.order_created.pending', 0)
            if pending > 1000:
                await send_alert(f"队列积压严重: {pending} 条消息待处理")
                
            # 死信队列告警  
            dlq_count = metrics.get('queue.dlq.count', 0)
            if dlq_count > 50:
                await send_alert(f"死信队列消息过多: {dlq_count} 条")
                
            # 处理时间告警
            avg_time = metrics.get('processing.order_created.avg_time', 0)
            if avg_time > 30000:  # 30秒
                await send_alert(f"消息处理时间过长: {avg_time}ms")
                
        except Exception as e:
            logger.error("监控检查失败", error=str(e))
            
        await asyncio.sleep(60)  # 每分钟检查一次
```

## 故障排除

### 常见问题

#### Q1: 消息丢失怎么办？

**症状:** 发送的消息没有被处理

**可能原因:**
1. Redis 连接中断
2. 消费者没有正确启动
3. 消息处理器抛出异常但没有正确处理

**解决方案:**
```python
# 1. 检查Redis连接
try:
    await mq.redis.ping()
    print("Redis连接正常")
except Exception as e:
    print(f"Redis连接失败: {e}")

# 2. 检查消息是否在队列中
pending_count = await mq.redis.llen("order_created:pending")
processing_count = await mq.redis.llen("order_created:processing")
print(f"待处理: {pending_count}, 处理中: {processing_count}")

# 3. 检查死信队列
dlq_count = await mq.redis.llen("dlq:queue")
print(f"死信队列: {dlq_count}")
```

#### Q2: 消息处理过慢

**症状:** 队列积压，消息处理不及时

**可能原因:**
1. 工作协程数不足
2. 处理函数执行时间过长
3. Redis性能瓶颈

**解决方案:**
```python
# 1. 增加工作协程数
config = MQConfig(max_workers=20)  # 增加到20个

# 2. 优化处理函数
async def optimized_handler(payload: dict) -> None:
    # 使用异步IO
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, json=payload)
    
    # 避免阻塞操作
    await asyncio.to_thread(blocking_operation, payload)

# 3. 监控处理时间
import time

async def timed_handler(payload: dict) -> None:
    start_time = time.time()
    try:
        await actual_handler(payload)
    finally:
        processing_time = time.time() - start_time
        if processing_time > 5:  # 处理时间超过5秒
            logger.warning("处理时间过长", time=processing_time, payload=payload)
```

#### Q3: 内存使用过高

**症状:** 应用内存持续增长

**可能原因:**
1. 本地队列积压
2. 消息对象没有正确释放
3. Redis连接池过大

**解决方案:**
```python
# 1. 调整队列大小
config = MQConfig(
    task_queue_size=10,  # 减少本地队列大小
    connection_pool_size=10,  # 减少连接池大小
)

# 2. 监控内存使用
import psutil
import gc

async def memory_monitor():
    while True:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > 500:  # 内存超过500MB
            logger.warning("内存使用过高", memory_mb=memory_mb)
            gc.collect()  # 强制垃圾回收
            
        await asyncio.sleep(60)
```


### 性能诊断

#### 延迟分析

```python
import time
from collections import defaultdict

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    async def analyze_handler(self, handler_name: str, handler_func):
        """分析处理器性能"""
        async def wrapped_handler(payload: dict):
            start_time = time.time()
            try:
                result = await handler_func(payload)
                return result
            finally:
                end_time = time.time()
                processing_time = (end_time - start_time) * 1000  # 毫秒
                self.metrics[handler_name].append(processing_time)
                
                # 定期输出统计信息
                if len(self.metrics[handler_name]) % 100 == 0:
                    times = self.metrics[handler_name]
                    avg_time = sum(times) / len(times)
                    max_time = max(times)
                    min_time = min(times)
                    
                    print(f"{handler_name} 性能统计 (最近100次):")
                    print(f"  平均时间: {avg_time:.2f}ms")
                    print(f"  最大时间: {max_time:.2f}ms") 
                    print(f"  最小时间: {min_time:.2f}ms")
        
        return wrapped_handler

# 使用示例
analyzer = PerformanceAnalyzer()

@mq.register_handler("order_created")
async def handle_order(payload: dict):
    # 处理逻辑
    await process_order(payload)

# 包装处理器进行性能分析
mq.handlers["order_created"] = await analyzer.analyze_handler(
    "order_created", 
    handle_order
)
```

