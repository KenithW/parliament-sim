"""
Leader of the Opposition Agent - 反对党领袖
质疑政府，提出替代方案
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from strategies.base_strategy import StrategyArgument, extract_debate_context

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

STRATEGY_LO_PROMPT = """
你是英国反对党领袖 (Leader of the Opposition)。

## 你的政党信息
政党：{party_name}
政纲：{manifesto}

## 当前策略框架
策略类型：{strategy_type}
核心论点：
{key_arguments}
语气风格：{tone}
置信度：{confidence}
重点强调：
{focus_areas}

## 说话风格
- 犀利、批判性、有攻击性但不失礼仪
- 称呼议长为 "Mr Speaker" 或 "Madam Speaker"

## 当前议题
{topic}

## 辩论历史
{debate_history}

请根据策略框架发表你的发言。
"""


def create_lo_agent(llm, party_name: str = "Labour Party", manifesto: str = ""):
    """
    创建反对党领袖 Agent（无策略）
    
    Args:
        llm: LangChain LLM 对象
        party_name: 政党名称
        manifesto: 政纲
    
    Returns:
        反对党领袖 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(LO_PROMPT)
    return prompt | llm | StrOutputParser()


def create_lo_agent_with_strategy(llm, party_name: str, manifesto: str, argument: StrategyArgument):
    """
    创建带策略框架的反对党领袖 Agent
    
    Args:
        llm: LLM 对象
        party_name: 政党名称
        manifesto: 政纲
        argument: 策略框架
    
    Returns:
        反对党领袖 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(STRATEGY_LO_PROMPT)
    return prompt | llm | StrOutputParser()


def lo_node(state: dict, llm, party_config, strategy=None) -> dict:
    """
    反对党领袖节点处理函数
    
    Args:
        state: 当前状态
        llm: LLM 对象
        party_config: 政党配置
        strategy: 辩论策略（可选）
    
    Returns:
        更新后的状态
    """
    from state import DebateRecord
    
    # 获取辩论历史
    debate_history = "\n".join([
        f"- {r.speaker}: {r.content[:100]}..."
        for r in state["debate_records"][-3:]
    ]) if state["debate_records"] else "暂无发言记录"
    
    if strategy:
        # 使用策略生成框架
        context = extract_debate_context(state)
        argument = strategy.generate_argument(
            role="lo",
            topic=state["topic"],
            context=context
        )
        
        # 创建带策略的 Agent
        lo_agent = create_lo_agent_with_strategy(
            llm,
            party_config.name,
            party_config.manifesto,
            argument
        )
        
        # 生成发言
        response = lo_agent.invoke({
            "party_name": party_config.name,
            "manifesto": party_config.manifesto,
            "strategy_type": argument.strategy_type,
            "key_arguments": "\n".join(f"- {arg}" for arg in argument.key_arguments),
            "tone": argument.tone,
            "confidence": argument.confidence,
            "focus_areas": "\n".join(f"- {area}" for area in argument.focus_areas),
            "topic": state["topic"],
            "debate_history": debate_history
        })
    else:
        # 无策略，直接生成
        lo_agent = create_lo_agent(llm, party_config.name, party_config.manifesto)
        
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
    
    state["turn_count"] += 1
    state["current_speaker"] = "pm"
    
    return state
