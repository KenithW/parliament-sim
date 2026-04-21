# 🧪 议会模拟算法对比实验

## 概述

本框架用于研究不同人工智能算法在议会辩论场景中的表现差异，评估维度包括：
- **论证质量**：逻辑连贯性、论据充分性
- **说服效果**：对中立听众的影响
- **辩论结果**：投票胜负

## 已实现的策略

### Phase 1 (当前版本)

| 策略 | 说明 | 特点 |
|------|------|------|
| `baseline` | 纯 LLM 生成 | 对照组，无策略干预 |
| `heuristic_rule` | 启发式规则 | 基于硬编码决策规则 |

### Phase 2 (计划中)

- `a_star` - A* 搜索最优论证路径
- `genetic` - 遗传算法进化论点
- `heuristic_search` - 启发式搜索最佳策略

## 使用方法

### 运行对比实验

```bash
# 运行所有策略对比（默认 5 次）
python run_experiment.py --topic "是否应该增加 NHS 预算" --strategies all --runs 5

# 运行单个策略
python run_experiment.py --topic "经济政策" --strategies baseline --runs 3

# 指定输出目录
python run_experiment.py --topic "移民政策" --strategies all --runs 5 --output results/my_experiment
```

### 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--topic` | `-t` | 辩论议题 | "是否应该增加 NHS 预算" |
| `--strategies` | `-s` | 策略列表 (`all` 或单个策略名) | `all` |
| `--runs` | `-n` | 每种策略运行次数 | `5` |
| `--output` | `-o` | 输出目录 | 自动生成 |

## 输出结果

实验完成后，结果保存在 `results/experiment_YYYYMMDD_HHMMSS/` 目录下：

```
results/experiment_20260405_143022/
├── results.csv              # 主要统计数据
├── detailed_scores.csv      # 详细维度得分
├── metadata.json            # 实验元数据
└── debates/
    ├── debate_baseline_run1.md
    ├── debate_baseline_run2.md
    ├── debate_heuristic_rule_run1.md
    └── ...
```

### results.csv 格式

```csv
experiment_id,strategy,run_number,topic,opening_score,closing_score,overall_score,win_result,debate_file
exp_001,baseline,1,NHS 预算，6.80,7.20,7.00,LOSS,debate_baseline_run1.md
exp_001,heuristic_rule,1,NHS 预算，7.40,7.80,7.60,WIN,debate_heuristic_rule_run1.md
```

### detailed_scores.csv 格式

```csv
experiment_id,strategy,run_number,speech_type,logical_coherence,evidence_quality,persuasiveness,rebuttal_strength,language_tone,overall_score,comment
exp_001,baseline,1,opening,7.0,6.5,7.2,6.0,7.5,7.04,"论点清晰但缺乏数据支持"
exp_001,baseline,1,closing,6.8,6.2,7.0,6.5,7.8,6.86,"总结有力但反驳不足"
```

## 评估维度

LLM 裁判从 5 个维度对发言进行评分（1-10 分）：

1. **逻辑连贯性** (Logical Coherence) - 论点推理链条是否清晰
2. **论据质量** (Evidence Quality) - 是否使用具体数据、事实、案例
3. **说服力** (Persuasiveness) - 对中立听众的影响程度
4. **反驳力度** (Rebuttal Strength) - 对对方论点的有效回应
5. **语言表达** (Language & Tone) - 措辞是否专业、得体

**综合得分计算**：
- 开场发言 (50%) + 总结发言 (50%)
- 各维度权重相等

## 实验流程

```
┌─────────────────────────────────────────────────────────┐
│ 1. 初始化 LLM                                           │
│    - 使用 Ollama 本地模型                                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 对于每种策略                                         │
│    For run in 1..runs:                                  │
│      a. 运行 6 轮辩论                                     │
│         (Speaker → PM → LO → Chancellor →               │
│          Shadow Chancellor → PM → LO → Vote)            │
│      b. 保存辩论记录到 Markdown 文件                      │
│      c. LLM 裁判评估开场和总结发言                        │
│      d. 判定胜负（投票为主，评分为辅）                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. 生成统计报告                                         │
│    - 计算每种策略的平均得分                              │
│    - 计算胜率                                            │
│    - 导出 CSV 文件                                        │
└─────────────────────────────────────────────────────────┘
```

