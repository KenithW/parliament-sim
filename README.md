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
  react_strategy.py
  monte_carlo_strategy.py
  bandit_strategy.py

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
- `react`: observes the last opposing claim, reasons about it, then selects a response action.
- `monte_carlo`: samples candidate tactical moves and chooses the highest expected value.
- `bandit`: learns within one experiment run which tactical moves receive better rewards.

## Memory

The simulation uses short-term memory inside each debate:

- recent transcript
- current phase: opening, middle, closing
- last opposing speech
- government and opposition speech history
- recent strategy moves

This is enough for `react`, `monte_carlo`, and `genetic`. `bandit` also keeps
run-level memory during one experiment process, so it should be tested with
multiple runs.

## Quick Start

Use the mock LLM to test the pipeline without Ollama:

```bash
python main.py --mock-llm
python run_experiment.py --mock-llm --strategy heuristic_rule --runs 2
```

Use Ollama for real generation:

```bash
pip install -r requirements.txt
ollama pull phi:latest
python run_experiment.py --strategy heuristic_rule --runs 3 --topic "Should NHS funding be increased?"
```

## Running Each Method

Run one algorithm per experiment folder. This is intentional: different
algorithms need different parameters, and some need many runs to show their
effect clearly.

Use `--mock-llm` first if you only want to check the pipeline quickly. Remove
`--mock-llm` when running the real Ollama model.

### 1. Baseline

No algorithmic guidance. This is the control group.

```bash
python run_experiment.py --strategy baseline --runs 5 --turns 7 --output results/baseline_exp
```

Use this to answer: how good is plain role-prompt multi-agent debate without a
strategy algorithm?

### 2. Heuristic Rule

Uses fixed rules based on debate phase, side, and opponent response.

```bash
python run_experiment.py --strategy heuristic_rule --runs 5 --turns 7 --output results/heuristic_rule_exp
```

Use this to test whether simple explainable rules improve debate quality over
baseline.

### 3. Genetic

Selects and mutates tactical advice templates inside each turn.

```bash
python run_experiment.py --strategy genetic --runs 5 --turns 7 --output results/genetic_exp
```

Use this to test whether lightweight evolutionary search produces better
tactical choices.

### 4. ReAct

Observes the previous opposing speech, identifies the type of challenge, then
chooses a response action.

```bash
python run_experiment.py --strategy react --runs 5 --turns 7 --output results/react_exp
```

Use this to test whether explicit observe-reason-act behavior improves
multi-agent interaction.

### 5. Monte Carlo

Samples candidate tactical moves and chooses the one with the best estimated
value.

```bash
python run_experiment.py --strategy monte_carlo --runs 5 --turns 7 --monte-carlo-samples 20 --output results/monte_carlo_exp
```

Main parameter:

- `--monte-carlo-samples`: number of samples used to estimate each action. More samples are slower but more stable.

Use this to test whether simulated action selection improves debate outcomes.

### 6. Bandit

Learns which tactical moves get better rewards during the same experiment run.
Run more trials for this method.

```bash
python run_experiment.py --strategy bandit --runs 20 --turns 7 --bandit-epsilon 0.25 --output results/bandit_exp
```

Main parameter:

- `--bandit-epsilon`: exploration rate. Higher means more exploration; lower means more exploitation.

Use this to test whether repeated reward feedback helps the system prefer
better debate actions.

### Showing Live Debate

Add `--show-debate` to print each agent speech while the experiment runs:

```bash
python run_experiment.py --strategy react --runs 1 --turns 7 --show-debate
```

### Suggested Evaluation Sequence

Run these commands separately, then compare the CSV files:

```bash
python run_experiment.py --strategy baseline --runs 5 --turns 7 --output results/baseline_exp
python run_experiment.py --strategy heuristic_rule --runs 5 --turns 7 --output results/heuristic_rule_exp
python run_experiment.py --strategy genetic --runs 5 --turns 7 --output results/genetic_exp
python run_experiment.py --strategy react --runs 5 --turns 7 --output results/react_exp
python run_experiment.py --strategy monte_carlo --runs 5 --turns 7 --monte-carlo-samples 20 --output results/monte_carlo_exp
python run_experiment.py --strategy bandit --runs 20 --turns 7 --bandit-epsilon 0.25 --output results/bandit_exp
```

## Outputs

Each experiment writes:

- `<strategy>_runs.csv`: one CSV per algorithm, easier for later statistics
- `all_runs.csv`: combined runs if needed
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

For clean evaluation, run one strategy per experiment folder. Compare the
resulting per-strategy CSV files later.

That makes the comparison clean and easy to explain.
