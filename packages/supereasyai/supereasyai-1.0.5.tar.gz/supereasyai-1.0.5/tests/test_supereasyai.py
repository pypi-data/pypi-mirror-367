import os, pytest
from types import FunctionType
from dotenv import load_dotenv
from supereasyai import (
    AI, create_openai, create_groq, Message, SystemMessage, UserMessage, DeveloperMessage,
    AssistantMessage, ToolMessage, ToolCall, AssistantMessageStream, pack_messages, unpack_messages,
    FormattedAssistantMessage
)

load_dotenv()

@pytest.fixture(autouse=True)
def openai_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("No OPENAI_API_KEY")
    return key

@pytest.fixture(autouse=True)
def openai_model():
    key = os.getenv("OPENAI_MODEL")
    if not key:
        pytest.skip("No OPENAI_MODEL")
    return key

@pytest.fixture(autouse=True)
def groq_api_key():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        pytest.skip("No GROQ_API_KEY")
    return key

@pytest.fixture(autouse=True)
def groq_model():
    key = os.getenv("GROQ_MODEL")
    if not key:
        pytest.skip("No GROQ_MODEL")
    return key


class Steps:
    def __init__(self, steps: list[str]) -> None:
        self.steps: list[str] = steps


class Reasoning:
    def __init__(self, steps: Steps, answer: str) -> None:
        self.steps: Steps = steps
        self.answer: str = answer


