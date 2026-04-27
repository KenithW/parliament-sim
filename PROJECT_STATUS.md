# Project Status

Current goal: compare strategy algorithms for multi-agent parliamentary dialogue.

## Kept

- Fixed multi-agent debate flow.
- Six strategy algorithms: baseline, heuristic rule, genetic, react, monte carlo, bandit.
- Short-term debate memory for strategy decisions.
- Shared evaluator.
- Final voting panel with five fixed voter profiles.
- Repeated experiment runner.
- CSV summaries and detailed transcripts.

## Removed

- LangGraph workflow.
- PMQs mode.
- Voting system.
- Separate agent modules.
- Standalone algorithm demos.
- Research-suite wrapper.

## Main Commands

```bash
python main.py --mock-llm
python run_experiment.py --mock-llm --strategy heuristic_rule --runs 2
python test_all_algorithms.py
```

`main.py` now prints the debate turn by turn, including strategy moves,
evaluation scores, and the final vote.

Use one strategy per experiment run. For example, use `--runs 20` for `bandit`
so its run-level memory can learn from rewards.
