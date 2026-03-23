"""
Heuristic Rules Engine - 硬编码启发式规则引擎
用于快速决策和策略选择
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class StrategyType(Enum):
    """策略类型"""
    AGGRESSIVE = "aggressive"      # 激进
    DEFENSIVE = "defensive"        # 防御
    MODERATE = "moderate"          # 温和
    COMPROMISE = "compromise"      # 妥协


@dataclass
class HeuristicConfig:
    """启发式配置"""
    party_type: str                 # 政党类型
    current_polls: float            # 当前民调支持率 (%)
    topic_sensitivity: str          # 议题敏感度 (high/medium/low)
    public_opinion_shift: float     # 公众舆论变化 (-1~1)


class HeuristicDecisionMaker:
    """
    基于硬编码规则的决策者
    
    规则说明:
    - 如果支持率低 -> 采取激进行动
    - 如果议题敏感度高 -> 谨慎回应
    - 如果对方激进 -> 根据角色决定反击或防御
    """
    
    def __init__(self, config: HeuristicConfig):
        self.config = config
        self.strategy_history = []
    
    def decide_strategy(self, opponent_strategy: StrategyType) -> StrategyType:
        """
        根据规则和对手策略决定自己的策略
        
        Args:
            opponent_strategy: 对手使用的策略
        
        Returns:
            选择的策略
        """
        score = 0  # 策略评分
        
        print(f"[HEURISTIC] 分析中:")
        print(f"  - 政党：{self.config.party_type}")
        print(f"  - 民调支持率：{self.config.current_polls}%")
        print(f"  - 议题敏感度：{self.config.topic_sensitivity}")
        print(f"  - 对手策略：{opponent_strategy.value}")
        
        # ======================
        # 规则 1: 民调支持率决定基础策略
        # ======================
        if self.config.current_polls < 40:
            # 支持率低 -> 激进
            score += StrategyType.AGGRESSIVE.value
            print("  + 支持率低，增加激进倾向")
        elif self.config.current_polls > 60:
            # 支持率高 -> 稳健
            score += StrategyType.MODERATE.value
            print("  + 支持率高，保持稳健")
        else:
            # 中间 -> 灵活
            score += StrategyType.COMPROMISE.value
            print("  + 支持率中等，尝试妥协")
        
        # ======================
        # 规则 2: 议题敏感度调整
        # ======================
        if self.config.topic_sensitivity == "high":
            score += StrategyType.DEFENSIVE.value * 2
            print("  + 议题高度敏感，加强防御")
        elif self.config.topic_sensitivity == "low":
            score += StrategyType.AGGRESSIVE.value * 1.5
            print("  + 议题不敏感，可以更激进")
        
        # ======================
        # 规则 3: 应对对手
        # ======================
        if opponent_strategy == StrategyType.AGGRESSIVE:
            if self.config.party_type == "labour":
                # 工党面对攻击时更坚定
                score += StrategyType.AGGRESSIVE.value * 1.5
                print("  + 作为工党，对抗激进对手")
            else:
                # 其他党派对激进采取防御
                score += StrategyType.DEFENSIVE.value
                print("  + 对激进对手采取防御")
        
        # ======================
        # 规则 4: 民调趋势影响
        # ======================
        if self.config.public_opinion_shift > 0.2:
            score += StrategyType.AGGRESSIVE.value
            print("  + 舆论向好，增加冒险")
        elif self.config.public_opinion_shift < -0.2:
            score += StrategyType.COMPROMISE.value
            print("  + 舆论恶化，寻求妥协")
        
        # ======================
        # 选择最高分的策略
        # ======================
        best_strategy = max(StrategyType, key=lambda x: score.get(x, 0))
        
        # 记录历史
        self.strategy_history.append({
            "turn": len(self.strategy_history),
            "strategy": best_strategy.value,
            "opponent": opponent_strategy.value,
            "score": score
        })
        
        print(f"\n[HEURISTIC] 决定使用策略：{best_strategy.value.upper()}\n")
        
        return best_strategy
    
    def get_strategy_trend(self) -> List[str]:
        """获取策略变化趋势"""
        return [record["strategy"] for record in self.strategy_history]
    
    def calculate_effectiveness(self, outcome: str) -> float:
        """
        评估策略有效性
        
        Args:
            outcome: 结果 ("positive", "neutral", "negative")
        
        Returns:
            得分 (0~1)
        """
        scores = {"positive": 1.0, "neutral": 0.5, "negative": 0.2}
        last_strategy = self.strategy_history[-1]["strategy"]
        
        print(f"\n[HEURISTIC] 策略评估:")
        print(f"  - 使用策略：{last_strategy}")
        print(f"  - 实际结果：{outcome}")
        print(f"  - 得分：{scores[outcome]}")
        
        return scores[outcome]


# ======================
# 便捷工厂函数
# ======================
def create_heuristic_agent(
    party_type: str = "conservative",
    current_polls: float = 45.0,
    topic_sensitivity: str = "medium",
    public_opinion_shift: float = 0.0
) -> HeuristicDecisionMaker:
    """创建启发式 Agent"""
    
    config = HeuristicConfig(
        party_type=party_type,
        current_polls=current_polls,
        topic_sensitivity=topic_sensitivity,
        public_opinion_shift=public_opinion_shift
    )
    
    return HeuristicDecisionMaker(config)


# ======================
# 测试示例
# ======================
if __name__ == "__main__":
    print("=" * 60)
    print("HEURISTIC RULES ENGINE TEST")
    print("=" * 60)
    
    # 创建首相的启发式代理
    pm = create_heuristic_agent(
        party_type="conservative",
        current_polls=42.0,
        topic_sensitivity="high",
        public_opinion_shift=-0.1
    )
    
    # 模拟几个回合的决策
    strategies = [
        StrategyType.MODERATE,
        StrategyType.AGGRESSIVE,
        StrategyType.COMPROMISE,
    ]
    
    for i, opp_strategy in enumerate(strategies):
        print(f"\n{'='*60}")
        print(f"ROUND {i+1}")
        print('='*60)
        
        chosen = pm.decide_strategy(opp_strategy)
        print(f"RESULT: {chosen.value}")
    
    print("\n" + "="*60)
    print("STRATEGY HISTORY:")
    print(pm.get_strategy_trend())
    print("="*60)
