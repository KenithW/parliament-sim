#!/usr/bin/env python3
"""
UK Parliament Algorithm Comparison Experiment
英国议会模拟算法对比实验

使用方法:
    python run_experiment.py --topic "是否应该增加 NHS 预算" --strategies all --runs 5
    python run_experiment.py --topic "经济政策" --strategies baseline --runs 3
"""

import argparse
from pathlib import Path
from datetime import datetime

from strategies import BaselineStrategy, HeuristicRuleStrategy
from experiments.runner import ExperimentRunner
from config import LLM_CONFIG


def create_llm():
    """创建 LLM 实例"""
    if LLM_CONFIG.get("provider") != "ollama":
        raise ValueError("当前实验只支持 Ollama，请将 config.py 中的 LLM_CONFIG['provider'] 设为 'ollama'")

    from langchain_ollama import ChatOllama
    return ChatOllama(
        base_url=LLM_CONFIG.get("base_url", "http://localhost:11434"),
        model=LLM_CONFIG.get("model", "qwen2.5:7b"),
        temperature=0.7,
    )


def get_strategies(strategy_arg: str):
    """
    获取策略列表
    
    Args:
        strategy_arg: 策略参数 (all 或单个策略名)
    
    Returns:
        策略列表
    """
    all_strategies = {
        "baseline": BaselineStrategy(),
        "heuristic_rule": HeuristicRuleStrategy(),
        # Phase 2 可以添加更多策略
        # "a_star": AStarStrategy(),
        # "genetic": GeneticStrategy(),
        # "heuristic_search": HeuristicSearchStrategy(),
    }
    
    if strategy_arg == "all":
        return list(all_strategies.values())
    elif strategy_arg in all_strategies:
        return [all_strategies[strategy_arg]]
    else:
        raise ValueError(f"未知策略：{strategy_arg}. 可用选项：{list(all_strategies.keys())}")


def main():
    parser = argparse.ArgumentParser(
        description="🧪 UK Parliament Algorithm Comparison Experiment"
    )
    parser.add_argument(
        "--topic", "-t",
        type=str,
        default="是否应该增加 NHS（国家医疗服务）的预算？",
        help="辩论议题"
    )
    parser.add_argument(
        "--strategies", "-s", "--strategy",
        type=str,
        default="all",
        help="策略列表：all 或单个策略名 (baseline, heuristic_rule)"
    )
    parser.add_argument(
        "--runs", "-n",
        type=int,
        default=5,
        help="每种策略运行次数 (默认：5)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出目录（默认自动生成）"
    )
    
    args = parser.parse_args()
    
    # 创建 LLM
    print("\n🔧 初始化 LLM...")
    llm = create_llm()
    print(f"   使用模型：{LLM_CONFIG.get('model', 'unknown')}")
    
    # 获取策略
    print("\n📋 加载策略...")
    strategies = get_strategies(args.strategies)
    print(f"   已加载 {len(strategies)} 种策略：{', '.join(s.name() for s in strategies)}")
    
    # 创建运行器
    runner = ExperimentRunner(strategies=strategies, llm=llm)
    
    # 运行实验
    results = runner.run_comparison(
        topic=args.topic,
        num_runs=args.runs,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
