"""Minimal role definitions for the multi-agent parliament simulation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    id: str
    title: str
    side: str
    party: str
    stance: str


ROLES = {
    "speaker": Role(
        id="speaker",
        title="Speaker",
        side="neutral",
        party="Parliament",
        stance="Maintain order and introduce the debate without taking a side.",
    ),
    "pm": Role(
        id="pm",
        title="Prime Minister",
        side="government",
        party="Government",
        stance="Defend the government's policy as practical, affordable, and responsible.",
    ),
    "minister": Role(
        id="minister",
        title="Cabinet Minister",
        side="government",
        party="Government",
        stance="Support the Prime Minister with implementation detail and evidence.",
    ),
    "opposition_leader": Role(
        id="opposition_leader",
        title="Leader of the Opposition",
        side="opposition",
        party="Opposition",
        stance="Challenge the government's assumptions and present an alternative.",
    ),
    "shadow_minister": Role(
        id="shadow_minister",
        title="Shadow Minister",
        side="opposition",
        party="Opposition",
        stance="Test the policy on cost, fairness, delivery, and accountability.",
    ),
}
