"""
Quick Start Script - 算法集成快速测试
运行此脚本可以快速测试所有算法模块
"""

import sys
from datetime import datetime

def print_header(title):
    """打印标题分隔符"""
    print("\n" + "=" * 60)
    print(f"{title}")
    print("=" * 60)


def test_heuristic_rules():
    """测试硬编码启发式规则"""
    print_header("1. HEURISTIC RULES TEST")
    
    from algorithms.heuristic_rules import (
        create_heuristic_agent, 
        StrategyType,
        HeuristicConfig
    )
    
    # 创建首相的启发式代理
    pm = create_heuristic_agent(
        party_type="conservative",
        current_polls=42.0,
        topic_sensitivity="high",
        public_opinion_shift=-0.1
    )
    
    # 模拟几个回合
    opponents = [StrategyType.MODERATE, StrategyType.AGGRESSIVE, StrategyType.COMPROMISE]
    
    for i, opp_strategy in enumerate(opponents):
        print(f"\nRound {i+1} vs {opp_strategy.value}:")
        chosen = pm.decide_strategy(opp_strategy)
        print(f"  → Decision: {chosen.value}")
    
    print(f"\nStrategy Trend: {pm.get_strategy_trend()}")


def test_genetic_algorithm():
    """测试遗传算法"""
    print_header("2. GENETIC ALGORITHM TEST")
    
    from algorithms.genetic import GeneticAlgorithm
    
    ga = GeneticAlgorithm(
        population_size=30,
        mutation_rate=0.15,
        crossover_rate=0.8,
        generations=5
    )
    
    best_policy = ga.evolve()
    analysis = ga.get_policy_analysis()
    
    print("\nBest Policy Analysis:")
    for key, value in analysis.items():
        if isinstance(value, float) and key != "emotional_intensity":
            print(f"  • {key}: {value:.3f}")
        else:
            print(f"  • {key}: {value}")
    
    print("\n💡 Recommended policy direction:")
    policy_dict = ga.get_policy_analysis()
    for name, score in policy_dict.items():
        if isinstance(score, float) and name not in ["emotional_intensity", "rhetorical_style"]:
            direction = "INCREASE" if score > 0.6 else ("DECREASE" if score < 0.4 else "MAINTAIN")
            print(f"  → {direction} {name}")


def test_q_learning():
    """测试 Q-Learning 算法"""
    print_header("3. Q-LEARNING AGENT TEST")
    
    from algorithms.q_learning import (
        QLearningAgent, 
        State as QLState,
        ActionLibrary
    )
    
    agent = QLearningAgent(
        learning_rate=0.15,
        discount_factor=0.95,
        epsilon=0.3,
        epsilon_decay=0.995
    )
    
    # 训练一个 episode
    initial_state = QLState(
        turn=0,
        my_speaker="PM",
        opponent_strength=0.5,
        public_approval=50.0,
        debate_momentum=0.0
    )
    
    # 简单模拟学习过程
    state = initial_state
    total_reward = 0
    
    for step in range(5):
        action = agent.get_action(state)
        reward = abs(action.base_success_rate - random.uniform(0, 1))  # 随机奖励
        
        next_state = QLState(
            turn=state.turn + 1,
            my_speaker=state.my_speaker,
            opponent_strength=random.uniform(0.3, 0.7),
            public_approval=min(100, state.public_approval + reward * 3),
            debate_momentum=random.uniform(-0.5, 0.5)
        )
        
        agent.record_experience(state, action, reward, next_state, done=(step == 4))
        total_reward += reward
        
        print(f"Step {step}: {action.name} → Reward: {reward:.2f}")
        state = next_state
    
    print(f"\nTotal Episode Reward: {total_reward:.2f}")
    print(f"Training Episodes: {agent.episode_count}")


def test_heuristic_search():
    """测试启发式搜索"""
    print_header("4. HEURISTIC SEARCH TEST")
    
    from algorithms.heuristic_search import HeuristicSearchEngine
    
    engine = HeuristicSearchEngine()
    
    context = {
        "my_role": "PM",
        "opponent_strength": 0.6,
        "public_approval": 48,
        "debate_momentum": 0.1
    }
    
    # 构建决策树
    root = engine.build_decision_tree(context, max_depth=3)
    
    # 寻找最佳策略
    best_strategy, score = engine.find_best_strategy(root, method="beam_search")
    
    print(f"\nBest Strategy: {best_strategy}")
    print(f"Score: {score:.2f}")
    print(f"\nRecommendation:")
    rec = engine.real_time_recommendation("aggressive_attack", context)
    print(f"  → {rec['recommended_strategy']}")


def run_integration_demo():
    """运行完整集成演示"""
    print_header("5. INTEGRATION DEMO - Strategic PM")
    
    try:
        from hybrid_agents.strategic_pm import StrategicPrimeMinister
        
        pm = StrategicPrimeMinister()
        
        # 准备阶段
        mock_context = {
            "topic": "NHS Funding Increase?",
            "turn_count": 0,
            "max_turns": 10,
            "debate_records": [],
            "mode": "debate"
        }
        
        print("\nInitializing Strategic Prime Minister...")
        pm.prepare_for_debate(mock_context["topic"], mock_context)
        
        # 模拟几个回合
        for round_num in range(1, 4):
            mock_context["turn_count"] = round_num
            
            result = pm.decide_strategy(mock_context)
            
            print(f"\n--- Round {round_num} ---")
            print(f"Selected Action: {result['action']}")
            print(f"Confidence: {result['confidence']:.2f}")
        
        print("\n✅ Integration demo completed successfully!")
        
    except ImportError as e:
        print(f"\n⚠️  Cannot load hybrid agent: {e}")
        print("This is expected if the module hasn't been created yet.")


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 UK Parliament Simulation - AI Algorithms Test Suite")
    print("   英国议会模拟 - AI 算法测试套件")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    import random
    
    # 逐个测试
    test_heuristic_rules()
    test_genetic_algorithm()
    test_q_learning()
    test_heuristic_search()
    
    # 尝试集成演示
    run_integration_demo()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)
    print("\n📚 For detailed tutorials, see:")
    print("   C:\\Users\\93508\\.openclaw\\workspace\\tutorials\\")
    print("\n🎯 Next steps:")
    print("   1. Study each algorithm independently")
    print("   2. Try modifying parameters and observe effects")
    print("   3. Integrate into your parliament simulation project")
    print("   4. Experiment with hybrid approaches\n")


if __name__ == "__main__":
    main()