## 辩论流程（实验模式）

实验模式采用简化的 6 轮辩论流程：

| 轮次 | 发言人 | 角色 | 评估点 |
|------|--------|------|--------|
| 1 | Speaker | 议长 | 开场（计入评估） |
| 2 | PM | 首相 | |
| 3 | LO | 反对党领袖 | |
| 4 | Chancellor | 财政大臣 | |
| 5 | Shadow Chancellor | 影子财政大臣 | |
| 6 | PM | 首相 | |
| 7 | LO | 反对党领袖 | 总结（计入评估） |
| 8 | Vote | 投票 | 胜负判定 |

**注意**：实际评估的是 PM 的开场（第 1 轮实质发言）和 LO 的总结（最后 1 轮实质发言）。

## 策略如何影响发言

策略通过**策略框架**指导 LLM 生成发言：

```python
# 策略返回框架
StrategyArgument(
    strategy_type="aggressive_attack",
    key_arguments=["攻击对方弱点", "质疑对方记录"],
    tone="confrontational",
    confidence=0.8,
    focus_areas=["批判", "质疑"]
)

# LLM 根据框架生成发言
prompt = f"""
你是首相。使用以下策略框架：
- 策略类型：aggressive_attack
- 核心论点：攻击对方弱点，质疑对方记录
- 语气风格：confrontational
- 置信度：0.8

议题：{topic}
辩论历史：{history}

请发表你的发言。
"""
```

## 扩展新策略

要添加新策略，需要：

1. 继承 `DebateStrategy` 抽象基类
2. 实现 `generate_argument()` 方法
3. 实现 `name()` 方法
4. 在 `run_experiment.py` 的 `get_strategies()` 中注册

示例：

```python
# strategies/my_new_strategy.py
from strategies.base_strategy import DebateStrategy, StrategyArgument

class MyNewStrategy(DebateStrategy):
    def generate_argument(self, role: str, topic: str, context: dict) -> StrategyArgument:
        # 实现你的策略逻辑
        return StrategyArgument(
            strategy_type="my_strategy",
            key_arguments=["论点 1", "论点 2"],
            tone="balanced",
            confidence=0.75,
            focus_areas=["重点 1"]
        )
    
    def name(self) -> str:
        return "my_new_strategy"
```

## 依赖项

```bash
pip install -r requirements.txt
```

核心依赖：
- `langchain` - LLM 编排框架
- `langgraph` - 辩论流程控制
- `langchain-ollama` - 本地 LLM 支持
- `pandas` - 数据分析

## 配置

在 `config.py` 中修改：

```python
# 模型配置
LLM_CONFIG = {
    "provider": "ollama",
    "base_url": "http://localhost:11434",
    "model": "qwen2.5:7b",
}

# 实验配置
EXPERIMENT_CONFIG = {
    "max_turns": 6,              # 辩论轮数
    "weight_opening": 0.5,       # 开场权重
    "weight_closing": 0.5,       # 总结权重
}
```

## 常见问题

**Q: 如何更换 LLM 模型？**

A: 在 `config.py` 中修改 `LLM_CONFIG["model"]`，当前实验链路只支持 Ollama 本地模型。

**Q: 实验运行很慢怎么办？**

A: 可以减少 `--runs` 参数，或使用更快的 LLM 模型。

**Q: 如何查看详细的评估结果？**

A: 查看 `detailed_scores.csv` 文件，包含每个维度的详细得分。

**Q: 胜负如何判定？**

A: 优先使用投票结果，无投票时使用综合评分（≥7.0 为 WIN）。

## 下一步计划

- [ ] 实现 A* 搜索策略
- [ ] 实现遗传算法策略
- [ ] 实现启发式搜索策略
- [ ] 添加可视化图表（雷达图、柱状图）
- [ ] 支持更多评估维度
- [ ] 添加实时辩论直播功能

## License

MIT License
