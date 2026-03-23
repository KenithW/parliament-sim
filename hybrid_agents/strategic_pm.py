"""
Strategic Prime Minister Agent - 战略首相
集成了遗传算法、Q-Learning 和启发式搜索的智能决策者
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import sys
sys.path.insert(0, 'D:\\PyCharmProgram\\parliament-sim')

# 导入原有组件
from langchain_core.prompts import ChatPromptTemplate
from state import DebateRecord, ParliamentState

# 导入我们的 AI 算法模块
from algorithms.genetic import GeneticAlgorithm, HeuristicDecisionMaker
from algorithms.q_learning import QLearningAgent, State as QLState, ActionLibrary
from algorithms.heuristic_search import HeuristicSearchEngine


class StrategicPrimeMinister:
    """
    战略首相 Agent
    
    融合了多种 AI 算法来优化辩论策略：
    
    1. **遗传算法** - 长期政策立场进化
    2. **Q-Learning** - 从历史中学习最优战术
    3. **启发式搜索** - 实时策略选择和快速响应
    4. **硬编码规则** - 基础决策框架
    
    使用场景：
    - 需要长期战略规划的复杂议题
    - 对手使用了智能策略
    - 民调压力大的敏感时期
    """
    
    def __init__(self):
        # ======================
        # 初始化各算法模块
        # ======================
        
        # 1. 遗传算法 - 用于政策进化（每几轮运行一次）
        self.ga = GeneticAlgorithm(
            population_size=20,
            mutation_rate=0.15,
            generations=5  # 简化版，只进化 5 代
        )
        
        # 2. Q-Learning - 学习即时战术
        self.q_agent = QLearningAgent(
            learning_rate=0.15,      # 更快的学习率
            epsilon=0.4,             # 更多探索
            epsilon_decay=0.98       # 较慢的衰减
        )
        
        # 3. 启发式搜索 - 实时决策
        self.hsearch_engine = HeuristicSearchEngine()
        
        # 4. 硬编码启发式规则
        self.heuristic_rules = None
        
        # ======================
        # 状态跟踪
        # ======================
        self.strategy_history = []
        self.evolution_rounds = []
        
        # 提示词模板
        self.pm_prompt = ChatPromptTemplate.from_template("""
你是不容许党的首相。当前辩论议题：{topic}

## 你的战略分析

### 长期政策立场（来自遗传算法）
- 经济自由化：{policy_economy}
- 社会福利投入：{policy_welfare}
- 环境保护力度：{policy_environment}

### 当前战术建议（来自 Q-Learning）
- 建议行动：{q_action}
- 信心度：{q_confidence}

### 实时环境评估
- 对手强度：{opponent_strength:.2f}
- 公众支持：{public_approval}%
- 舆论趋势：{momentum:+.2f}

