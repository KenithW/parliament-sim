# 🏛️ UK Parliament Simulation

英国议会模拟系统 - 使用 LangChain 和 LangGraph 构建的多 Agent 辩论系统（增强版）

## 📋 功能特点

### 核心功能
- **多 Agent 系统**: 议长、首相、反对党领袖、财政大臣等角色
- **LangGraph 流程**: 基于状态机的辩论流程控制
- **本地模型支持**: 使用 Ollama 运行本地 LLM（免费！）
- **辩论记录**: 自动保存 Markdown 格式的辩论记录

### 🆕 新增功能
- **🎯 首相问答环节 (PMQs)**: 每周首相接受议员质询
- **📊 投票系统**: 模拟议会投票、计票、结果记录
- **👥 更多角色**:
  - 财政大臣 (Chancellor)
  - 影子财政大臣 (Shadow Chancellor)
  - 后座议员 (Backbenchers)

## 🚀 快速开始

### 1. 安装依赖

```bash
cd D:\PyCharmProgram\parliament-sim
pip install -r requirements.txt
```

### 2. 确保 Ollama 运行

```bash
# 检查 Ollama 状态
ollama list

# 如果没有模型，拉取一个
ollama pull qwen2.5:7b
```

### 3. 运行模拟

```bash
# 辩论模式（默认）
python main.py

# 首相问答环节
python main.py --mode pmqs

# 完整议程（PMQs + 辩论 + 投票）
python main.py --mode full

# 指定议题
python main.py --topic "是否应该提高最低工资？"

# 启用投票
python main.py --with-vote

# 保存记录
python main.py --save
```

## 📁 项目结构

```
parliament-sim/
├── main.py              # 主入口
├── workflow.py          # LangGraph 辩论流程（增强版）
├── state.py             # 状态定义
├── config.py            # 配置
├── requirements.txt     # 依赖
├── agents/
│   ├── speaker.py       # 议长 Agent
│   ├── pm.py            # 首相 Agent
│   ├── lo.py            # 反对党领袖 Agent
│   ├── chancellor.py    # 财政大臣 Agent ✨
│   ├── shadow_chancellor.py # 影子财政大臣 Agent ✨
│   └── backbencher.py   # 后座议员 Agent ✨
├── tools/
│   ├── voting.py        # 投票系统 ✨
│   └── pmqs.py          # 首相问答工具 ✨
├── parties/
│   ├── conservative.md  # 保守党
│   ├── labour.md        # 工党
│   └── libdem.md        # 自民党
└── debates/             # 辩论记录输出
```

## 🤖 可用角色

| 角色 | 文件 | 职责 |
|------|------|------|
| Speaker | `agents/speaker.py` | 主持辩论、维持秩序 |
| PM | `agents/pm.py` | 首相，执政党领袖 |
| LO | `agents/lo.py` | 反对党领袖 |
| Chancellor | `agents/chancellor.py` | 财政大臣，经济政策 |
| Shadow Chancellor | `agents/shadow_chancellor.py` | 影子财政大臣 |
| Backbencher | `agents/backbencher.py` | 后座议员，选区代表 |

## 🎯 运行模式

### 1. 辩论模式 (debate)

标准议会辩论流程：
```
Speaker → PM → LO → Chancellor → Shadow Chancellor → Backbenchers → Vote
```

```bash
python main.py --mode debate --topic "NHS 预算议题" --with-vote
```

### 2. 首相问答模式 (pmqs)

首相问答环节，议员质询首相：
```bash
python main.py --mode pmqs
```

### 3. 完整模式 (full)

完整议会议程：
```
1. PMQs (首相问答)
2. 正式辩论
3. 投票
```

```bash
python main.py --mode full --topic "经济政策"
```

## 📊 投票系统

投票结果自动计算：

```
✅ 投票结果

议题：是否应该增加 NHS 预算？

| 选项 | 票数 |
|------|------|
| 赞成 (Aye) | 345 |
| 反对 (No) | 268 |
| 弃权 (Abstain) | 20 |

结果：PASSED
```

## 🔧 配置选项

在 `config.py` 中修改:

```python
# 政党配置
PARTIES = {...}

# 辩论规则
DEBATE_CONFIG = {
    "max_turns": 10,
    "question_time": True,  # 启用 PMQs
}

# 模型设置
LLM_CONFIG = {
    "provider": "ollama",  # 或 "openai"
    "model": "qwen2.5:7b",
}
```

## 📝 示例输出

### 辩论模式
```
============================================================
🏛️  英国议会模拟 - 辩论开始
议题：是否应该增加 NHS（国家医疗服务）的预算？
============================================================

[SPEAKER] (回合 0)
----------------------------------------
Order! Order! The House will now debate...

[PM] (回合 1)
----------------------------------------
Mr Speaker, this government believes...

[LO] (回合 2)
----------------------------------------
Mr Speaker, the Prime Minister's claims...

[CHANCELLOR] (回合 3)
----------------------------------------
Mr Speaker, the Treasury's position...

✅ 辩论完成！
📊 投票结果：345 Aye, 268 No - PASSED
```

### PMQ 模式
```
============================================================
🎯 Prime Minister's Questions (PMQs)
============================================================

❓ 问题 1 (Shadow Minister - Labour)
----------------------------------------
Will the Prime Minister explain why...

💬 首相回答
----------------------------------------
What I can tell the House is...
```

## 🎯 扩展建议

### 添加新角色
1. 在 `agents/` 创建新文件
2. 定义 Agent prompt 和 node 函数
3. 在 `workflow.py` 中添加节点和边

### 添加新政党
1. 在 `parties/` 创建 Markdown 文件
2. 在 `config.py` 的 `PARTIES` 中添加配置

### 使用云端模型
修改 `config.py`:
```python
LLM_CONFIG = {
    "provider": "openai",
    "model": "gpt-4o",
}
```

## 📚 依赖

- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Ollama](https://ollama.ai/)

## 🎭 下一步计划

- [ ] Web UI 界面
- [ ] 实时辩论直播
- [ ] 更多政党（SNP、Green、UKIP）
- [ ] 历史辩论模式重现
- [ ] 事实核查工具集成

---

**Have fun debating! 🏛️**
