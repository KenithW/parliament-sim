"""
Prime Minister Agent - 首相
代表执政党，提出政策并辩护
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

PM_PROMPT = """
你是英国首相 (Prime Minister)，代表执政党。

## 你的政党信息
政党：{party_name}
政纲：{manifesto}

## 你的职责
- 提出和辩护政府政策
- 回应反对党的质疑
- 展现领导力和说服力
- 为执政党的决策负责

## 说话风格
- 自信、坚定、有说服力
- 称呼议长为 "Mr Speaker" 或 "Madam Speaker"
- 称呼反对党为 "The Right Honourable Gentleman/Lady"
- 使用 "This government believes..." 等正式表达

## 当前议题
{topic}

## 辩论历史
{debate_history}

请发表你的发言。
"""


def create_pm_agent(llm, party_name: str = "Conservative Party", manifesto: str = ""):
    """
    创建首相 Agent
    
    Args:
        llm: LangChain LLM 对象
        party_name: 政党名称
        manifesto: 政纲
    
    Returns:
        首相 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(PM_PROMPT)
    return prompt | llm | StrOutputParser()


def pm_node(state: dict, llm, party_config) -> dict:
    """
    首相节点处理函数
    
    Args:
        state: 当前状态
        llm: LLM 对象
        party_config: 政党配置
    
    Returns:
        更新后的状态
    """
    from state import DebateRecord
    
    pm_agent = create_pm_agent(llm, party_config.name, party_config.manifesto)
    
    # 获取辩论历史
    debate_history = "\n".join([
        f"- {r.speaker}: {r.content[:100]}..."
        for r in state["debate_records"][-3:]
    ]) if state["debate_records"] else "暂无发言记录"
    
    # 生成首相发言
    response = pm_agent.invoke({
        "party_name": party_config.name,
        "manifesto": party_config.manifesto,
        "topic": state["topic"],
        "debate_history": debate_history
    })
    
    # 记录发言
    record = DebateRecord(
        speaker="pm",
        content=response,
        turn=state["turn_count"]
    )
    state["debate_records"].append(record)
    state["messages"].append(("assistant", f"[PM]: {response}"))
    
    state["current_speaker"] = "lo"
    
    return state
