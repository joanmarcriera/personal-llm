from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import ModelBackend, ModelProfile
from personal_llm.models.backends import ChatBackend, LlamaCppBackend, MLXBackend, MockBackend, OllamaBackend


@dataclass(slots=True)
class ModelRegistry:
    settings: AppSettings

    def _config(self) -> dict[str, Any]:
        return self.settings.load_yaml("config/models.yaml")

    def get_profile(self, profile_name: str | None = None) -> ModelProfile:
        config = self._config()
        selected_name = profile_name or self.settings.model_profile or config["default_model_profile"]
        profiles = config["profiles"]
        if selected_name not in profiles:
            raise KeyError(f"Unknown model profile: {selected_name}")
        payload = dict(profiles[selected_name])
        payload["backend"] = ModelBackend(payload["backend"])
        return ModelProfile.model_validate(payload)

    def build_backend(self, profile_name: str | None = None) -> ChatBackend:
        profile = self.get_profile(profile_name)
        selected_backend = profile.backend
        if self.settings.model_backend != "auto":
            selected_backend = ModelBackend(self.settings.model_backend)
        if selected_backend == ModelBackend.MOCK:
            return MockBackend(profile=profile)
        if selected_backend == ModelBackend.OLLAMA:
            return OllamaBackend(settings=self.settings, profile=profile)
        if selected_backend == ModelBackend.MLX:
            return MLXBackend(profile=profile)
        if selected_backend == ModelBackend.LLAMA_CPP:
            return LlamaCppBackend(profile=profile)
        return MockBackend(profile=profile)
