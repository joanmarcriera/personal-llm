from __future__ import annotations

from personal_llm.config.settings import get_settings
from personal_llm.core.policy import PolicyEngine


def test_policy_refuses_off_topic_query() -> None:
    engine = PolicyEngine(get_settings())
    decision = engine.route_query("Recommend a few blockbuster movies.")
    assert decision.allow is False
    assert "professional-domain" in decision.reason

