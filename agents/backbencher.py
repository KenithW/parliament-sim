"""
Backbencher Agent - 后座议员
普通议员，代表选区利益，提问质询
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import random

BACKBENCHER_PROMPT = """
你是英国后座议员 (Backbencher)，代表执政党或反对党的普通议员。

## 你的信息
政党：{party_name}
派系：{faction}  (党内：{faction_type})
选区：{constituency}

## 你的职责
- 代表选区利益发声
- 提问质询政府政策
- 在党内表达后座议员观点
- 可能支持或反叛党内立场

## 说话风格
- 接地气、关注具体议题
- 称呼议长为 "Mr Speaker"
- 使用 "My constituents are concerned...", "In my constituency..."
- 后座议员可能更直接、更少外交辞令

## 当前议题
{topic}

## 辩论历史
{debate_history}

请发表你的发言。
"""


def create_backbencher_agent(llm, party_name: str, faction: str, constituency: str):
    """
    创建后座议员 Agent
    
    Args:
        llm: LangChain LLM 对象
        party_name: 政党名称
        faction: 派系 (如 "moderate", "hardline", "rebel")
        constituency: 选区
    
    Returns:
        后座议员 Agent 链
    """
    # 确定派系类型
    faction_type = "忠诚支持" if faction == "loyal" else "批判质疑" if faction == "critical" else "独立摇摆"
    
    prompt = ChatPromptTemplate.from_template(BACKBENCHER_PROMPT)
    return prompt | llm | StrOutputParser()


def backbencher_node(state: dict, llm, backbencher_config) -> dict:
    """
    后座议员节点处理函数
    
    Args:
        state: 当前状态
        llm: LLM 对象
        backbencher_config: 后座议员配置 {party, faction, constituency}
    
    Returns:
        更新后的状态
    """
    from state import DebateRecord
    
    backbencher_agent = create_backbencher_agent(
        llm,
        backbencher_config["party_name"],
        backbencher_config["faction"],
        backbencher_config["constituency"]
    )
    
    # 获取辩论历史
    debate_history = "\n".join([
        f"- {r.speaker}: {r.content[:100]}..."
        for r in state["debate_records"][-3:]
    ]) if state["debate_records"] else "暂无发言记录"
    
    # 生成后座议员发言
    response = backbencher_agent.invoke({
        "party_name": backbencher_config["party_name"],
        "faction": backbencher_config["faction"],
        "faction_type": backbencher_config.get("faction_type", "普通"),
        "constituency": backbencher_config["constituency"],
        "topic": state["topic"],
        "debate_history": debate_history
    })
    
    # 记录发言
    record = DebateRecord(
        speaker=f"backbencher_{backbencher_config['party_name']}",
        content=response,
        turn=state["turn_count"]
    )
    state["debate_records"].append(record)
    state["messages"].append(("assistant", f"[Backbencher ({backbencher_config['party_name']})]: {response}"))
    
    return state


# 预设的后座议员配置
BACKBENCHER_PRESETS = [
    {
        "party_name": "Conservative Party",
        "faction": "loyal",
        "constituency": "Surrey Heath",
        "focus": "商业、减税"
    },
    {
        "party_name": "Conservative Party",
        "faction": "critical",
        "constituency": "Devon North",
        "focus": "农村、农业"
    },
    {
        "party_name": "Labour Party",
        "faction": "loyal",
        "constituency": "Manchester Central",
        "focus": "工人权益、公共服务"
    },
    {
        "party_name": "Labour Party",
        "faction": "critical",
        "constituency": "Glasgow East",
        "focus": "社会公平、住房"
    },
]
