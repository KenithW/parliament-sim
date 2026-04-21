"""
Experiment Runner - 实验运行器

负责运行策略对比实验
"""

from typing import List, Dict
from pathlib import Path
from datetime import datetime

from strategies.base_strategy import DebateStrategy
from evaluation.evaluator import DebateEvaluator
from experiments.results import ExperimentResults
from state import create_initial_state, DebateRecord
from config import LLM_CONFIG


class ExperimentRunner:
    """
    实验运行器
    
    运行多种策略的对比实验，收集评估数据
    """
    
    def __init__(self, strategies: List[DebateStrategy], llm):
        """
        初始化运行器
        
        Args:
            strategies: 策略列表
            llm: LangChain LLM 对象
        """
        self.strategies = strategies
        self.llm = llm
        self.evaluator = DebateEvaluator(llm)
    
    def run_comparison(
        self,
        topic: str,
        num_runs: int = 5,
        output_dir: str = None
    ) -> ExperimentResults:
        """
        运行对比实验
        
        Args:
            topic: 辩论议题
            num_runs: 每种策略运行次数
            output_dir: 输出目录
        
        Returns:
            ExperimentResults: 实验结果
        """
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"results/experiment_{timestamp}"
        
        results = ExperimentResults(topic=topic)
        
        print("\n" + "=" * 70)
        print("🧪 UK Parliament Algorithm Comparison Experiment")
        print("    英国议会模拟算法对比实验")
        print("=" * 70)
        print(f"\n📌 议题：{topic}")
        print(f"📌 策略数量：{len(self.strategies)}")
        print(f"📌 每种运行次数：{num_runs}")
        print(f"📌 输出目录：{output_dir}")
        print("\n开始实验...\n")
        
        for strategy in self.strategies:
            print(f"\n{'=' * 70}")
            print(f"运行策略：{strategy.name()}")
            print(f"{'=' * 70}")
            
            strategy_results = []
            
            for run in range(num_runs):
                print(f"\n  ▶ 第 {run + 1}/{num_runs} 次运行...")
                
                try:
                    # 运行辩论
                    debate_state = self.run_single_debate(
                        topic=topic,
                        strategy=strategy,
                        run_number=run + 1
                    )
                    
                    # 评估辩论
                    evaluation = self.evaluator.evaluate_debate(
                        debate_records=debate_state["debate_records"],
                        topic=topic
                    )
                    
                    # 判定胜负
                    vote_result = debate_state.get("votes", {})
                    win_result = self._determine_winner(
                        evaluation=evaluation,
                        vote_result=vote_result
                    )
                    
                    # 保存辩论记录
                    debate_file = results.save_debate_record(
                        debate_records=debate_state["debate_records"],
                        strategy=strategy.name(),
                        run_number=run + 1,
                        output_dir=output_dir
                    )
                    
                    # 收集结果
                    run_result = {
                        "strategy": strategy.name(),
                        "run_number": run + 1,
                        "topic": topic,
                        "opening_score": evaluation["opening"]["overall_score"],
                        "closing_score": evaluation["closing"]["overall_score"],
                        "overall_score": evaluation["overall"]["overall_score"],
                        "win_result": win_result,
                        "debate_file": debate_file,
                        "detailed_scores": evaluation
                    }
                    
                    strategy_results.append(run_result)
                    results.add_result(run_result)
                    
                    print(f"  ✓ 完成 - 得分：{run_result['overall_score']:.2f}, 结果：{win_result}")
                    
                except Exception as e:
                    print(f"  ✗ 失败：{e}")
                    import traceback
                    traceback.print_exc()
            
            # 打印策略平均分
            if strategy_results:
                avg_score = sum(r["overall_score"] for r in strategy_results) / len(strategy_results)
                wins = sum(1 for r in strategy_results if r["win_result"] == "WIN")
                print(f"\n  📊 {strategy.name()} 平均得分：{avg_score:.2f}, 胜率：{wins}/{num_runs}")
        
        # 保存结果
        results.to_csv(output_dir)
        
        # 打印摘要
        print("\n" + results.summary())
        
        print(f"\n✅ 实验完成！结果已保存至：{output_dir}")
        print(f"   - results.csv: 主要统计数据")
        print(f"   - detailed_scores.csv: 详细维度得分")
        print(f"   - metadata.json: 实验元数据")
        print(f"   - debates/: 辩论记录\n")
        
        return results
    
    def run_single_debate(
        self,
        topic: str,
        strategy: DebateStrategy,
        run_number: int
    ) -> Dict:
        """
        运行单场辩论
        
        Args:
            topic: 议题
            strategy: 策略
            run_number: 运行编号
        
        Returns:
            最终状态字典
        """
        # 导入 workflow
        from workflow import run_experiment_debate
        
        # 运行辩论
        final_state = run_experiment_debate(
            topic=topic,
            strategy=strategy,
            max_turns=6
        )
        
        return final_state
    
    def _determine_winner(self, evaluation: Dict, vote_result: Dict) -> str:
        """
        判定胜负
        
        规则：
        - 有投票结果时，以投票为准
        - 无投票时，以评分为准（>=7.0 为 WIN）
        
        Args:
            evaluation: 评估结果
            vote_result: 投票结果
        
        Returns:
            "WIN" 或 "LOSS"
        """
        if vote_result and "ayes" in vote_result:
            # 有投票结果，以投票为准
            ayes = vote_result.get("ayes", 0)
            nos = vote_result.get("nos", 0)
            return "WIN" if ayes > nos else "LOSS"
        else:
            # 无投票，以评分为准
            score = evaluation["overall"]["overall_score"]
            return "WIN" if score >= 7.0 else "LOSS"
