from __future__ import annotations

from personal_llm.config.settings import get_settings
from personal_llm.core.policy import PolicyEngine
from personal_llm.prompts.loader import PromptLibrary


def test_original_model_profile_disables_runtime_policy() -> None:
    settings = get_settings().model_copy(update={"guardrail_profile": "original_model"})
    engine = PolicyEngine(settings)

    decision = engine.route_query("Who will win the football league this year?")

    assert decision.allow is True


def test_strict_profile_refuses_mixed_queries() -> None:
    settings = get_settings().model_copy(update={"guardrail_profile": "strict"})
    engine = PolicyEngine(settings)

    decision = engine.route_query(
        "Compare Kubernetes autoscaling tradeoffs and which football team has the best defense."
    )

    assert decision.allow is False


def test_relaxed_profile_uses_relaxed_prompt() -> None:
    settings = get_settings().model_copy(update={"guardrail_profile": "relaxed"})
    prompts = PromptLibrary(settings)

    prompt = prompts.system_prompt()

    assert "mainly on technical, operational, and business topics" in prompt
