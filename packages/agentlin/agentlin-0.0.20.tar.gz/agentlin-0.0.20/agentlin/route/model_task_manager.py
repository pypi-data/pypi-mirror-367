import os
import traceback
from openai.types.chat.chat_completion import ChatCompletion
from typing_extensions import Any, AsyncGenerator, Union, AsyncIterable
import asyncio
import inspect

import openai
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from agentlin.core.types import *
from agentlin.core.agent_schema import create_logger
from agentlin.route.task_manager import InMemoryTaskManager


MODEL_TASK_MANAGER = "model_task_manager"

class ModelTaskManager(InMemoryTaskManager):
    def __init__(
        self,
        agent_id: str,
    ):
        super().__init__()
        self.API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        self.BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if not self.BASE_URL:
            raise ValueError("OPENAI_BASE_URL environment variable is not set.")
        self.client = openai.AsyncOpenAI(api_key=self.API_KEY, base_url=self.BASE_URL)

        logger_id = f"{agent_id}/{MODEL_TASK_MANAGER}"
        self.LOG_DIR = os.getenv("LOG_DIR", "output/logs")
        self.logger = create_logger(os.path.join(self.LOG_DIR, "agents"), logger_id)
        self.logger.info(f"Initialized {logger_id} for agent {agent_id}")

        self.token_counter = 0
        self._total_reasoning_tokens = 0

    def track_tokens(self, tokens: int, message: str = "") -> None:
        """Track token usage for monitoring and recording."""
        self.token_counter += tokens
        self.logger.info(f"Received {tokens} tokens, new total {self.token_counter}")

        # Store the response content for reasoning context (avoid empty or JSON strings)
        if message and not message.startswith("{"):
            self._last_response_content = message
        self._last_reasoning_tokens = tokens
        self._total_reasoning_tokens += tokens

    def capture_reasoning_from_response(self, model: str, response: ChatCompletionChunk) -> None:
        """Helper method to capture reasoning tokens from OpenAI API response."""
        if hasattr(response, "usage") and hasattr(response.usage, "completion_tokens_details"):
            if hasattr(response.usage.completion_tokens_details, "reasoning_tokens"):
                self._last_reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens
                self._total_reasoning_tokens += self._last_reasoning_tokens
                self.logger.debug(f"Captured {self._last_reasoning_tokens} reasoning tokens from {model} response")

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
        await self.upsert_task(request.params)
        task_send_params: TaskSendParams = request.params
        request_id = request.id
        task_id = task_send_params.id
        session_id = task_send_params.sessionId
        return self._stream_generator(request, session_id, request_id, task_id)

    async def _stream_generator(
        self,
        request: SendTaskStreamingRequest,
        session_id: str,
        request_id: str,
        task_id: str,
    ) -> AsyncIterable[SendTaskStreamingResponse]:
        resp = await self.working_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

        # 获取任务参数
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        messages: list[DialogData] = payload.get("messages", [])
        inference_args: dict = payload.get("inference_args", {})

        # arg_names = inspect.signature(self.client.chat.completions.create).parameters
        args_to_remove = set(["debug"])
        # for arg_name in inference_args.keys():
        #     if arg_name not in arg_names:
        #         args_to_remove.add(arg_name)
        for arg_name in args_to_remove:
            if arg_name in inference_args:
                inference_args.pop(arg_name)

        try:
            # 调用OpenAI流式API
            stream = await self.client.chat.completions.create(
                messages=messages,
                stream=True,
                **inference_args,
            )

            # 处理流式响应
            async for chunk in stream:
                self.capture_reasoning_from_response(chunk.model, chunk)
                # 发送增量内容更新
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata=chunk.model_dump(),
                    ),
                )

            resp = await self.complete_streaming_response(request_id=request_id, task_id=task_id)
            yield resp

        except Exception as e:
            # 处理错误情况
            error_message = f"处理请求时发生错误: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_message)
            error = JSONRPCError(code=-32000, message=error_message)
            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error)
            yield resp


    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        await self.upsert_task(request.params)
        return await self._invoke(request)

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        # 获取任务参数
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        messages: list[DialogData] = payload.get("messages", [])
        inference_args: dict = payload.get("inference_args", {})

        response: ChatCompletion = await self.client.chat.completions.create(
            messages=messages,
            stream=False,
            **inference_args,
        )
        self.capture_reasoning_from_response(response.model, response)

        task = await self.update_store(
            task_send_params.id,
            TaskStatus(state=TaskState.COMPLETED),
            response,
        )
        return SendTaskResponse(id=request.id, result=task)
