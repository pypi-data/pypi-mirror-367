from collections import defaultdict
from pathlib import Path
from typing_extensions import Any, AsyncIterable
import json
import uuid
from fastmcp import Client as MCPClient
from loguru import logger
import copy
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from deeplin.inference_engine import build_inference_engine
from agentlin.core.multimodal import is_text_content
from agentlin.core.types import *
from agentlin.core.agent_schema import (
    AgentCore,
    content_to_text,
    extract_code,
    extract_thought,
    parse_config_from_ipynb,
    parse_function_call_response,
    remove_thoughts,
    messages_to_text,
    create_logger,
)
from agentlin.route.agent_task_manager import AgentConfig, CodeInterpreterConfig, get_agent_id, get_agent_config
from agentlin.route.reference_manager import ReferenceManager
from agentlin.route.subagent import SubAgentConfig
from agentlin.route.task_manager import InMemoryTaskManager, merge_streams
from agentlin.route.tool_task_manager import ToolTaskManager
from agentlin.route.code_task_manager import CodeTaskManager, ExecuteRequest
from agentlin.route.model_task_manager import ModelTaskManager
from agentlin.tools.tool_calendar import format_datetime_with_holiday
from agentlin.tools.types import ToolResult


class SessionState(BaseModel):
    session_id: str
    user_id: str
    host_frontend_id: str
    host_agent_id: str
    host_code_kernel_id: Optional[str] = None
    agent_config: AgentConfig

    # 短期记忆
    history_messages: list[DialogData] = []
    thought_messages: list[DialogData] = []
    execution_messages: list[DialogData] = []  # 代码解释器运行记录
    dialog_id2references: dict[str, ReferenceManager] = {}  # 引用池, 用于溯源。会话级别
    mcp_tools: list[ToolData] = []  # 已注册的工具列表

    # 长期记忆
    instruction: str = ""  # 用户指令
    user_profile: str = ""  # 用户个人信息
    language: Literal["zh", "en"] = "en"  # 用户语言

    # 运行时 - 这些属性不参与 BaseModel 的序列化和验证
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    def __init__(self, **data):
        # 提取运行时管理器，避免传入 BaseModel 验证
        model_task_manager = data.pop("model_task_manager", None)
        tool_task_manager = data.pop("tool_task_manager", None)
        code_task_manager = data.pop("code_task_manager", None)

        # 先调用父类的 __init__
        super().__init__(**data)

        # 然后设置运行时属性
        self.model_task_manager: ModelTaskManager = model_task_manager
        self.tool_task_manager: ToolTaskManager = tool_task_manager
        self.code_task_manager: CodeTaskManager = code_task_manager

    def get_subagent_by_name(self, name: str) -> Optional[SubAgentConfig]:
        for subagent in self.agent_config.builtin_subagents:
            if subagent.name == name:
                return subagent
        return None

    def get_subagents(self, allowed_subagents: Optional[list[str]] = None) -> list[SubAgentConfig]:
        if allowed_subagents is None:
            return self.agent_config.builtin_subagents
        filtered_subagents = []
        for subagent in self.agent_config.builtin_subagents:
            if subagent.name in allowed_subagents:
                filtered_subagents.append(subagent)
        return filtered_subagents

    def get_tools(self, allowed_tools: Optional[list[str]] = None) -> list[ToolData]:
        if allowed_tools is None:
            return self.agent_config.builtin_tools
        filtered_tools = []
        for tool in self.agent_config.builtin_tools:
            if tool["name"] in allowed_tools:
                filtered_tools.append(tool)
        return filtered_tools


