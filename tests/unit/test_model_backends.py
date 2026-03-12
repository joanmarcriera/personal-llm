from __future__ import annotations

import sys
from types import ModuleType

from personal_llm.core.schemas import ModelBackend
from personal_llm.core.schemas import ModelProfile
from personal_llm.models.backends import MLXBackend


def test_mlx_backend_loads_model_once(monkeypatch) -> None:
    calls = {"load": 0, "generate": 0}

    fake_module = ModuleType("mlx_lm")

    def fake_load(model_name: str) -> tuple[str, str]:
        calls["load"] += 1
        return f"model::{model_name}", "tokenizer"

    def fake_generate(model: str, tokenizer: str, prompt: str, max_tokens: int) -> str:
        calls["generate"] += 1
        return f"{model}|{tokenizer}|{max_tokens}|{prompt[:20]}"

    fake_module.load = fake_load
    fake_module.generate = fake_generate
    monkeypatch.setitem(sys.modules, "mlx_lm", fake_module)

    backend = MLXBackend(
        profile=ModelProfile(
            family="qwen",
            model_name="Qwen/Qwen2.5-3B-Instruct",
            backend=ModelBackend.MLX,
            context_window=32768,
            quantization="q4_k_m",
            parameter_count=3_000_000_000,
            prompt_style="chatml",
        )
    )

    first = backend.generate("system", "user one")
    second = backend.generate("system", "user two")

    assert calls["load"] == 1
    assert calls["generate"] == 2
    assert "model::Qwen/Qwen2.5-3B-Instruct" in first
    assert "model::Qwen/Qwen2.5-3B-Instruct" in second
