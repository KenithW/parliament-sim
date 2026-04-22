"""Fast local LLM substitute for testing the experiment pipeline."""

from dataclasses import dataclass


@dataclass
class _Response:
    content: str


class MockLLM:
    def invoke(self, prompt: str):
        text = prompt.lower()
        tactic = _tactic(text)
        if "role: speaker" in text:
            body = "Order. The House will proceed with a focused and orderly debate."
        elif "role: prime minister" in text:
            body = (
                "Mr Speaker, the government supports this policy because it links public need "
                "to a deliverable plan, clear funding choices, and measurable outcomes."
            )
        elif "role: cabinet minister" in text:
            body = (
                "The department would deliver this through staged funding, transparent reporting, "
                "and evidence from local services so Parliament can judge progress."
            )
        elif "role: leader of the opposition" in text:
            body = (
                "Mr Speaker, the opposition accepts the problem but challenges the government's "
                "cost assumptions, timetable, and lack of safeguards for households."
            )
        elif "role: shadow minister" in text:
            body = (
                "The House needs stronger evidence, an independent review, and a fairer alternative "
                "before accepting the government's claim that this plan will work."
            )
        else:
            body = "This speech presents a clear parliamentary argument with evidence, rebuttal, and policy detail."
        if tactic:
            body = f"{body} {tactic}"
        return _Response(body)


def _tactic(text: str) -> str:
    if "tactic: direct_rebuttal" in text or "tactic: rebuttal_first" in text:
        return "However, the previous claim fails because it ignores costed delivery evidence and a clearer policy test."
    if "tactic: implementation_focus" in text or "tactic: delivery_record" in text:
        return "The plan would publish quarterly data, define outcomes, and compare results against local service reports."
    if "tactic: evidence_push" in text:
        return "The strongest case rests on transparent evidence, cost data, and measurable outcomes for the public."
    if "tactic: contrast_choice" in text or "tactic: accountability_attack" in text:
        return "The choice is between accountable delivery and an unfunded promise with unclear safeguards."
    if "tactic: consensus_builder" in text:
        return "A credible compromise would include safeguards, independent review, and cross-party reporting."
    return ""
