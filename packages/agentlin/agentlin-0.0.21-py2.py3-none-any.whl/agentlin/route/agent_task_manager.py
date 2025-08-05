from pathlib import Path
from typing_extensions import Any, AsyncGenerator, Union, AsyncIterable
import asyncio
import os
import sys

from fastmcp import Client
from fastmcp.client.transports import ClientTransportT
from fastmcp.client.elicitation import ElicitRequestParams, ElicitResult, RequestContext, ClientSession, LifespanContextT

from agentlin.core.types import *
from agentlin.core.agent_schema import AgentCore, parse_config_from_ipynb
from agentlin.route.subagent import SubAgentConfig, SubAgentLoader
from agentlin.route.task_manager import InMemoryTaskManager
from agentlin.core.agent_message_queue import AgentMessageQueue


class CodeInterpreterConfig(BaseModel):
    jupyter_host: str  # Jupyter host URL
    jupyter_port: int  # Jupyter port
    jupyter_token: str  # Jupyter token
    jupyter_timeout: int  # Jupyter timeout
    jupyter_username: str  # Jupyter username


class AgentConfig(BaseModel):
    name: str
    description: str
    developer_prompt: str
    code_for_agent: str
    code_for_interpreter: str
    allowed_tools: list[str] = ["*"]

    engine: str = "api"
    model: str

    tool_mcp_config: dict[str, Any] = {
        "mcpServers": {
            "aime_sse_server": {"url": "http://localhost:7778/tool_mcp"},
        }
    }
    code_mcp_config: dict[str, Any] = {
        "mcpServers": {
            "aime_sse_server": {"url": "http://localhost:7778/code_mcp"},
        }
    }

    code_interpreter_config: CodeInterpreterConfig
    inference_args: dict[str, Any] = {}

    # 内置工具列表
    builtin_tools: list[dict[str, Any]] = [
        {
            "type": "function",
            "function": {
                "name": "CodeInterpreter",
                "description": "在受限、安全的沙盒环境中执行 Python 3 代码的解释器，可用于数据处理、科学计算、自动化脚本、可视化等任务，支持大多数标准库及常见第三方科学计算库。",
                "parameters": {
                    "type": "object",
                    "required": ["code"],
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "要执行的 Python 代码",
                        }
                    },
                },
            },
        },
    ]
    builtin_subagents: list[SubAgentConfig] = []

    def get_builtin_tools(self, allowed_subagents: Optional[list[str]] = None) -> list[dict[str, Any]]:
        """获取内置工具列表"""
        for tool in self.builtin_tools:
            if tool["function"]["name"] == "Task":
                # 如果内置工具中已经有 Task 工具，则更新 description
                subagents_texts = []
                for subagent in self.builtin_subagents:
                    if allowed_subagents is not None and subagent.name not in allowed_subagents:
                        continue
                    # 只添加允许的子代理
                    subagents_texts.append(f"- {subagent.name}: {subagent.description} (Tools: {', '.join(subagent.allowed_tools)})")
                subagents_text = "\n".join(subagents_texts)
                tool["function"]["description"] = tool["function"]["description"].replace("{{subagents}}", subagents_text)
        return self.builtin_tools


async def get_agent_id(host_frontend_id: str) -> str:
    frontend_to_agent_map = {
        "AInvest": "aime",
        "iWencai": "wencai",
        "ARC-AGI": "agi",
    }
    return frontend_to_agent_map.get(host_frontend_id, "aime")


async def get_agent_config(agent_id: str) -> AgentConfig:
    if agent_id == "aime":
        return await get_aime_agent_config()
    # elif agent_id == "wencai":
    #     return await get_wencai_agent_config()
    else:
        return await get_agi_agent_config()


