from __future__ import annotations

from personal_llm.config.settings import get_settings
from personal_llm.core.schemas import ModelBackend
from personal_llm.models.backends import MockBackend
from personal_llm.models.registry import ModelRegistry


def test_model_registry_uses_profile_backend_by_default() -> None:
    settings = get_settings().model_copy(
        update={"model_backend": "auto", "model_profile": "qwen2.5-7b-instruct"}
    )
    registry = ModelRegistry(settings)
    profile = registry.get_profile()

    assert profile.backend == ModelBackend.MLX


def test_small_qwen_profile_uses_mlx_backend() -> None:
    settings = get_settings().model_copy(
        update={"model_backend": "auto", "model_profile": "qwen2.5-3b-instruct"}
    )
    registry = ModelRegistry(settings)
    profile = registry.get_profile()

    assert profile.backend == ModelBackend.MLX
    assert profile.parameter_count < 7_000_000_000


def test_model_registry_allows_explicit_backend_override() -> None:
    settings = get_settings().model_copy(
        update={"model_backend": "mock", "model_profile": "qwen2.5-7b-instruct"}
    )
    registry = ModelRegistry(settings)

    backend = registry.build_backend()

    assert isinstance(backend, MockBackend)
