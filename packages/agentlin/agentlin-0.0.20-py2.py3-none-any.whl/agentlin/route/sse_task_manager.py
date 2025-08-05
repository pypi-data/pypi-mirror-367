"""
集成 SSE 消息队列的任务管理器

将任务状态变化自动发布为 SSE 事件，实现实时的任务状态流式推送
"""

import asyncio
import json
from typing import Dict, Optional, Any, AsyncIterable, Union
from loguru import logger

from agentlin.core.sse_message_queue import SSEMessageQueue, SSEEvent
from agentlin.route.task_manager import InMemoryTaskManager
from agentlin.core.types import (
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    TaskStatus,
    TaskState,
    JSONRPCError,
    JSONRPCResponse
)


class SSETaskManager(InMemoryTaskManager, SSEMessageQueue):
    """
    集成 SSE 消息队列的任务管理器

    功能特性：
    1. 自动将任务状态变化发布为 SSE 事件
    2. 支持任务执行过程的实时流式推送
    3. 提供基于频道的任务订阅机制
    4. 与现有任务管理系统无缝集成
    """

    def __init__(self, *args, **kwargs):
        # 初始化时传递所有参数给父类
        InMemoryTaskManager.__init__(self)
        SSEMessageQueue.__init__(self, *args, **kwargs)

        # SSE 任务相关配置
        self.task_sse_enabled = True
        self.default_task_channel_prefix = "task"

        # 注册 SSE RPC 方法
        SSEMessageQueue.register_sse_rpc_methods(self)

        self.logger.info("SSE 任务管理器初始化完成")

    def get_task_channel(self, task_id: str) -> str:
        """获取任务的 SSE 频道名称"""
        return f"{self.default_task_channel_prefix}.{task_id}"

    def get_global_task_channel(self) -> str:
        """获取全局任务频道名称"""
        return f"{self.default_task_channel_prefix}.global"

    async def publish_task_event(
        self,
        task_id: str,
        event_type: str,
        data: Dict[str, Any],
        to_global: bool = True
    ) -> bool:
        """
        发布任务相关的 SSE 事件

        Args:
            task_id: 任务ID
            event_type: 事件类型
            data: 事件数据
            to_global: 是否同时发布到全局频道

        Returns:
            发布成功则返回True
        """
        if not self.task_sse_enabled:
            return True

        # 发布到任务专用频道
        task_channel = self.get_task_channel(task_id)
        success = await self.publish_sse_event(task_channel, event_type, data)

        # 发布到全局任务频道
        if to_global and success:
            global_channel = self.get_global_task_channel()
            await self.publish_sse_event(
                global_channel,
                event_type,
                {**data, "task_id": task_id}
            )

        return success

    async def update_store(self, task_id: str, status: TaskStatus, metadata: Optional[Dict] = None) -> Any:
        """重写任务状态更新，添加 SSE 事件发布"""
        # 调用父类方法更新任务状态
        task = await super().update_store(task_id, status, metadata)

        # 发布任务状态变化事件
        await self.publish_task_event(
            task_id=task_id,
            event_type="task_status_updated",
            data={
                "task_id": task_id,
                "status": status.model_dump() if hasattr(status, 'model_dump') else status.dict(),
                "metadata": metadata,
                "timestamp": asyncio.get_event_loop().time()
            }
        )

        return task

    async def enqueue_events_for_sse(self, task_id: str, task_update_event: Any) -> None:
        """重写 SSE 事件入队，同时发布到消息队列"""
        # 调用父类方法处理本地 SSE 订阅者
        await super().enqueue_events_for_sse(task_id, task_update_event)

        # 发布到消息队列 SSE 系统
        event_data = None
        event_type = "task_update"

        if isinstance(task_update_event, TaskArtifactUpdateEvent):
            event_type = "task_artifact_update"
            event_data = {
                "artifact_id": task_update_event.id,
                "metadata": task_update_event.metadata,
                "timestamp": asyncio.get_event_loop().time()
            }

        elif isinstance(task_update_event, TaskStatusUpdateEvent):
            event_type = "task_status_update"
            event_data = {
                "status": task_update_event.status.model_dump() if hasattr(task_update_event.status, 'model_dump') else task_update_event.status.dict(),
                "final": task_update_event.final,
                "metadata": getattr(task_update_event, 'metadata', None),
                "timestamp": asyncio.get_event_loop().time()
            }

        elif isinstance(task_update_event, JSONRPCError):
            event_type = "task_error"
            event_data = {
                "error": {
                    "code": task_update_event.code,
                    "message": task_update_event.message,
                    "data": task_update_event.data
                },
                "timestamp": asyncio.get_event_loop().time()
            }

        else:
            # 通用事件处理
            event_data = {
                "event": str(task_update_event),
                "event_type": type(task_update_event).__name__,
                "timestamp": asyncio.get_event_loop().time()
            }

        if event_data:
            await self.publish_task_event(
                task_id=task_id,
                event_type=event_type,
                data=event_data
            )

    async def create_task_sse_stream(
        self,
        task_id: str,
        subscriber_id: Optional[str] = None,
        last_event_id: Optional[str] = None
    ) -> AsyncIterable[Dict[str, str]]:
        """
        为特定任务创建 SSE 事件流

        Args:
            task_id: 任务ID
            subscriber_id: 订阅者ID
            last_event_id: 最后接收的事件ID

        Yields:
            SSE 格式的事件字典
        """
        task_channel = self.get_task_channel(task_id)

        async for event in self.create_sse_stream(task_channel, subscriber_id, last_event_id):
            yield event

    async def create_global_task_sse_stream(
        self,
        subscriber_id: Optional[str] = None,
        last_event_id: Optional[str] = None
    ) -> AsyncIterable[Dict[str, str]]:
        """
        创建全局任务 SSE 事件流

        Args:
            subscriber_id: 订阅者ID
            last_event_id: 最后接收的事件ID

        Yields:
            SSE 格式的事件字典
        """
        global_channel = self.get_global_task_channel()

        async for event in self.create_sse_stream(global_channel, subscriber_id, last_event_id):
            yield event

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        """重写任务订阅，支持 SSE 流式响应"""
        # 获取任务参数
        task_send_params = request.params
        task_id = task_send_params.id

        # 设置 SSE 消费者（兼容现有的本地 SSE 系统）
        sse_event_queue = await self.setup_sse_consumer(task_id)

        # 启动任务处理（异步执行）
        asyncio.create_task(self._process_task_async(request))

        # 返回组合的 SSE 流（本地 + 消息队列）
        return self._create_combined_sse_stream(request.id, task_id, sse_event_queue)

    async def _process_task_async(self, request: SendTaskStreamingRequest):
        """异步处理任务（避免阻塞 SSE 流）"""
        try:
            # 调用原始的任务处理逻辑
            # 这里需要根据实际的任务类型调用对应的处理方法
            # 比如如果是 SessionTaskManager，就调用其 _stream_generator
            task_send_params = request.params
            task_id = task_send_params.id

            # 发布任务开始事件
            await self.publish_task_event(
                task_id=task_id,
                event_type="task_started",
                data={
                    "request_id": request.id,
                    "task_params": task_send_params.model_dump() if hasattr(task_send_params, 'model_dump') else task_send_params.dict(),
                    "timestamp": asyncio.get_event_loop().time()
                }
            )

            # 实际的任务处理逻辑应该在子类中实现
            await self._execute_task_logic(request)

        except Exception as e:
            # 发布错误事件
            await self.publish_task_event(
                task_id=task_send_params.id,
                event_type="task_error",
                data={
                    "error": str(e),
                    "timestamp": asyncio.get_event_loop().time()
                }
            )
            logger.error(f"任务处理异常: {e}")

    async def _execute_task_logic(self, request: SendTaskStreamingRequest):
        """
        执行实际的任务逻辑

        子类应该重写此方法来实现具体的任务处理
        """
        # 默认实现：只是等待一下然后完成
        await asyncio.sleep(1)

        task_send_params = request.params
        task_id = task_send_params.id

        # 发布任务完成事件
        await self.publish_task_event(
            task_id=task_id,
            event_type="task_completed",
            data={
                "result": "Task completed successfully",
                "timestamp": asyncio.get_event_loop().time()
            }
        )

    async def _create_combined_sse_stream(
        self,
        request_id: str,
        task_id: str,
        local_sse_queue: asyncio.Queue
    ) -> AsyncIterable[SendTaskStreamingResponse]:
        """
        创建组合的 SSE 流（本地队列 + 消息队列）

        Args:
            request_id: 请求ID
            task_id: 任务ID
            local_sse_queue: 本地 SSE 事件队列

        Yields:
            SendTaskStreamingResponse 对象
        """
        # 创建消息队列 SSE 流
        mq_sse_stream = self.create_task_sse_stream(task_id)

        # 创建本地 SSE 流
        local_sse_stream = self.dequeue_events_for_sse(request_id, task_id, local_sse_queue)

        # 合并两个流
        async def combined_stream():
            local_task = asyncio.create_task(self._consume_local_stream(local_sse_stream))
            mq_task = asyncio.create_task(self._consume_mq_stream(mq_sse_stream, request_id))

            try:
                # 等待任一流完成或出错
                done, pending = await asyncio.wait(
                    [local_task, mq_task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                # 获取完成的结果
                for task in done:
                    async for item in task.result():
                        yield item

                # 取消未完成的任务
                for task in pending:
                    task.cancel()

            except Exception as e:
                logger.error(f"组合 SSE 流处理错误: {e}")
                # 发送错误响应
                yield SendTaskStreamingResponse(
                    id=request_id,
                    error=JSONRPCError(code=-32000, message=f"SSE stream error: {str(e)}")
                )

        async for item in combined_stream():
            yield item

    async def _consume_local_stream(self, local_stream: AsyncIterable[SendTaskStreamingResponse]):
        """消费本地 SSE 流"""
        async for item in local_stream:
            yield item

    async def _consume_mq_stream(self, mq_stream: AsyncIterable[Dict[str, str]], request_id: str):
        """消费消息队列 SSE 流并转换为 SendTaskStreamingResponse"""
        async for sse_event in mq_stream:
            try:
                # 解析 SSE 事件数据
                if "data" in sse_event:
                    event_data = json.loads(sse_event["data"])

                    # 根据事件类型创建相应的响应
                    if sse_event.get("event") == "task_artifact_update":
                        yield SendTaskStreamingResponse(
                            id=request_id,
                            result=TaskArtifactUpdateEvent(
                                id=event_data.get("artifact_id", ""),
                                metadata=event_data.get("metadata", {})
                            )
                        )

                    elif sse_event.get("event") == "task_status_update":
                        yield SendTaskStreamingResponse(
                            id=request_id,
                            result=TaskStatusUpdateEvent(
                                id=event_data.get("task_id", ""),
                                status=TaskStatus(**event_data.get("status", {})),
                                final=event_data.get("final", False),
                                metadata=event_data.get("metadata")
                            )
                        )

                    elif sse_event.get("event") == "task_error":
                        error_info = event_data.get("error", {})
                        yield SendTaskStreamingResponse(
                            id=request_id,
                            error=JSONRPCError(
                                code=error_info.get("code", -32000),
                                message=error_info.get("message", "Unknown error"),
                                data=error_info.get("data")
                            )
                        )

                    # 跳过心跳和其他系统事件
                    elif sse_event.get("event") not in ["heartbeat"]:
                        # 处理其他类型的事件
                        yield SendTaskStreamingResponse(
                            id=request_id,
                            result=TaskArtifactUpdateEvent(
                                id="system",
                                metadata={
                                    "event_type": sse_event.get("event", "unknown"),
                                    "data": event_data
                                }
                            )
                        )

            except Exception as e:
                logger.error(f"解析消息队列 SSE 事件失败: {e}")
                # 继续处理下一个事件
                continue


# 示例：扩展 SessionTaskManager 以支持 SSE 消息队列
class SSESessionTaskManager(SSETaskManager):
    """集成 SSE 消息队列的会话任务管理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 导入 session manager 的实际实现
        from agentlin.route.session_manager import SessionTaskManager
        self._session_manager = SessionTaskManager()

    async def _handle_regular_message(self, message):
        return await super()._handle_regular_message(message)

    async def on_send_task(self, request):
        return await super().on_send_task(request)



    async def _execute_task_logic(self, request: SendTaskStreamingRequest):
        """执行会话任务的实际逻辑"""
        # 调用原始的 SessionTaskManager 逻辑
        task_send_params = request.params
        session_id = task_send_params.sessionId

        # 调用原始的流生成器
        original_stream = await self._session_manager.on_send_task_subscribe(request)

        # 处理原始流并发布到消息队列
        async for response in original_stream:
            if isinstance(response, SendTaskStreamingResponse):
                # 将响应事件发布到消息队列
                if response.result:
                    await self.enqueue_events_for_sse(task_send_params.id, response.result)
                if response.error:
                    await self.enqueue_events_for_sse(task_send_params.id, response.error)
