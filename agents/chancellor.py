"""
Chancellor Agent - 财政大臣
负责经济政策、财政预算辩护
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

CHANCELLOR_PROMPT = """
你是英国财政大臣 (Chancellor of the Exchequer)，代表执政党。

## 你的职责
- 负责国家财政和经济政策
- 辩护政府预算和税收政策
- 回应经济相关的质疑
- 管理财政部事务

## 说话风格
- 专业、数据驱动、经济术语
- 称呼议长为 "Mr Speaker"
- 使用 "The Treasury believes...", "Our economic plan..."
- 强调经济增长、财政责任

## 你的政党信息
政党：{party_name}
政纲：{manifesto}

## 当前议题
{topic}

## 辩论历史
{debate_history}

请发表你的发言。
"""


def create_chancellor_agent(llm, party_name: str = "Conservative Party", manifesto: str = ""):
    """
    创建财政大臣 Agent
    
    Args:
        llm: LangChain LLM 对象
        party_name: 政党名称
        manifesto: 政纲
    
    Returns:
        财政大臣 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(CHANCELLOR_PROMPT)
    return prompt | llm | StrOutputParser()


def chancellor_node(state: dict, llm, party_config) -> dict:
    """
    财政大臣节点处理函数
    
    Args:
        state: 当前状态
        llm: LLM 对象
        party_config: 政党配置
    
    Returns:
        更新后的状态
    """
    from state import DebateRecord
    
    chancellor_agent = create_chancellor_agent(llm, party_config.name, party_config.manifesto)
    
    # 获取辩论历史
    debate_history = "\n".join([
        f"- {r.speaker}: {r.content[:100]}..."
        for r in state["debate_records"][-3:]
    ]) if state["debate_records"] else "暂无发言记录"
    
    # 生成财政大臣发言
    response = chancellor_agent.invoke({
        "party_name": party_config.name,
        "manifesto": party_config.manifesto,
        "topic": state["topic"],
        "debate_history": debate_history
    })
    
    # 记录发言
    record = DebateRecord(
        speaker="chancellor",
        content=response,
        turn=state["turn_count"]
    )
    state["debate_records"].append(record)
    state["messages"].append(("assistant", f"[Chancellor]: {response}"))
    
    # 下一个发言者由 workflow 决定
    state["current_speaker"] = "shadow_chancellor"
    
    return state
