"""Interfaces reserved for later full implementations. Each agent has explicit I/O."""

from typing import Any


class StrategyAgent:
    def plan(self, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("StrategyAgent is not implemented yet.")


class CreativeAgent:
    def generate(self, brief: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("CreativeAgent is not implemented yet.")


class AnalyticsAgent:
    def analyze(self, metrics: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("AnalyticsAgent is not implemented yet.")


class GrowthAgent:
    def recommend(self, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("GrowthAgent is not implemented yet.")


class PublishingAgent:
    def publish(self, asset: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("PublishingAgent is not implemented yet.")


class OnboardingAgent:
    def summarize(self, answers: dict[str, Any]) -> dict[str, Any]:
        return {"stage": answers.get("creator_stage"), "answers": answers}


class PlatformAnalysisAgent:
    def analyze(self, accounts: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "account_count": len(accounts),
            "platforms": sorted({item.get("platform") for item in accounts if item.get("platform")}),
            "note": "Analysis uses only connected account snapshots. Missing APIs are not invented.",
        }


class ContentExperimentAgent:
    def propose(self, context: dict[str, Any]) -> dict[str, Any]:
        return {"experiments": [], "context_keys": sorted(context.keys())}


class MonetizationAgent:
    def workspace(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": context.get("monetization_status", "UNKNOWN"),
            "note": "CreatorOS does not promise revenue. This workspace only organizes your answers.",
        }
