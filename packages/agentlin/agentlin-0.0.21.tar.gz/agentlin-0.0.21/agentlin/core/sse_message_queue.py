"""
基于 AgentMessageQueue 的 SSE 流式响应消息队列扩展

实现原理：
1. 扩展消息队列支持 SSE 事件发布和订阅
2. 提供实时事件流传输能力
3. 支持多客户端同时订阅同一事件流
4. 与现有的 RPC 和消息传递机制无缝集成
"""

import asyncio
import json
import uuid
import time
from typing import Dict, Set, Optional, AsyncIterable, Any, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from agentlin.core.agent_message_queue import (
    AgentMessageQueue,
    AgentMessage,
    MessageType,
    MSG_RPC_REQUEST,
    MSG_RPC_RESPONSE
)
from agentlin.core.types import (
    SendTaskStreamingResponse,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    JSONRPCError
)


# SSE 相关消息类型
MSG_SSE_EVENT = "SSE_EVENT"
MSG_SSE_SUBSCRIBE = "SSE_SUBSCRIBE"
MSG_SSE_UNSUBSCRIBE = "SSE_UNSUBSCRIBE"


@dataclass
class SSEEvent:
    """SSE 事件数据结构"""

    event_id: str
    event_type: str
    channel: str
    data: Dict[str, Any]
    timestamp: float = None
    retry_count: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class SSESubscription:
    """SSE 订阅信息"""

    subscriber_id: str
    channel: str
    last_event_id: Optional[str] = None
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class SSEMessageQueue(AgentMessageQueue):
    """
    支持 SSE 流式响应的消息队列

    扩展 AgentMessageQueue 以支持：
    1. SSE 事件的发布和订阅
    2. 多客户端实时事件流
    3. 事件持久化和重放
    4. 与现有 RPC 系统的集成
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # SSE 相关状态管理
        self.sse_subscribers: Dict[str, Set[str]] = {}  # channel -> set of subscriber_ids
        self.sse_subscriptions: Dict[str, SSESubscription] = {}  # subscriber_id -> subscription
        self.sse_event_queues: Dict[str, asyncio.Queue] = {}  # subscriber_id -> event queue
        self.sse_event_history: Dict[str, list[SSEEvent]] = {}  # channel -> event history (for replay)

        # SSE 配置
        self.sse_history_size = 100  # 每个频道保留的历史事件数量
        self.sse_heartbeat_interval = 30  # SSE 心跳间隔（秒）

        # 注册 SSE 消息处理器
        self.register_message_handler(MSG_SSE_EVENT, self._handle_sse_event)
        self.register_message_handler(MSG_SSE_SUBSCRIBE, self._handle_sse_subscribe)
        self.register_message_handler(MSG_SSE_UNSUBSCRIBE, self._handle_sse_unsubscribe)

        # 启动心跳任务
        self._heartbeat_task = None

    async def initialize(self):
        """初始化 SSE 消息队列"""
        await super().initialize()

        # 启动 SSE 心跳任务
        self._heartbeat_task = asyncio.create_task(self._sse_heartbeat_loop())
        self.logger.info("SSE 消息队列初始化完成")

    async def close(self):
        """关闭 SSE 消息队列"""
        # 停止心跳任务
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # 清理所有 SSE 订阅
        await self._cleanup_all_sse_subscriptions()

        await super().close()

    async def publish_sse_event(
        self,
        channel: str,
        event_type: str,
        data: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> bool:
        """
        发布 SSE 事件到指定频道

        Args:
            channel: 事件频道
            event_type: 事件类型
            data: 事件数据
            event_id: 可选的事件ID（如果不提供则自动生成）

        Returns:
            成功发布则返回True
        """
        if event_id is None:
            event_id = str(uuid.uuid4())

        sse_event = SSEEvent(
            event_id=event_id,
            event_type=event_type,
            channel=channel,
            data=data
        )

        # 保存到历史记录
        await self._save_sse_event_to_history(sse_event)

        # 广播事件到所有相关实例
        message = AgentMessage(
            sender=self.agent_id,
            message_type=MSG_SSE_EVENT,
            payload=asdict(sse_event)
        )

        success = await self.broadcast_message(
            message_type=MSG_SSE_EVENT,
            payload=asdict(sse_event),
            target_pattern=f"sse.{channel}"
        )

        self.logger.debug(f"发布 SSE 事件到频道 {channel}: {event_type}")
        return success

    async def subscribe_sse_channel(
        self,
        channel: str,
        subscriber_id: Optional[str] = None,
        last_event_id: Optional[str] = None
    ) -> tuple[str, asyncio.Queue]:
        """
        订阅 SSE 频道

        Args:
            channel: 要订阅的频道
            subscriber_id: 订阅者ID（如果不提供则自动生成）
            last_event_id: 最后接收的事件ID（用于断线重连）

        Returns:
            tuple of (subscriber_id, event_queue)
        """
        if subscriber_id is None:
            subscriber_id = str(uuid.uuid4())

        # 创建事件队列
        event_queue = asyncio.Queue(maxsize=1000)

        # 保存订阅信息
        subscription = SSESubscription(
            subscriber_id=subscriber_id,
            channel=channel,
            last_event_id=last_event_id
        )

        self.sse_subscriptions[subscriber_id] = subscription
        self.sse_event_queues[subscriber_id] = event_queue

        # 添加到频道订阅者列表
        if channel not in self.sse_subscribers:
            self.sse_subscribers[channel] = set()
        self.sse_subscribers[channel].add(subscriber_id)

        # 如果提供了 last_event_id，发送历史事件
        if last_event_id:
            await self._replay_sse_events(subscriber_id, channel, last_event_id)

        self.logger.info(f"订阅者 {subscriber_id} 订阅频道 {channel}")
        return subscriber_id, event_queue

    async def unsubscribe_sse_channel(self, subscriber_id: str) -> bool:
        """
        取消订阅 SSE 频道

        Args:
            subscriber_id: 订阅者ID

        Returns:
            成功取消订阅则返回True
        """
        if subscriber_id not in self.sse_subscriptions:
            return False

        subscription = self.sse_subscriptions[subscriber_id]
        channel = subscription.channel

        # 从频道订阅者列表中移除
        if channel in self.sse_subscribers:
            self.sse_subscribers[channel].discard(subscriber_id)
            if not self.sse_subscribers[channel]:
                del self.sse_subscribers[channel]

        # 清理订阅信息
        del self.sse_subscriptions[subscriber_id]

        # 关闭事件队列
        if subscriber_id in self.sse_event_queues:
            queue = self.sse_event_queues[subscriber_id]
            # 发送结束信号
            try:
                await queue.put(None)
            except:
                pass
            del self.sse_event_queues[subscriber_id]

        self.logger.info(f"订阅者 {subscriber_id} 取消订阅频道 {channel}")
        return True

    async def create_sse_stream(
        self,
        channel: str,
        subscriber_id: Optional[str] = None,
        last_event_id: Optional[str] = None
    ) -> AsyncIterable[Dict[str, str]]:
        """
        创建 SSE 事件流

        Args:
            channel: 频道名称
            subscriber_id: 订阅者ID
            last_event_id: 最后的事件ID（用于重连）

        Yields:
            SSE 格式的事件字典
        """
        self.logger.info(f"创建 SSE 流：频道 {channel}, 订阅者 {subscriber_id}")
        subscriber_id, event_queue = await self.subscribe_sse_channel(
            channel, subscriber_id, last_event_id
        )

        try:
            while True:
                try:
                    self.logger.debug(f"等待 SSE 事件：订阅者 {subscriber_id}, 频道 {channel}")
                    # 等待事件，带超时以支持心跳
                    event = await asyncio.wait_for(
                        event_queue.get(),
                        timeout=self.sse_heartbeat_interval
                    )

                    if event is None:  # 结束信号
                        break

                    # 转换为 SSE 格式
                    if isinstance(event, SSEEvent):
                        yield {
                            "id": event.event_id,
                            "event": event.event_type,
                            "data": json.dumps(event.data, ensure_ascii=False)
                        }
                    elif isinstance(event, dict):
                        # 兼容其他格式
                        yield {
                            "data": json.dumps(event, ensure_ascii=False)
                        }

                except asyncio.TimeoutError:
                    # 发送心跳
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps({"timestamp": time.time()})
                    }

                except Exception as e:
                    self.logger.error(f"SSE 流处理错误: {e}")
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": str(e)})
                    }
                    break

        finally:
            # 清理订阅
            await self.unsubscribe_sse_channel(subscriber_id)

    async def _handle_sse_event(self, message: AgentMessage):
        """处理 SSE 事件消息"""
        try:
            payload = message.payload or {}
            sse_event = SSEEvent(**payload)

            # 分发事件到本地订阅者
            await self._distribute_sse_event(sse_event)

        except Exception as e:
            self.logger.error(f"处理 SSE 事件失败: {e}")

    async def _handle_sse_subscribe(self, message: AgentMessage):
        """处理 SSE 订阅消息"""
        # 实现订阅逻辑（如果需要跨实例订阅同步）
        pass

    async def _handle_sse_unsubscribe(self, message: AgentMessage):
        """处理 SSE 取消订阅消息"""
        # 实现取消订阅逻辑（如果需要跨实例订阅同步）
        pass

    async def _distribute_sse_event(self, sse_event: SSEEvent):
        """分发 SSE 事件到本地订阅者"""
        channel = sse_event.channel

        if channel not in self.sse_subscribers:
            return

        # 获取频道的所有订阅者
        subscribers = self.sse_subscribers[channel].copy()

        for subscriber_id in subscribers:
            if subscriber_id in self.sse_event_queues:
                try:
                    await self.sse_event_queues[subscriber_id].put(sse_event)
                except Exception as e:
                    self.logger.error(f"分发事件到订阅者 {subscriber_id} 失败: {e}")
                    # 移除失效的订阅者
                    await self.unsubscribe_sse_channel(subscriber_id)

    async def _save_sse_event_to_history(self, sse_event: SSEEvent):
        """保存 SSE 事件到历史记录"""
        channel = sse_event.channel

        if channel not in self.sse_event_history:
            self.sse_event_history[channel] = []

        self.sse_event_history[channel].append(sse_event)

        # 限制历史记录大小
        if len(self.sse_event_history[channel]) > self.sse_history_size:
            self.sse_event_history[channel] = self.sse_event_history[channel][-self.sse_history_size:]

    async def _replay_sse_events(self, subscriber_id: str, channel: str, last_event_id: str):
        """重放 SSE 事件（用于断线重连）"""
        if channel not in self.sse_event_history:
            return

        history = self.sse_event_history[channel]

        # 找到最后一个事件的位置
        start_index = 0
        for i, event in enumerate(history):
            if event.event_id == last_event_id:
                start_index = i + 1
                break

        # 重放后续事件
        for event in history[start_index:]:
            if subscriber_id in self.sse_event_queues:
                try:
                    await self.sse_event_queues[subscriber_id].put(event)
                except Exception as e:
                    self.logger.error(f"重放事件到订阅者 {subscriber_id} 失败: {e}")
                    break

    async def _sse_heartbeat_loop(self):
        """SSE 心跳循环"""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.sse_heartbeat_interval)

                # 发送心跳到所有活跃的订阅者
                for subscriber_id in list(self.sse_event_queues.keys()):
                    try:
                        heartbeat_event = SSEEvent(
                            event_id=str(uuid.uuid4()),
                            event_type="heartbeat",
                            channel="system",
                            data={"timestamp": time.time()}
                        )
                        await self.sse_event_queues[subscriber_id].put(heartbeat_event)
                    except Exception as e:
                        self.logger.debug(f"心跳发送失败，移除订阅者 {subscriber_id}: {e}")
                        await self.unsubscribe_sse_channel(subscriber_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"SSE 心跳循环错误: {e}")

    async def _cleanup_all_sse_subscriptions(self):
        """清理所有 SSE 订阅"""
        subscribers = list(self.sse_subscriptions.keys())
        for subscriber_id in subscribers:
            await self.unsubscribe_sse_channel(subscriber_id)

    # RPC 方法：远程调用 SSE 事件发布
    @staticmethod
    def register_sse_rpc_methods(sse_queue: 'SSEMessageQueue'):
        """注册 SSE 相关的 RPC 方法"""

        @sse_queue.register_rpc("publish_sse_event")
        async def rpc_publish_sse_event(channel: str, event_type: str, data: dict, event_id: str = None):
            """RPC 方法：发布 SSE 事件"""
            return await sse_queue.publish_sse_event(channel, event_type, data, event_id)

        @sse_queue.register_rpc("get_sse_subscribers")
        async def rpc_get_sse_subscribers(channel: str = None):
            """RPC 方法：获取订阅者信息"""
            if channel:
                return {
                    "channel": channel,
                    "subscribers": list(sse_queue.sse_subscribers.get(channel, set()))
                }
            else:
                return {
                    "all_channels": {
                        ch: list(subs) for ch, subs in sse_queue.sse_subscribers.items()
                    }
                }
