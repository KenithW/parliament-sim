"""Run the same debate flow under multiple strategies."""

import time
from datetime import datetime
from typing import List

from config import OUTPUT_ROOT
from evaluation.evaluator import DebateEvaluator
from evaluation.voting import VotingPanel
from experiments.results import ExperimentResults
from simulation.engine import run_debate
from simulation.roles import ROLES
from strategies.base_strategy import DebateStrategy


class ExperimentRunner:
    def __init__(self, strategies: List[DebateStrategy], llm, evaluator_mode: str = "heuristic"):
        self.strategies = strategies
        self.llm = llm
        self.evaluator = DebateEvaluator(llm=llm, mode=evaluator_mode)
        self.voting_panel = VotingPanel()
        self.evaluator_mode = evaluator_mode

    def run_comparison(
        self,
        topic: str,
        num_runs: int = 3,
        output_dir: str = None,
        max_turns: int = 7,
        show_debate: bool = False,
        **_,
    ) -> ExperimentResults:
        if output_dir is None:
            output_dir = f"{OUTPUT_ROOT}/experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        results = ExperimentResults(topic=topic)
        print(f"Topic: {topic}", flush=True)
        print(f"Strategies: {', '.join(s.name() for s in self.strategies)}", flush=True)
        print(f"Runs per strategy: {num_runs}", flush=True)
        print(f"Evaluator: {self.evaluator_mode}", flush=True)
        print(f"Output: {output_dir}\n", flush=True)

        for strategy in self.strategies:
            for run_number in range(1, num_runs + 1):
                start = time.perf_counter()
                if show_debate:
                    print(f"\n--- {strategy.name()} run {run_number}: live debate ---", flush=True)
                state = run_debate(
                    self.llm,
                    topic,
                    strategy,
                    max_turns=max_turns,
                    on_turn=_print_turn if show_debate else None,
                    on_turn_start=_print_turn_start if show_debate else None,
                )
                duration = time.perf_counter() - start
                evaluation = self.evaluator.evaluate(state.records, topic)
                vote = self.voting_panel.vote(evaluation)
                transcript = results.save_transcript(
                    state.records,
                    strategy.name(),
                    run_number,
                    output_dir,
                    evaluation=evaluation,
                    vote=vote,
                )

                row = {
                    "experiment_id": results.experiment_id,
                    "strategy": strategy.name(),
                    "run": run_number,
                    "run_number": run_number,
                    "topic": topic,
                    "score_winner": evaluation["comparison"]["winner"],
                    "winner": vote["winner"],
                    "government_score": round(evaluation["government"]["overall"], 3),
                    "opposition_score": round(evaluation["opposition"]["overall"], 3),
                    "government_margin": round(evaluation["comparison"]["margin"], 3),
                    "total_quality": round(evaluation["comparison"]["total_quality"], 3),
                    "government_votes": vote["government_votes"],
                    "opposition_votes": vote["opposition_votes"],
                    "abstentions": vote["abstentions"],
                    "vote_margin": vote["vote_margin"],
                    "duration_s": round(duration, 3),
                    "turns": state.turn_count,
                    "transcript": transcript,
                }
                results.add(row)
                print(
                    f"{strategy.name()} run {run_number}: "
                    f"quality={row['total_quality']:.2f}, "
                    f"margin={row['government_margin']:+.2f}, "
                    f"vote={row['government_votes']}-{row['opposition_votes']}-{row['abstentions']}, "
                    f"winner={row['winner']}",
                    flush=True,
                )

        results.save(output_dir)
        print("\n" + results.summary(), flush=True)
        return results


def _print_turn(record) -> None:
    role = ROLES[record.role]
    print(f"\n[Turn {record.turn}] {role.title} ({record.side})", flush=True)
    print(f"Strategy move: {record.strategy}", flush=True)
    print(record.content.strip() or "[empty speech]", flush=True)


def _print_turn_start(turn: int, role_id: str, strategy_move: str) -> None:
    role = ROLES[role_id]
    print(f"\nGenerating Turn {turn}: {role.title} ({role.side})", flush=True)
    print(f"Strategy move: {strategy_move}", flush=True)
