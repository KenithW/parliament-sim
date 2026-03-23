"""
Voting System Tool - 投票系统
处理议会投票、计票、结果记录
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import random


class VoteOption(Enum):
    AYE = "aye"       # 赞成
    NO = "no"         # 反对
    ABSTAIN = "abstain"  # 弃权


@dataclass
class VoteRecord:
    """投票记录"""
    topic: str
    ayes: int
    nos: int
    abstentions: int
    result: str  # "passed" or "rejected"
    voters: Dict[str, VoteOption]


def calculate_result(ayes: int, nos: int, abstentions: int = 0) -> str:
    """
    计算投票结果
    
    Args:
        ayes: 赞成票数
        nos: 反对票数
        abstentions: 弃权票数
    
    Returns:
        "passed" 或 "rejected"
    """
    if ayes > nos:
        return "passed"
    elif nos > ayes:
        return "rejected"
    else:
        return "tie"  # 平局，议长可能投决定性票


def simulate_vote(
    topic: str,
    government_size: int = 350,
    opposition_size: int = 250,
    government_rebels: int = 0,
    opposition_rebels: int = 0,
    abstentions: int = 20
) -> VoteRecord:
    """
    模拟议会投票
    
    Args:
        topic: 投票议题
        government_size: 执政党议员数
        opposition_size: 反对党议员数
        government_rebels: 执政党反叛议员数
        opposition_rebels: 反对党反叛议员数
        abstentions: 弃权数
    
    Returns:
        VoteRecord 对象
    """
    # 计算票数
    # 执政党：大部分投赞成，反叛者投反对
    gov_ayes = government_size - government_rebels
    gov_nos = government_rebels
    
    # 反对党：大部分投反对，反叛者投赞成
    opp_nos = opposition_size - opposition_rebels
    opp_ayes = opposition_rebels
    
    # 总票数
    ayes = gov_ayes + opp_ayes
    nos = gov_nos + opp_nos
    
    result = calculate_result(ayes, nos, abstentions)
    
    # 生成投票者详情
    voters = {}
    voters["government_loyal"] = VoteOption.AYE
    voters["government_rebels"] = VoteOption.NO
    voters["opposition_loyal"] = VoteOption.NO
    voters["opposition_rebels"] = VoteOption.AYE
    voters["abstainers"] = VoteOption.ABSTAIN
    
    return VoteRecord(
        topic=topic,
        ayes=ayes,
        nos=nos,
        abstentions=abstentions,
        result=result,
        voters=voters
    )


def format_vote_result(record: VoteRecord) -> str:
    """
    格式化投票结果输出
    
    Args:
        record: 投票记录
    
    Returns:
        格式化字符串
    """
    result_emoji = "✅" if record.result == "passed" else "❌" if record.result == "rejected" else "⚖️"
    
    output = f"""
{result_emoji} **投票结果**

**议题**: {record.topic}

| 选项 | 票数 |
|------|------|
| 赞成 (Aye) | {record.ayes} |
| 反对 (No) | {record.nos} |
| 弃权 (Abstain) | {record.abstentions} |

**结果**: {record.result.upper()}

---
"""
    return output


def create_voting_tool():
    """
    创建投票工具
    
    Returns:
        投票工具函数
    """
    return simulate_vote


def vote_node(state: dict, vote_config: dict = None) -> dict:
    """
    投票节点处理函数
    
    Args:
        state: 当前状态
        vote_config: 投票配置
    
    Returns:
        更新后的状态
    """
    if vote_config is None:
        vote_config = {
            "government_size": 350,
            "opposition_size": 250,
            "government_rebels": random.randint(5, 30),
            "opposition_rebels": random.randint(2, 15),
            "abstentions": 20
        }
    
    # 执行投票
    vote_result = simulate_vote(
        topic=state["topic"],
        **vote_config
    )
    
    # 存储投票结果
    state["votes"] = {
        "ayes": vote_result.ayes,
        "nos": vote_result.nos,
        "abstentions": vote_result.abstentions,
        "result": vote_result.result
    }
    
    # 打印结果
    print(format_vote_result(vote_result))
    
    # 标记辩论结束
    state["ended"] = True
    
    return state
