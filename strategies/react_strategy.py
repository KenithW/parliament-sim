"""ReAct-style strategy: observe the last opposing claim, then act."""

from typing import Dict

from strategies.base_strategy import DebateStrategy, StrategyAdvice


class ReActStrategy(DebateStrategy):
    def name(self) -> str:
        return "react"

    def advise(self, role: str, topic: str, context: Dict) -> StrategyAdvice:
        opponent_last = context.get("opponent_last", "").lower()
        phase = context.get("phase", "middle")

        if phase == "opening":
            return StrategyAdvice(
                name="observe_frame_act",
                goal="frame the issue while anticipating the strongest objection",
                tone="clear and deliberate",
                moves=["state position", "identify likely objection", "set evaluation criteria"],
                evidence_need="medium",
            )

        if any(word in opponent_last for word in ("cost", "funding", "tax", "budget")):
            return StrategyAdvice(
                name="react_cost_rebuttal",
                goal="respond directly to the opponent's cost challenge",
                tone="precise",
                moves=["acknowledge cost concern", "explain funding logic", "compare fiscal risk"],
                evidence_need="high",
            )

        if any(word in opponent_last for word in ("evidence", "data", "report", "review")):
            return StrategyAdvice(
                name="react_evidence_push",
                goal="answer the demand for proof with concrete evidence standards",
                tone="evidence-focused",
                moves=["name evidence threshold", "explain measurement", "challenge weak evidence"],
                evidence_need="high",
            )

        if any(word in opponent_last for word in ("fair", "household", "public", "service")):
            return StrategyAdvice(
                name="react_values_response",
                goal="connect the argument to fairness and public impact",
                tone="empathetic but firm",
                moves=["recognize affected citizens", "state fairness test", "contrast outcomes"],
                evidence_need="medium",
            )

        return StrategyAdvice(
            name="react_general_rebuttal",
            goal="answer the previous claim and move the debate forward",
            tone="firm but parliamentary",
            moves=["summarize opponent claim", "identify weakness", "advance alternative test"],
            evidence_need="medium",
        )
