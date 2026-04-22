"""Strategy interface.

A strategy does not write the speech. It gives the speaking agent tactical
guidance, while the LLM still produces the final utterance.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StrategyAdvice:
    name: str
    goal: str
    tone: str
    moves: List[str] = field(default_factory=list)
    evidence_need: str = "medium"


class DebateStrategy(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def advise(self, role: str, topic: str, context: Dict) -> StrategyAdvice:
        pass

    def generate_argument(self, role: str, topic: str, context: Dict) -> StrategyAdvice:
        """Backward-compatible alias used by older callers."""
        return self.advise(role, topic, context)
