import datetime
from enum import Enum
from typing_extensions import Union, Any, Literal, List, Annotated, Optional
from pydantic import BaseModel, Field, TypeAdapter, ConfigDict, field_serializer
import uuid
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionContentPartParam
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam

from agentlin.code_interpreter.types import Block


ContentData = ChatCompletionContentPartParam
DialogData = ChatCompletionMessageParam
BlockData = Block
ToolData = ChatCompletionToolParam

class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    UNKNOWN = "unknown"


class TaskStatus(BaseModel):
    state: TaskState
    payload: Any = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

    @field_serializer("timestamp")
    def serialize_dt(self, dt: datetime.datetime, _info):
        return dt.isoformat()


class Task(BaseModel):
    id: str
    sessionId: Optional[str] = None
    status: TaskStatus
    metadata: Optional[dict[str, Any]] = None


class TaskStatusUpdateEvent(BaseModel):
    id: str
    status: TaskStatus
    final: bool = False
    metadata: Optional[dict[str, Any]] = None


class TaskArtifactUpdateEvent(BaseModel):
    id: str
    metadata: Optional[dict[str, Any]] = None


class AuthenticationInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    schemes: List[str]
    credentials: Optional[str] = None


class PushNotificationConfig(BaseModel):
    url: str
    token: Optional[str] = None
    authentication: Optional[AuthenticationInfo] = None


class TaskIdParams(BaseModel):
    id: str
    metadata: Optional[dict[str, Any]] = None


class TaskQueryParams(TaskIdParams):
    pass


class TaskSendParams(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    sessionId: str = Field(default_factory=lambda: uuid.uuid4().hex)
    payload: dict
    acceptedOutputModes: Optional[List[str]] = None
    pushNotification: Optional[PushNotificationConfig] = None
    metadata: Optional[dict[str, Any]] = None


class TaskPushNotificationConfig(BaseModel):
    id: str
    pushNotificationConfig: PushNotificationConfig


## RPC Messages


class JSONRPCMessage(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[int | str] = Field(default_factory=lambda: uuid.uuid4().hex)


class JSONRPCRequest(JSONRPCMessage):
    method: str
    params: Optional[dict[str, Any]] = None


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(JSONRPCMessage):
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None


class SendTaskRequest(JSONRPCRequest):
    method: Literal["tasks/send"] = "tasks/send"
    params: TaskSendParams


class SendTaskResponse(JSONRPCResponse):
    result: Optional[Task] = None


class SendTaskStreamingRequest(JSONRPCRequest):
    method: Literal["tasks/sendSubscribe"] = "tasks/sendSubscribe"
    params: TaskSendParams


class SendTaskStreamingResponse(JSONRPCResponse):
    result: Optional[TaskStatusUpdateEvent | TaskArtifactUpdateEvent] = None


class GetTaskRequest(JSONRPCRequest):
    method: Literal["tasks/get"] = "tasks/get"
    params: TaskQueryParams


class GetTaskResponse(JSONRPCResponse):
    result: Optional[Task] = None


class CancelTaskRequest(JSONRPCRequest):
    method: Literal["tasks/cancel",] = "tasks/cancel"
    params: TaskIdParams


class CancelTaskResponse(JSONRPCResponse):
    result: Optional[Task] = None


class SetTaskPushNotificationRequest(JSONRPCRequest):
    method: Literal["tasks/pushNotification/set",] = "tasks/pushNotification/set"
    params: TaskPushNotificationConfig


class SetTaskPushNotificationResponse(JSONRPCResponse):
    result: Optional[TaskPushNotificationConfig] = None


class GetTaskPushNotificationRequest(JSONRPCRequest):
    method: Literal["tasks/pushNotification/get",] = "tasks/pushNotification/get"
    params: TaskIdParams


class GetTaskPushNotificationResponse(JSONRPCResponse):
    result: Optional[TaskPushNotificationConfig] = None


class TaskResubscriptionRequest(JSONRPCRequest):
    method: Literal["tasks/resubscribe",] = "tasks/resubscribe"
    params: TaskIdParams


TaskRequest = Union[
    SendTaskRequest,
    GetTaskRequest,
    CancelTaskRequest,
    SetTaskPushNotificationRequest,
    GetTaskPushNotificationRequest,
    TaskResubscriptionRequest,
    SendTaskStreamingRequest,
]
A2ARequest = TypeAdapter(
    Annotated[
        TaskRequest,
        Field(discriminator="method"),
    ]
)

## Error types


class JSONParseError(JSONRPCError):
    code: int = -32700
    message: str = "Invalid JSON payload"
    data: Optional[Any] = None


class InvalidRequestError(JSONRPCError):
    code: int = -32600
    message: str = "Request payload validation error"
    data: Optional[Any] = None


class MethodNotFoundError(JSONRPCError):
    code: int = -32601
    message: str = "Method not found"
    data: None = None


class InvalidParamsError(JSONRPCError):
    code: int = -32602
    message: str = "Invalid parameters"
    data: Optional[Any] = None


class InternalError(JSONRPCError):
    code: int = -32603
    message: str = "Internal error"
    data: Optional[Any] = None


class TaskNotFoundError(JSONRPCError):
    code: int = -32001
    message: str = "Task not found"
    data: None = None


class TaskNotCancelableError(JSONRPCError):
    code: int = -32002
    message: str = "Task cannot be canceled"
    data: None = None


class PushNotificationNotSupportedError(JSONRPCError):
    code: int = -32003
    message: str = "Push Notification is not supported"
    data: None = None


class UnsupportedOperationError(JSONRPCError):
    code: int = -32004
    message: str = "This operation is not supported"
    data: None = None


class ContentTypeNotSupportedError(JSONRPCError):
    code: int = -32005
    message: str = "Incompatible content types"
    data: None = None


class RPCTimeoutError(JSONRPCError):
    code: int = -32006
    message: str = "RPC call timed out"
    data: None = None


class RPCMethodNotFoundError(JSONRPCError):
    code: int = -32007
    message: str = "RPC method not found"
    data: None = None


class RPCExecutionError(JSONRPCError):
    code: int = -32008
    message: str = "RPC method execution failed"
    data: Optional[Any] = None


## RPC-specific request/response types

class RPCCallRequest(JSONRPCRequest):
    """RPC方法调用请求"""
    method: Literal["rpc/call"] = "rpc/call"
    params: dict[str, Any]  # 包含 target_agent_id, rpc_method, args, kwargs


class RPCCallResponse(JSONRPCResponse):
    """RPC方法调用响应"""
    result: Optional[Any] = None


def are_modalities_compatible(server_output_modes: List[str], client_output_modes: List[str]):
    """Modalities are compatible if they are both non-empty
    and there is at least one common element."""
    if client_output_modes is None or len(client_output_modes) == 0:
        return True

    if server_output_modes is None or len(server_output_modes) == 0:
        return True

    return any(x in server_output_modes for x in client_output_modes)


def append_metadata(metadata: dict[str, list], new_metadata: dict[str, Any]) -> None:
    """Append data to the metadata dictionary."""
    for key, value in new_metadata.items():
        if key not in metadata:
            metadata[key] = []
        if isinstance(value, list):
            metadata[key].extend(value)
        else:
            if not isinstance(metadata[key], list):
                metadata[key] = [metadata[key]]
            metadata[key].append(value)

def send_task_request(
    request_id: str,
    session_id: str,
    task_id: str,
    payload: dict[str, Any],
):
    return SendTaskRequest(
        id=request_id,
        params=TaskSendParams(
            id=task_id,
            sessionId=session_id,
            payload=payload,
        ),
    )