class SessionRequest(BaseModel):
    user_id: str
    host_frontend_id: str
    user_message_content: list[ContentData]

    key: Optional[str] = None
    agent_config: Optional[AgentConfig] = None
    allowed_tools: Optional[list[str]] = None  # 允许的工具列表. None 为允许所有，[] 为不允许任何
    disallowed_tools: Optional[list[str]] = None  # 不允许的工具列表. None 和 [] 不进行处理
    allowed_subagents: Optional[list[str]] = None  # 允许的子代理列表. None 为允许所有，[] 为不允许任何
    stop_tools: Optional[list[str]] = None  # 遇到 stop_tools 时终止. None 和 [] 不进行处理
    client_tools: Optional[list[ToolData]] = None

    # completion 模式。
    # 存在 history_messages 或 thought_messages 非空时，
    # 不清空驻留在内存中的 thought_messages 栈，
    # 而是将传进来的 history_messages 或 thought_messages 拼到末尾，继续 agent 循环
    history_messages: list[dict] = []
    thought_messages: list[dict] = []

    # 用户指令记忆
    instruction: Optional[str] = None
    inference_args: Optional[dict[str, Any]] = None
    cwd: Optional[str] = None  # 当前工作目录, 用于 file_system_mcp 和代码解释器


class ExecuteSubAgentRequest(BaseModel):
    subagent_type: str
    description: str
    prompt: str


