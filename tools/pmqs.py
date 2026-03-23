"""
Prime Minister's Questions (PMQs) Tool - 首相问答环节
每周首相接受议员质询的环节
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, List


PMQ_QUESTION_PROMPT = """
你是英国下议院议员，正在首相问答环节 (PMQs) 向首相提问。

## 你的信息
政党：{party_name}
角色：{role}
选区：{constituency}

## PMQs 规则
- 问题要尖锐、直接
- 可以涉及任何政策领域
- 常用 "Will the Prime Minister..." 开头
- 可以讽刺、质疑政府记录

## 当前背景
执政时间：{government_tenure}
热门议题：{hot_topics}

请提出一个质询问题。
"""

PMQ_RESPONSE_PROMPT = """
你是英国首相 (Prime Minister)，正在回答首相问答环节 (PMQs) 的问题。

## 你的政党信息
政党：{party_name}
政纲：{manifesto}

## PMQs 回答技巧
- 避免直接回答敏感问题
- 转向政府成就
- 反击反对党
- 使用 "What I can tell the House is..."
- 保持自信和幽默

## 问题
{question}

## 当前背景
执政时间：{government_tenure}
热门议题：{hot_topics}

请回答这个质询问题。
"""


def create_questioner_agent(llm, party_name: str, role: str, constituency: str):
    """
    创建提问议员 Agent
    
    Args:
        llm: LLM 对象
        party_name: 政党名称
        role: 角色 (如 "backbencher", "shadow minister", "committee chair")
        constituency: 选区
    
    Returns:
        提问 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(PMQ_QUESTION_PROMPT)
    return prompt | llm | StrOutputParser()


def create_pm_responder_agent(llm, party_name: str, manifesto: str):
    """
    创建首相回答 Agent
    
    Args:
        llm: LLM 对象
        party_name: 政党名称
        manifesto: 政纲
    
    Returns:
        首相回答 Agent 链
    """
    prompt = ChatPromptTemplate.from_template(PMQ_RESPONSE_PROMPT)
    return prompt | llm | StrOutputParser()


def run_pmq_session(
    llm,
    topic: str,
    num_questions: int = 6,
    government_tenure: str = "18 个月",
    hot_topics: List[str] = None
) -> List[Dict]:
    """
    运行首相问答环节
    
    Args:
        llm: LLM 对象
        topic: 主要议题
        num_questions: 问题数量
        government_tenure: 执政时间
        hot_topics: 热门议题列表
    
    Returns:
        问答记录列表
    """
    if hot_topics is None:
        hot_topics = ["NHS", "经济", "移民", "教育", "住房"]
    
    from config import PARTIES
    
    gov_party = PARTIES["conservative"]
    opp_party = PARTIES["labour"]
    
    pmq_records = []
    
    print(f"\n{'='*60}")
    print("🎯 Prime Minister's Questions (PMQs)")
    print("   首相问答环节")
    print(f"{'='*60}\n")
    
    # 创建首相回答 Agent
    pm_responder = create_pm_responder_agent(llm, gov_party.name, gov_party.manifesto)
    
    for i in range(num_questions):
        # 交替执政党和反对党提问
        if i % 2 == 0:
            questioner_party = opp_party
            questioner_role = "Shadow Minister"
            questioner_constituency = "Birmingham Ladywood"
        else:
            questioner_party = gov_party
            questioner_role = "Backbencher"
            questioner_constituency = "Cotswolds"
        
        # 创建提问 Agent
        questioner = create_questioner_agent(
            llm,
            questioner_party.name,
            questioner_role,
            questioner_constituency
        )
        
        # 生成问题
        question = questioner.invoke({
            "party_name": questioner_party.name,
            "role": questioner_role,
            "constituency": questioner_constituency,
            "government_tenure": government_tenure,
            "hot_topics": ", ".join(hot_topics)
        })
        
        print(f"\n❓ 问题 {i+1} ({questioner_role} - {questioner_party.name})")
        print(f"{'-'*40}")
        print(question[:200])
        
        # 首相回答
        response = pm_responder.invoke({
            "party_name": gov_party.name,
            "manifesto": gov_party.manifesto,
            "question": question,
            "government_tenure": government_tenure,
            "hot_topics": ", ".join(hot_topics)
        })
        
        print(f"\n💬 首相回答")
        print(f"{'-'*40}")
        print(response[:200])
        
        pmq_records.append({
            "turn": i,
            "questioner_party": questioner_party.name,
            "questioner_role": questioner_role,
            "question": question,
            "response": response
        })
    
    print(f"\n{'='*60}")
    print(f"✅ PMQs 结束 - 共 {num_questions} 个问题")
    print(f"{'='*60}\n")
    
    return pmq_records
