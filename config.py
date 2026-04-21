"""
Parliament Simulation Configuration
英国议会模拟配置
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class PartyConfig:
    name: str
    color: str
    manifesto: str
    leader: str

# 政党配置
PARTIES: Dict[str, PartyConfig] = {
    "conservative": PartyConfig(
        name="Conservative Party",
        color="blue",
        manifesto="经济稳定、减税、强化国防、控制移民",
        leader="Prime Minister"
    ),
    "labour": PartyConfig(
        name="Labour Party",
        color="red",
        manifesto="公共服务投资、工人权益、绿色能源、社会公平",
        leader="Leader of the Opposition"
    ),
    "libdem": PartyConfig(
        name="Liberal Democrats",
        color="orange",
        manifesto="公民自由、教育改革、欧盟关系、比例代表制",
        leader="LibDem Leader"
    )
}

# Agent 角色配置
AGENT_ROLES = [
    "speaker",      # 议长 - 中立主持
    "pm",           # 首相 - 执政党领袖
    "lo",           # 反对党领袖
    "chancellor",   # 财政大臣
    "shadow_chancellor",  # 影子财政大臣
]

# 辩论流程配置
DEBATE_CONFIG = {
    "max_turns": 10,           # 最大回合数
    "turn_time_limit": 500,    # 每回合字数限制
    "question_time": True,     # 启用首相问答环节
}

# 模型配置（使用 Ollama 本地模型）
LLM_CONFIG = {
    "provider": "ollama",
    "base_url": "http://localhost:11434",
    "model": "qwen2.5:7b",
}

# 实验配置
EXPERIMENT_CONFIG = {
    "max_turns": 6,              # 缩短到 6 轮
    "evaluate_opening": True,    # 评估开场
    "evaluate_closing": True,    # 评估总结
    "weight_opening": 0.5,       # 开场权重
    "weight_closing": 0.5,       # 总结权重
    "speakers": ["pm", "lo", "chancellor", "shadow_chancellor", "pm", "lo"],
}

