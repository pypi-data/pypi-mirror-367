import os, json
from types import FunctionType
from typing import Any, Literal, Iterator
from supereasyai.ai import AIBase, function_to_tool
from supereasyai.messages import AssistantMessage, AssistantMessageStream, Message, ToolCall, pack_messages, FormattedAssistantMessage
from doms_json import generate_json_schema, json_call
from openai import OpenAI as OpenAIClient, Stream, NOT_GIVEN
from openai.types.chat import ChatCompletion, ChatCompletionChunk


class OpenAIAssistantMessageStream(AssistantMessageStream):
    def __init__(self, stream: Stream[ChatCompletionChunk]) -> None:
        self.__stream__: Stream[ChatCompletionChunk] = stream

    def __iter__(self) -> Iterator[str]:
        content: str | None = None
        tool_calls: dict[int, dict] = {}
        for chunk in self.__stream__:
            delta = chunk.choices[0].delta
            if delta:
                if delta.content:
                    if content == None:
                        content = delta.content
                    else:
                        content += delta.content
                    yield delta.content
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        if tool_call.index in tool_calls:
                            tool_calls[tool_call.index]["arguments"] += tool_call.function.arguments
                        else:
                            tool_calls[tool_call.index] = {
                                "id": tool_call.id,
                                "arguments": tool_call.function.arguments,
                                "name": tool_call.function.name
                            }
        self.__assistant_message__ = AssistantMessage(
            content,
            [ToolCall(tool_call["id"], tool_call["name"], json.loads(tool_call["arguments"])) for tool_call in tool_calls.values()] if tool_calls else None
        )


class OpenAIBase(AIBase):
    def __init__(self, api_key: str | None = None, api_environment_key: str = "AI_API_KEY", base_url: str | None = None):
        self.__client__: OpenAIClient = OpenAIClient(
            api_key=(api_key if api_key else os.environ.get(api_environment_key)),
            base_url=base_url
        )
        
    def query(self,
              messages: list[Message],
              format: type | None = None,
              model: str | None = None,
              temperature: float | None = None,
              tools: list[dict | FunctionType] | None = None,
              tool_choice: Literal["none", "auto", "required"] | None = None,
              force_tool: str | None = None,
              stream: bool = False) -> AssistantMessage | OpenAIAssistantMessageStream:
        if stream and format:
            raise Exception("Cannot stream a formatted message")
        tool_schemas: list[dict] | None = None
        if tools:
            tool_schemas = []
            for tool in tools:
                if type(tool) == dict:
                    tool_schemas.append(tool)
                else:
                    tool_schemas.append(function_to_tool(tool))
        response: ChatCompletion | Stream[ChatCompletionChunk] = self.__client__.chat.completions.create(
            model=model,
            messages=pack_messages(messages),
            temperature=temperature if temperature else NOT_GIVEN,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": format.__name__,
                    "schema": generate_json_schema(format),
                    "strict": True
                }
            } if format else NOT_GIVEN,
            tools=tool_schemas if tool_schemas else NOT_GIVEN,
            tool_choice=({"type": "function", "function": {"name": force_tool}} if force_tool else (tool_choice if tool_choice else NOT_GIVEN)),
            stream=stream
        )
        if type(response) == ChatCompletion:
            content: str | None = response.choices[0].message.content
            tool_calls: list[ToolCall] | None = [ToolCall(tool_call.id, tool_call.function.name, json.loads(tool_call.function.arguments)) for tool_call in response.choices[0].message.tool_calls] if response.choices[0].message.tool_calls else None
            if format and content:
                return FormattedAssistantMessage(content, json_call(format, json.loads(content)), tool_calls)
            return AssistantMessage(content, tool_calls)
        else:
            return OpenAIAssistantMessageStream(response)