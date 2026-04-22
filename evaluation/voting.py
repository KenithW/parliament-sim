"""Voting stage after the debate.

Voters are lightweight judging agents with fixed preferences. They do not join
the debate; they read the finished transcript and decide which side persuaded
them.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Voter:
    name: str
    priority: str
    weights: Dict[str, float]


VOTERS = [
    Voter(
        name="Fiscal Conservative",
        priority="cost control and deliverability",
        weights={"evidence": 0.35, "coherence": 0.25, "role_consistency": 0.20, "persuasiveness": 0.15, "rebuttal": 0.05},
    ),
    Voter(
        name="Public Service Advocate",
        priority="public impact and fairness",
        weights={"persuasiveness": 0.30, "evidence": 0.25, "coherence": 0.20, "rebuttal": 0.15, "role_consistency": 0.10},
    ),
    Voter(
        name="Swing MP",
        priority="balanced, credible argument",
        weights={"coherence": 0.25, "persuasiveness": 0.25, "evidence": 0.20, "rebuttal": 0.15, "role_consistency": 0.15},
    ),
    Voter(
        name="Evidence-focused MP",
        priority="specific evidence and rebuttal quality",
        weights={"evidence": 0.40, "rebuttal": 0.25, "coherence": 0.20, "persuasiveness": 0.10, "role_consistency": 0.05},
    ),
    Voter(
        name="Procedural MP",
        priority="parliamentary role discipline",
        weights={"role_consistency": 0.35, "coherence": 0.25, "persuasiveness": 0.15, "evidence": 0.15, "rebuttal": 0.10},
    ),
]


class VotingPanel:
    def __init__(self, voters: List[Voter] = None):
        self.voters = voters or VOTERS

    def vote(self, evaluation: Dict) -> Dict:
        ballots = []
        government_votes = 0
        opposition_votes = 0
        abstentions = 0

        for voter in self.voters:
            gov_score = _weighted_score(evaluation["government"], voter.weights)
            opp_score = _weighted_score(evaluation["opposition"], voter.weights)
            margin = gov_score - opp_score

            if abs(margin) < 0.15:
                choice = "abstain"
                abstentions += 1
            elif margin > 0:
                choice = "government"
                government_votes += 1
            else:
                choice = "opposition"
                opposition_votes += 1

            ballots.append(
                {
                    "voter": voter.name,
                    "priority": voter.priority,
                    "vote": choice,
                    "government_score": round(gov_score, 3),
                    "opposition_score": round(opp_score, 3),
                    "reason": _reason(voter, choice, margin),
                }
            )

        if government_votes > opposition_votes:
            winner = "government"
        elif opposition_votes > government_votes:
            winner = "opposition"
        else:
            winner = "tie"

        return {
            "winner": winner,
            "government_votes": government_votes,
            "opposition_votes": opposition_votes,
            "abstentions": abstentions,
            "vote_margin": government_votes - opposition_votes,
            "ballots": ballots,
        }


def _weighted_score(scores: Dict, weights: Dict[str, float]) -> float:
    return sum(float(scores.get(metric, 5.0)) * weight for metric, weight in weights.items())


def _reason(voter: Voter, choice: str, margin: float) -> str:
    if choice == "abstain":
        return f"Both sides were close for this voter's priority: {voter.priority}."
    side = "government" if margin > 0 else "opposition"
    return f"The {side} side better satisfied this voter's priority: {voter.priority}."
