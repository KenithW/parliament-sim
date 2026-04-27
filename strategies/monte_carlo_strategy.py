"""Lightweight Monte Carlo strategy selector.

This estimates the value of candidate tactical moves from the current short-term
debate memory. It does not simulate full future LLM conversations, which keeps
the experiment fast and explainable.
"""

from random import Random
from typing import Dict, List

from strategies.base_strategy import DebateStrategy, StrategyAdvice


class MonteCarloStrategy(DebateStrategy):
    def __init__(self, samples: int = 12, seed: int = 11):
        self.samples = samples
        self.seed = seed

    def name(self) -> str:
        return "monte_carlo"

    def advise(self, role: str, topic: str, context: Dict) -> StrategyAdvice:
        rng = Random(f"{self.seed}:{role}:{topic}:{context.get('turn', 0)}")
        candidates = _candidate_advices()
        best = max(
            candidates,
            key=lambda advice: self._estimate_value(advice, context, rng),
        )
        return best

    def _estimate_value(self, advice: StrategyAdvice, context: Dict, rng: Random) -> float:
        total = 0.0
        for _ in range(max(1, self.samples)):
            total += self._score_candidate(advice, context) + rng.uniform(-0.2, 0.2)
        return total / max(1, self.samples)

    def _score_candidate(self, advice: StrategyAdvice, context: Dict) -> float:
        score = 5.0
        phase = context.get("phase", "middle")
        opponent_last = context.get("opponent_last", "").lower()
        side = context.get("side")

        if phase == "opening" and advice.name in {"frame_issue", "values_frame"}:
            score += 1.2
        if phase == "closing" and advice.name in {"contrast_choice", "consensus_close"}:
            score += 1.2
        if opponent_last and advice.name in {"direct_rebuttal", "evidence_push"}:
            score += 1.0
        if any(word in opponent_last for word in ("cost", "budget", "funding")) and advice.name == "evidence_push":
            score += 1.0
        if side == "government" and advice.name == "implementation_focus":
            score += 0.9
        if side == "opposition" and advice.name == "contrast_choice":
            score += 0.9
        if advice.evidence_need == "high":
            score += 0.3
        return score


def _candidate_advices() -> List[StrategyAdvice]:
    return [
        StrategyAdvice("frame_issue", "set the debate criteria", "confident", ["define problem", "state test"], "medium"),
        StrategyAdvice("direct_rebuttal", "defeat the latest opposing claim", "firm", ["rebut claim", "explain flaw"], "high"),
        StrategyAdvice("evidence_push", "win through evidence and metrics", "precise", ["use data", "name measurement"], "high"),
        StrategyAdvice("implementation_focus", "show how the policy works", "practical", ["explain delivery", "address constraints"], "high"),
        StrategyAdvice("contrast_choice", "make the choice between sides clear", "sharp", ["compare alternatives", "name risk"], "medium"),
        StrategyAdvice("consensus_close", "appeal to undecided voters", "constructive", ["offer safeguard", "summarize common ground"], "medium"),
        StrategyAdvice("values_frame", "connect policy to public values", "empathetic", ["name impact", "state principle"], "medium"),
    ]