请发表你的发言，体现战略思维和适应能力。
""")
    
    def prepare_for_debate(self, topic: str, initial_state: dict):
        """
        辩论前准备
        
        Args:
            topic: 辩论议题
            initial_state: 初始状态（包含民调、支持率等）
        """
        print("\n" + "=" * 60)
        print("🧬 STRATEGIC PM AGENT - Pre-debate Preparation")
        print("=" * 60)
        
        # 启动遗传算法进行短期政策进化
        print("\n[GA] Running policy evolution...")
        best_policy = self.ga.evolve()
        policy_analysis = self.ga.get_policy_analysis()
        
        print("\n📊 Evolved Policy Position:")
        for key, value in policy_analysis.items():
            if isinstance(value, float) and key != "emotional_intensity":
                print(f"  • {key}: {value:.2f}")
        
        # 初始化 Q-Learning Agent
        print("\n[QL] Initializing policy learning history...")
        
        # 保存进化记录
        self.evolution_rounds.append({
            "round": len(self.evolution_rounds),
            "topic": topic,
            "policy": policy_analysis,
            "timestamp": str(datetime.now())
        })
        
        print("\n✅ Pre-debate preparation complete!")
    
    def decide_strategy(
        self,
        current_state: ParliamentState,
        opponent_move: Optional[str] = None
    ) -> Dict:
        """
        决定当前回合的策略
        
        Args:
            current_state: 当前辩论状态
            opponent_move: 对手最新动作（可选）
        
        Returns:
            策略决策字典
        """
        # 提取关键信息
        context = {
            "my_role": "PM",
            "opponent_strength": self._estimate_opponent_strength(current_state),
            "public_approval": self._estimate_public_approval(current_state),
            "debate_momentum": self._calculate_momentum(current_state),
            "current_turn": current_state["turn_count"]
        }
        
        print(f"\n{'='*60}")
        print(f"ROUND {current_state['turn_count']} - Strategic Decision")
        print('='*60)
        
        # Step 1: 使用 Q-Learning 选择基本战术
        ql_state = QLState(
            turn=context["current_turn"],
            my_speaker="PM",
            opponent_strength=context["opponent_strength"],
            public_approval=context["public_approval"],
            debate_momentum=context["debate_momentum"]
        )
        
        q_action = self.q_agent.get_action(ql_state)
        
        # Step 2: 使用启发式搜索进行实时调整
        if opponent_move and context["current_turn"] > 2:
            print("\n[HSEARCH] Real-time adjustment needed...")
            search_result = self.hsearch_engine.real_time_recommendation(
                opponent_move,
                context
            )
            
            # 融合两个系统的建议
            final_strategy = self._fuse_strategies(q_action.name, search_result["recommended_strategy"])
        else:
            final_strategy = q_action.name
        
        # Step 3: 更新 Q-Learning (在得到实际结果后)
        # 这里我们模拟奖励信号
        reward = self._simulate_reward(final_strategy, current_state)
        
        next_state = QLState(
            turn=context["current_turn"] + 1,
            my_speaker="PM",
            opponent_strength=random.uniform(0.3, 0.7),
            public_approval=min(100, max(0, context["public_approval"] + reward * 5)),
            debate_momentum=random.uniform(-0.5, 0.5)
        )
        
        self.q_agent.record_experience(
            ql_state,
            q_action,
            reward,
            next_state,
            done=(context["current_turn"] >= 10)
        )
        
        # 记录决策历史
        decision_record = {
            "turn": context["current_turn"],
            "ql_action": q_action.name,
            "hs_strategy": final_strategy,
            "context": {k: round(v, 2) if isinstance(v, float) else v 
                       for k, v in context.items()},
            "reward": reward
        }
        self.strategy_history.append(decision_record)
        
        result = {
            "action": q_action.name,
            "strategy": final_strategy,
            "confidence": self._calculate_confidence(context),
            "reasoning": self._generate_reasoning(decision_record)
        }
        
        print(f"\n💡 Decided strategy: {final_strategy}")
        print(f"   Confidence: {result['confidence']:.2f}")
        
        return result
    
    def generate_response(
        self,
        topic: str,
        current_state: ParliamentState,
        strategic_context: Dict
    ) -> str:
        """
        生成具体的发言稿
        
        Args:
            topic: 辩论议题
            current_state: 当前状态
            strategic_context: 策略上下文（包含 GA 和 HL 的建议）
        
        Returns:
            发言稿文本
        """
        # 获取策略元素
        action_type = strategic_context["action"]
        strategy_type = strategic_context["strategy"]
        
        # 根据策略类型选择不同的 prompt
        if action_type == "aggressive_attack":
            style = "confident_and_daring"
        elif action_type == "defensive_block":
            style = "cautious_and_factual"
        elif action_type == "seek_compromise":
            style = "moderate_and_balanced"
        else:
            style = "standard"
        
        # 填充模板
        response = self.pm_prompt.invoke({
            "topic": topic,
            "policy_economy": strategic_context.get("ga_policy", {}).get("经济自由化", 0.5),
            "policy_welfare": strategic_context.get("ga_policy", {}).get("社会福利投入", 0.5),
            "policy_environment": strategic_context.get("ga_policy", {}).get("环境保护力度", 0.5),
            "q_action": strategic_context["action"],
            "q_confidence": strategic_context.get("confidence", 0.5),
            "opponent_strength": strategic_context.get("context", {}).get("opponent_strength", 0.5),
            "public_approval": strategic_context.get("context", {}).get("public_approval", 50),
            "momentum": strategic_context.get("context", {}).get("debate_momentum", 0)
        })
        
        return response.content
    
    def _estimate_opponent_strength(self, state: ParliamentState) -> float:
        """估计对手的论点强度"""
        # 简化版本：基于对手的发言历史和长度
        records = state.get("debate_records", [])[-3:]
        
        if not records:
            return 0.5  # 默认中性
        
        # 计算平均发言质量（简化为字数和关键词密度）
        total_length = sum(len(r.content) for r in records)
        avg_length = total_length / len(records)
        
        # 长度作为强度的代理
        return min(1.0, max(0.0, avg_length / 200))
    
    def _estimate_public_approval(self, state: ParliamentState) -> float:
        """估计当前公众支持度"""
        # 简单版本：基于辩论进展和时间
        turn = state.get("turn_count", 0)
        base_approval = 50.0
        
        # 早期回合稍微有利
        early_bonus = max(0, 5 - turn) * 0.5
        
        return base_approval + early_bonus
    
    def _calculate_momentum(self, state: ParliamentState) -> float:
        """计算辩论势头"""
        records = state.get("debate_records", [])
        
        if len(records) < 2:
            return 0.0
        
        # 最近两轮的发言长度变化
        recent_lengths = [len(r.content) for r in records[-2:]]
        
        if len(recent_lengths) == 2:
            change = recent_lengths[1] - recent_lengths[0]
            return change / 100  # 归一化
        return 0.0
    
    def _fuse_strategies(self, ql_strategy: str, hs_strategy: str) -> str:
        """融合 Q-Learning 和启发式搜索的建议"""
        # 如果两者一致，直接使用
        if ql_strategy == hs_strategy:
            return ql_strategy
        
        # 如果不一致，优先使用启发式搜索结果（更贴近实时环境）
        return hs_strategy
    
    def _simulate_reward(self, action: str, state: ParliamentState) -> float:
        """模拟策略效果奖励"""
        # 简化版奖励函数
        base_reward = 0.0
        
        if action == "aggressive_attack":
            base_reward = random.uniform(0.5, 1.5) if random.random() < 0.4 else -0.5
        elif action == "defensive_block":
            base_reward = random.uniform(0.2, 0.8)
        elif action == "seek_compromise":
            base_reward = random.uniform(0.3, 0.6)
        else:
            base_reward = random.uniform(0.1, 0.5)
        
        return base_reward
    
    def _calculate_confidence(self, context: Dict) -> float:
        """计算策略置信度"""
        factors = [
            context.get("public_approval", 50) / 100,  # 支持度
            1 - abs(context.get("opponent_strength", 0.5) - 0.5),  # 对手强度适中时更高
            min(1, 10 / max(1, context.get("current_turn", 1)))  # 时间因素
        ]
        
        return sum(factors) / len(factors)
    
    def _generate_reasoning(self, decision: Dict) -> str:
        """生成策略选择的理由"""
        reasoning_parts = []
        
        action = decision.get("action", "")
        strategy = decision.get("strategy", "")
        
        if "attack" in action:
            reasoning_parts.append("Taking an offensive stance given opponent's weakness")
        if "defend" in action:
            reasoning_parts.append("Defensive positioning to protect current support levels")
        if "compromise" in action:
            reasoning_parts.append("Seeking middle ground to maintain broad appeal")
        
        if "HS" in strategy:
            reasoning_parts.append("Real-time analysis suggests tactical adjustment")
        
        return "; ".join(reasoning_parts) if reasoning_parts else "Following learned optimal strategy"
    
    def export_strategy_report(self) -> str:
        """导出策略分析报告"""
        lines = [
            "# Strategic PM Agent Strategy Report",
            "",
            f"## Evolution Summary",
            f"Generations run: {self.ga.episode_count if hasattr(self.ga, 'episode_count') else 'N/A'}",
            f"Policy iterations: {len(self.evolution_rounds)}",
            "",
            f"## Learning Summary",
            f"Q-Learning episodes: {self.q_agent.episode_count}",
            f"Average reward: {self.q_agent.total_reward / max(1, self.q_agent.episode_count):.3f}",
            "",
            f"## Strategy History",
            f"Total decisions: {len(self.strategy_history)}",
            "",
            "| Turn | Q-Action | HS-Strategy | Reward |",
            "|------|----------|-------------|--------|"
        ]
        
        for record in self.strategy_history[:10]:  # 只显示前 10 个
            lines.append(
                f"| {record['turn']} | {record['action']} | {record['strategy']} | {record['reward']:.2f} |"
            )
        
        return "\n".join(lines)


# ======================
# 使用示例
# ======================
if __name__ == "__main__":
    from datetime import datetime
    import random
    
    print("=" * 60)
    print("STRATEGIC PM AGENT TEST")
    print("=" * 60)
    
    # 创建战略首相
    pm = StrategicPrimeMinister()
    
    # 准备辩论
    mock_state = {
        "topic": "Should we increase NHS funding?",
        "turn_count": 0,
        "max_turns": 10,
        "debate_records": [],
        "mode": "debate"
    }
    
    pm.prepare_for_debate(mock_state["topic"], mock_state)
    
    # 模拟几个回合的决策
    for turn in range(1, 5):
        mock_state["turn_count"] = turn
        
        result = pm.decide_strategy(mock_state)
        
        print(f"\n--- Round {turn} Output ---")
        print(f"Action: {result['action']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
    
    # 导出报告
    print("\n" + "=" * 60)
    print(pm.export_strategy_report())
