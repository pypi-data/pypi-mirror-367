from supereasyai.bases.open_ai_base import OpenAIBase
from supereasyai.bases.groq_base import GroqBase


class OllamaBase(OpenAIBase):
    def __init__(self) -> None:
        super().__init__(api_key="ollama", base_url="http://localhost:11434/v1")