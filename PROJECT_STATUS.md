# 🏛️ 议会模拟算法对比实验 - 项目状态

**最后更新**: 2026-04-05  
**当前阶段**: Phase 1 框架完成，Ollama 本地链路修复中

---

## 📋 项目目标

研究不同人工智能方法在议会模拟场景中，在论证质量、说服效果以及辩论结果方面的表现差异。

---

## ✅ 已完成 (Phase 1)

### 核心框架

- [x] **策略抽象层** (`strategies/`)
  - [x] `base_strategy.py` - 抽象接口 `DebateStrategy` 和 `StrategyArgument` 数据类
  - [x] `baseline_strategy.py` - 纯 LLM 对照组
  - [x] `heuristic_rule_strategy.py` - 启发式规则策略（基于硬编码决策规则）

- [x] **评估系统** (`evaluation/`)
  - [x] `evaluator.py` - LLM 裁判，5 维度评分系统
    - 逻辑连贯性、论据质量、说服力、反驳力度、语言表达

- [x] **实验框架** (`experiments/`)
  - [x] `runner.py` - 实验运行器
  - [x] `results.py` - 结果数据和 CSV 导出

- [x] **实验入口** 
  - [x] `run_experiment.py` - CLI 入口脚本

### Agent 改造（支持策略注入）

- [x] `agents/pm.py` - 首相 Agent 支持策略框架
- [x] `agents/lo.py` - 反对党领袖 Agent 支持策略框架
- [x] `agents/chancellor.py` - 财政大臣 Agent 支持策略框架
- [x] `agents/shadow_chancellor.py` - 影子财政大臣 Agent 支持策略框架

### 流程改造

- [x] `workflow.py` - 添加实验模式 `run_experiment_debate()` 和 `build_experiment_graph()`
- [x] `config.py` - 添加 `EXPERIMENT_CONFIG` 配置

### 文档

- [x] `EXPERIMENT_README.md` - 完整使用说明

---

## 🔲 待完成 (Phase 2)

### 新增策略实现

- [ ] `strategies/a_star_strategy.py` - A*搜索策略
  - 用途：搜索最优论证路径和发言顺序
  - 复用：`algorithms/a_star.py`

- [ ] `strategies/genetic_strategy.py` - 遗传算法策略
  - 用途：进化政策立场和辩论策略组合
  - 复用：`algorithms/genetic.py`

- [ ] `strategies/heuristic_search_strategy.py` - 启发式搜索策略
  - 用途：实时辩论应对和快速策略选择
  - 复用：`algorithms/heuristic_search.py`

### 可选增强

- [ ] 结果可视化（雷达图、柱状图）
- [ ] 学习曲线绘制（如果需要展示 Q-Learning 学习过程）
- [ ] 统计显著性检验

---

## 📐 关键设计决策

### 实验流程

```
辩论流程 (6 轮):
  Speaker → PM → LO → Chancellor → Shadow Chancellor → PM → LO → Vote
   ↓                                              ↓
 开场 (评估)                                    总结 (评估)
```

### 评估设计

- **评估时机**: 辩论结束后统一评估
- **评估对象**: 开场（第 1 轮）和总结（最后 1 轮）
- **权重分配**: 开场 50% + 总结 50%
- **评估维度**: 5 个维度各占 20%（逻辑、论据、说服力、反驳、表达）

### 胜负判定

- **优先级 1**: 投票结果（如果有）
- **优先级 2**: 综合评分（≥7.0 为 WIN，否则 LOSS）

### 策略影响方式

**策略框架 + LLM 生成**（而非直接生成内容）：

```python
StrategyArgument(
    strategy_type="aggressive_attack",
    key_arguments=["攻击对方弱点", "质疑对方记录"],
    tone="confrontational",
    confidence=0.8,
    focus_areas=["批判", "质疑"]
)

# LLM 根据框架生成完整发言
```

---

## 🚀 使用方法

### 运行实验

