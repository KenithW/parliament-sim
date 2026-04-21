"""
Baseline Strategy - 纯 LLM 生成策略

作为对照组，不使用任何策略框架，直接由 LLM 自然生成发言
"""

from strategies.base_strategy import DebateStrategy, StrategyArgument
from typing import Dict


class BaselineStrategy(DebateStrategy):
    """
    Baseline 策略 - 纯 LLM 生成
    
    特点：
    - 无策略干预
    - 让 LLM 自由发挥
    - 作为其他策略的对照基准
    """
    
    def generate_argument(
        self,
        role: str,
        topic: str,
        context: Dict
    ) -> StrategyArgument:
        """
        生成 baseline 策略框架（实际无策略）
        
        Returns:
            返回一个中性策略框架，LLM 将自由生成内容
        """
        return StrategyArgument(
            strategy_type="natural",
            key_arguments=[],
            tone="natural",
            confidence=1.0,
            focus_areas=[]
        )
    
    def name(self) -> str:
        return "baseline"
