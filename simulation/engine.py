"""Fixed multi-agent debate flow."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List

from config import DEBATE_FLOW
from simulation.roles import ROLES
from strategies.base_strategy import DebateStrategy, StrategyAdvice


@dataclass
class DebateRecord:
    turn: int
    role: str
    side: str
    content: str
    strategy: str

    @property
    def speaker(self) -> str:
        return self.role


@dataclass
class DebateState:
    topic: str
    records: List[DebateRecord] = field(default_factory=list)

    @property
    def turn_count(self) -> int:
        return len(self.records)


def run_debate(
    llm,
    topic: str,
    strategy: DebateStrategy,
    max_turns: int = 7,
    on_turn: Callable[[DebateRecord], None] = None,
    on_turn_start: Callable[[int, str, str], None] = None,
) -> DebateState:
    state = DebateState(topic=topic)
    flow = DEBATE_FLOW[: max(1, max_turns)]

    for turn, role_id in enumerate(flow):
        role = ROLES[role_id]
        if role.side == "neutral":
            content = f"Order. The House will debate: {topic}"
            advice_name = "chairing"
        else:
            context = _build_context(state, role.side, turn)
            advice = strategy.advise(role=role_id, topic=topic, context=context)
            if on_turn_start:
                on_turn_start(turn, role_id, advice.name)
            content = _invoke_text(llm, _build_prompt(topic, role_id, advice, state))
            advice_name = advice.name

        record = DebateRecord(
            turn=turn,
            role=role_id,
            side=role.side,
            content=content,
            strategy=advice_name,
        )
        state.records.append(record)
        if on_turn:
            on_turn(record)

    return state


def _build_context(state: DebateState, side: str, turn: int) -> Dict:
    opponent_last = ""
    for record in reversed(state.records):
        if record.side not in {side, "neutral"}:
            opponent_last = record.content
            break
    government_records = [record for record in state.records if record.side == "government"]
    opposition_records = [record for record in state.records if record.side == "opposition"]
    strategy_history = [record.strategy for record in state.records if record.side != "neutral"]
    return {
        "turn": turn,
        "phase": _phase(turn),
        "side": side,
        "history": state.records,
        "opponent_last": opponent_last,
        "government_speeches": government_records,
        "opposition_speeches": opposition_records,
        "strategy_history": strategy_history,
        "memory_summary": _memory_summary(government_records, opposition_records, strategy_history),
    }


def _build_prompt(topic: str, role_id: str, advice: StrategyAdvice, state: DebateState) -> str:
    role = ROLES[role_id]
    history = _history_snippet(state.records)
    moves = "; ".join(advice.moves) if advice.moves else "use your role naturally"
    return f"""
You are a participant in a UK parliament-style multi-agent debate.

Topic: {topic}
Role: {role.title}
Side: {role.side}
Party: {role.party}
Role stance: {role.stance}

Recent debate history:
{history}

Strategy advice:
- tactic: {advice.name}
- goal: {advice.goal}
- tone: {advice.tone}
- moves: {moves}
- evidence need: {advice.evidence_need}

Write one concise parliamentary speech, 90-150 words.
Address the previous opposing point when there is one.
Stay in role and avoid meta commentary about the strategy.
""".strip()


def _history_snippet(records: List[DebateRecord], limit: int = 4) -> str:
    if not records:
        return "No previous speeches."
    lines = []
    for record in records[-limit:]:
        title = ROLES[record.role].title
        text = " ".join(record.content.split())[:220]
        lines.append(f"- {title}: {text}")
    return "\n".join(lines)


def _phase(turn: int) -> str:
    if turn <= 1:
        return "opening"
    if turn >= len(DEBATE_FLOW) - 2:
        return "closing"
    return "middle"


def _memory_summary(government_records: List[DebateRecord], opposition_records: List[DebateRecord], strategy_history: List[str]) -> str:
    return (
        f"government_speeches={len(government_records)}, "
        f"opposition_speeches={len(opposition_records)}, "
        f"recent_strategy_moves={strategy_history[-4:]}"
    )


def _invoke_text(llm, prompt: str) -> str:
    response = llm.invoke(prompt)
    if hasattr(response, "content"):
        return str(response.content).strip()
    return str(response).strip()