```bash
# 运行所有策略对比（默认 5 次）
python run_experiment.py --topic "是否应该增加 NHS 预算" --strategies all --runs 5

# 运行单个策略
python run_experiment.py --topic "经济政策" --strategies baseline --runs 3

# 指定输出目录
python run_experiment.py --topic "移民政策" --strategies all --runs 5 --output results/my_experiment
```

### 输出结果

```
results/experiment_YYYYMMDD_HHMMSS/
├── results.csv           # 主要统计数据
├── detailed_scores.csv   # 详细维度得分
├── metadata.json         # 实验元数据
└── debates/
    ├── debate_baseline_run1.md
    ├── debate_heuristic_rule_run1.md
    └── ...
```

---

## 📁 项目结构

```
parliament-sim/
├── strategies/                    # 策略层（新增）
│   ├── __init__.py
│   ├── base_strategy.py          # 抽象接口
│   ├── baseline_strategy.py      # 纯 LLM 对照组
│   └── heuristic_rule_strategy.py # 启发式规则
│
├── evaluation/                    # 评估系统（新增）
│   ├── __init__.py
│   └── evaluator.py              # LLM 裁判
│
├── experiments/                   # 实验框架（新增）
│   ├── __init__.py
│   ├── runner.py                 # 实验运行器
│   └── results.py                # 结果数据
│
├── run_experiment.py             # 实验入口（新增）
├── PROJECT_STATUS.md             # 本文件（新增）
├── EXPERIMENT_README.md          # 详细使用说明（新增）
│
├── workflow.py                   # 改造：添加实验模式
├── config.py                     # 改造：添加实验配置
│
├── agents/                       # 改造：支持策略注入
│   ├── pm.py
│   ├── lo.py
│   ├── chancellor.py
│   └── shadow_chancellor.py
│
├── algorithms/                   # 现有算法（Phase 2 复用）
│   ├── a_star.py
│   ├── genetic.py
│   ├── heuristic_rules.py
│   ├── heuristic_search.py
│   └── q_learning.py
│
└── results/                      # 输出目录（运行时生成）
```

---

## 🔧 依赖项

```bash
pip install -r requirements.txt
```

核心依赖：
- `langchain` - LLM 编排框架
- `langgraph` - 辩论流程控制
- `langchain-ollama` - 本地 LLM 支持
- `pandas` - 数据分析

---

## 📝 下一步行动

### 继续 Phase 2 实现

1. 实现 `AStarStrategy` - 复用 `algorithms/a_star.py`
2. 实现 `GeneticStrategy` - 复用 `algorithms/genetic.py`
3. 实现 `HeuristicSearchStrategy` - 复用 `algorithms/heuristic_search.py`
4. 在 `run_experiment.py` 中注册新策略
5. 测试完整对比实验

### 验证 Phase 1

1. 安装依赖
2. 确认 Ollama 正在运行且已拉取 `qwen2.5:7b`
3. 运行单次实验验证框架
4. 检查 CSV 输出格式
5. 检查辩论记录保存

---

## 📊 预期输出示例

```
╔══════════════════════════════════════════════════════════╗
║           算法对比实验报告                               ║
╠══════════════════════════════════════════════════════════╣
║ 实验配置                                                 ║
║   议题：是否应该增加 NHS 预算                             ║
║   运行次数：5                                            ║
║   策略：baseline, heuristic_rule                         ║
╠══════════════════════════════════════════════════════════╣
║ 平均得分对比                                             ║
║                                                          ║
║   baseline       : 6.84                                  ║
║   heuristic_rule : 7.38                                  ║
╠══════════════════════════════════════════════════════════╣
║ 胜率统计                                                 ║
║   baseline       : 40.0% (2/5)                           ║
║   heuristic_rule : 60.0% (3/5)                           ║
╚══════════════════════════════════════════════════════════╝
```

---

## 📞 联系信息

如需继续开发，请告诉 AI 助手：
> "继续实现议会模拟实验的 Phase 2，需要添加 A*搜索、遗传算法和启发式搜索三种策略"

AI 助手可以读取本文件了解项目上下文。
