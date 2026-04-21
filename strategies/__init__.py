"""
Debate Strategies - 辩论策略层

提供多种辩论策略实现，用于对比实验
"""

from strategies.base_strategy import (
    DebateStrategy,
    StrategyArgument,
    extract_debate_context,
)
from strategies.baseline_strategy import BaselineStrategy
from strategies.heuristic_rule_strategy import HeuristicRuleStrategy

__all__ = [
    "DebateStrategy",
    "StrategyArgument",
    "extract_debate_context",
    "BaselineStrategy",
    "HeuristicRuleStrategy",
]
