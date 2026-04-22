# Project Status

Current goal: compare strategy algorithms for multi-agent parliamentary dialogue.

## Kept

- Fixed multi-agent debate flow.
- Three strategy algorithms: baseline, heuristic rule, genetic.
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
python run_experiment.py --mock-llm --runs 2
python test_all_algorithms.py
```

`main.py` now prints the debate turn by turn, including strategy moves,
evaluation scores, and the final vote.
