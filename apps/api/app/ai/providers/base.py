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

    def generate_embedding(self, text: str) -> list[float]:
        raise NotImplementedError("Embeddings are not enabled for this provider.")

    def generate_image(self, prompt: str) -> bytes:
        raise NotImplementedError("Image generation is not enabled for this provider.")

    def transcribe_audio(self, audio: bytes) -> str:
        raise NotImplementedError("Transcription is not enabled for this provider.")

    def generate_speech(self, text: str) -> bytes:
        raise NotImplementedError("Speech generation is not enabled for this provider.")
