"""Epsilon-greedy bandit strategy.

The strategy learns only within the current experiment process. Run it with
multiple runs if you want the learning behavior to matter.
"""

from random import Random
from typing import Dict, List

from strategies.base_strategy import DebateStrategy, StrategyAdvice
from strategies.monte_carlo_strategy import _candidate_advices


class BanditStrategy(DebateStrategy):
    def __init__(self, epsilon: float = 0.25, seed: int = 23):
        self.epsilon = epsilon
        self.rng = Random(seed)
        self.arms = _candidate_advices()
        self.counts = {advice.name: 0 for advice in self.arms}
        self.rewards = {advice.name: 0.0 for advice in self.arms}
        self.pending_choices: List[str] = []

    def name(self) -> str:
        return "bandit"

    def advise(self, role: str, topic: str, context: Dict) -> StrategyAdvice:
        if self.rng.random() < self.epsilon or not any(self.counts.values()):
            advice = self.rng.choice(self.arms)
        else:
            advice = max(self.arms, key=lambda item: self._average_reward(item.name))
        self.pending_choices.append(advice.name)
        return advice

    def observe_result(self, run_result: Dict) -> None:
        reward = self._reward(run_result)
        for arm in self.pending_choices:
            self.counts[arm] += 1
            self.rewards[arm] += reward
        self.pending_choices.clear()

    def memory_snapshot(self) -> Dict:
        return {
            arm: {
                "count": self.counts[arm],
                "avg_reward": round(self._average_reward(arm), 4),
            }
            for arm in sorted(self.counts)
        }

    def _average_reward(self, arm: str) -> float:
        if self.counts[arm] == 0:
            return 0.0
        return self.rewards[arm] / self.counts[arm]

    def _reward(self, run_result: Dict) -> float:
        quality = float(run_result.get("total_quality", 0.0))
        vote_margin = abs(float(run_result.get("vote_margin", 0.0))) * 0.2
        return quality + vote_margin
