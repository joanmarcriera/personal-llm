from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import ModelProfile


class ChatBackend(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str: ...


@dataclass(slots=True)
class MockBackend:
    profile: ModelProfile

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return (
            "Mock response for local smoke testing.\n\n"
            f"System policy summary: {system_prompt[:200]}\n\n"
            f"User prompt summary: {user_prompt[:400]}"
        )


@dataclass(slots=True)
class OllamaBackend:
    settings: AppSettings
    profile: ModelProfile
    _client: httpx.Client | None = field(init=False, default=None, repr=False)

    def _http_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(base_url=self.settings.ollama_url, timeout=120.0)
        return self._client

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._http_client().post(
            "/api/chat",
            json={
                "model": self.profile.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload.get("message", {}).get("content", ""))


@dataclass(slots=True)
class MLXBackend:
    profile: ModelProfile
    _model: Any | None = field(init=False, default=None, repr=False)
    _tokenizer: Any | None = field(init=False, default=None, repr=False)

    def _load_model(self) -> tuple[Any, Any]:
        if self._model is None or self._tokenizer is None:
            from mlx_lm import load

            self._model, self._tokenizer = load(self.profile.model_name)
        return self._model, self._tokenizer

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        from mlx_lm import generate

        model, tokenizer = self._load_model()
        prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>\n"
        return str(generate(model, tokenizer, prompt=prompt, max_tokens=512))


@dataclass(slots=True)
class LlamaCppBackend:
    profile: ModelProfile
    _llm: Any | None = field(init=False, default=None, repr=False)

    def _client(self) -> Any:
        if self._llm is None:
            from llama_cpp import Llama

            self._llm = Llama(
                model_path=self.profile.model_name,
                n_ctx=self.profile.context_window,
                verbose=False,
            )
        return self._llm

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client().create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        return str(response["choices"][0]["message"]["content"])