async def get_agi_agent_config() -> AgentConfig:
    # 这里可以根据 agent_id 从数据库或配置文件中获取 AgentConfig
    # 这里使用一个示例配置
    home_path = Path(__file__).parent.parent.parent
    subagent_dir = home_path / "assets/agi/agents"
    path = home_path / "assets/agi/main.ipynb"
    code_for_interpreter, code_for_agent, developer_prompt = parse_config_from_ipynb(path)
    experience_filepath = home_path / "assets/agi/experience.jsonl"
    code_for_agent = code_for_agent.replace("{{experience_filepath}}", str(experience_filepath))
    code_for_interpreter = code_for_interpreter.replace("{{experience_filepath}}", str(experience_filepath))
    loader = SubAgentLoader()
    subagents = await loader.load_subagents(subagent_dir)
    for subagent in subagents:
        # 替换 subagent 的 experience_filepath
        subagent.code_for_interpreter = subagent.code_for_interpreter.replace("{{experience_filepath}}", str(experience_filepath))
        subagent.code_for_agent = subagent.code_for_agent.replace("{{experience_filepath}}", str(experience_filepath))

    # 添加 Task 工具
    task_tool = {
        "type": "function",
        "function": {
            "name": "Task",
            "description": """\
Launch a new agent to handle complex, multi-step tasks autonomously.

Available agent types and the tools they have access to:
{{subagents}}

When using the Task tool, you must specify a subagent_type parameter to select which agent type to use.

When to use the Task tool:
- For complex, multi-step tasks that require autonomous handling.

Usage notes:
1. Launch multiple agents concurrently whenever possible to maximize performance.
2. The agent will return a single message back to you.
3. Each agent invocation is stateless.
4. Your prompt should contain a highly detailed task description.
5. Clearly tell the agent whether you expect it to write code or do research.""",
            "parameters": {
                "type": "object",
                "required": ["subagent_type", "description", "prompt"],
                "properties": {
                    "subagent_type": {
                        "type": "string",
                        "description": "The type of specialized agent to use for this task",
                    },
                    "description": {
                        "type": "string",
                        "description": "A short (3-5 word) description of the task",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The task for the agent to perform",
                    },
                },
                "additionalProperties": False,
            },
        },
    }

    json_data = {
        "name": "aime",
        "description": "AIME Agent for handling user requests",
        "developer_prompt": developer_prompt,
        "code_for_interpreter": code_for_interpreter,
        "code_for_agent": code_for_agent,
        "allowed_tools": ["*"],

        "engine": "api",
        "model": "o3",

        "tool_mcp_config": {
            "mcpServers": {
                # "web": {"url": "http://localhost:7779/web_mcp/"},
                # "file_system": {"url": "http://localhost:7779/file_system_mcp/"},

                # "todo": {
                #     "command": "/Users/lxy/anaconda3/envs/agent/bin/python",
                #     "args": ["-m", "agentlin", "launch", "--mcp-server", "todo", "--host", "localhost", "--port", "7780", "--path", "/todo_mcp", "--debug"],
                #     "env": {
                #         "PYTHONPATH": home_path.resolve().as_posix(),
                #         "TODO_FILE_PATH": (home_path / "todos.json").resolve().as_posix(),
                #     },
                #     "cwd": home_path.resolve().as_posix(),
                # },
                # "todo": {
                #     "command": "/Users/lxy/anaconda3/envs/agent/bin/python",
                #     "args": ["agentlin/tools/server/todo_mcp_server.py", "--host", "localhost", "--port", "7780", "--debug"],
                #     "env": {
                #         "PYTHONPATH": home_path.resolve().as_posix(),
                #         "TODO_FILE_PATH": (home_path / "todos.json").resolve().as_posix(),
                #     },
                #     "cwd": home_path.resolve().as_posix(),
                # },
                "todo": {
                    "url": "http://localhost:7780/todo_mcp/",
                }
            }
        },
        "code_mcp_config": {
            "mcpServers": {
                "aime_sse_server": {"url": "http://localhost:7778/code_mcp"},
            }
        },
        "code_interpreter_config": {
            "jupyter_host": "localhost",
            "jupyter_port": 8888,
            "jupyter_token": "jupyter_server_token",
            "jupyter_timeout": 60,
            "jupyter_username": "user",
        },
        "inference_args": {
            "debug": True,
        },
        "builtin_tools": [
            {
                "type": "function",
                "function": {
                    "name": "CodeInterpreter",
                    "description": "在受限、安全的沙盒环境中执行 Python 3 代码的解释器，可用于数据处理、科学计算、自动化脚本、可视化等任务，支持大多数标准库及常见第三方科学计算库。",
                    "parameters": {
                        "type": "object",
                        "required": ["code"],
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "要执行的 Python 代码",
                            }
                        },
                    },
                },
            },
            task_tool,
        ],
        "builtin_subagents": subagents,
    }
    config = AgentConfig.model_validate(json_data)
    return config

