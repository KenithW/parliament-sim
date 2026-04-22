# Parliament Strategy Experiment

This project has one purpose:

> Run the same multi-agent parliament debate with different strategy algorithms, then compare which strategy produces better dialogue outcomes.

It is intentionally small. The parliament flow is fixed; the experimental variable is the strategy.

## Structure

```text
main.py                 # run one demo debate
run_experiment.py       # compare strategies across repeated runs
config.py               # model, flow, and scoring settings

simulation/
  roles.py              # role definitions
  engine.py             # fixed multi-agent debate flow

strategies/
  baseline_strategy.py  # no algorithmic guidance
  heuristic_rule_strategy.py
  genetic_strategy.py

evaluation/
  evaluator.py          # shared scoring logic
  voting.py             # final voter panel

experiments/
  runner.py             # repeated strategy comparison
  results.py            # CSV and transcript output
```

## Strategies

- `baseline`: lets the LLM respond naturally from the role prompt.
- `heuristic_rule`: uses transparent rules to choose opening, rebuttal, delivery, or accountability tactics.
- `genetic`: evolves lightweight tactical advice templates before each speech.

## Quick Start

Use the mock LLM to test the pipeline without Ollama:

```bash
python main.py --mock-llm
python run_experiment.py --mock-llm --runs 2
```

Use Ollama for real generation:

```bash
pip install -r requirements.txt
ollama pull qwen3.5:4b
python run_experiment.py --strategies all --runs 3 --topic "Should NHS funding be increased?"
```

## Outputs

Each experiment writes:

- `runs.csv`: one row per strategy run
- `summary.csv`: aggregated comparison by strategy
- `metadata.json`: experiment setup
- `transcripts/`: full debate transcripts with strategy moves, scores, and vote details

The key comparison fields are:

- `total_quality`
- `government_score`
- `opposition_score`
- `government_margin`
- `winner`
- `government_votes`
- `opposition_votes`
- `abstentions`
- `duration_s`

## Debate And Vote

The demo command shows the full debate:

```bash
python main.py --mock-llm --strategy heuristic_rule --turns 7
```

For each turn it prints:

- role and side
- selected strategy move
- generated speech

After the debate, a fixed voter panel casts ballots:

- Fiscal Conservative
- Public Service Advocate
- Swing MP
- Evidence-focused MP
- Procedural MP

The vote winner is the main final result. The score winner is still saved, so
you can compare "quality score" against "which side won the simulated vote".

## Research Design

Keep these fixed:

- topic
- role list
- debate turn order
- LLM model
- number of turns
- evaluator

Change only:

- strategy algorithm

That makes the comparison clean and easy to explain.
