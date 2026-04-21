"""
Chancellor Agent - 财政大臣
负责经济政策、财政预算辩护
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from strategies.base_strategy import StrategyArgument, extract_debate_context

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

STRATEGY_CHANCELLOR_PROMPT = """
你是英国财政大臣 (Chancellor of the Exchequer)，代表执政党。

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
- 专业、数据驱动、经济术语
- 称呼议长为 "Mr Speaker"

## 当前议题
{topic}

## 辩论历史
{debate_history}

请根据策略框架发表你的发言。
"""


def create_chancellor_agent(llm, party_name: str = "Conservative Party", manifesto: str = ""):
    """
    创建财政大臣 Agent（无策略）
    
    Args:
        llm: LangChain LLM 对象
        party_name: 政党名称
        manifesto: 政纲
    
    Returns:
        财政大臣 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(CHANCELLOR_PROMPT)
    return prompt | llm | StrOutputParser()


def create_chancellor_agent_with_strategy(llm, party_name: str, manifesto: str, argument: StrategyArgument):
    """
    创建带策略框架的财政大臣 Agent
    
    Args:
        llm: LLM 对象
        party_name: 政党名称
        manifesto: 政纲
        argument: 策略框架
    
    Returns:
        财政大臣 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(STRATEGY_CHANCELLOR_PROMPT)
    return prompt | llm | StrOutputParser()


def chancellor_node(state: dict, llm, party_config, strategy=None) -> dict:
    """
    财政大臣节点处理函数
    
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
            role="chancellor",
            topic=state["topic"],
            context=context
        )
        
        # 创建带策略的 Agent
        chancellor_agent = create_chancellor_agent_with_strategy(
            llm,
            party_config.name,
            party_config.manifesto,
            argument
        )
        
        # 生成发言
        response = chancellor_agent.invoke({
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
        chancellor_agent = create_chancellor_agent(llm, party_config.name, party_config.manifesto)
        
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
    
    state["turn_count"] += 1
    state["current_speaker"] = "shadow_chancellor"
    
    return state