async def get_aime_agent_config() -> AgentConfig:
    # 这里可以根据 agent_id 从数据库或配置文件中获取 AgentConfig
    # 这里使用一个示例配置
    home_path = Path(__file__).parent.parent.parent
    subagent_dir = home_path / "assets/aime/agents"
    path = home_path / "assets/aime/main.ipynb"
    code_for_interpreter, code_for_agent, developer_prompt = parse_config_from_ipynb(path)
    loader = SubAgentLoader()
    subagents = await loader.load_subagents(subagent_dir)
    task_tool = {
        "type": "function",
        "function": {
            "name": "Task",
            "description": """\
Launch a new agent to handle complex, multi-step tasks autonomously.

Available agent types and the tools they have access to:
{{subagents}}

When using the Task tool, you must specify a subagent_type parameter to select which agent type to use.

When to use the Task tool:
- When you are instructed to execute custom slash commands. Use the Task tool with the slash command invocation as the entire prompt.
- For complex, multi-step tasks that require autonomous handling.

When NOT to use the Task tool:
- If you want to read a specific file path, use the Read or Glob tool instead.
- If you are searching for a specific class definition, use the Glob tool instead.
- If you are searching for code within a specific file or set of 2-3 files, use the Read tool instead.

Usage notes:
1. Launch multiple agents concurrently whenever possible to maximize performance.
2. The agent will return a single message back to you.
3. Each agent invocation is stateless.
4. Your prompt should contain a highly detailed task description.
5. Clearly tell the agent whether you expect it to write code or do research.""",
            "parameters": {
                "type": "object",
                "required": ["subagent_type", "description", "prompt"],
                "properties": {
                    "subagent_type": {
                        "type": "string",
                        "description": "The type of specialized agent to use for this task",
                    },
                    "description": {
                        "type": "string",
                        "description": "A short (3-5 word) description of the task",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The task for the agent to perform",
                    },
                },
                "additionalProperties": False,
            },
        },
    }

    json_data = {
        "name": "aime",
        "description": "AIME Agent for handling user requests",
        "developer_prompt": developer_prompt,
        "code_for_interpreter": code_for_interpreter,
        "code_for_agent": code_for_agent,
        "allowed_tools": ["*"],

        "engine": "api",
        "model": "o3",

        "tool_mcp_config": {
            "mcpServers": {
                # "web": {"url": "http://localhost:7779/web_mcp/"},
                "file_system": {"url": "http://localhost:7779/file_system_mcp/"},
            }
        },
        "code_mcp_config": {
            "mcpServers": {
                "aime_sse_server": {"url": "http://localhost:7778/code_mcp"},
            }
        },
        "code_interpreter_config": {
            "jupyter_host": "localhost",
            "jupyter_port": 8888,
            "jupyter_token": "jupyter_server_token",
            "jupyter_timeout": 60,
            "jupyter_username": "user",
        },
        "inference_args": {
            "debug": True,
        },
        "builtin_tools": [
            {
                "type": "function",
                "function": {
                    "name": "CodeInterpreter",
                    "description": "在受限、安全的沙盒环境中执行 Python 3 代码的解释器，可用于数据处理、科学计算、自动化脚本、可视化等任务，支持大多数标准库及常见第三方科学计算库。",
                    "parameters": {
                        "type": "object",
                        "required": ["code"],
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "要执行的 Python 代码",
                            }
                        },
                    },
                },
            },
            task_tool,
        ],
        "builtin_subagents": subagents,
    }
    config = AgentConfig.model_validate(json_data)
    return config


