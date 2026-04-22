"""Single debate demo entry point."""

import argparse
import sys

from config import DEFAULT_TOPIC, LLM_CONFIG
from evaluation.evaluator import DebateEvaluator
from evaluation.voting import VotingPanel
from run_experiment import create_llm, make_strategies
from simulation.engine import run_debate
from simulation.roles import ROLES


def main() -> None:
    _utf8()
    parser = argparse.ArgumentParser(description="Run one parliament-style multi-agent debate.")
    parser.add_argument("--topic", "-t", default=DEFAULT_TOPIC)
    parser.add_argument("--strategy", "-s", default="heuristic_rule", choices=["baseline", "heuristic_rule", "genetic"])
    parser.add_argument("--turns", "-n", type=int, default=7)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--max-tokens", type=int, default=180)
    parser.add_argument("--request-timeout", type=int, default=120)
    parser.add_argument("--evaluator", choices=["heuristic", "llm"], default="heuristic")
    parser.add_argument("--mock-llm", action="store_true")
    args = parser.parse_args()

    llm = create_llm(args.temperature, args.max_tokens, args.request_timeout, args.mock_llm)
    strategy = make_strategies(args.strategy)[0]
    print(f"Model: {'mock' if args.mock_llm else LLM_CONFIG['model']}", flush=True)
    print(f"Strategy: {strategy.name()}", flush=True)
    print(f"Topic: {args.topic}", flush=True)
    print(f"Timeout: {args.request_timeout}s\n", flush=True)
    state = run_debate(
        llm,
        args.topic,
        strategy,
        max_turns=args.turns,
        on_turn=_print_turn,
        on_turn_start=_print_turn_start,
    )
    evaluation = DebateEvaluator(llm=llm, mode=args.evaluator).evaluate(state.records, args.topic)
    vote = VotingPanel().vote(evaluation)

    print(flush=True)
    print("Evaluation", flush=True)
    print(f"- Government score: {evaluation['government']['overall']:.2f}", flush=True)
    print(f"- Opposition score: {evaluation['opposition']['overall']:.2f}", flush=True)
    print(f"- Score winner: {evaluation['comparison']['winner']}", flush=True)
    print(flush=True)
    print("Final vote", flush=True)
    print(
        f"- Government: {vote['government_votes']} | "
        f"Opposition: {vote['opposition_votes']} | "
        f"Abstain: {vote['abstentions']}",
        flush=True,
    )
    print(f"- Winner: {vote['winner']}", flush=True)
    for ballot in vote["ballots"]:
        print(f"  {ballot['voter']}: {ballot['vote']} - {ballot['reason']}", flush=True)


def _print_turn(record) -> None:
    role = ROLES[record.role]
    print(f"\n[Turn {record.turn}] {role.title} ({record.side})", flush=True)
    print(f"Strategy move: {record.strategy}", flush=True)
    print(record.content.strip() or "[empty speech]", flush=True)


def _print_turn_start(turn: int, role_id: str, strategy_move: str) -> None:
    role = ROLES[role_id]
    print(f"\nGenerating Turn {turn}: {role.title} ({role.side})", flush=True)
    print(f"Strategy move: {strategy_move}", flush=True)


def _utf8() -> None:
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


if __name__ == "__main__":
    main()
