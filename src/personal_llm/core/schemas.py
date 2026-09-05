from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    LOCAL_FILE = "local_file"
    GOOGLE_DRIVE = "google_drive"
    EMAIL_EXPORT = "email_export"
    LINKWARDEN_EXPORT = "linkwarden_export"
    CODE_REPOSITORY = "code_repository"
    SPREADSHEET = "spreadsheet"
    DIAGRAM = "diagram"


class SensitivityLabel(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


class ModelBackend(StrEnum):
    MLX = "mlx"
    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    MOCK = "mock"


class SourceDocument(BaseModel):
    id: str
    source_type: SourceType
    uri: str
    title: str
    content_path: str
    checksum: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    sensitivity: SensitivityLabel = SensitivityLabel.CONFIDENTIAL
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DomainClassification(BaseModel):
    label: Literal["allowed", "mixed", "disallowed"]
    allowed_scores: dict[str, float] = Field(default_factory=dict)
    disallowed_scores: dict[str, float] = Field(default_factory=dict)
    primary_allowed: list[str] = Field(default_factory=list)
    primary_disallowed: list[str] = Field(default_factory=list)


class ExtractedDocument(BaseModel):
    id: str
    source_id: str
    source_type: SourceType
    title: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    checksum: str
    sensitivity: SensitivityLabel = SensitivityLabel.RESTRICTED
    classification: DomainClassification | None = None
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChunkRecord(BaseModel):
    id: str
    document_id: str
    source_id: str
    chunk_index: int
    text: str
    token_estimate: int
    metadata: dict[str, Any] = Field(default_factory=dict)
    domains: list[str] = Field(default_factory=list)
    classification_label: Literal["allowed", "mixed", "disallowed"]
    sensitivity: SensitivityLabel = SensitivityLabel.RESTRICTED


class EmbeddingRecord(BaseModel):
    chunk_id: str
    vector: list[float]
    model_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    domains: list[str] = Field(default_factory=list)


class TrainingExample(BaseModel):
    id: str
    system: str
    user: str
    assistant: str
    allowed_domains: list[str] = Field(default_factory=list)
    refusal: bool = False
    source_chunk_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalCase(BaseModel):
    id: str
    prompt: str
    expected_behavior: Literal["answer", "refuse"]
    allowed_domains: list[str] = Field(default_factory=list)
    require_citations: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelProfile(BaseModel):
    family: str
    model_name: str
    backend: ModelBackend
    context_window: int
    quantization: str
    parameter_count: int
    prompt_style: str


class PolicyDecision(BaseModel):
    allow: bool
    reason: str
    redirect_domains: list[str]
    classifier: DomainClassification


class EvaluationResult(BaseModel):
    total_cases: int
    passed_cases: int
    restriction_compliance: float
    citation_coverage: float
    hallucination_proxy: float
    domain_alignment: float
    details: list[dict[str, Any]] = Field(default_factory=list)
