import json
from typing import Any

import httpx
from app.ai.providers.base import AINotConfiguredError, AIProvider, AIProviderError
from app.core.config import Settings
from pydantic import BaseModel, ValidationError


class OpenAICompatibleProvider(AIProvider):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _ensure_configured(self) -> None:
        if not self._settings.ai_api_key.strip():
            raise AINotConfiguredError("AI provider is not configured.")

    def generate_text(self, prompt: str) -> str:
        self._ensure_configured()
        return self._complete(prompt)

    def generate_structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        self._ensure_configured()
        last_error: Exception | None = None
        current_prompt = (
            prompt + "\n\nReturn only valid JSON matching the required schema. No markdown."
        )
        for _ in range(2):
            raw = self._complete(current_prompt, json_mode=True)
            try:
                data = json.loads(raw)
                return schema.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
                current_prompt = (
                    "The previous JSON was invalid. Correct it to match the schema. "
                    f"Error: {exc}\nPrevious output:\n{raw}"
                )
        raise AIProviderError(f"AI returned invalid structured output: {last_error}")

    def _complete(self, prompt: str, json_mode: bool = False) -> str:
        payload: dict[str, Any] = {
            "model": self._settings.ai_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {
            "Authorization": f"Bearer {self._settings.ai_api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self._settings.ai_base_url.rstrip('/')}/chat/completions"
        try:
            with httpx.Client(timeout=45.0) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code >= 400:
                    raise AIProviderError(self._error_message(response))
                data = response.json()
        except httpx.HTTPError as exc:
            raise AIProviderError("AI provider request failed.") from exc
        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("AI provider returned an unexpected response.") from exc

    @staticmethod
    def _error_message(response: httpx.Response) -> str:
        try:
            payload = response.json()
            error = payload.get("error") if isinstance(payload, dict) else None
            if isinstance(error, dict):
                message = str(error.get("message") or "").strip()
                code = str(error.get("code") or error.get("type") or "").strip()
                if message and code in {"insufficient_quota", "credit_balance_exhausted"}:
                    return (
                        "OpenAI has no credits on this API key. "
                        "Add billing credit at https://platform.openai.com/settings/organization/billing/"
                    )
                if message:
                    return message
            if isinstance(error, str) and error.strip():
                return error.strip()
        except ValueError:
            pass
        if response.status_code == 429:
            return "OpenAI rate limit or quota exceeded. Wait or add billing credit, then try again."
        if response.status_code == 401:
            return "OpenAI rejected the API key. Check AI_API_KEY in .env."
        return f"AI provider request failed ({response.status_code})."
