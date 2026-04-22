"""Small genetic-style strategy selector.

This keeps the experiment lightweight: the algorithm evolves tactical advice
templates, not generated text. Fitness is based on role fit, debate timing, and
whether the previous opponent speech needs a rebuttal.
"""

from dataclasses import replace
from random import Random
from typing import Dict, List

from strategies.base_strategy import DebateStrategy, StrategyAdvice


class GeneticStrategy(DebateStrategy):
    def __init__(self, population_size: int = 8, generations: int = 4, seed: int = 7):
        self.population_size = population_size
        self.generations = generations
        self.seed = seed

    def name(self) -> str:
        return "genetic"

    def advise(self, role: str, topic: str, context: Dict) -> StrategyAdvice:
        rng = Random(f"{self.seed}:{role}:{topic}:{context.get('turn', 0)}")
        population = self._initial_population()

        for _ in range(self.generations):
            ranked = sorted(
                population,
                key=lambda item: self._fitness(item, context),
                reverse=True,
            )
            parents = ranked[: max(2, self.population_size // 3)]
            population = parents[:]
            while len(population) < self.population_size:
                population.append(self._mutate(rng.choice(parents), rng))

        return max(population, key=lambda item: self._fitness(item, context))

    def _initial_population(self) -> List[StrategyAdvice]:
        return [
            StrategyAdvice("evidence_push", "win through concrete evidence", "precise", ["use data", "compare outcomes"], "high"),
            StrategyAdvice("rebuttal_first", "neutralize the opponent's strongest claim", "firm", ["rebut directly", "expose assumption"], "high"),
            StrategyAdvice("values_frame", "connect policy to public values", "empathetic", ["name affected citizens", "state principle"], "medium"),
            StrategyAdvice("implementation_focus", "show how the policy would work", "practical", ["sequence actions", "name constraints"], "high"),
            StrategyAdvice("contrast_choice", "make the debate a clear choice", "sharp", ["contrast options", "define risk"], "medium"),
            StrategyAdvice("consensus_builder", "sound credible to undecided listeners", "constructive", ["concede one point", "propose safeguard"], "medium"),
        ]

    def _fitness(self, advice: StrategyAdvice, context: Dict) -> float:
        score = 1.0
        if context.get("opponent_last") and "rebut" in " ".join(advice.moves + [advice.name]):
            score += 2.0
        if context.get("side") == "government" and advice.name in {"implementation_focus", "evidence_push"}:
            score += 1.2
        if context.get("side") == "opposition" and advice.name in {"rebuttal_first", "contrast_choice"}:
            score += 1.2
        if int(context.get("turn", 0)) >= 5 and advice.name in {"contrast_choice", "consensus_builder"}:
            score += 0.8
        if advice.evidence_need == "high":
            score += 0.3
        return score

    def _mutate(self, advice: StrategyAdvice, rng: Random) -> StrategyAdvice:
        tones = ["precise", "firm", "measured", "constructive", "urgent"]
        move_pool = ["use data", "rebut directly", "name trade-off", "offer safeguard", "compare outcomes"]
        moves = list(advice.moves)
        if rng.random() < 0.6 and move_pool:
            moves = (moves + [rng.choice(move_pool)])[-3:]
        evidence_need = "high" if rng.random() < 0.65 else "medium"
        return replace(advice, tone=rng.choice(tones), moves=moves, evidence_need=evidence_need)
