"""
Base Strategy - 策略抽象接口

定义所有辩论策略必须实现的抽象基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from state import ParliamentState


@dataclass
class StrategyArgument:
    """
    策略框架 - 用于指导 LLM 生成发言
    
    Attributes:
        strategy_type: 策略类型标识
        key_arguments: 核心论点列表
        tone: 语气风格 (aggressive, defensive, moderate, etc.)
        confidence: 置信度 (0~1)
        focus_areas: 重点强调领域
    """
    strategy_type: str
    key_arguments: List[str] = field(default_factory=list)
    tone: str = "neutral"
    confidence: float = 1.0
    focus_areas: List[str] = field(default_factory=list)


class DebateStrategy(ABC):
    """
    辩论策略抽象基类
    
    所有策略实现必须继承此类并实现抽象方法
    """
    
    @abstractmethod
    def generate_argument(
        self,
        role: str,
        topic: str,
        context: Dict
    ) -> StrategyArgument:
        """
        生成策略框架
        
        Args:
            role: 发言人角色 (PM, LO, Chancellor, etc.)
            topic: 辩论议题
            context: 辩论上下文信息
        
        Returns:
            StrategyArgument: 策略框架
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """
        策略名称
        
        Returns:
            策略的唯一标识名称
        """
        pass


def extract_debate_context(state: ParliamentState) -> Dict:
    """
    从议会状态中提取辩论上下文
    
    Args:
        state: 当前议会状态
    
    Returns:
        包含辩论上下文的字典
    """
    context = {
        "turn": state["turn_count"],
        "max_turns": state["max_turns"],
        "topic": state["topic"],
        "previous_speaker": None,
        "opponent_last_points": [],
        "debate_history_summary": "",
        "all_records": [],
    }
    
    if state["debate_records"]:
        # 获取上一个发言人
        last_record = state["debate_records"][-1]
        context["previous_speaker"] = last_record.speaker
        
        # 提取对方论点（简化版：取最近 3 条记录的要点）
        recent_records = state["debate_records"][-3:]
        context["all_records"] = [
            {"speaker": r.speaker, "content": r.content, "turn": r.turn}
            for r in recent_records
        ]
        
        # 生成历史摘要
        history_lines = []
        for r in recent_records:
            speaker_display = _get_speaker_display_name(r.speaker)
            summary = r.content[:150].replace("\n", " ")
            if len(r.content) > 150:
                summary += "..."
            history_lines.append(f"- {speaker_display}: {summary}")
        
        context["debate_history_summary"] = "\n".join(history_lines)
        
        # 提取对方论点关键词（简化版）
        opponent_speakers = ["lo", "shadow_chancellor", "backbencher"]
        for record in recent_records:
            if record.speaker in opponent_speakers:
                # 提取前 100 字符作为论点参考
                context["opponent_last_points"].append(
                    record.content[:100].replace("\n", " ")
                )
    
    return context


def _get_speaker_display_name(speaker_id: str) -> str:
    """将 speaker ID 转换为显示名称"""
    mapping = {
        "speaker": "Speaker",
        "pm": "Prime Minister",
        "lo": "Leader of the Opposition",
        "chancellor": "Chancellor of the Exchequer",
        "shadow_chancellor": "Shadow Chancellor",
        "backbencher_0": "Backbencher (Gov)",
        "backbencher_1": "Backbencher (Opp)",
    }
    return mapping.get(speaker_id, speaker_id)
