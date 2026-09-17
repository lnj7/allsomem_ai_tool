import json

from app.ai.agents.content_schema import GeneratedContent
from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import AIProvider


class IdeaAgent:
    prompt_version = "content_idea_v1"

    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider

    def generate(self, context: dict, request: dict) -> GeneratedContent:
        prompt = (
            load_prompt("content_idea_v1.txt")
            + "\n\nCreator context:\n"
            + json.dumps(context, default=str)
            + "\n\nRequest:\n"
            + json.dumps(request, default=str)
        )
        result = self._provider.generate_structured(prompt, GeneratedContent)
        return GeneratedContent.model_validate(result)


class ContentAgent(IdeaAgent):
    pass
