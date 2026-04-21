"""
Debate Evaluator - 辩论评估器

使用 LLM 作为裁判，对辩论发言进行多维度评分
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Optional
from dataclasses import dataclass
from state import DebateRecord


class EvaluationMetrics(BaseModel):
    """评估指标模型"""
    
    logical_coherence: float = Field(description="逻辑连贯性 (1-10 分)")
    evidence_quality: float = Field(description="论据质量 (1-10 分)")
    persuasiveness: float = Field(description="说服力 (1-10 分)")
    rebuttal_strength: float = Field(description="反驳力度 (1-10 分)")
    language_tone: float = Field(description="语言表达 (1-10 分)")
    overall_comment: str = Field(description="简短评语")


class DebateEvaluator:
    """
    辩论评估器
    
    使用 LLM 对发言内容进行多维度评分
    """
    
    EVALUATION_PROMPT = """
你是一位专业的英国议会辩论评估员。请根据以下标准评估发言内容（每项 1-10 分）。

【评估标准】
1. 逻辑连贯性 (Logical Coherence)
   - 论点是否有清晰的推理链条
   - 是否存在逻辑谬误或自相矛盾

2. 论据质量 (Evidence Quality)
   - 是否使用了具体数据、事实、案例
   - 论据来源是否可靠

3. 说服力 (Persuasiveness)
   - 对中立听众的影响程度
   - 情感诉求与理性论证的平衡

4. 反驳力度 (Rebuttal Strength)
   - 对对方论点的有效回应
   - 是否成功化解对方攻击
   - 如果是开场发言，此项权重降低

5. 语言表达 (Language & Tone)
   - 措辞是否专业、得体
   - 是否符合议会礼仪和角色身份

【发言内容】
{content}

【辩论背景】
- 发言人角色：{role}
- 所属政党：{party}
- 发言类型：{speech_type}
- 议题：{topic}

