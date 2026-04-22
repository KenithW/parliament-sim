from strategies.base_strategy import DebateStrategy, StrategyAdvice
from strategies.baseline_strategy import BaselineStrategy
from strategies.genetic_strategy import GeneticStrategy
from strategies.heuristic_rule_strategy import HeuristicRuleStrategy

STRATEGY_REGISTRY = {
    "baseline": BaselineStrategy,
    "heuristic_rule": HeuristicRuleStrategy,
    "genetic": GeneticStrategy,
}

__all__ = [
    "BaselineStrategy",
    "DebateStrategy",
    "GeneticStrategy",
    "HeuristicRuleStrategy",
    "STRATEGY_REGISTRY",
    "StrategyAdvice",
]
