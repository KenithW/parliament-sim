"""
Q-Learning Algorithm - Q 学习算法
用于 Agent 从历史辩论中学习最优策略
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import random


@dataclass
class State:
    """环境状态"""
    turn: int                              # 当前回合
    my_speaker: str                        # 我是谁
    opponent_strength: float               # 对手强度 (0~1)
    public_approval: float                 # 公众支持度 (%)
    debate_momentum: float                 # 辩论势头 (-1~1)
    
    def to_tuple(self) -> tuple:
        """离散化状态为元组（用于 Q-table 索引）"""
        # 离散化
        speaker_idx = ["PM", "LO", "Chancellor"].index(self.my_speaker) if self.my_speaker in ["PM", "LO", "Chancellor"] else 2
        
        opp_strong = 0 if self.opponent_strength < 0.3 else (1 if self.opponent_strength < 0.7 else 2)
        approval = 0 if self.public_approval < 40 else (1 if self.public_approval < 60 else 2)
        momentum = 0 if self.debate_momentum < -0.3 else (1 if self.debate_momentum < 0.3 else 2)
        
        return (speaker_idx, opp_strong, approval, momentum)
    
    def __hash__(self):
        return hash(self.to_tuple())


@dataclass
class Action:
    """行动类型"""
    name: str
    base_success_rate: float      # 基础成功率
    risk_level: int               # 风险等级 (1~3)


class ActionLibrary:
    """行动库"""
    
    AGGRESSIVE = Action("aggressive_attack", base_success_rate=0.4, risk_level=3)
    DEFENSIVE = Action("defensive_block", base_success_rate=0.7, risk_level=1)
    COMPROMISE = Action("seek_compromise", base_success_rate=0.5, risk_level=2)
    FACILITATE = Action("facilitate_debate", base_success_rate=0.6, risk_level=1)
    CHALLENGE = Action("challenge_opponent", base_success_rate=0.45, risk_level=2)
    
    ALL_ACTIONS = [AGGRESSIVE, DEFENSIVE, COMPROMISE, FACILITATE, CHALLENGE]


class QLearningAgent:
    """
    Q-Learning Agent - 通过试错学习
    
    应用场景：
    - 学习何时进攻、何时防御
    - 根据对手风格调整策略
    - 积累最佳实践
    
    Q-learning 核心公式：
    Q(s,a) ← Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
    """
    
    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.3,           # 探索率
        epsilon_decay: float = 0.99,
        min_epsilon: float = 0.05
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        
        # Q-table: state -> action -> value
        self.q_table: Dict[tuple, Dict[str, float]] = defaultdict(
            lambda: {a.name: 0.0 for a in ActionLibrary.ALL_ACTIONS}
        )
        
        self.episode_count = 0
        self.total_reward = 0
        
    def get_action(self, state: State) -> Action:
        """
        选择动作（ε-greedy 策略）
        
        Args:
            state: 当前状态
        
        Returns:
            选择的行动
        """
        state_key = state.to_tuple()
        
        # ε-greedy: 以 ε 概率随机探索，否则贪婪选择
        if random.random() < self.epsilon:
            action = random.choice(ActionLibrary.ALL_ACTIONS)
            print(f"[QL] Exploring with action: {action.name}")
        else:
            q_values = self.q_table[state_key]
            best_action_name = max(q_values, key=q_values.get)
            action = next(a for a in ActionLibrary.ALL_ACTIONS if a.name == best_action_name)
            print(f"[QL] Exploiting best action: {best_action_name} (Q={q_values[best_action_name]:.3f})")
        
        return action
    
    def update_q_value(
        self,
        state: State,
        action: Action,
        reward: float,
        next_state: State,
        done: bool = False
    ):
        """
        更新 Q 值
        
        Q-learning 更新规则:
        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        
        Args:
            state: 当前状态
            action: 执行的动作
            reward: 奖励信号
            next_state: 下一个状态
            done: 是否 episode 结束
        """
        current_state_key = state.to_tuple()
        next_state_key = next_state.to_tuple()
        
        # 获取当前 Q 值
        current_q = self.q_table[current_state_key][action.name]
        
        # 计算目标 Q 值
        if done:
            target_q = reward
        else:
            max_next_q = max(self.q_table[next_state_key].values())
            target_q = reward + self.discount_factor * max_next_q
        
        # 更新 Q 值
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self.q_table[current_state_key][action.name] = new_q
        
        print(f"[QL] Updated Q[{current_state_key}]['{action.name}'] from {current_q:.3f} to {new_q:.3f}")
    
    def decay_epsilon(self):
        """衰减探索率"""
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
    
    def record_experience(
        self,
        state: State,
        action: Action,
        reward: float,
        next_state: State,
        done: bool
    ):
        """记录一次经验并进行学习"""
        self.update_q_value(state, action, reward, next_state, done)
        
        if done:
            self.episode_count += 1
            self.total_reward += reward
            self.decay_epsilon()
            
            print(f"\n[QL] Episode {self.episode_count}: "
                  f"Total Reward = {self.total_reward:.2f}, "
                  f"Epsilon = {self.epsilon:.3f}\n")
    
    def train_episode(
        self,
        initial_state: State,
        max_steps: int = 10
    ) -> List[Tuple[State, Action, float]]:
        """
        训练一个完整的 episode
        
        Args:
            initial_state: 初始状态
            max_steps: 最大步数
        
        Returns:
            经验列表 [(state, action, reward), ...]
        """
        experience = []
        current_state = initial_state
        total_reward = 0
        
        print(f"\n{'='*60}")
        print(f"EPISODE TRAINING START")
        print(f"Initial State: speaker={current_state.my_speaker}, "
              f"approval={current_state.public_approval:.1f}%")
        print(f"{'='*60}")
        
        for step in range(max_steps):
            # 选择动作
            action = self.get_action(current_state)
            
            # 模拟环境（这里简化为随机奖励）
            # 实际应该调用辩论引擎获取真实结果
            reward = self._simulate_step(current_state, action)
            done = False
            
            # 生成下一个状态
            next_state = State(
                turn=current_state.turn + 1,
                my_speaker=current_state.my_speaker,
                opponent_strength=random.uniform(0.2, 0.8),
                public_approval=current_state.public_approval + reward * 5,
                debate_momentum=random.uniform(-0.5, 0.5)
            )
            done = (step >= max_steps - 1 or 
                   abs(current_state.public_approval - next_state.public_approval) > 10)
            
            # 记录并学习
            self.record_experience(current_state, action, reward, next_state, done)
            experience.append((current_state, action, reward))
            
            total_reward += reward
            current_state = next_state
            
            if done:
                break
        
        print(f"\n✅ EPISODE COMPLETE | Total Reward: {total_reward:.2f}")
        
        return experience
    
    def _simulate_step(self, state: State, action: Action) -> float:
        """
        模拟一步的奖励
        
        实际应用中应该基于真实的辩论结果
        这里我们用简化的模型模拟
        """
        # 基础奖励
        success_probability = action.base_success_rate
        
        # 根据状态调整
        bonus = 0
        
        # 如果对方很强，攻击可能更有效（出其不意）
        if action.name == "aggressive_attack" and state.opponent_strength > 0.6:
            bonus += 0.2
        
        # 如果自己支持度高，防御更稳健
        if action.name == "defensive_block" and state.public_approval > 50:
            bonus += 0.1
        
        # 加入噪声
        success = random.random() < (success_probability + bonus)
        
        if success:
            reward = 1.0 + (state.public_approval / 100) * 0.5
        else:
            reward = -0.5
        
        return reward
    
    def get_best_policy(self, state: State) -> str:
        """获取给定状态下的最佳策略"""
        state_key = state.to_tuple()
        q_values = self.q_table[state_key]
        best_action = max(q_values, key=q_values.get)
        return best_action
    
    def export_q_table(self) -> str:
        """导出 Q-table 到字符串（可用于保存或分析）"""
        lines = ["# Q-Table Summary"]
        lines.append(f"# Episodes trained: {self.episode_count}")
        lines.append(f"# Epsilon (exploration rate): {self.epsilon:.3f}")
        lines.append("")
        
        # 统计每个状态的最优动作
        lines.append("# Optimal Actions by State:")
        lines.append("-" * 60)
        
        for state_key, q_values in list(self.q_table.items())[:10]:  # 只输出前 10 个
            best_action = max(q_values, key=q_values.get)
            best_value = q_values[best_action]
            
            speaker_names = ["PM", "LO", "Other"]
            speaker = speaker_names[state_key[0]] if state_key[0] < 3 else "Other"
            opp_strength = {0: "weak", 1: "medium", 2: "strong"}[state_key[1]]
            approval = {0: "low", 1: "medium", 2: "high"}[state_key[2]]
            
            lines.append(f"{speaker}/{opp_strength}/approval{approval}: "
                        f"{best_action} (Q={best_value:.2f})")
        
        return "\n".join(lines)


# ======================
# 使用示例和测试
# ======================
if __name__ == "__main__":
    print("=" * 60)
    print("Q-LEARNING TEST - Strategic Debate Learning")
    print("=" * 60)
    
    # 创建 Agent
    agent = QLearningAgent(
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=0.3,
        epsilon_decay=0.995
    )
    
    # 训练多个 episode
    num_episodes = 20
    
    for episode in range(num_episodes):
        # 创建初始状态
        initial_state = State(
            turn=episode,
            my_speaker="PM",
            opponent_strength=random.uniform(0.3, 0.7),
            public_approval=45.0 + random.uniform(-10, 10),
            debate_momentum=random.uniform(-0.5, 0.5)
        )
        
        # 训练
        agent.train_episode(initial_state, max_steps=5)
    
    # 总结学习成果
    print("\n" + "=" * 60)
    print("🎓 LEARNING SUMMARY")
    print("=" * 60)
    print(agent.export_q_table())
    
    print("\n💡 How to use trained policy:")
    test_state = State(
        turn=0,
        my_speaker="PM",
        opponent_strength=0.6,
        public_approval=50.0,
        debate_momentum=0.2
    )
    
    best_policy = agent.get_best_policy(test_state)
    print(f"For state {test_state.to_tuple()}, "
          f"use action: '{best_policy}'")
