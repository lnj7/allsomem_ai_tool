from app.ai.providers.base import AIProvider
from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import Settings

OpenAIProvider = OpenAICompatibleProvider


class AIGateway:
    def __init__(self, settings: Settings, provider: AIProvider | None = None) -> None:
        self._provider = provider or OpenAICompatibleProvider(settings)

    def generate_text(self, prompt: str) -> str:
        return self._provider.generate_text(prompt)

    def generate_structured(self, prompt: str, schema):
        return self._provider.generate_structured(prompt, schema)