class AgentTaskManager(InMemoryTaskManager, AgentMessageQueue):
    def __init__(
        self,
        host_frontend_id: str,
        agent_id: str,
        *,
        rabbitmq_host: str = "localhost",
        rabbitmq_port: int = 5672,
        auto_ack: bool = False,
        reconnect_initial_delay: float = 5.0,
        reconnect_max_delay: float = 60.0,
        message_timeout: float = 30.0,
        rpc_timeout: float = 30.0,
    ):
        InMemoryTaskManager.__init__(self)
        AgentMessageQueue.__init__(
            self,
            agent_id=agent_id,
            rabbitmq_host=rabbitmq_host,
            rabbitmq_port=rabbitmq_port,
            auto_ack=auto_ack,
            reconnect_initial_delay=reconnect_initial_delay,
            reconnect_max_delay=reconnect_max_delay,
            message_timeout=message_timeout,
            rpc_timeout=rpc_timeout,
        )

        self.host_frontend_id = host_frontend_id
        config = {}
        self.client = Client(
            config,
            elicitation_handler=self.on_elicitation,
        )

    async def on_elicitation(
        self,
        message: str,
        response_type: type,
        params: ElicitRequestParams,
        context: RequestContext[ClientSession, LifespanContextT],
    ):
        # Present the message to the user and collect input
        # user_input = input(f"{message}: ")
        print(f"{message}")
        print("===Params===")
        print(params)
        print("===Context===")
        print(context)
        data = {
            "params": params.model_dump(),
        }
        result = await self.call_rpc(self.host_frontend_id, "elicitation", message, response_type, data, context)
        if not result:
            self.logger.error(f"Failed to send elicitation message to {self.host_frontend_id}")
            return ElicitResult(action="reject")

        return ElicitResult(action="accept", content=result)

    async def get_tools(self, allowed_tools: Optional[list[str]] = None) -> list[dict[str, Any]]:
        async with self.client:
            tools = await self.client.list_tools()
            results = []
            for tool in tools:
                if allowed_tools is None:
                    results.append(tool.model_dump())
                    continue
                # 如果指定了 allowed_tools，则只返回这些工具
                tool_name = tool.name
                if tool_name in allowed_tools:
                    results.append(tool.model_dump())
        return results

    async def _handle_regular_message(self, message):
        return await super()._handle_regular_message(message)

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
        request_id: int | str | None,
        task_id: str,
    ) -> AsyncIterable[SendTaskStreamingResponse]:
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        history_messages: list[DialogData] = payload["history_messages"]
        inference_args: dict = payload.get("inference_args", {})

        # 获取OpenAI配置
        model = inference_args.get("model", "gpt-4")
        max_tokens = inference_args.get("max_tokens", 10 * 1024)
        temperature = inference_args.get("temperature", 0.7)
        tools = inference_args.get("tools", None)

        try:
            # 发送任务状态更新 - 开始处理
            resp = await self.working_streaming_response(request_id, task_id)
            yield resp

            # 调用OpenAI流式API
            stream = await self.client.chat.completions.create(
                model=model,
                messages=history_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                tools=tools,
            )

            # 处理流式响应
            async for chunk in stream:
                # 发送增量内容更新
                yield SendTaskStreamingResponse(
                    id=request.id,
                    result=TaskArtifactUpdateEvent(
                        id=task_send_params.id,
                        metadata=chunk.model_dump(),
                    ),
                )
            # 发送最终完成响应
            resp = await self.complete_streaming_response(request_id, task_id)
            yield resp

        except Exception as e:
            # 处理错误情况
            error = JSONRPCError(code=-32000, message=f"处理请求时发生错误: {str(e)}")
            resp = await self.fail_streaming_response(request_id, task_id, error)
            yield resp
