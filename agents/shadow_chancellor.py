"""
Shadow Chancellor Agent - 影子财政大臣
反对党的经济发言人，质疑政府财政政策
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from strategies.base_strategy import StrategyArgument, extract_debate_context

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

STRATEGY_SHADOW_CHANCELLOR_PROMPT = """
你是影子财政大臣 (Shadow Chancellor)，代表反对党。

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
- 犀利、批判性、经济数据驱动
- 称呼议长为 "Mr Speaker"

## 当前议题
{topic}

## 辩论历史
{debate_history}

请根据策略框架发表你的发言。
"""


def create_shadow_chancellor_agent(llm, party_name: str = "Labour Party", manifesto: str = ""):
    """
    创建影子财政大臣 Agent（无策略）
    
    Args:
        llm: LangChain LLM 对象
        party_name: 政党名称
        manifesto: 政纲
    
    Returns:
        影子财政大臣 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(SHADOW_CHANCELLOR_PROMPT)
    return prompt | llm | StrOutputParser()


def create_shadow_chancellor_agent_with_strategy(llm, party_name: str, manifesto: str, argument: StrategyArgument):
    """
    创建带策略框架的影子财政大臣 Agent
    
    Args:
        llm: LLM 对象
        party_name: 政党名称
        manifesto: 政纲
        argument: 策略框架
    
    Returns:
        影子财政大臣 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(STRATEGY_SHADOW_CHANCELLOR_PROMPT)
    return prompt | llm | StrOutputParser()


def shadow_chancellor_node(state: dict, llm, party_config, strategy=None) -> dict:
    """
    影子财政大臣节点处理函数
    
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
            role="shadow_chancellor",
            topic=state["topic"],
            context=context
        )
        
        # 创建带策略的 Agent
        shadow_agent = create_shadow_chancellor_agent_with_strategy(
            llm,
            party_config.name,
            party_config.manifesto,
            argument
        )
        
        # 生成发言
        response = shadow_agent.invoke({
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
        shadow_agent = create_shadow_chancellor_agent(llm, party_config.name, party_config.manifesto)
        
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
    
    state["turn_count"] += 1
    state["current_speaker"] = "pm"
    
    return state