class SessionTaskManager(InMemoryTaskManager):
    def __init__(self, debug=False):
        super().__init__()
        self.sessions: dict[str, SessionState] = {}
        self.debug = debug

    def build_system_content(self, session_id: str, session_state: SessionState) -> str:
        developer_prompt = session_state.agent_config.developer_prompt
        user_profile = session_state.user_profile
        code_for_agent = session_state.agent_config.code_for_agent

        developer_prompt = developer_prompt.replace("{{code_functions}}", code_for_agent)
        developer_prompt = developer_prompt.replace("{{all_user_profile}}", user_profile)

        system_content = [
            {"type": "text", "text": developer_prompt},
        ]
        return system_content

    def query_nlu(self, query: str):
        # 这里可以调用 NLU 服务进行查询
        return ""

    def build_system_code_for_interpreter(self, session_id: str, session_state: SessionState) -> str:
        code_mcp_config = session_state.agent_config.code_mcp_config
        code_for_interpreter = session_state.agent_config.code_for_interpreter
        code = code_for_interpreter
        code = code.replace("{{code_mcp_config}}", json.dumps(code_mcp_config, ensure_ascii=False))
        code = code.replace("{{session_id}}", session_id)
        code = code.replace("{{host_agent_id}}", session_state.host_agent_id)
        code = code.replace("{{host_frontend_id}}", session_state.host_frontend_id)
        if self.debug:
            logger.debug(f"Total system code for session {session_id}:\n{code}")
        return code

    async def lazy_init_kernel(self, session_id: str, session_state: SessionState) -> str:
        kernel_id = session_state.host_code_kernel_id
        if kernel_id:
            return kernel_id
        code_task_manager = session_state.code_task_manager
        kernel_id = code_task_manager.create_kernel()
        session_state.host_code_kernel_id = kernel_id
        code = self.build_system_code_for_interpreter(session_id, session_state)
        req = ExecuteRequest(
            kernel_id=kernel_id,
            code=code,
            mode="full",
        )
        request = SendTaskRequest(
            params=TaskSendParams(
                sessionId=session_id,
                payload=req.model_dump(),
            )
        )
        resp = await code_task_manager.on_send_task(request)
        if resp.error:
            logger.error(f"Failed to create kernel: {resp.error}")
        return kernel_id

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        host_frontend_id: str,
        agent_config: Optional[AgentConfig] = None,
    ) -> SessionState:
        if agent_config is None:
            host_agent_id = await get_agent_id(host_frontend_id)
            agent_config = await get_agent_config(host_agent_id)
        host_agent_id = agent_config.name

        model = agent_config.model
        agent_config.inference_args.setdefault("max_tokens", 10 * 1024)  # 设置默认最大 token 数量
        agent_config.inference_args.setdefault("model", model)  # 设置默认模型
        model_task_manager = ModelTaskManager(
            agent_id=host_agent_id,
        )
        tool_mcp_config = agent_config.tool_mcp_config
        # tool_mcp_client = MCPClient(tool_mcp_config)
        # async with tool_mcp_client:
        #     tools = await tool_mcp_client.list_tools()
        tool_task_manager = ToolTaskManager(
            host_frontend_id=host_frontend_id,
            agent_id=agent_config.name,
            config=tool_mcp_config,
        )
        mcp_tools = await tool_task_manager.get_tools()
        mcp_tools = [{"type": "function", "function": tool} for tool in mcp_tools]

        code_interpreter_config = agent_config.code_interpreter_config
        if not code_interpreter_config:
            raise ValueError("Code interpreter configuration is required for CodeTaskManager.")
        code_task_manager = CodeTaskManager(
            agent_id=host_agent_id,
            jupyter_host=code_interpreter_config.jupyter_host,
            jupyter_port=code_interpreter_config.jupyter_port,
            jupyter_token=code_interpreter_config.jupyter_token,
            jupyter_timeout=code_interpreter_config.jupyter_timeout,
            jupyter_username=code_interpreter_config.jupyter_username,
        )
        state = SessionState(
            session_id=session_id,
            user_id=user_id,
            host_frontend_id=host_frontend_id,
            host_agent_id=host_agent_id,
            host_code_kernel_id=None,
            agent_config=agent_config,
            tool_task_manager=tool_task_manager,
            code_task_manager=code_task_manager,
            model_task_manager=model_task_manager,
            mcp_tools=mcp_tools,
        )
        self.sessions[session_id] = state
        return state

    def get_session(self, session_id: str):
        return self.sessions.get(session_id, None)

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            session_state = self.sessions[session_id]
            kernel_id = session_state.host_code_kernel_id
            if kernel_id:
                session_state.code_task_manager.delete_kernel(kernel_id)
            del self.sessions[session_id]

    async def streaming_chat(
        self,
        user_message_content: list[ContentData],
        host_frontend_id: str,
        trace_id: str = uuid.uuid4().hex,
        session_id: str = uuid.uuid4().hex,
        task_id: str = uuid.uuid4().hex,
        user_id: str = uuid.uuid4().hex,
        key: Optional[str] = None,
        host_agent_config: Optional[AgentConfig] = None,
        allowed_tools: Optional[list[str]] = None,
        disallowed_tools: Optional[list[str]] = None,
        allowed_subagents: Optional[list[str]] = None,
        stop_tools: Optional[list[str]] = None,
        client_tools: Optional[list[ToolData]] = None,
        history_messages: Optional[list[DialogData]] = None,
        thought_messages: Optional[list[DialogData]] = None,
        instruction: Optional[str] = None,
        inference_args: Optional[dict[str, Any]] = None,
        cwd: Optional[str] = None,
    ):
        """
        向 SessionTaskManager 发送一个任务请求，开始一个会话。
        Args:
            user_message_content: 用户消息内容
            host_frontend_id: 前端 ID, 可选 AInvest, iWencai 等
            trace_id: 跟踪 ID
            session_id: 会话 ID
            task_id: 任务 ID
            user_id: 用户 ID
            key: 消息键值
            host_agent_config: 主机代理配置
            allowed_tools: 允许的工具列表. None 为允许所有，[] 为不允许任何
            disallowed_tools: 不允许的工具列表. None 和 [] 不进行处理
            allowed_subagents: 允许的子代理列表. None 为允许所有，[] 为不允许任何
            stop_tools: 遇到 stop_tools 时终止. None 和 [] 不进行处理
            client_tools: 客户端工具列表
            instruction: 用户指令
            inference_args: 推理参数
            cwd: 当前工作目录, 用于 file_system_mcp 和代码解释器
        Returns:
            AsyncIterable[SendTaskStreamingResponse | JSONRPCResponse]: 任务流响应
        """
        req = SessionRequest(
            user_id=user_id if user_id else "default_user",
            host_frontend_id=host_frontend_id,
            user_message_content=user_message_content,
            key=key,
            agent_config=host_agent_config,
            allowed_tools=allowed_tools,
            disallowed_tools=disallowed_tools,
            allowed_subagents=allowed_subagents,
            stop_tools=stop_tools,
            client_tools=client_tools,
            history_messages=history_messages if history_messages is not None else [],
            thought_messages=thought_messages if thought_messages is not None else [],
            instruction=instruction,
            inference_args=inference_args,
            cwd=cwd,
        )
        request = SendTaskStreamingRequest(
            id=trace_id,
            params=TaskSendParams(
                id=task_id if task_id else uuid.uuid4().hex,
                sessionId=session_id,
                payload=req.model_dump(),
            ),
        )
        return await self.on_send_task_subscribe(request)

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        subscribe_request = SendTaskStreamingRequest(
            id=request.id,
            params=request.params,
        )
        stream = await self.on_send_task_subscribe(subscribe_request)
        message_content = []
        block_list = []
        async for response in stream:
            # 处理流响应
            if isinstance(response, SendTaskStreamingResponse):
                result = response.result
                if isinstance(result, TaskArtifactUpdateEvent):
                    # 处理任务结果更新事件
                    if result.metadata:
                        message_content.append(result.metadata.get("message_content", []))
                        block_list.extend(result.metadata.get("block_list", []))
        # 最终返回一个完整的任务响应
        return SendTaskResponse(
            id=request.id,
            result=TaskArtifactUpdateEvent(
                id=request.params.id,
                metadata={
                    "message_content": message_content,
                    "block_list": block_list,
                },
            ),
        )

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
        # 响应优化，立即接受任务
        resp = await self.working_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

        # 安全检测
        req = self._validate_request(request)
        if isinstance(req, JSONRPCError):
            logger.error(f"Error in tool task: {req}")
            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=req)
            yield resp
            return

        # 开始处理任务

        # 获得上下文
        user_id = req.user_id
        host_frontend_id = req.host_frontend_id
        user_message_content = req.user_message_content
        key = req.key or f"msg_{uuid.uuid4().hex}"

        session_state = self.get_session(session_id)
        if session_state:
            logger.debug("recover session_state")
        if session_state is None or req.agent_config is not None:
            # 新的 session，或者新的 agent，都需要重新开一个 session
            session_state = await self.create_session(
                session_id,
                user_id,
                host_frontend_id,
                agent_config=req.agent_config,
            )
        if req.instruction is not None:
            session_state.instruction = req.instruction
        else:
            # session_state.instruction = self.fetch_user_instruction(user_id)
            pass

        model_task_manager = session_state.model_task_manager
        tool_task_manager = session_state.tool_task_manager
        code_task_manager = session_state.code_task_manager
        history_messages: list[dict] = session_state.history_messages
        thought_messages: list[dict] = session_state.thought_messages

        # 确认 tools 有哪些
        builtin_tools = session_state.agent_config.get_builtin_tools(req.allowed_subagents)
        mcp_tools = session_state.mcp_tools
        tools: list[ToolData] = builtin_tools + mcp_tools + (req.client_tools or [])
        tools = copy.deepcopy(tools)  # 深拷贝，避免修改原始工具列表
        if req.allowed_tools and "*" not in req.allowed_tools:
            tools = [tool for tool in tools if tool.get("function", {}).get("name") in req.allowed_tools]
        if req.disallowed_tools and len(req.disallowed_tools) > 0:
            tools = [tool for tool in tools if tool.get("function", {}).get("name") not in req.disallowed_tools]

        # 确认推理参数
        inference_args = dict()
        inference_args.update(session_state.agent_config.inference_args)
        if req.inference_args:
            inference_args.update(req.inference_args)
        inference_args["tools"] = tools

        # if self.debug:
        #     logger.debug(f"Session {session_id} inference_args: {json.dumps(inference_args, ensure_ascii=False, indent=2)}")

        # 初始化引用管理器
        reference_manager = ReferenceManager()
        session_state.dialog_id2references[task_id] = reference_manager

        current_step = 0
        if len(thought_messages) > 0:
            current_step = sum([1 for m in thought_messages if m["role"] == "assistant"])

        if len(history_messages) == 0:
            system_content = self.build_system_content(session_id, session_state)
            history_messages.append({"role": "system", "content": system_content})

        if req.history_messages:
            history_messages.extend(req.history_messages)
        if req.thought_messages:
            thought_messages.extend(req.thought_messages)

        if not req.history_messages and not req.thought_messages:
            thought_messages.clear()
        else:
            logger.debug("completion mode: not clearing thought_messages")

        # 我们把跟用户对话时效性强相关的内容放在 role: "user" 中，避免 system content 的缓存失效
        if user_message_content:
            query = content_to_text(user_message_content)
            nlu = self.query_nlu(query)
            language = session_state.language
            current_time = datetime.datetime.now()
            current_time = format_datetime_with_holiday(current_time, language=language)
            if len([m for m in history_messages if m["role"] != "system"]) == 0:
                prefix_content = [
                    {"type": "text", "text": session_state.instruction},
                    # {"type": "text", "text": f"Current time: {current_time}"},
                    # {"type": "text", "text": f"Language: {language}"},
                    # {"type": "text", "text": f"NLU: {nlu}" if nlu else ""},
                    # {"type": "text", "text": f"User Query:\n\n"},
                ]
            else:
                prefix_content = [
                    # {"type": "text", "text": f"Current time: {current_time}"},
                    # {"type": "text", "text": f"Language: {language}"},
                    # {"type": "text", "text": f"NLU: {nlu}" if nlu else ""},
                    # {"type": "text", "text": f"User Query:\n\n"},
                ]
            history_messages.append({"role": "user", "content": prefix_content + user_message_content})

        while True:
            current_step += 1
            if self.debug:
                logger.debug(f"历史消息数量: {len(history_messages)}, 当前推理深度: {current_step}")
            # 调用推理引擎获取回复
            messages = history_messages + thought_messages
            if self.debug:
                logger.debug(messages_to_text([m for m in messages if m["role"] != "system"]))

            reasoning_content = []
            tool_calls = []
            answer_content = ""
            # 先考虑把 tool_calls 整理出来。整理完可能是空列表。
            # "tool_calls": [
            #     {
            #         "function": {
            #             "arguments": "{}",
            #             "name": "Search"
            #         },
            #         "id": "call_g16uvNKM2r7L36PcHmgbPAAo",
            #         "type": "function"
            #     }
            # ]

            model_request = await self.streaming_request(
                request_id=request_id,
                task_id=task_id,
                session_id=session_id,
                payload={
                    "messages": messages,
                    "inference_args": inference_args,
                },
            )
            stream = await model_task_manager.on_send_task_subscribe(model_request)
            async for chunk in stream:
                if isinstance(chunk, SendTaskStreamingResponse):
                    result = chunk.result
                    if isinstance(result, TaskArtifactUpdateEvent):
                        metadata = result.metadata
                        if metadata:
                            chunk = ChatCompletionChunk.model_validate(metadata)
                            if chunk.choices and len(chunk.choices) > 0:
                                choice = chunk.choices[0]
                                if choice.finish_reason:
                                    # 处理完成原因
                                    pass
                                if choice.delta.content:
                                    answer_content += choice.delta.content
                                if hasattr(choice.delta, "reasoning_content"):
                                    reasoning_content.append({"type": "text", "text": choice.delta.reasoning_content})
                                if choice.delta.tool_calls:
                                    tool_calls.extend([t.model_dump() for t in choice.delta.tool_calls])

                            # yield SendTaskStreamingResponse(
                            #     id=request_id,
                            #     result=TaskArtifactUpdateEvent(
                            #         id=task_id,
                            #         metadata={
                            #             "block_list": [chunk],
                            #             "current_step": current_step,
                            #             "key": f"{key}/model_msg_{current_step}",
                            #         },
                            #     ),
                            # )
                            # 只发射按 reasoning_content, answer_content 和 tool_calls 分类后的结果
            if self.debug:
                logger.debug(f"🤖【assistant】: {answer_content}{tool_calls if tool_calls else ''}")

            if answer_content:
                thought = extract_thought(answer_content)
                if thought:
                    reasoning_content.append({"type": "text", "text": [{"type": "text", "text": "<think>"}]})
                    reasoning_content.append({"type": "text", "text": thought})
                    reasoning_content.append({"type": "text", "text": [{"type": "text", "text": "</think>"}]})

                response_without_thoughts = remove_thoughts(answer_content)
                code = extract_code(response_without_thoughts)
                call_id = f"call_{uuid.uuid4().hex}"
                if code and len(code.strip()) > 0:
                    call_args = {
                        "code": code,
                    }
                    tool_call = {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "arguments": json.dumps(call_args, ensure_ascii=False),
                            "name": "CodeInterpreter",
                        },
                    }
                    tool_calls.append(tool_call)

            if reasoning_content:
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata={
                            "block_list": reasoning_content,
                            "current_step": current_step,
                            "key": f"{key}_assistant_thought_{current_step}",
                        },
                    ),
                )
                thought_messages.append({"role": "assistant", "content": reasoning_content})

            if tool_calls:
                # 1. 开始执行
                call_id_to_name_args: dict[str, tuple[str, dict[str, Any]]] = {}
                block_list = []
                should_stop_tool_calls = False
                for tool_call in tool_calls:
                    call_id, call_name, call_args = parse_function_call_response(tool_call)
                    call_id_to_name_args[call_id] = (call_name, call_args)
                    block_list.append(
                        {
                            "type": "tool_call",
                            "data": {
                                "tool_name": call_name,
                                "tool_args": call_args,
                                "call_id": call_id,
                            },
                        }
                    )
                    if call_name in (req.stop_tools or []):
                        should_stop_tool_calls = True
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata={
                            "block_list": block_list,
                            "current_step": current_step,
                            "key": f"{key}_assistant_msg_{current_step}",
                        },
                    ),
                )
                if should_stop_tool_calls:
                    # 如果遇到 stop_tools，则终止当前会话
                    logger.info(f"Session {session_id} stopped by tool call: {req.stop_tools}")
                    # 使用 break，使得 complete response 正常工作
                    break

                # 2. 执行
                call_response_streams = []  # 冷流。放进去的流只有定义，还未执行
                for call_id, (call_name, call_args) in call_id_to_name_args.items():
                    # builtin tools
                    if call_name == "Task":
                        # 3. 启动新的代理来处理复杂的多步骤任务
                        subagent_req = ExecuteSubAgentRequest.model_validate(call_args)
                        subagent_type = subagent_req.subagent_type
                        description = subagent_req.description
                        prompt = subagent_req.prompt
                        subagent = session_state.get_subagent_by_name(subagent_type)
                        if subagent is None:
                            error_message = f"Subagent '{subagent_type}' not found while calling Task."
                            logger.error(error_message)
                            resp = await self.tool_result_streaming_response(
                                request_id=request_id,
                                task_id=call_id,
                                message_content=[{"type": "text", "text": error_message}],
                                block_list=[],
                            )
                            call_response_stream = AsyncIterable[SendTaskStreamingResponse]([resp])
                            continue
                        subagent_config = session_state.agent_config.model_copy()
                        subagent_config.name = subagent.name
                        subagent_config.description = subagent.description
                        if subagent.model:
                            subagent_config.model = subagent.model  # Optional model name
                        subagent_config.developer_prompt = subagent.developer_prompt
                        subagent_config.code_for_agent = subagent.code_for_agent
                        subagent_config.code_for_interpreter = subagent.code_for_interpreter
                        subagent_config.allowed_tools = subagent.allowed_tools
                        disallowed_tools = req.disallowed_tools or []
                        if "Task" not in disallowed_tools:
                            disallowed_tools.append("Task")  # 子代理不允许调用 Task 工具

                        task_req = SessionRequest(
                            user_id=user_id,
                            host_frontend_id=host_frontend_id,
                            user_message_content=[{"type": "text", "text": prompt}],
                            key=f"{key}_subagent_{subagent_type}_{current_step}",
                            agent_config=subagent_config,
                            allowed_tools=subagent.allowed_tools,  # 子代理允许的工具
                            disallowed_tools=disallowed_tools,  # 子代理不允许的工具
                            allowed_subagents=[],  # 子代理不允许其他子代理
                            stop_tools=[],  # 子代理不需要停止工具
                            client_tools=[],  # 子代理不需要客户端工具
                            instruction="",  # 子代理不需要偏好记忆
                            inference_args=None,  # 子代理不需要指定推理参数
                            cwd=req.cwd,  # 子代理需要当前工作目录
                        )
                        subagent_session_id = f"{session_id}_{subagent_type}_{uuid.uuid4().hex}"
                        task_request = SendTaskRequest(
                            id=request_id,
                            params=TaskSendParams(
                                id=call_id,
                                sessionId=subagent_session_id,  # 子代理使用全新的会话 ID，和当前会话隔离
                                payload=task_req.model_dump(),
                            ),
                        )
                        call_response_stream = await self.on_send_task_subscribe(task_request)
                    elif call_name == "CodeInterpreter":
                        code = call_args.get("code", "")
                        kernel_id = await self.lazy_init_kernel(session_id, session_state)

                        # 3. 执行代码
                        code_req = ExecuteRequest(kernel_id=kernel_id, code=code, mode="full", msg_id=call_id)
                        code_request = SendTaskStreamingRequest(
                            id=request_id,
                            params=TaskSendParams(
                                id=call_id,
                                sessionId=session_id,
                                payload=code_req.model_dump(),
                            ),
                        )
                        call_response_stream = await code_task_manager.on_send_task_subscribe(code_request)
                    else:
                        # 3. 执行工具调用
                        tool_request = SendTaskRequest(
                            id=request_id,
                            params=TaskSendParams(
                                id=call_id,
                                sessionId=session_id,
                                payload={
                                    "call_name": call_name,
                                    "call_args": call_args,
                                },
                            ),
                        )
                        call_response_stream = await tool_task_manager.on_send_task_subscribe(tool_request)
                    call_response_streams.append(call_response_stream)

                # 4. 处理执行结果, 处理引用
                call_id_to_result: dict[str, ToolResult] = defaultdict(lambda: ToolResult(message_content=[], block_list=[]))
                async for call_response in merge_streams(*call_response_streams):  # 冷流变“热“：开始正式执行。merge 表示多个流的异步并行合并
                    if self.debug:
                        logger.debug(call_response)
                    if isinstance(call_response, SendTaskStreamingResponse):
                        result = call_response.result
                        if isinstance(result, TaskArtifactUpdateEvent):
                            metadata = result.metadata
                            call_id = result.id
                            if metadata:
                                # 要求：
                                # 1. 及时把 streaming response 返回给前端
                                # 2. 记录执行结果到上下文，按照 call_id 区分
                                metadata["current_step"] = current_step
                                call_name, call_args = call_id_to_name_args[call_id]
                                if call_name == "CodeInterpreter":
                                    metadata["key"] = f"{key}_code_result_msg_{current_step}"
                                else:
                                    metadata["key"] = f"{key}_tool_result_msg_{current_step}"

                                message_content_delta = metadata.pop("message_content", [])
                                block_list_delta = metadata.pop("block_list", [])
                                tool_result = ToolResult(
                                    message_content=message_content_delta,
                                    block_list=block_list_delta,
                                )
                                new_tool_result = reference_manager.process_tool_result(tool_result)
                                call_id_to_result[call_id].extend_result(new_tool_result)
                                if self.debug:
                                    logger.debug(f"Tool call {call_id} result: {new_tool_result.model_dump_json(indent=2)}")
                                # metadata["message_content"] = new_tool_result.message_content  # 前端不需要 message_content
                                metadata["block_list"] = new_tool_result.block_list  # 前端需要 block_list, 这里的 block_list 已经附带真正的 reference number 了
                                metadata["message_content"] = new_tool_result.message_content

                                if len(metadata["block_list"]) > 0 and len(metadata["message_content"]) > 0:
                                    yield SendTaskStreamingResponse(
                                        id=request_id,
                                        result=TaskArtifactUpdateEvent(
                                            id=call_id,
                                            metadata=metadata,
                                        ),
                                    )
                        elif isinstance(result, TaskStatusUpdateEvent):
                            logger.debug(f"Received TaskStatusUpdateEvent: {result} for task {task_id}")
                # 5. 记录工具调用结果到上下文
                thought_messages.append({"role": "assistant", "content": "", "tool_calls": tool_calls})
                if not call_id_to_result:
                    logger.debug(f"No tool call results for session {session_id}, current step {current_step}.")
                for call_id, result in call_id_to_result.items():
                    logger.debug(f"Tool call {call_id} result: {result.model_dump_json(indent=2)}")
                    message_content = result.message_content
                    call_name, _ = call_id_to_name_args[call_id]
                    if not message_content:
                        if call_name == "CodeInterpreter":
                            message_content = [{"type": "text", "text": "ok"}]

                    # 兼容一下 OpenAI 的 tool result 只能是 text 的情况
                    is_all_text = is_text_content(message_content)
                    if is_all_text:
                        thought_messages.append({"role": "tool", "content": message_content, "tool_call_id": call_id})
                    else:
                        thought_messages.append({"role": "tool", "content": [{"type": "text", "text": f"The execution results of {call_name} will be provided by the user as following:"}], "tool_call_id": call_id})
                        message_content.append({"type": "text", "text": f"The execution results of {call_name} are provided as above."})
                        thought_messages.append({"role": "user", "content": message_content})
                # 处理 call_id 匹配，当断流的时候没拿到 call_id 的结果时，可能会导致 call_id_to_result 为空，与 tool_calls 匹配不上
                for tool_call in tool_calls:
                    call_id, call_name, call_args = parse_function_call_response(tool_call)
                    if call_id not in call_id_to_result:
                        # 可能是断流，需要补上工具结果
                        thought_messages.append({"role": "tool", "content": [{"type": "text", "text": f"Tool call {call_name} with arguments '{str(call_args)[:20]}' did not return any result."}], "tool_call_id": call_id})
            else:
                # 没有调工具就是回答了
                response_content = [{"type": "text", "text": remove_thoughts(answer_content)}]

                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata={
                            "message_content": response_content,
                            "block_list": response_content,
                            "key": f"{key}_assistant_answer_{current_step}",
                        },
                    ),
                )

                history_messages.append({"role": "assistant", "content": response_content})
                break
        resp = await self.complete_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

    def _validate_request(self, request: Union[SendTaskRequest, SendTaskStreamingRequest]):
        task_send_params: TaskSendParams = request.params
        try:
            req = SessionRequest.model_validate(task_send_params.payload)
        except Exception as e:
            self.logger.error(f"Invalid request payload: {e}")
            return InvalidParamsError(message=str(e))
        return req

    async def on_get_task(self, request):
        return await super().on_get_task(request)

    async def on_cancel_task(self, request):
        return await super().on_cancel_task(request)

    async def on_get_task_push_notification(self, request):
        return await super().on_get_task_push_notification(request)

    async def on_resubscribe_to_task(self, request):
        return await super().on_resubscribe_to_task(request)

    async def on_set_task_push_notification(self, request):
        return await super().on_set_task_push_notification(request)
