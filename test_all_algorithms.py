"""Smoke tests for the simplified strategy-comparison pipeline."""

from evaluation.evaluator import DebateEvaluator
from evaluation.voting import VotingPanel
from run_experiment import make_strategies
from simulation.engine import run_debate
from tools.mock_llm import MockLLM


def test_strategy_registry():
    strategies = make_strategies("all")
    assert [strategy.name() for strategy in strategies] == [
        "baseline",
        "heuristic_rule",
        "genetic",
        "react",
        "monte_carlo",
        "bandit",
    ]


def test_single_debate_runs():
    strategy = make_strategies("heuristic_rule")[0]
    state = run_debate(MockLLM(), "Should NHS funding be increased?", strategy, max_turns=5)
    assert state.turn_count == 5
    assert any(record.side == "government" for record in state.records)
    assert any(record.side == "opposition" for record in state.records)


def test_evaluator_returns_comparison():
    strategy = make_strategies("baseline")[0]
    state = run_debate(MockLLM(), "Should NHS funding be increased?", strategy, max_turns=5)
    result = DebateEvaluator(mode="heuristic").evaluate(state.records, state.topic)
    assert result["comparison"]["winner"] in {"government", "opposition", "tie"}
    assert result["comparison"]["total_quality"] > 0


def test_voting_panel_returns_ballots():
    strategy = make_strategies("heuristic_rule")[0]
    state = run_debate(MockLLM(), "Should NHS funding be increased?", strategy, max_turns=5)
    evaluation = DebateEvaluator(mode="heuristic").evaluate(state.records, state.topic)
    vote = VotingPanel().vote(evaluation)
    assert vote["winner"] in {"government", "opposition", "tie"}
    assert len(vote["ballots"]) == 5


if __name__ == "__main__":
    test_strategy_registry()
    test_single_debate_runs()
    test_evaluator_returns_comparison()
    test_voting_panel_returns_ballots()
    print("All smoke tests passed.")
