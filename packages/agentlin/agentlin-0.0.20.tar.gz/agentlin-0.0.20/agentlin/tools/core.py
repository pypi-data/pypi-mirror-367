import json
import subprocess
from typing import Any, Dict, List, Optional, Union, Set

from loguru import logger

from agentlin.tools.types import BaseTool, FunctionDeclaration, ToolResult, sanitize_parameters


class Config:
    def get_tool_discovery_command(self) -> str:
        return "python discover.py"

    def get_tool_call_command(self) -> str:
        return "python call_tool.py"

    def get_mcp_servers(self):
        return {}

    def get_mcp_server_command(self):
        return None

    def get_debug_mode(self) -> bool:
        return False


class DiscoveredTool(BaseTool):
    def __init__(self, config: Config, name: str, description: str, parameter_schema: Dict[str, Any]):
        self.config = config
        discovery_cmd = config.get_tool_discovery_command()
        call_command = config.get_tool_call_command()
        description += f"""

This tool was discovered by executing `{discovery_cmd}` on project root.
When called, this tool will execute `{call_command} {name}`.

Tool discovery and call commands can be configured in project/user settings.
"""
        super().__init__(name, name, description, parameter_schema, False, False)

    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        call_command = self.config.get_tool_call_command()
        process = subprocess.Popen(
            [call_command, self.name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate(input=json.dumps(params).encode())
        code = process.returncode

        stdout_str = stdout.decode()
        stderr_str = stderr.decode()

        if code != 0 or stderr_str:
            text = f"""Stdout: {stdout_str or '(empty)'}
Stderr: {stderr_str or '(empty)'}
Error: (none)
Exit Code: {code}
Signal: (none)"""
            message_content = [{"type": "text", "text": text}]
            block_list = [{"type": "text", "text": text}]
            return ToolResult(message_content, block_list)

        message_content = [{"type": "text", "text": stdout_str}]
        block_list = [{"type": "text", "text": stdout_str}]
        return ToolResult(message_content, block_list)


class ToolRegistry:
    def __init__(self, config: Config):
        self.tools: Dict[str, BaseTool] = {}
        self.config = config

    def get_function_declarations(self) -> List[FunctionDeclaration]:
        return [tool.schema for tool in self.tools.values()]

    def get_all_tools(self) -> List[BaseTool]:
        return list(self.tools.values())

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)

    def register_tool(self, tool: BaseTool) -> None:
        if tool.name in self.tools:
            logger.warning(f'Warning: Tool "{tool.name}" already registered. Overwriting.')
        self.tools[tool.name] = tool

    async def discover_tools(self):
        # 清除已发现的工具（根据类型判定）
        self.tools = {k: v for k, v in self.tools.items() if not isinstance(v, DiscoveredTool)}
        # MCP 相关略过，需另实现 discover_mcp_tools
        discovery_cmd = self.config.get_tool_discovery_command()
        functions = await discover_and_register_tools_from_command(discovery_cmd)
        if not functions:
            return
        for func in functions:
            self.register_tool(
                DiscoveredTool(
                    self.config,
                    func.name,
                    func.description or "",
                    func.parameters,
                )
            )


async def discover_and_register_tools_from_command(discovery_cmd: str):
    if not discovery_cmd:
        return

    try:
        proc = subprocess.Popen(discovery_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Discovery command failed: {stderr.decode()}")

        tools = json.loads(stdout.decode())
        if not isinstance(tools, list):
            raise ValueError("Expected discovery output to be a JSON array")

        functions: List[FunctionDeclaration] = []
        for item in tools:
            if isinstance(item, dict):
                if "function_declarations" in item:
                    functions.extend(FunctionDeclaration(**f) for f in item["function_declarations"])
                elif "functionDeclarations" in item:
                    functions.extend(FunctionDeclaration(**f) for f in item["functionDeclarations"])
                elif "name" in item:
                    functions.append(FunctionDeclaration(**item))

        for func in functions:
            sanitize_parameters(func.parameters)
        return functions
    except Exception as e:
        logger.error(f"Error discovering tools: {e}")
        raise
