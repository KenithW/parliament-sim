from strategies.base_strategy import DebateStrategy, StrategyAdvice
from strategies.bandit_strategy import BanditStrategy
from strategies.baseline_strategy import BaselineStrategy
from strategies.genetic_strategy import GeneticStrategy
from strategies.heuristic_rule_strategy import HeuristicRuleStrategy
from strategies.monte_carlo_strategy import MonteCarloStrategy
from strategies.react_strategy import ReActStrategy

STRATEGY_REGISTRY = {
    "baseline": BaselineStrategy,
    "heuristic_rule": HeuristicRuleStrategy,
    "genetic": GeneticStrategy,
    "react": ReActStrategy,
    "monte_carlo": MonteCarloStrategy,
    "bandit": BanditStrategy,
}

__all__ = [
    "BanditStrategy",
    "BaselineStrategy",
    "DebateStrategy",
    "GeneticStrategy",
    "HeuristicRuleStrategy",
    "MonteCarloStrategy",
    "ReActStrategy",
    "STRATEGY_REGISTRY",
    "StrategyAdvice",
]
