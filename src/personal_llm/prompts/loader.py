from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from personal_llm.config.settings import AppSettings


@dataclass(slots=True)
class PromptLibrary:
    settings: AppSettings

    def load_text(self, filename: str) -> str:
        path = self.settings.resolve(Path("prompts") / filename)
        return path.read_text(encoding="utf-8")

    def guardrail_profile(self) -> dict[str, Any]:
        config = self.settings.load_yaml("config/guardrails.yaml")
        profiles = config.get("profiles", {})
        if not isinstance(profiles, dict):
            raise TypeError("config/guardrails.yaml profiles must be a mapping.")
        profile_name = self.settings.guardrail_profile or config.get("default_profile", "standard")
        profile = profiles.get(profile_name)
        if not isinstance(profile, dict):
            raise KeyError(f"Unknown guardrail profile: {profile_name}")
        return profile

    def system_prompt(self) -> str:
        profile = self.guardrail_profile()
        prompt_file = profile.get("system_prompt", "system_professional.md")
        if not isinstance(prompt_file, str):
            raise TypeError("Guardrail profile system_prompt must be a string.")
        return self.load_text(prompt_file)

    def refusal_prompt(self) -> str:
        profile = self.guardrail_profile()
        prompt_file = profile.get("refusal_prompt", "refusal_redirect.md")
        if not isinstance(prompt_file, str):
            raise TypeError("Guardrail profile refusal_prompt must be a string.")
        return self.load_text(prompt_file)

    def runtime_policy_enabled(self) -> bool:
        return bool(self.guardrail_profile().get("enable_runtime_policy", True))

    def refuse_mixed_queries(self) -> bool:
        return bool(self.guardrail_profile().get("refuse_mixed_queries", False))

    def exclude_disallowed_retrieval(self) -> bool:
        return bool(self.guardrail_profile().get("exclude_disallowed_retrieval", True))

    def include_refusal_examples(self) -> bool:
        return bool(self.guardrail_profile().get("include_refusal_examples", True))
