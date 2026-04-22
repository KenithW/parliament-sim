"""Baseline strategy: no algorithmic intervention."""

from typing import Dict

from strategies.base_strategy import DebateStrategy, StrategyAdvice


class BaselineStrategy(DebateStrategy):
    def name(self) -> str:
        return "baseline"

    def advise(self, role: str, topic: str, context: Dict) -> StrategyAdvice:
        return StrategyAdvice(
            name="natural_response",
            goal="answer naturally from the role's political position",
            tone="formal and balanced",
            moves=[],
            evidence_need="medium",
        )
