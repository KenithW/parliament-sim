"""Shared debate evaluator used by every strategy."""

import json
import re
from typing import Dict, List

from config import SCORING_DIMENSIONS


class DebateEvaluator:
    def __init__(self, llm=None, mode: str = "heuristic"):
        self.llm = llm
        self.mode = mode

    def evaluate(self, records: List, topic: str) -> Dict:
        if self.mode == "llm" and self.llm is not None:
            return self._llm_evaluate(records, topic)
        return self._heuristic_evaluate(records)

    def evaluate_debate(self, debate_records: List, topic: str) -> Dict:
        result = self.evaluate(debate_records, topic)
        return {
            "opening": result["government"],
            "closing": result["opposition"],
            "overall": {
                **result["comparison"],
                "overall_score": result["comparison"]["margin"] + 5.0,
                "overall_comment": result["comparison"]["winner"],
            },
        }

    def _heuristic_evaluate(self, records: List) -> Dict:
        gov_text = " ".join(r.content for r in records if r.side == "government")
        opp_text = " ".join(r.content for r in records if r.side == "opposition")
        gov = self._score_text(gov_text)
        opp = self._score_text(opp_text)
        return self._compare(gov, opp)

    def _score_text(self, text: str) -> Dict:
        lower = text.lower()
        length_score = min(2.0, len(text) / 700)
        evidence_hits = _count(lower, ["data", "evidence", "report", "cost", "funding", "%", "study"])
        rebuttal_hits = _count(lower, ["however", "but", "fails", "wrong", "claim", "opposition", "government"])
        policy_hits = _count(lower, ["because", "therefore", "deliver", "plan", "policy", "outcome"])
        role_hits = _count(lower, ["government", "opposition", "minister", "speaker", "house"])

        scores = {
            "coherence": _clamp(4.5 + length_score + policy_hits * 0.45),
            "evidence": _clamp(4.0 + length_score * 0.5 + evidence_hits * 0.7),
            "rebuttal": _clamp(3.8 + rebuttal_hits * 0.8),
            "persuasiveness": _clamp(4.2 + policy_hits * 0.35 + rebuttal_hits * 0.35 + length_score),
            "role_consistency": _clamp(4.5 + role_hits * 0.6),
        }
        scores["overall"] = sum(scores[d] for d in SCORING_DIMENSIONS) / len(SCORING_DIMENSIONS)
        return scores

    def _llm_evaluate(self, records: List, topic: str) -> Dict:
        transcript = "\n".join(f"{r.side.upper()} {r.role}: {r.content}" for r in records)
        prompt = f"""
Score this parliament-style multi-agent debate.

Topic: {topic}
Transcript:
{transcript}

Return JSON only:
{{
  "government": {{"coherence": 1-10, "evidence": 1-10, "rebuttal": 1-10, "persuasiveness": 1-10, "role_consistency": 1-10}},
  "opposition": {{"coherence": 1-10, "evidence": 1-10, "rebuttal": 1-10, "persuasiveness": 1-10, "role_consistency": 1-10}}
}}
""".strip()
        try:
            response = self.llm.invoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            data = json.loads(_extract_json(raw))
            gov = _normalize_scores(data["government"])
            opp = _normalize_scores(data["opposition"])
            return self._compare(gov, opp)
        except Exception:
            return self._heuristic_evaluate(records)

    def _compare(self, gov: Dict, opp: Dict) -> Dict:
        gov["overall"] = sum(gov[d] for d in SCORING_DIMENSIONS) / len(SCORING_DIMENSIONS)
        opp["overall"] = sum(opp[d] for d in SCORING_DIMENSIONS) / len(SCORING_DIMENSIONS)
        margin = gov["overall"] - opp["overall"]
        winner = "government" if margin > 0 else "opposition" if margin < 0 else "tie"
        return {
            "government": gov,
            "opposition": opp,
            "comparison": {
                "winner": winner,
                "margin": margin,
                "total_quality": (gov["overall"] + opp["overall"]) / 2,
            },
        }


def _count(text: str, needles: List[str]) -> int:
    return sum(text.count(item) for item in needles)


def _clamp(value: float) -> float:
    return max(1.0, min(10.0, value))


def _extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return match.group(0) if match else text


def _normalize_scores(scores: Dict) -> Dict:
    return {dimension: _clamp(float(scores.get(dimension, 5.0))) for dimension in SCORING_DIMENSIONS}
