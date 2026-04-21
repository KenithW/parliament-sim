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

STRATEGY_PM_PROMPT = """
你是英国首相 (Prime Minister)，代表执政党。

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
- 自信、坚定、有说服力
- 称呼议长为 "Mr Speaker" 或 "Madam Speaker"
- 使用正式表达

## 当前议题
{topic}

## 辩论历史
{debate_history}

请根据策略框架发表你的发言。
"""


from strategies.base_strategy import StrategyArgument, extract_debate_context


def create_pm_agent(llm, party_name: str = "Conservative Party", manifesto: str = ""):
    """
    创建首相 Agent（无策略）
    
    Args:
        llm: LangChain LLM 对象
        party_name: 政党名称
        manifesto: 政纲
    
    Returns:
        首相 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(PM_PROMPT)
    return prompt | llm | StrOutputParser()


def create_pm_agent_with_strategy(llm, party_name: str, manifesto: str, argument: StrategyArgument):
    """
    创建带策略框架的首相 Agent
    
    Args:
        llm: LLM 对象
        party_name: 政党名称
        manifesto: 政纲
        argument: 策略框架
    
    Returns:
        首相 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(STRATEGY_PM_PROMPT)
    return prompt | llm | StrOutputParser()


def pm_node(state: dict, llm, party_config, strategy=None) -> dict:
    """
    首相节点处理函数
    
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
            role="pm",
            topic=state["topic"],
            context=context
        )
        
        # 创建带策略的 Agent
        pm_agent = create_pm_agent_with_strategy(
            llm,
            party_config.name,
            party_config.manifesto,
            argument
        )
        
        # 生成发言
        response = pm_agent.invoke({
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
        pm_agent = create_pm_agent(llm, party_config.name, party_config.manifesto)
        
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
    
    state["turn_count"] += 1
    state["current_speaker"] = "lo"
    
    return state
