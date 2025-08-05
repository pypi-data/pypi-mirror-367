from typing import Any, Dict, List, Optional, Union, Set
from pydantic import BaseModel

from agentlin.core.types import ContentData
from agentlin.code_interpreter.types import Block

from openai.types.chat.chat_completion_tool import ChatCompletionTool

ToolCallSchema = ChatCompletionTool


class ToolResult(BaseModel):
    message_content: list[dict] = []
    block_list: list[dict] = []
    key: Optional[str] = None

    def append_content(self, content: ContentData):
        """Append content to the message_content list."""
        self.message_content.append(content)

    def append_block(self, block: Block):
        """Append block to the block_list."""
        self.block_list.append(block)

    def extend_content(self, content_list: List[ContentData]):
        """Extend message_content with a list of ContentData."""
        self.message_content.extend(content_list)

    def extend_blocks(self, block_list: List[Block]):
        """Extend block_list with a list of Block."""
        self.block_list.extend(block_list)

    def extend_result(self, other: "ToolResult"):
        """Extend this ToolResult with another ToolResult."""
        self.message_content.extend(other.message_content)
        self.block_list.extend(other.block_list)


ToolParams = Dict[str, Any]
Schema = Dict[str, Any]


def sanitize_parameters(schema: Optional[Schema]) -> None:
    _sanitize_parameters(schema, set())


def _sanitize_parameters(schema: Optional[Schema], visited: Set[int]) -> None:
    if not schema or id(schema) in visited:
        return
    visited.add(id(schema))

    if "anyOf" in schema:
        schema.pop("default", None)
        for sub in schema["anyOf"]:
            if isinstance(sub, dict):
                _sanitize_parameters(sub, visited)

    if "items" in schema and isinstance(schema["items"], dict):
        _sanitize_parameters(schema["items"], visited)

    if "properties" in schema:
        for value in schema["properties"].values():
            if isinstance(value, dict):
                _sanitize_parameters(value, visited)

    if schema.get("type") == "string" and "format" in schema:
        if schema["format"] not in ("enum", "date-time"):
            schema["format"] = None


class FunctionDeclaration:
    def __init__(
        self,
        name: str,
        description: Optional[str] = "",
        parameters: Optional[Schema] = None,
    ):
        self.name = name
        self.description = description or ""
        self.parameters = parameters or {}


class BaseTool:
    def __init__(
        self,
        name: str,
        title: str,
        description: str,
        parameter_schema: Dict[str, Any],
        is_output_markdown: bool,
        can_update_output: bool,
    ):
        self.name = name
        self.title = title
        self.description = description
        self.schema = FunctionDeclaration(name, description, parameter_schema)
        self.is_output_markdown = is_output_markdown
        self.can_update_output = can_update_output
