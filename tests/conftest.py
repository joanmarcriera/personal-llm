from __future__ import annotations

import os

os.environ.setdefault("PERSONAL_LLM_VECTOR_BACKEND", "memory")
os.environ.setdefault("PERSONAL_LLM_MODEL_BACKEND", "mock")
os.environ.setdefault("PERSONAL_LLM_EMBEDDING_PROVIDER", "hash")

from personal_llm.config.settings import get_settings  # noqa: E402

get_settings.cache_clear()

