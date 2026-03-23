"""
Parliament State Definition
定义 LangGraph 的状态结构
"""

from typing import TypedDict, List, Annotated, Optional
from langgraph.graph.message import add_messages
from dataclasses import dataclass, field


def set_value(existing, new):
    """简单的值替换 reducer - 总是使用新值"""
    return new


@dataclass
class DebateRecord:
    """辩论记录"""
    speaker: str
    content: str
    turn: int


@dataclass
class VoteRecord:
    """投票记录"""
    topic: str
    ayes: int
    nos: int
    abstentions: int
    result: str


@dataclass
class PMQRecord:
    """首相问答记录"""
    turn: int
    questioner_party: str
    questioner_role: str
    question: str
    response: str


class ParliamentState(TypedDict):
    """
    议会辩论状态
    
    Attributes:
        messages: 所有消息历史（自动去重合并）
        current_speaker: 当前发言者（使用 set_value reducer 允许更新）
        topic: 当前辩论议题
        turn_count: 当前回合数
        max_turns: 最大回合数
        debate_records: 辩论记录列表
        votes: 投票结果
        pmq_records: PMQ 问答记录
        ended: 是否结束
        mode: 当前模式 ("debate", "pmqs", "vote")
    """
    messages: Annotated[List, add_messages]
    current_speaker: Annotated[str, set_value]
    topic: str
    turn_count: int
    max_turns: int
    debate_records: List[DebateRecord]
    votes: dict
    pmq_records: List[PMQRecord]
    ended: bool
    mode: str


def create_initial_state(
    topic: str,
    max_turns: int = 10,
    mode: str = "debate"
) -> ParliamentState:
    """
    创建初始状态
    
    Args:
        topic: 辩论议题
        max_turns: 最大回合数
        mode: 模式 ("debate", "pmqs", "vote")
    
    Returns:
        初始状态对象
    """
    return ParliamentState(
        messages=[],
        current_speaker="speaker",
        topic=topic,
        turn_count=0,
        max_turns=max_turns,
        debate_records=[],
        votes={},
        pmq_records=[],
        ended=False,
        mode=mode
    )
