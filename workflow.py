"""
Parliament Debate Workflow - Enhanced Version
使用 LangGraph 构建辩论流程（增强版）

功能:
- 首相问答环节 (PMQs)
- 投票系统
- 更多角色 (财政大臣、影子财政大臣、后座议员)
"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import sys
sys.path.insert(0, 'D:\\PyCharmProgram\\parliament-sim')

from state import ParliamentState, DebateRecord, create_initial_state
from config import PARTIES, LLM_CONFIG, DEBATE_CONFIG
from agents.speaker import speaker_node
from agents.pm import pm_node
from agents.lo import lo_node
from agents.chancellor import chancellor_node
from agents.shadow_chancellor import shadow_chancellor_node
from agents.backbencher import backbencher_node
from tools.voting import vote_node, format_vote_result
from tools.pmqs import run_pmq_session


def create_llm():
    """
    创建 LLM 实例
    
    支持 Ollama 本地模型和 OpenAI 云端模型
    """
    if LLM_CONFIG["provider"] == "ollama":
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            base_url=LLM_CONFIG["base_url"],
            model=LLM_CONFIG["model"],
            temperature=0.7,
        )
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=LLM_CONFIG["model"],
            temperature=0.7,
        )
    return llm


def should_continue_debate(state: ParliamentState) -> str:
    """
    判断是否继续辩论
    
    Returns:
        "continue" 或 "end"
    """
    if state["ended"] or state["turn_count"] >= state["max_turns"]:
        return "end"
    return "continue"


def should_trigger_vote(state: ParliamentState) -> str:
    """
    判断是否触发投票
    
    Returns:
        "vote" 或 "continue"
    """
    if state["turn_count"] >= state["max_turns"]:
        return "vote"
    return "continue"


def build_parliament_graph():
    """
    构建议会辩论图（完整版）
    
    Returns:
        编译后的 LangGraph
    """
    # 创建状态图
    workflow = StateGraph(ParliamentState)
    
    # 创建 LLM 实例
    llm = create_llm()
    
    # 获取政党配置
    gov_party = PARTIES["conservative"]
    opp_party = PARTIES["labour"]
    
    # 添加节点
    workflow.add_node("speaker", lambda s: speaker_node(s, llm))
    workflow.add_node("pm", lambda s: pm_node(s, llm, gov_party))
    workflow.add_node("lo", lambda s: lo_node(s, llm, opp_party))
    workflow.add_node("chancellor", lambda s: chancellor_node(s, llm, gov_party))
    workflow.add_node("shadow_chancellor", lambda s: shadow_chancellor_node(s, llm, opp_party))
    workflow.add_node("vote", lambda s: vote_node(s))
    
    # 后座议员配置
    backbencher_configs = [
        {"party_name": "Conservative Party", "faction": "loyal", "constituency": "Surrey Heath"},
        {"party_name": "Labour Party", "faction": "loyal", "constituency": "Manchester Central"},
    ]
    
    for i, config in enumerate(backbencher_configs):
        workflow.add_node(f"backbencher_{i}", lambda s, c=config: backbencher_node(s, llm, c))
    
    # 定义流程
    workflow.add_edge(START, "speaker")
    
    # 议长开场后进入 PM 发言
    workflow.add_edge("speaker", "pm")
    
    # PM 发言后到 LO
    workflow.add_edge("pm", "lo")
    
    # LO 发言后到财政大臣
    workflow.add_edge("lo", "chancellor")
    
    # 财政大臣到影子财政大臣
    workflow.add_edge("chancellor", "shadow_chancellor")
    
    # 影子财政大臣到后座议员
    workflow.add_edge("shadow_chancellor", "backbencher_0")
    
    # 后座议员交替
    workflow.add_edge("backbencher_0", "backbencher_1")
    
    # 后座议员回到议长
    workflow.add_edge("backbencher_1", "speaker")
    
    # 议长判断是否继续或投票
    workflow.add_conditional_edges(
        "speaker",
        should_trigger_vote,
        {
            "vote": "vote",
            "continue": "pm"
        }
    )
    
    # 投票后结束
    workflow.add_edge("vote", END)
    
    # 编译图
    app = workflow.compile()
    
    return app


def run_pmq_mode(topic: str = "政府政策质询"):
    """
    运行首相问答环节 (PMQs)
    
    Args:
        topic: 主要议题
    
    Returns:
        PMQ 记录列表
    """
    print(f"\n{'='*60}")
    print("🎯 Prime Minister's Questions (PMQs)")
    print("   首相问答环节")
    print(f"{'='*60}\n")
    
    llm = create_llm()
    
    from tools.pmqs import run_pmq_session
    records = run_pmq_session(llm, topic, num_questions=6)
    
    return records


def run_debate_mode(topic: str, max_turns: int = 10, with_vote: bool = True):
    """
    运行辩论模式
    
    Args:
        topic: 辩论议题
        max_turns: 最大回合数
        with_vote: 是否包含投票
    
    Returns:
        最终状态
    """
    print(f"\n{'='*60}")
    print(f"🏛️  英国议会模拟 - 辩论开始")
    print(f"议题：{topic}")
    print(f"{'='*60}\n")
    
    # 创建初始状态
    initial_state = create_initial_state(topic, max_turns, mode="debate")
    
    # 构建并运行图
    app = build_parliament_graph()
    
    # 运行辩论
    final_state = None
    for event in app.stream(initial_state, stream_mode="values"):
        if event["debate_records"]:
            last_record = event["debate_records"][-1]
            print(f"\n[{last_record.speaker.upper()}] (回合 {last_record.turn})")
            print(f"{'-'*40}")
            # 打印前 200 字符
            content = last_record.content[:200]
            if len(last_record.content) > 200:
                content += "..."
            print(content)
        
        final_state = event
    
    # 打印总结
    print(f"\n{'='*60}")
    print(f"🏛️  辩论结束 - 共 {final_state['turn_count']} 回合")
    
    if final_state["votes"]:
        print(f"\n📊 投票结果:")
        print(f"  赞成：{final_state['votes'].get('ayes', 0)}")
        print(f"  反对：{final_state['votes'].get('nos', 0)}")
        print(f"  弃权：{final_state['votes'].get('abstentions', 0)}")
        print(f"  结果：{final_state['votes'].get('result', 'unknown')}")
    
    print(f"{'='*60}\n")
    
    return final_state


def run_full_session(topic: str, max_turns: int = 10):
    """
    运行完整议会 session（辩论 + PMQs + 投票）
    
    Args:
        topic: 议题
        max_turns: 辩论最大回合数
    
    Returns:
        完整记录
    """
    print("\n" + "="*60)
    print("🏛️  UK Parliament Full Session")
    print("    英国议会完整议程")
    print("="*60)
    
    # 1. 首相问答环节
    print("\n📌 第一部分：首相问答 (PMQs)")
    pmq_records = run_pmq_mode(topic)
    
    # 2. 正式辩论
    print("\n📌 第二部分：正式辩论")
    debate_state = run_debate_mode(topic, max_turns, with_vote=True)
    
    # 3. 汇总
    print("\n" + "="*60)
    print("✅ 议会议程完成")
    print("="*60)
    
    return {
        "pmq": pmq_records,
        "debate": debate_state
    }


if __name__ == "__main__":
    # 示例：运行完整议程
    topic = "是否应该增加 NHS（国家医疗服务）的预算？"
    run_full_session(topic, max_turns=8)