请严格按照以下 JSON 格式输出评分：
{{
    "logical_coherence": <1-10 的数字>,
    "evidence_quality": <1-10 的数字>,
    "persuasiveness": <1-10 的数字>,
    "rebuttal_strength": <1-10 的数字>,
    "language_tone": <1-10 的数字>,
    "overall_comment": "<简短的中文评语>"
}}
"""
    
    def __init__(self, llm):
        """
        初始化评估器
        
        Args:
            llm: LangChain LLM 对象
        """
        self.llm = llm
        self.chain = self._build_eval_chain()
    
    def _build_eval_chain(self):
        """构建评估链"""
        prompt = ChatPromptTemplate.from_template(self.EVALUATION_PROMPT)
        return prompt | self.llm | JsonOutputParser()
    
    def evaluate_speech(
        self,
        content: str,
        role: str,
        party: str,
        speech_type: str,
        topic: str
    ) -> Dict:
        """
        评估单个发言
        
        Args:
            content: 发言内容
            role: 发言人角色 (pm, lo, chancellor, etc.)
            party: 所属政党
            speech_type: 发言类型 (opening/closing/other)
            topic: 议题
        
        Returns:
            包含各维度得分的字典
        """
        try:
            result = self.chain.invoke({
                "content": content,
                "role": self._get_role_display(role),
                "party": party,
                "speech_type": speech_type,
                "topic": topic
            })
            
            # 确保所有字段都存在
            return {
                "logical_coherence": float(result.get("logical_coherence", 5.0)),
                "evidence_quality": float(result.get("evidence_quality", 5.0)),
                "persuasiveness": float(result.get("persuasiveness", 5.0)),
                "rebuttal_strength": float(result.get("rebuttal_strength", 5.0)),
                "language_tone": float(result.get("language_tone", 5.0)),
                "overall_comment": result.get("overall_comment", ""),
            }
        except Exception as e:
            print(f"⚠️  评估失败：{e}")
            # 返回默认分数
            return {
                "logical_coherence": 5.0,
                "evidence_quality": 5.0,
                "persuasiveness": 5.0,
                "rebuttal_strength": 5.0,
                "language_tone": 5.0,
                "overall_comment": f"评估出错：{str(e)}",
            }
    
    def evaluate_debate(
        self,
        debate_records: List[DebateRecord],
        topic: str
    ) -> Dict:
        """
        评估整场辩论
        
        只评估开场（第 1 轮）和总结（最后 1 轮）
        
        Args:
            debate_records: 辩论记录列表
            topic: 议题
        
        Returns:
            包含开场、总结和综合得分的字典
        """
        if not debate_records:
            return {
                "opening": None,
                "closing": None,
                "overall": None
            }
        
        substantive_records = [r for r in debate_records if r.speaker != "speaker"]
        if not substantive_records:
            return {
                "opening": None,
                "closing": None,
                "overall": None
            }

        # 提取开场和总结（跳过 Speaker 的主持发言）
        opening_record = substantive_records[0]
        closing_record = substantive_records[-1]
        
        print(f"\n📊 评估辩论：共 {len(debate_records)} 轮发言")
        print(f"   开场：{opening_record.speaker}")
        print(f"   总结：{closing_record.speaker}")
        
        # 评估开场
        print("\n  评估开场发言...")
        opening_score = self.evaluate_speech(
            content=opening_record.content,
            role=opening_record.speaker,
            party=self._get_party_for_role(opening_record.speaker),
            speech_type="opening",
            topic=topic
        )
        opening_score["overall_score"] = self._calculate_overall_score(opening_score)
        
        # 评估总结
        print("  评估总结发言...")
        closing_score = self.evaluate_speech(
            content=closing_record.content,
            role=closing_record.speaker,
            party=self._get_party_for_role(closing_record.speaker),
            speech_type="closing",
            topic=topic
        )
        closing_score["overall_score"] = self._calculate_overall_score(closing_score)
        
        # 计算综合得分（50% + 50%）
        overall_score = self._calculate_overall(opening_score, closing_score)
        
        return {
            "opening": opening_score,
            "closing": closing_score,
            "overall": overall_score
        }
    
    def _calculate_overall_score(self, scores: Dict) -> float:
        """计算单项综合得分（5 个维度平均）"""
        dimensions = ["logical_coherence", "evidence_quality", "persuasiveness", 
                      "rebuttal_strength", "language_tone"]
        total = sum(scores.get(d, 5.0) for d in dimensions)
        return total / len(dimensions)
    
    def _calculate_overall(self, opening: Dict, closing: Dict) -> Dict:
        """
        计算综合得分（开场 50% + 总结 50%）
        
        Returns:
            包含各维度综合得分和总评的字典
        """
        dimensions = ["logical_coherence", "evidence_quality", "persuasiveness", 
                      "rebuttal_strength", "language_tone"]
        
        overall = {}
        for dim in dimensions:
            opening_val = opening.get(dim, 5.0)
            closing_val = closing.get(dim, 5.0)
            overall[dim] = (opening_val + closing_val) / 2
        
        # 综合总分
        overall["overall_score"] = self._calculate_overall_score(overall)
        
        # 综合评语
        overall["overall_comment"] = (
            f"开场：{opening.get('overall_comment', '')} | "
            f"总结：{closing.get('overall_comment', '')}"
        )
        
        return overall
    
    def _get_role_display(self, role: str) -> str:
        """将角色 ID 转换为显示名称"""
        mapping = {
            "pm": "Prime Minister",
            "lo": "Leader of the Opposition",
            "chancellor": "Chancellor of the Exchequer",
            "shadow_chancellor": "Shadow Chancellor",
            "speaker": "Speaker",
            "backbencher_0": "Backbencher (Government)",
            "backbencher_1": "Backbencher (Opposition)",
        }
        return mapping.get(role, role)

    def _get_party_for_role(self, role: str) -> str:
        """根据角色返回所属政党"""
        if role in {"pm", "chancellor", "backbencher_0"}:
            return "conservative"
        if role in {"lo", "shadow_chancellor", "backbencher_1"}:
            return "labour"
        return "neutral"
