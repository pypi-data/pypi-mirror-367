from supereasyai.ai import (
    AI,
    function_to_tool,
    NoModel
)
from supereasyai.messages import (
    NotStreamed,
    ToolNotFound,
    Content,
    TextContent,
    ImageURLContent,
    InputAudioContent,
    FileContent,
    ToolCall,
    Message,
    SystemMessage,
    DeveloperMessage,
    UserMessage,
    ToolMessage,
    AssistantMessage,
    AssistantMessageStream,
    FormattedAssistantMessage,
    pack_content,
    pack_tool_calls,
    pack_messages,
    unpack_content,
    unpack_tool_calls,
    unpack_messages,
    run_tool_calls
)
from supereasyai.bases import (
    OpenAIBase,
    GroqBase,
    OllamaBase
)


def create_openai(api_key: str | None = None, model: str | None = None, api_environment_key: str = "AI_API_KEY") -> AI:
    return AI(base=OpenAIBase(api_key=api_key, api_environment_key=api_environment_key), model=model)

def create_groq(api_key: str | None = None, model: str | None = None, api_environment_key: str = "AI_API_KEY") -> AI:
    return AI(base=GroqBase(api_key=api_key, api_environment_key=api_environment_key), model=model)

def create_ollama(model: str | None = None) -> AI:
    return AI(base=OllamaBase(), model=model)