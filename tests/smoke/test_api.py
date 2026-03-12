from __future__ import annotations

from fastapi.testclient import TestClient

from personal_llm.api.app import create_app
from personal_llm.config.settings import get_settings


def test_chat_completion_refuses_disallowed_query() -> None:
    app = create_app(get_settings())
    client = TestClient(app)
    response = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Who won the football match?"}]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "restricted" in payload["choices"][0]["message"]["content"] or "professional" in payload["choices"][0]["message"]["content"]

