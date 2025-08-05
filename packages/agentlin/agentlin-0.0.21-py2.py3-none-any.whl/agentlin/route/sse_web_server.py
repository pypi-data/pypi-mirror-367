"""
基于消息队列的 SSE 流式响应 Web 服务器

提供 RESTful API 和 SSE 流式接口，实现：
1. 任务的 SSE 流式订阅
2. 实时任务状态推送
3. 跨实例的任务事件同步
4. 支持断线重连的 SSE 机制
"""

import asyncio
import json
import uuid
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, HTTPException, Query, Header
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from loguru import logger

from agentlin.route.sse_task_manager import SSESessionTaskManager
from agentlin.core.types import (
    SendTaskRequest,
    SendTaskResponse,
    SendTaskStreamingRequest,
    TaskSendParams,
    GetTaskRequest,
    GetTaskResponse
)


# 请求/响应模型
class SSESubscribeRequest(BaseModel):
    """SSE 订阅请求"""
    channel: str
    last_event_id: Optional[str] = None


class TaskSSESubscribeRequest(BaseModel):
    """任务 SSE 订阅请求"""
    task_id: str
    last_event_id: Optional[str] = None


class PublishEventRequest(BaseModel):
    """发布事件请求"""
    channel: str
    event_type: str
    data: Dict[str, Any]
    event_id: Optional[str] = None


# 创建 FastAPI 应用
app = FastAPI(
    title="SSE Task Manager API",
    description="基于消息队列的 SSE 流式任务管理 API",
    version="1.0.0"
)

# 创建 SSE 任务管理器实例
sse_task_manager = SSESessionTaskManager(
    agent_id="sse_web_server",
    rabbitmq_host="localhost",
    rabbitmq_port=5672
)


@app.on_event("startup")
async def startup():
    """应用启动时初始化消息队列"""
    try:
        await sse_task_manager.initialize()
        logger.info("SSE 任务管理器初始化成功")
    except Exception as e:
        logger.error(f"SSE 任务管理器初始化失败: {e}")
        raise


@app.on_event("shutdown")
async def shutdown():
    """应用关闭时清理资源"""
    try:
        await sse_task_manager.close()
        logger.info("SSE 任务管理器已关闭")
    except Exception as e:
        logger.error(f"SSE 任务管理器关闭失败: {e}")


# ============ 任务管理接口 ============

