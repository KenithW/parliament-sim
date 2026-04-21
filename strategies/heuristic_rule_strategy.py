"""
Heuristic Rule Strategy - 启发式规则策略

基于硬编码的决策规则生成辩论策略框架
"""

from strategies.base_strategy import DebateStrategy, StrategyArgument
from typing import Dict
from enum import Enum


class StrategyType(Enum):
    """策略类型"""
    AGGRESSIVE = "aggressive"      # 激进
    DEFENSIVE = "defensive"        # 防御
    MODERATE = "moderate"          # 温和
    COMPROMISE = "compromise"      # 妥协


class HeuristicRuleStrategy(DebateStrategy):
    """
    启发式规则策略
    
    基于以下规则决定策略：
    - 民调支持率：低→激进，高→稳健
    - 议题敏感度：高→防御，低→激进
    - 对手策略：根据角色决定应对
    - 舆论趋势：向好→冒险，恶化→妥协
    """
    
    # 策略到论点的映射
    ARGUMENT_MAPPING = {
        StrategyType.AGGRESSIVE: StrategyArgument(
            strategy_type="aggressive_attack",
            key_arguments=[
                "攻击对方政策弱点",
                "质疑对方执政记录",
                "强调对方承诺未兑现"
            ],
            tone="confrontational",
            confidence=0.8,
            focus_areas=["批判", "质疑", "进攻"]
        ),
        StrategyType.DEFENSIVE: StrategyArgument(
            strategy_type="defensive_block",
            key_arguments=[
                "防御己方政策立场",
                "澄清对方误解",
                "强调己方成就"
            ],
            tone="measured",
            confidence=0.7,
            focus_areas=["辩护", "澄清", "稳固"]
        ),
        StrategyType.MODERATE: StrategyArgument(
            strategy_type="moderate_response",
            key_arguments=[
                "寻求共识点",
                "平衡各方利益",
                "强调务实方案"
            ],
            tone="balanced",
            confidence=0.75,
            focus_areas=["平衡", "务实", "共识"]
        ),
        StrategyType.COMPROMISE: StrategyArgument(
            strategy_type="seek_compromise",
            key_arguments=[
                "提出折中方案",
                "强调合作重要性",
                "呼吁跨党派支持"
            ],
            tone="conciliatory",
            confidence=0.65,
            focus_areas=["妥协", "合作", "团结"]
        ),
    }
    
    def __init__(
        self,
        party_type: str = "conservative",
        current_polls: float = 50.0,
        topic_sensitivity: str = "medium",
        public_opinion_shift: float = 0.0
    ):
        """
        初始化启发式策略
        
        Args:
            party_type: 政党类型 (conservative/labour)
            current_polls: 当前民调支持率 (%)
            topic_sensitivity: 议题敏感度 (high/medium/low)
            public_opinion_shift: 舆论变化 (-1~1)
        """
        self.party_type = party_type
        self.current_polls = current_polls
        self.topic_sensitivity = topic_sensitivity
        self.public_opinion_shift = public_opinion_shift
        self.strategy_history = []
    
    def generate_argument(
        self,
        role: str,
        topic: str,
        context: Dict
    ) -> StrategyArgument:
        """
        根据规则生成策略框架
        
        Args:
            role: 发言人角色
            topic: 议题
            context: 辩论上下文
        
        Returns:
            StrategyArgument: 策略框架
        """
        # 决定策略
        strategy = self._decide_strategy(role, context)
        
        # 映射到策略框架
        return self.ARGUMENT_MAPPING[strategy]
    
    def _decide_strategy(self, role: str, context: Dict) -> StrategyType:
        """
        根据规则决定策略
        
        规则：
        1. 支持率低 (<40) → 激进
        2. 支持率高 (>60) → 稳健
        3. 议题敏感度高 → 防御
        4. 舆论向好 → 激进
        5. 舆论恶化 → 妥协
        """
        score = {}  # 各策略得分
        
        # 规则 1: 民调支持率
        if self.current_polls < 40:
            score[StrategyType.AGGRESSIVE] = score.get(StrategyType.AGGRESSIVE, 0) + 2
        elif self.current_polls > 60:
            score[StrategyType.MODERATE] = score.get(StrategyType.MODERATE, 0) + 2
        else:
            score[StrategyType.COMPROMISE] = score.get(StrategyType.COMPROMISE, 0) + 1
        
        # 规则 2: 议题敏感度
        if self.topic_sensitivity == "high":
            score[StrategyType.DEFENSIVE] = score.get(StrategyType.DEFENSIVE, 0) + 2
        elif self.topic_sensitivity == "low":
            score[StrategyType.AGGRESSIVE] = score.get(StrategyType.AGGRESSIVE, 0) + 1
        
        # 规则 3: 舆论趋势
        if self.public_opinion_shift > 0.2:
            score[StrategyType.AGGRESSIVE] = score.get(StrategyType.AGGRESSIVE, 0) + 1
        elif self.public_opinion_shift < -0.2:
            score[StrategyType.COMPROMISE] = score.get(StrategyType.COMPROMISE, 0) + 1
        
        # 规则 4: 根据角色调整
        if role in ["pm", "chancellor"]:
            # 执政党更倾向稳健
            score[StrategyType.MODERATE] = score.get(StrategyType.MODERATE, 0) + 0.5
        else:
            # 反对党更倾向激进
            score[StrategyType.AGGRESSIVE] = score.get(StrategyType.AGGRESSIVE, 0) + 0.5
        
        # 返回得分最高的策略
        if score:
            return max(score, key=score.get)
        return StrategyType.MODERATE
    
    def name(self) -> str:
        return "heuristic_rule"
    
    def update_context(
        self,
        current_polls: float = None,
        topic_sensitivity: str = None,
        public_opinion_shift: float = None
    ):
        """更新上下文参数"""
        if current_polls is not None:
            self.current_polls = current_polls
        if topic_sensitivity is not None:
            self.topic_sensitivity = topic_sensitivity
        if public_opinion_shift is not None:
            self.public_opinion_shift = public_opinion_shift
