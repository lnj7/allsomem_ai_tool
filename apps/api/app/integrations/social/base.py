from abc import ABC, abstractmethod


class SocialPlatformAdapter(ABC):
    @abstractmethod
    def publish(self, payload: dict) -> dict:
        raise NotImplementedError


class UnconfiguredPlatformAdapter(SocialPlatformAdapter):
    def publish(self, payload: dict) -> dict:
        raise RuntimeError(
            "This social platform is not configured. Official API credentials are required before publishing."
        )