@app.post("/api/v1/tasks", response_model=SendTaskResponse)
async def create_task(request: SendTaskRequest):
    """
    创建新任务（非流式）
    """
    try:
        response = await sse_task_manager.on_send_task(request)
        return response
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tasks/stream")
async def create_task_stream(request: SendTaskStreamingRequest):
    """
    创建任务并返回 SSE 流式响应
    """
    try:
        # 获取流式响应
        stream = await sse_task_manager.on_send_task_subscribe(request)

        # 转换为 SSE 格式
        async def sse_generator():
            async for response in stream:
                logger.info(f"任务更新: {response.model_dump_json(exclude_none=True)}")
                yield {
                    "id": str(uuid.uuid4()),
                    "event": "task_update",
                    "data": response.model_dump_json(exclude_none=True)
                }

        return EventSourceResponse(sse_generator())

    except Exception as e:
        logger.error(f"创建流式任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: str):
    """
    获取任务信息
    """
    try:
        request = GetTaskRequest(
            id=str(uuid.uuid4()),
            params={"task_id": task_id}
        )
        response = await sse_task_manager.on_get_task(request)
        return response
    except Exception as e:
        logger.error(f"获取任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ SSE 流式接口 ============

@app.get("/api/v1/sse/tasks/{task_id}")
async def task_sse_stream(
    task_id: str,
    last_event_id: Optional[str] = Header(None, alias="Last-Event-ID")
):
    """
    订阅特定任务的 SSE 事件流

    支持断线重连：客户端可以通过 Last-Event-ID 头部传递最后接收的事件ID
    """
    try:
        # 创建任务专用的 SSE 流
        stream = sse_task_manager.create_task_sse_stream(
            task_id=task_id,
            last_event_id=last_event_id
        )

        return EventSourceResponse(stream)

    except Exception as e:
        logger.error(f"创建任务 SSE 流失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sse/tasks")
async def global_tasks_sse_stream(
    last_event_id: Optional[str] = Header(None, alias="Last-Event-ID")
):
    """
    订阅全局任务事件流

    获取所有任务的状态变化事件
    """
    try:
        stream = sse_task_manager.create_global_task_sse_stream(
            last_event_id=last_event_id
        )

        return EventSourceResponse(stream)

    except Exception as e:
        logger.error(f"创建全局任务 SSE 流失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sse/channels/{channel}")
async def channel_sse_stream(
    channel: str,
    last_event_id: Optional[str] = Header(None, alias="Last-Event-ID")
):
    """
    订阅指定频道的 SSE 事件流

    通用的频道订阅接口，可以订阅任意自定义频道
    """
    try:
        stream = sse_task_manager.create_sse_stream(
            channel=channel,
            last_event_id=last_event_id
        )

        return EventSourceResponse(stream)

    except Exception as e:
        logger.error(f"创建频道 SSE 流失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 事件发布接口 ============

@app.post("/api/v1/events/publish")
async def publish_event(request: PublishEventRequest):
    """
    发布事件到指定频道

    允许外部系统向 SSE 频道发布自定义事件
    """
    try:
        success = await sse_task_manager.publish_sse_event(
            channel=request.channel,
            event_type=request.event_type,
            data=request.data,
            event_id=request.event_id
        )

        return {"success": success, "message": "Event published successfully"}

    except Exception as e:
        logger.error(f"发布事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tasks/{task_id}/events")
async def publish_task_event(
    task_id: str,
    event_type: str,
    data: Dict[str, Any]
):
    """
    发布任务相关事件
    """
    try:
        success = await sse_task_manager.publish_task_event(
            task_id=task_id,
            event_type=event_type,
            data=data
        )

        return {"success": success, "message": "Task event published successfully"}

    except Exception as e:
        logger.error(f"发布任务事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 管理接口 ============

@app.get("/api/v1/sse/subscribers")
async def get_sse_subscribers(channel: Optional[str] = Query(None)):
    """
    获取 SSE 订阅者信息
    """
    try:
        if channel:
            subscribers = sse_task_manager.sse_subscribers.get(channel, set())
            return {
                "channel": channel,
                "subscriber_count": len(subscribers),
                "subscribers": list(subscribers)
            }
        else:
            return {
                "all_channels": {
                    ch: {
                        "subscriber_count": len(subs),
                        "subscribers": list(subs)
                    }
                    for ch, subs in sse_task_manager.sse_subscribers.items()
                }
            }
    except Exception as e:
        logger.error(f"获取订阅者信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sse/channels")
async def get_sse_channels():
    """
    获取所有 SSE 频道列表
    """
    try:
        channels = list(sse_task_manager.sse_subscribers.keys())
        return {
            "channels": channels,
            "total_channels": len(channels)
        }
    except Exception as e:
        logger.error(f"获取频道列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 健康检查接口 ============

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "sse-task-manager"}


@app.get("/readiness")
async def readiness_check():
    """就绪状态检查"""
    try:
        # 检查消息队列连接状态
        if sse_task_manager.connection and not sse_task_manager.connection.is_closed:
            return {"status": "ready", "message_queue": "connected"}
        else:
            raise HTTPException(status_code=503, detail="Message queue not ready")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


# ============ 示例接口 ============

@app.post("/api/v1/demo/simple-task")
async def create_simple_demo_task(
    message: str = "Hello, SSE World!",
    duration: int = 5
):
    """
    创建一个简单的演示任务

    任务会定期发送进度更新事件，便于测试 SSE 功能
    """
    task_id = str(uuid.uuid4())

    # 创建任务请求
    request = SendTaskStreamingRequest(
        id=str(uuid.uuid4()),
        params=TaskSendParams(
            id=task_id,
            sessionId=str(uuid.uuid4()),
            payload={
                "message": message,
                "duration": duration,
                "demo": True
            }
        )
    )

    # 异步执行演示任务
    asyncio.create_task(_execute_demo_task(task_id, message, duration))

    return {
        "task_id": task_id,
        "message": "Demo task created",
        "sse_url": f"/api/v1/sse/tasks/{task_id}",
        "global_sse_url": "/api/v1/sse/tasks"
    }


async def _execute_demo_task(task_id: str, message: str, duration: int):
    """执行演示任务"""
    try:
        # 发布任务开始事件
        await sse_task_manager.publish_task_event(
            task_id=task_id,
            event_type="demo_task_started",
            data={
                "message": f"Demo task started: {message}",
                "duration": duration
            }
        )

        # 模拟任务执行过程
        for i in range(duration):
            await asyncio.sleep(1)

            progress = (i + 1) / duration * 100
            await sse_task_manager.publish_task_event(
                task_id=task_id,
                event_type="demo_task_progress",
                data={
                    "step": i + 1,
                    "total_steps": duration,
                    "progress": progress,
                    "message": f"Processing step {i + 1}/{duration}"
                }
            )

        # 发布任务完成事件
        await sse_task_manager.publish_task_event(
            task_id=task_id,
            event_type="demo_task_completed",
            data={
                "message": f"Demo task completed: {message}",
                "total_time": duration
            }
        )

    except Exception as e:
        # 发布错误事件
        await sse_task_manager.publish_task_event(
            task_id=task_id,
            event_type="demo_task_error",
            data={
                "error": str(e),
                "message": "Demo task failed"
            }
        )
        logger.error(f"演示任务执行失败: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "sse_web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
