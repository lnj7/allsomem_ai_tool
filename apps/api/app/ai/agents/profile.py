import json

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import AIProvider
from app.schemas.product import CreatorProfileSchema


class StrategyAgent:
    prompt_version = "creator_profile_v1"

    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider

    def generate_profile(self, context: dict) -> CreatorProfileSchema:
        prompt = (
            load_prompt("creator_profile_v1.txt")
            + "\n\nCreator context:\n"
            + json.dumps(context, default=str)
        )
        result = self._provider.generate_structured(prompt, CreatorProfileSchema)
        return CreatorProfileSchema.model_validate(result)


class CreatorProfileAgent(StrategyAgent):
    pass
