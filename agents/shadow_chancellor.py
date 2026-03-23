"""
Shadow Chancellor Agent - 影子财政大臣
反对党的经济发言人，质疑政府财政政策
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

SHADOW_CHANCELLOR_PROMPT = """
你是影子财政大臣 (Shadow Chancellor)，代表反对党。

## 你的职责
- 质疑和批评政府财政政策
- 提出反对党的经济替代方案
- 监督财政部和预算
- 为下次大选的经济政策做准备

## 说话风格
- 犀利、批判性、经济数据驱动
- 称呼议长为 "Mr Speaker"
- 称呼财政大臣为 "The Right Honourable Chancellor"
- 使用 "The government's economic record shows...", "Working families cannot afford..."
- 适时使用讽刺和反问

## 你的政党信息
政党：{party_name}
政纲：{manifesto}

## 当前议题
{topic}

## 辩论历史
{debate_history}

请发表你的发言。
"""


def create_shadow_chancellor_agent(llm, party_name: str = "Labour Party", manifesto: str = ""):
    """
    创建影子财政大臣 Agent
    
    Args:
        llm: LangChain LLM 对象
        party_name: 政党名称
        manifesto: 政纲
    
    Returns:
        影子财政大臣 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(SHADOW_CHANCELLOR_PROMPT)
    return prompt | llm | StrOutputParser()


def shadow_chancellor_node(state: dict, llm, party_config) -> dict:
    """
    影子财政大臣节点处理函数
    
    Args:
        state: 当前状态
        llm: LLM 对象
        party_config: 政党配置
    
    Returns:
        更新后的状态
    """
    from state import DebateRecord
    
    shadow_agent = create_shadow_chancellor_agent(llm, party_config.name, party_config.manifesto)
    
    # 获取辩论历史
    debate_history = "\n".join([
        f"- {r.speaker}: {r.content[:100]}..."
        for r in state["debate_records"][-3:]
    ]) if state["debate_records"] else "暂无发言记录"
    
    # 生成影子财政大臣发言
    response = shadow_agent.invoke({
        "party_name": party_config.name,
        "manifesto": party_config.manifesto,
        "topic": state["topic"],
        "debate_history": debate_history
    })
    
    # 记录发言
    record = DebateRecord(
        speaker="shadow_chancellor",
        content=response,
        turn=state["turn_count"]
    )
    state["debate_records"].append(record)
    state["messages"].append(("assistant", f"[Shadow Chancellor]: {response}"))
    
    # 下一个发言者由 workflow 决定
    state["current_speaker"] = "chancellor"
    
    return state
