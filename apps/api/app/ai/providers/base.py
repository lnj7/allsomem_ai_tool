from abc import ABC, abstractmethod

from pydantic import BaseModel


class AINotConfiguredError(RuntimeError):
    pass


class AIProviderError(RuntimeError):
    pass


class AIProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        raise NotImplementedError
