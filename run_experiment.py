"""Compare debate strategies under the same multi-agent parliament flow."""

import argparse
import sys

from config import DEFAULT_TOPIC, LLM_CONFIG
from experiments.runner import ExperimentRunner
from strategies import STRATEGY_REGISTRY


def create_llm(temperature: float = 0.6, max_tokens: int = 180, request_timeout: int = 120, mock_llm: bool = False):
    if mock_llm:
        from tools.mock_llm import MockLLM

        return MockLLM()

    if LLM_CONFIG["provider"] != "ollama":
        raise ValueError("Only the Ollama provider is configured in this simplified project.")

    from langchain_ollama import ChatOllama

    return ChatOllama(
        base_url=LLM_CONFIG["base_url"],
        model=LLM_CONFIG["model"],
        temperature=temperature,
        num_predict=max_tokens,
        client_kwargs={"timeout": request_timeout},
        sync_client_kwargs={"timeout": request_timeout},
        keep_alive="5m",
    )


def make_strategies(value: str):
    if value == "all":
        names = list(STRATEGY_REGISTRY)
    else:
        names = [item.strip() for item in value.split(",") if item.strip()]

    unknown = [name for name in names if name not in STRATEGY_REGISTRY]
    if unknown:
        available = ", ".join(["all", *STRATEGY_REGISTRY.keys()])
        raise ValueError(f"Unknown strategy {unknown}. Available: {available}")

    return [STRATEGY_REGISTRY[name]() for name in names]


def get_strategies(value: str):
    return make_strategies(value)


def main() -> None:
    _utf8()
    parser = argparse.ArgumentParser(description="Parliament multi-agent strategy comparison.")
    parser.add_argument("--topic", "-t", default=DEFAULT_TOPIC)
    parser.add_argument("--strategies", "-s", default="all", help="all or comma list: baseline,heuristic_rule,genetic")
    parser.add_argument("--runs", "-n", type=int, default=3)
    parser.add_argument("--turns", type=int, default=7)
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--evaluator", choices=["heuristic", "llm"], default="heuristic")
    parser.add_argument("--show-debate", action="store_true", help="print every agent speech while the experiment runs")
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--max-tokens", type=int, default=180)
    parser.add_argument("--request-timeout", type=int, default=120)
    parser.add_argument("--mock-llm", action="store_true")
    args = parser.parse_args()

    llm = create_llm(args.temperature, args.max_tokens, args.request_timeout, args.mock_llm)
    runner = ExperimentRunner(
        strategies=make_strategies(args.strategies),
        llm=llm,
        evaluator_mode=args.evaluator,
    )
    runner.run_comparison(
        topic=args.topic,
        num_runs=args.runs,
        output_dir=args.output,
        max_turns=args.turns,
        show_debate=args.show_debate,
    )


def _utf8() -> None:
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


if __name__ == "__main__":
    main()