def test_supereasyai(openai_api_key, openai_model, groq_api_key, groq_model):
    # Pack some messages
    messages: list[Message] = [
        SystemMessage("System message"),
        DeveloperMessage("Developer message"),
        UserMessage("User message"),
        AssistantMessage("Assistant message"),
        FormattedAssistantMessage("{\"key\": \"value\"}", {"key": "value"}),
        AssistantMessage(tool_calls=[ToolCall("abc-123", "name", {"key": "value"})]),
        ToolMessage("abc-123", "name", "Tool message")
    ]
    packed_messages: dict = pack_messages(messages)
    assert packed_messages == [
        {
            "role": "system",
            "content": "System message"
        },
        {
            "role": "developer",
            "content": "Developer message"
        },
        {
            "role": "user",
            "content": "User message"
        },
        {
            "role": "assistant",
            "content": "Assistant message",
        },
        {
            "role": "assistant",
            "content": "{\"key\": \"value\"}",
        },
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "abc-123",
                    "type": "function",
                    "function": {
                        "name": "name",
                        "arguments": "{\"key\": \"value\"}"
                    }
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id": "abc-123",
            "name": "name",
            "content": "Tool message"
        }
    ]
    unpacked_messages: list[Message] = unpack_messages(packed_messages)
    for original, loaded in zip(messages, unpacked_messages):
        assert type(original) == type(loaded) or (isinstance(original, AssistantMessage) and type(loaded) == AssistantMessage)
        assert original.role == loaded.role
        assert original.content == loaded.content
        if isinstance(original, AssistantMessage) and type(loaded) == AssistantMessage:
            assert type(original.tool_calls) == type(loaded.tool_calls)
            if original.tool_calls != None and loaded.tool_calls != None:
                for original_tool_call, loaded_tool_call in zip(original.tool_calls, loaded.tool_calls):
                    assert original_tool_call.name == loaded_tool_call.name
                    assert original_tool_call.arguments == loaded_tool_call.arguments
                    assert original_tool_call.id == loaded_tool_call.id
        if type(original) == ToolMessage and type(loaded) == ToolMessage:
            assert original.tool_call_id == loaded.tool_call_id
            assert original.name == loaded.name
    # Define some functions for tool testing
    def add(a: int, b: int) -> int:
        """
        Add two integers

        :param a: The first number
        :param b: The second number

        |
        """
        return a + b
    def subtract(a: int, b: int) -> int:
        """
        Subtract two integers

        :param a: The first number
        :param b: The second number

        |
        """
        return a - b
    def get_password() -> str:
        return "Spaghetti"
    def get_secret(password: str) -> str:
        return "The secret is \"Meatballs\""
    # Create an OpenAI AI
    openai: AI = create_openai(
        api_key=openai_api_key,
        model=openai_model
    )
    assert openai.model == openai_model
    # Create a Groq AI
    groq: AI = create_groq(
        api_key=groq_api_key,
        model=groq_model
    )
    assert groq.model == groq_model
    # Run the same tests for both AIs
    for ai in [openai, groq]:
        # Simple text query
        messages: list[Message] = [UserMessage("Repeat these words exactly: \"Hello world!\"\nDon't say anything else.")]
        assert ai.query(messages).content == "Hello world!"
        # Simple stream text query
        response: AssistantMessageStream = ai.query(messages, stream=True)
        for chunk in response:
            pass
        assert response.content == "Hello world!"
        # Simple tool call
        tools: list[FunctionType] = [add, subtract]
        messages: list[Message] = [SystemMessage("Use the \"add\" tool to complete the user's request.\nYour final response should be in the following format:\n\"The answer is: {value}\""), UserMessage("What's 5 + 3?")]
        response: AssistantMessage = ai.query(messages, tools=tools)
        assert response.tool_calls != None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].arguments == {"a": 5, "b": 3}
        # Simple stream tool call
        response: AssistantMessageStream = ai.query(messages, stream=True, tools=tools)
        for chunk in response:
            pass
        assert response.tool_calls != None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "add"
        assert response.tool_calls[0].arguments == {"a": 5, "b": 3}
        # Query and run tool call
        response: list[AssistantMessage | ToolMessage] = ai.query_and_run_tools(messages, tools=tools)
        assert len(response) == 2
        assert type(response[0]) == AssistantMessage
        assert response[0].tool_calls != None
        assert len(response[0].tool_calls) == 1
        assert response[0].tool_calls[0].name == "add"
        assert response[0].tool_calls[0].arguments == {"a": 5, "b": 3}
        assert type(response[1]) == ToolMessage
        assert response[1].tool_call_id == response[0].tool_calls[0].id
        assert response[1].name == "add"
        assert response[1].content == "8"
        # Query and run tool call with "follow_up" autonomy
        response: list[AssistantMessage | ToolMessage] = ai.query_and_run_tools(messages, tools=tools, autonomy="follow_up")
        assert len(response) == 3
        assert type(response[0]) == AssistantMessage
        assert response[0].tool_calls != None
        assert len(response[0].tool_calls) == 1
        assert response[0].tool_calls[0].name == "add"
        assert response[0].tool_calls[0].arguments == {"a": 5, "b": 3}
        assert type(response[1]) == ToolMessage
        assert response[1].tool_call_id == response[0].tool_calls[0].id
        assert response[1].name == "add"
        assert response[1].content == "8"
        assert type(response[2]) == AssistantMessage
        assert response[2].tool_calls == None
        assert response[2].content == "The answer is: 8"
        # Query and run tool call with "full" autonomy
        tools: list[FunctionType] = [get_password, get_secret]
        messages: list[Message] = [SystemMessage("Get and return the secret value.\n To get the secret, you must first get the password.\nYour response must be just the secret word, exactly. Nothing else.")]
        response: list[AssistantMessage | ToolMessage] = ai.query_and_run_tools(messages, tools=tools, autonomy="full")
        assert type(response[-1]) == AssistantMessage
        assert response[-1].tool_calls == None
        assert response[-1].content == "Meatballs"
        # Query with a format
        messages: list[Message] = [SystemMessage("Think through the user's request to ensure you calculate the correct answer.\nYour final answer should be exactly as shown in the following format:\n\"The answer is: {value}\""), UserMessage("What's 5 + 3?")]
        response: FormattedAssistantMessage = ai.query(messages, format=Reasoning)
        assert type(response) == FormattedAssistantMessage
        assert type(response.formatted) == Reasoning
        assert response.formatted.answer == "The answer is: 8"
        # Query with tool calls and a format
        if ai != groq:
            tools: list[FunctionType] = [get_password, get_secret]
            messages: list[Message] = [SystemMessage("Get and return the secret value.\n To get the secret, you must first get the password.\nYour answer must be just the secret word, exactly. Nothing else.")]
            response: list[FormattedAssistantMessage | ToolMessage] = ai.query_and_run_tools(messages, format=Reasoning, tools=tools, autonomy="full")
            assert type(response[-1]) == FormattedAssistantMessage
            assert type(response[-1].formatted) == Reasoning
            assert response[-1].tool_calls == None
            assert response[-1].formatted.answer == "Meatballs"
