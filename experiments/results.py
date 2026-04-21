"""
Experiment Results - 实验结果数据

定义实验结果的数据结构和导出方法
"""

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


@dataclass
class ExperimentResults:
    """
    实验结果集合
    
    Attributes:
        results: 所有运行结果列表
        experiment_id: 实验 ID
        topic: 议题
        strategies: 使用的策略列表
        num_runs: 运行次数
    """
    results: List[Dict] = field(default_factory=list)
    experiment_id: str = ""
    topic: str = ""
    strategies: List[str] = field(default_factory=list)
    num_runs: int = 0
    
    def __post_init__(self):
        if not self.experiment_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.experiment_id = f"exp_{timestamp}"
        
        if self.results:
            self.strategies = list(set(r["strategy"] for r in self.results))
            self.num_runs = len(set(r["run_number"] for r in self.results))
    
    def add_result(self, result: Dict):
        """添加单个结果"""
        self.results.append(result)
        self.strategies = sorted(set(r["strategy"] for r in self.results))
        self.num_runs = len(set(r["run_number"] for r in self.results))
    
    def to_csv(self, output_dir: str) -> Path:
        """
        导出结果到 CSV 文件
        
        Args:
            output_dir: 输出目录
        
        Returns:
            输出目录路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. results.csv - 主要结果
        results_file = output_path / "results.csv"
        with open(results_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "experiment_id",
                "strategy",
                "run_number",
                "topic",
                "opening_score",
                "closing_score",
                "overall_score",
                "win_result",
                "debate_file"
            ])
            
            for r in self.results:
                writer.writerow([
                    self.experiment_id,
                    r["strategy"],
                    r["run_number"],
                    r["topic"],
                    f"{r['opening_score']:.2f}",
                    f"{r['closing_score']:.2f}",
                    f"{r['overall_score']:.2f}",
                    r["win_result"],
                    r["debate_file"]
                ])
        
        # 2. detailed_scores.csv - 详细维度得分
        detailed_file = output_path / "detailed_scores.csv"
        with open(detailed_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "experiment_id",
                "strategy",
                "run_number",
                "speech_type",
                "logical_coherence",
                "evidence_quality",
                "persuasiveness",
                "rebuttal_strength",
                "language_tone",
                "overall_score",
                "comment"
            ])
            
            for r in self.results:
                detailed = r.get("detailed_scores", {})
                
                # 开场得分
                if detailed.get("opening"):
                    o = detailed["opening"]
                    writer.writerow([
                        self.experiment_id,
                        r["strategy"],
                        r["run_number"],
                        "opening",
                        f"{o.get('logical_coherence', 0):.1f}",
                        f"{o.get('evidence_quality', 0):.1f}",
                        f"{o.get('persuasiveness', 0):.1f}",
                        f"{o.get('rebuttal_strength', 0):.1f}",
                        f"{o.get('language_tone', 0):.1f}",
                        f"{o.get('overall_score', 0):.2f}",
                        o.get("overall_comment", "").replace(",", ";")
                    ])
                
                # 总结得分
                if detailed.get("closing"):
                    c = detailed["closing"]
                    writer.writerow([
                        self.experiment_id,
                        r["strategy"],
                        r["run_number"],
                        "closing",
                        f"{c.get('logical_coherence', 0):.1f}",
                        f"{c.get('evidence_quality', 0):.1f}",
                        f"{c.get('persuasiveness', 0):.1f}",
                        f"{c.get('rebuttal_strength', 0):.1f}",
                        f"{c.get('language_tone', 0):.1f}",
                        f"{c.get('overall_score', 0):.2f}",
                        c.get("overall_comment", "").replace(",", ";")
                    ])
        
        # 3. metadata.json - 元数据
        metadata_file = output_path / "metadata.json"
        metadata = {
            "experiment_id": self.experiment_id,
            "topic": self.topic,
            "strategies": self.strategies,
            "num_runs": self.num_runs,
            "created_at": datetime.now().isoformat(),
            "total_results": len(self.results)
        }
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def summary(self) -> str:
        """
        生成统计摘要
        
        Returns:
            格式化的统计摘要字符串
        """
        if not self.results:
            return "暂无数据"
        
        # 转换为 DataFrame
        df = pd.DataFrame(self.results)
        
        # 构建摘要
        lines = []
        lines.append("╔" + "═" * 70 + "╗")
        lines.append("║           算法对比实验报告" + " " * 44 + "║")
        lines.append("╠" + "═" * 70 + "╣")
        lines.append("║ 实验配置" + " " * 60 + "║")
        lines.append(f"║   议题：{self.topic:<58} ║")
        lines.append(f"║   运行次数：{self.num_runs:<53} ║")
        strategies_str = ", ".join(self.strategies)
        lines.append(f"║   策略：{strategies_str:<57} ║")
        lines.append("╠" + "═" * 70 + "╣")
        lines.append("║ 平均得分对比" + " " * 54 + "║")
        lines.append("║" + " " * 70 + "║")
        
        # 按策略分组统计
        grouped = df.groupby("strategy")
        for strategy in sorted(grouped.groups.keys()):
            strategy_df = grouped.get_group(strategy)
            avg_score = strategy_df["overall_score"].mean()
            lines.append(f"║   {strategy:<20}: {avg_score:.2f}{' ' * 42} ║")
        
        lines.append("║" + " " * 70 + "║")
        lines.append("╠" + "═" * 70 + "╣")
        lines.append("║ 胜率统计" + " " * 60 + "║")
        
        # 胜率统计
        for strategy in sorted(grouped.groups.keys()):
            strategy_df = grouped.get_group(strategy)
            wins = len(strategy_df[strategy_df["win_result"] == "WIN"])
            total = len(strategy_df)
            win_rate = (wins / total * 100) if total > 0 else 0
            lines.append(f"║   {strategy:<20}: {win_rate:.1f}% ({wins}/{total}){' ' * 35} ║")
        
        lines.append("╚" + "═" * 70 + "╝")
        
        return "\n".join(lines)
    
    def to_dataframe(self) -> pd.DataFrame:
        """转换为 pandas DataFrame"""
        return pd.DataFrame(self.results)
    
    def save_debate_record(
        self,
        debate_records: List,
        strategy: str,
        run_number: int,
        output_dir: str
    ) -> str:
        """
        保存辩论记录到 Markdown 文件
        
        Args:
            debate_records: 辩论记录列表
            strategy: 策略名称
            run_number: 运行编号
            output_dir: 输出目录
        
        Returns:
            文件名
        """
        output_path = Path(output_dir) / "debates"
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"debate_{strategy}_run{run_number}.md"
        filepath = output_path / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# 🏛️ UK Parliament Debate Record\n\n")
            f.write(f"**Experiment:** {self.experiment_id}\n\n")
            f.write(f"**Strategy:** {strategy}\n\n")
            f.write(f"**Run:** {run_number}\n\n")
            f.write(f"**Topic:** {self.topic}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Turns:** {len(debate_records)}\n\n")
            f.write("---\n\n")
            
            for i, record in enumerate(debate_records):
                speaker_name = self._get_speaker_name(record.speaker)
                f.write(f"## Turn {record.turn}: {speaker_name}\n\n")
                f.write(f"{record.content}\n\n")
                f.write("---\n\n")
        
        return filename
    
    def _get_speaker_name(self, speaker_id: str) -> str:
        """获取发言人显示名称"""
        mapping = {
            "speaker": "Mr Speaker",
            "pm": "Prime Minister",
            "lo": "Leader of the Opposition",
            "chancellor": "Chancellor of the Exchequer",
            "shadow_chancellor": "Shadow Chancellor",
            "backbencher_0": "Backbencher (Government)",
            "backbencher_1": "Backbencher (Opposition)",
        }
        return mapping.get(speaker_id, speaker_id)
