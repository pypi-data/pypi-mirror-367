import copy
import json
from typing import Literal, Any, Iterator
from types import FunctionType
from doms_json import json_call


class NotStreamed(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ToolNotFound(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class Content:
    def __init__(self, type: Literal["text", "image_url", "input_audio", "file"]) -> None:
        self.type: Literal["text", "image_url", "input_audio", "file"] = type


class TextContent(Content):
    def __init__(self, text: str) -> None:
        super().__init__("text")
        self.text: str = text


class ImageURLContent(Content):
    def __init__(self, image_url: str) -> None:
        super().__init__("image_url")
        self.image_url: str = image_url


class InputAudioContent(Content):
    def __init__(self, data: str, format: str):
        super().__init__("input_audio")
        self.data: str = data
        self.format: str = format


class FileContent(Content):
    def __init__(self, filename: str, file_data: str) -> None:
        super().__init__("file")
        self.filename: str = filename
        self.file_data: str = file_data


class ToolCall:
    def __init__(self, id: str, name: str, arguments: dict[str, Any]) -> None:
        self.id: str = id
        self.name: str = name
        self.arguments: dict[str, Any] = arguments


class Message:
    def __init__(self, role: Literal["system", "developer", "assistant", "tool", "user"], content: str | list[Content] | None) -> None:
        self.role: str = role
        self.content: str | list[Content] | None = content


class SystemMessage(Message):
    def __init__(self, content: str) -> None:
        super().__init__("system", content)


class DeveloperMessage(Message):
    def __init__(self, content: str) -> None:
        super().__init__("developer", content)


class UserMessage(Message):
    def __init__(self, content: str | list[Content]) -> None:
        super().__init__("user", content)


class ToolMessage(Message):
    def __init__(self, tool_call_id: str, name: str, content: str) -> None:
        super().__init__("tool", content)
        self.tool_call_id: str = tool_call_id
        self.name: str = name


class AssistantMessage(Message):
    def __init__(self, content: str | None = None, tool_calls: list[ToolCall] | None = None) -> None:
        super().__init__("assistant", content)
        self.tool_calls: list[ToolCall] | None = tool_calls
    
    def run_tool_calls(self, tool_functions: list[FunctionType]) -> list[ToolMessage]:
        return run_tool_calls(self.tool_calls, tool_functions)


class FormattedAssistantMessage(AssistantMessage):
    def __init__(self, content: str, formatted: Any, tool_calls: list[ToolCall] | None = None) -> None:
        super().__init__(content, tool_calls)
        self.formatted: Any = formatted


class AssistantMessageStream(Message):
    def __init__(self) -> None:
        self.__assistant_message__: AssistantMessage | None = None
    
    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError()
    
    @property
    def content(self) -> str | None:
        if self.__assistant_message__:
            return self.__assistant_message__.content
        raise NotStreamed("Could not retreive content because the message has not been streamed yet")
    
    @property
    def tool_calls(self) -> list[ToolCall] | None:
        if self.__assistant_message__:
            return self.__assistant_message__.tool_calls
        raise NotStreamed("Could not retreive tool calls because the message has not been streamed yet")
    
    def run_tool_calls(self, tool_functions: list[FunctionType]) -> list[ToolMessage]:
        return run_tool_calls(self.tool_calls, tool_functions)


def pack_content(content: list[Content]) -> list[dict]:
    packed: list[dict] = []
    for item in copy.deepcopy(content):
        packed.append(vars(item))
    return packed

def pack_tool_calls(tool_calls: list[ToolCall]) -> list[dict]:
    packed: list[dict] = []
    for tool_call in copy.deepcopy(tool_calls):
        packed.append({
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.name,
                "arguments": json.dumps(tool_call.arguments)
            }
        })
    return packed

def pack_messages(messages: list[Message]) -> list[dict]:
    packed: list[dict] = []
    for message in messages:
        data: dict = {}
        if isinstance(message, AssistantMessageStream):
            data = {
                "role": "assistant",
                "content": message.content,
                "tool_calls": message.tool_calls
            }
        else:
            data = vars(copy.deepcopy(message))
        if type(message.content) == list:
            data["content"] = pack_content(message.content)
        if "tool_calls" in data:
            if message.tool_calls == None:
                data.pop("tool_calls")
            else:
                data["tool_calls"] = pack_tool_calls(message.tool_calls)
        if "formatted" in data:
            data.pop("formatted")
        packed.append(data)
    return packed

def unpack_content(content: list[dict]) -> list[Content]:
    unpacked: list[Content] = []
    for item in copy.deepcopy(content):
        content_type: type
        match item["type"]:
            case "text":
                content_type = TextContent
            case "image_url":
                content_type = ImageURLContent
            case "input_audio":
                content_type = InputAudioContent
            case "file":
                content_type = FileContent
        unpacked.append(content_type(**item))
    return unpacked

def unpack_tool_calls(tool_calls: list[dict]) -> list[ToolCall]:
    unpacked: list[ToolCall] = []
    for tool_call in copy.deepcopy(tool_calls):
        unpacked.append(ToolCall(tool_call["id"], tool_call["function"]["name"], json.loads(tool_call["function"]["arguments"])))
    return unpacked

def unpack_messages(messages: list[dict]) -> list[Message]:
    unpacked: list[Message] = []
    for message in copy.deepcopy(messages):
        message_type: type
        match message["role"]:
            case "system":
                message_type = SystemMessage
            case "developer":
                message_type = DeveloperMessage
            case "assistant":
                message_type = AssistantMessage
                if "tool_calls" in message and message["tool_calls"] != None:
                    message["tool_calls"] = unpack_tool_calls(message["tool_calls"])
            case "tool":
                message_type = ToolMessage
            case "user":
                message_type = UserMessage
                if type(message["content"]) == list:
                    message["content"] = unpack_content(message["content"])
        message.pop("role")
        unpacked.append(message_type(**message))
    return unpacked


def run_tool_calls(tool_calls: list[ToolCall], tool_functions: list[FunctionType]) -> list[ToolMessage]:
    functions: dict[str, FunctionType] = {}
    for tool_function in tool_functions:
        functions[tool_function.__name__] = tool_function
    tool_messages: list[ToolMessage] = []
    for tool_call in tool_calls:
        if tool_call.name not in functions:
            raise ToolNotFound(f"Tool not found {tool_call.name}")
        tool_messages.append(ToolMessage(
            tool_call.id,
            tool_call.name,
            f"{json_call(functions[tool_call.name], tool_call.arguments)}"
        ))
    return tool_messages