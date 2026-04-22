"""Shared configuration for the parliament strategy experiment."""

LLM_CONFIG = {
    "provider": "ollama",
    "base_url": "http://localhost:11434",
    "model": "phi:latest",
}

DEBATE_FLOW = [
    "speaker",
    "pm",
    "opposition_leader",
    "minister",
    "shadow_minister",
    "pm",
    "opposition_leader",
]

DEFAULT_TOPIC = "Should NHS funding be increased?"

SCORING_DIMENSIONS = [
    "coherence",
    "evidence",
    "rebuttal",
    "persuasiveness",
    "role_consistency",
]

OUTPUT_ROOT = "results"
