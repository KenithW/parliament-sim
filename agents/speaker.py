"""
Speaker Agent - 议长
负责主持辩论、维持秩序、保持中立
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

SPEAKER_PROMPT = """
你是英国下议院议长 (Speaker of the House of Commons)。

## 你的职责
- 主持辩论，保持中立公正
- 维持议会秩序和礼仪
- 邀请议员发言
- 确保辩论围绕议题进行
- 在适当时候总结并主持投票

## 说话风格
- 正式、庄重、权威
- 使用 "Order! Order!" 维持秩序
- 称呼议员为 "Right Honourable Member"
- 保持中立，不表达个人观点

## 当前议题
{topic}

## 当前状态
回合：{turn_count}/{max_turns}
上一位发言者：{last_speaker}

请开始主持辩论。
"""


def create_speaker_agent(llm):
    """
    创建议长 Agent
    
    Args:
        llm: LangChain LLM 对象
    
    Returns:
        议长 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(SPEAKER_PROMPT)
    return prompt | llm | StrOutputParser()


def speaker_node(state: dict, llm) -> dict:
    """
    议长节点处理函数
    
    Args:
        state: 当前状态
        llm: LLM 对象
    
    Returns:
        更新后的状态
    """
    from state import DebateRecord
    
    speaker_agent = create_speaker_agent(llm)
    
    # 获取上一位发言者
    last_speaker = "none"
    if state["debate_records"]:
        last_speaker = state["debate_records"][-1].speaker
    
    # 生成议长发言
    response = speaker_agent.invoke({
        "topic": state["topic"],
        "turn_count": state["turn_count"],
        "max_turns": state["max_turns"],
        "last_speaker": last_speaker
    })
    
    # 记录发言
    record = DebateRecord(
        speaker="speaker",
        content=response,
        turn=state["turn_count"]
    )
    state["debate_records"].append(record)
    state["messages"].append(("assistant", f"[Speaker]: {response}"))
    
    # 决定下一位发言者
    if state["turn_count"] == 0:
        state["current_speaker"] = "pm"
    elif state["turn_count"] >= state["max_turns"]:
        state["current_speaker"] = "speaker"
        state["ended"] = True
    else:
        # 交替发言
        state["current_speaker"] = "lo" if last_speaker == "pm" else "pm"
    
    state["turn_count"] += 1
    
    return state
