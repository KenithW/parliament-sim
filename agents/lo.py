"""
Leader of the Opposition Agent - 反对党领袖
质疑政府，提出替代方案
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

LO_PROMPT = """
你是英国反对党领袖 (Leader of the Opposition)。

## 你的政党信息
政党：{party_name}
政纲：{manifesto}

## 你的职责
- 质疑和批评政府政策
- 提出替代方案
- 代表反对党发声
- 为下次大选做准备

## 说话风格
- 犀利、批判性、有攻击性但不失礼仪
- 称呼议长为 "Mr Speaker" 或 "Madam Speaker"
- 称呼首相为 "The Right Honourable Prime Minister"
- 使用 "The government has failed to..." 等批判表达
- 适时使用讽刺和反问

## 当前议题
{topic}

## 辩论历史
{debate_history}

请发表你的发言。
"""


def create_lo_agent(llm, party_name: str = "Labour Party", manifesto: str = ""):
    """
    创建反对党领袖 Agent
    
    Args:
        llm: LangChain LLM 对象
        party_name: 政党名称
        manifesto: 政纲
    
    Returns:
        反对党领袖 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(LO_PROMPT)
    return prompt | llm | StrOutputParser()


def lo_node(state: dict, llm, party_config) -> dict:
    """
    反对党领袖节点处理函数
    
    Args:
        state: 当前状态
        llm: LLM 对象
        party_config: 政党配置
    
    Returns:
        更新后的状态
    """
    from state import DebateRecord
    
    lo_agent = create_lo_agent(llm, party_config.name, party_config.manifesto)
    
    # 获取辩论历史
    debate_history = "\n".join([
        f"- {r.speaker}: {r.content[:100]}..."
        for r in state["debate_records"][-3:]
    ]) if state["debate_records"] else "暂无发言记录"
    
    # 生成反对党领袖发言
    response = lo_agent.invoke({
        "party_name": party_config.name,
        "manifesto": party_config.manifesto,
        "topic": state["topic"],
        "debate_history": debate_history
    })
    
    # 记录发言
    record = DebateRecord(
        speaker="lo",
        content=response,
        turn=state["turn_count"]
    )
    state["debate_records"].append(record)
    state["messages"].append(("assistant", f"[LO]: {response}"))
    
    state["current_speaker"] = "pm"
    
    return state
