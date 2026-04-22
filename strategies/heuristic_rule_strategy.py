"""Rule-based strategy for transparent, explainable debate tactics."""

from typing import Dict

from strategies.base_strategy import DebateStrategy, StrategyAdvice


class HeuristicRuleStrategy(DebateStrategy):
    def name(self) -> str:
        return "heuristic_rule"

    def advise(self, role: str, topic: str, context: Dict) -> StrategyAdvice:
        turn = int(context.get("turn", 0))
        opponent_spoke = bool(context.get("opponent_last"))
        is_government = context.get("side") == "government"

        if turn <= 1:
            return StrategyAdvice(
                name="clear_opening",
                goal="frame the issue and set a clear test for success",
                tone="confident and accessible",
                moves=["state the central claim", "name one measurable outcome"],
                evidence_need="medium",
            )

        if opponent_spoke:
            return StrategyAdvice(
                name="direct_rebuttal",
                goal="answer the strongest opposing point before advancing your own",
                tone="firm but parliamentary",
                moves=["quote or paraphrase the opposing claim", "explain why it fails", "offer a better policy test"],
                evidence_need="high",
            )

        if is_government:
            return StrategyAdvice(
                name="delivery_record",
                goal="defend feasibility and implementation",
                tone="measured",
                moves=["explain delivery mechanism", "address fiscal trade-offs"],
                evidence_need="high",
            )

        return StrategyAdvice(
            name="accountability_attack",
            goal="press the government on cost, timelines, and trade-offs",
            tone="challenging",
            moves=["identify a gap", "ask for accountability", "contrast with an alternative"],
            evidence_need="high",
        )
