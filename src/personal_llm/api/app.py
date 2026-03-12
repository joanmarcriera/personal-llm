from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI

from personal_llm.api.schemas import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    EmbeddingObject,
    EmbeddingRequest,
    EmbeddingResponse,
)
from personal_llm.config.settings import AppSettings, get_settings
from personal_llm.core.policy import PolicyEngine
from personal_llm.models.registry import ModelRegistry
from personal_llm.prompts.loader import PromptLibrary
from personal_llm.rag.citations import format_citations
from personal_llm.rag.embeddings import EmbeddingService
from personal_llm.rag.retriever import Retriever


def create_app(settings: AppSettings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(title="personal-llm", version="0.1.0")
    policy = PolicyEngine(resolved_settings)
    prompts = PromptLibrary(resolved_settings)
    retriever = Retriever(resolved_settings)
    embeddings = EmbeddingService(resolved_settings)
    registry = ModelRegistry(resolved_settings)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

    @app.get("/metrics")
    async def metrics() -> dict[str, str]:
        return {"status": "metrics-placeholder", "vector_backend": resolved_settings.vector_backend}

    @app.post("/admin/reindex")
    async def admin_reindex() -> dict[str, str]:
        return {"status": "queued", "detail": "Use the CLI reindex command for the full pipeline."}

    @app.post("/v1/embeddings", response_model=EmbeddingResponse)
    async def create_embedding(request: EmbeddingRequest) -> EmbeddingResponse:
        inputs = request.input if isinstance(request.input, list) else [request.input]
        vectors = embeddings.embed_texts(inputs)
        return EmbeddingResponse(
            data=[EmbeddingObject(embedding=vector, index=index) for index, vector in enumerate(vectors)],
            model=request.model or f"{resolved_settings.embedding_provider}-embedding",
        )

    @app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
    async def create_chat_completion(request: ChatCompletionRequest) -> ChatCompletionResponse:
        user_messages = [message.content for message in request.messages if message.role == "user"]
        query = user_messages[-1] if user_messages else ""
        decision = policy.route_query(query)
        profile_name = request.model or resolved_settings.model_profile
        backend = registry.build_backend(profile_name=profile_name)

        if not decision.allow:
            answer = policy.refusal_message()
            citations: list[str] = []
        else:
            metadata_filters = dict(request.metadata_filters)
            if prompts.exclude_disallowed_retrieval():
                metadata_filters["classification_label"] = "allowed"
            chunks = retriever.retrieve(query=query, metadata_filters=metadata_filters)
            context_block = "\n\n".join(chunk.text for chunk in chunks)
            citations = format_citations(chunks).splitlines() if chunks else []
            system_prompt = prompts.system_prompt()
            user_prompt = f"{query}\n\nContext:\n{context_block}\n\nCitations:\n{format_citations(chunks)}"
            answer = backend.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid4().hex}",
            model=profile_name,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=answer),
                )
            ],
            citations=citations,
        )

    return app
