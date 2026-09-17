"""Interfaces reserved for later full implementations."""


class CreativeAgent:
    def generate(self) -> None:
        raise NotImplementedError("CreativeAgent is not implemented yet.")


class AnalyticsAgent:
    def analyze(self) -> None:
        raise NotImplementedError("AnalyticsAgent is not implemented yet.")


class GrowthAgent:
    def recommend(self) -> None:
        raise NotImplementedError("GrowthAgent is not implemented yet.")


class PublishingAgent:
    def publish(self) -> None:
        raise NotImplementedError("PublishingAgent is not implemented yet.")
