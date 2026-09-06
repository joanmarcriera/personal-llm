from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from personal_llm.config.settings import AppSettings
from personal_llm.connectors.base import SourceConnector
from personal_llm.connectors.code_repos import CodeRepositoryConnector
from personal_llm.connectors.email import EmailConnector
from personal_llm.connectors.google_drive import GoogleDriveConnector
from personal_llm.connectors.linkwarden import LinkwardenConnector
from personal_llm.connectors.local_files import LocalFilesConnector
from personal_llm.connectors.spreadsheets import SpreadsheetConnector
from personal_llm.core.io import ensure_directory, read_jsonl, write_jsonl, write_parquet
from personal_llm.core.schemas import (
    ChunkRecord,
    EmbeddingRecord,
    ExtractedDocument,
    SourceDocument,
    TrainingExample,
)
from personal_llm.pipelines.chunking import Chunker
from personal_llm.pipelines.dataset_builder import DatasetBuilder
from personal_llm.pipelines.dedup import DuplicateDetector
from personal_llm.pipelines.domain_classifier import DomainClassifier
from personal_llm.pipelines.extract import DocumentExtractor
from personal_llm.prompts.loader import PromptLibrary
from personal_llm.rag.embeddings import EmbeddingService
from personal_llm.vector_db.base import VectorStore, build_vector_store


@dataclass(slots=True)
class PipelineOrchestrator:
    settings: AppSettings
    extractor: DocumentExtractor = field(init=False)
    chunker: Chunker = field(init=False)
    classifier: DomainClassifier = field(init=False)
    duplicate_detector: DuplicateDetector = field(init=False)
    prompt_library: PromptLibrary = field(init=False)
    dataset_builder: DatasetBuilder = field(init=False)
    embedding_service: EmbeddingService = field(init=False)
    vector_store: VectorStore = field(init=False)
    source_manifest_path: Path = field(init=False)
    documents_manifest_path: Path = field(init=False)
    chunks_manifest_path: Path = field(init=False)
    embeddings_manifest_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.extractor = DocumentExtractor()
        self.chunker = Chunker()
        self.classifier = DomainClassifier(
            self.settings.resolve(Path("config/domain_taxonomy.yaml"))
        )
        self.duplicate_detector = DuplicateDetector()
        self.prompt_library = PromptLibrary(self.settings)
        self.dataset_builder = DatasetBuilder(self.prompt_library)
        self.embedding_service = EmbeddingService(self.settings)
        self.vector_store = build_vector_store(self.settings)
        self.source_manifest_path = self.settings.resolve(
            Path("data/processed/source_manifest.jsonl")
        )
        self.documents_manifest_path = self.settings.resolve(Path("data/processed/documents.jsonl"))
        self.chunks_manifest_path = self.settings.resolve(Path("data/processed/chunks.jsonl"))
        self.embeddings_manifest_path = self.settings.resolve(
            Path("data/processed/embeddings.jsonl")
        )

    def sync_sources(self, config_path: Path) -> list[SourceDocument]:
        config = self.settings.load_yaml(config_path)
        defaults = config.get("defaults", {})
        connectors = config.get("connectors", {})
        raw_dir = ensure_directory(self.settings.resolve(defaults.get("raw_dir", "data/raw")))

        connector_objects: dict[str, SourceConnector] = {
            "local_files": LocalFilesConnector(),
            "code_repositories": CodeRepositoryConnector(),
            "google_drive": GoogleDriveConnector(),
            "email": EmailConnector(),
            "linkwarden": LinkwardenConnector(),
            "spreadsheets": SpreadsheetConnector(),
        }
        documents: list[SourceDocument] = []
        for connector_name, connector in connector_objects.items():
            connector_config = connectors.get(connector_name, {})
            if not isinstance(connector_config, dict):
                continue
            if connector_config.get("enabled") is False:
                continue
            merged_config = dict(defaults)
            merged_config.update(connector_config)
            documents.extend(connector.discover(self.settings, raw_dir, merged_config))
        write_jsonl(self.source_manifest_path, documents)
        write_parquet(
            self.settings.resolve(Path("data/processed/source_manifest.parquet")), documents
        )
        return documents

    def extract_documents(self) -> list[ExtractedDocument]:
        sources = [
            SourceDocument.model_validate(row) for row in read_jsonl(self.source_manifest_path)
        ]
        documents: list[ExtractedDocument] = []
        for source in sources:
            documents.extend(self.extractor.extract(source))
        documents = self.duplicate_detector.filter_documents(documents)
        write_jsonl(self.documents_manifest_path, documents)
        write_parquet(self.settings.resolve(Path("data/processed/documents.parquet")), documents)
        return documents

    def classify_and_chunk_documents(self) -> list[ChunkRecord]:
        documents = [
            ExtractedDocument.model_validate(row)
            for row in read_jsonl(self.documents_manifest_path)
        ]
        classified: list[ExtractedDocument] = []
        chunks: list[ChunkRecord] = []
        for document in documents:
            classification = self.classifier.classify_text(document.text)
            document.classification = classification
            classified.append(document)
            chunks.extend(self.chunker.chunk_document(document))
        write_jsonl(self.documents_manifest_path, classified)
        write_jsonl(self.chunks_manifest_path, chunks)
        write_parquet(self.settings.resolve(Path("data/processed/chunks.parquet")), chunks)
        return chunks

    def build_training_dataset(self) -> list[TrainingExample]:
        chunks = [ChunkRecord.model_validate(row) for row in read_jsonl(self.chunks_manifest_path)]
        examples = self.dataset_builder.build_training_examples(chunks)
        target = self.settings.resolve(Path("data/training/example_sft.jsonl"))
        write_jsonl(target, examples)
        write_parquet(self.settings.resolve(Path("data/training/example_sft.parquet")), examples)
        return examples

    def embed_chunks(self) -> list[EmbeddingRecord]:
        chunks = [ChunkRecord.model_validate(row) for row in read_jsonl(self.chunks_manifest_path)]
        if self.prompt_library.exclude_disallowed_retrieval():
            indexed_chunks = [
                chunk for chunk in chunks if chunk.classification_label != "disallowed"
            ]
        else:
            indexed_chunks = chunks
        embeddings = self.embedding_service.embed_chunks(indexed_chunks)
        self.vector_store.bootstrap()
        self.vector_store.upsert(embeddings)
        write_jsonl(self.embeddings_manifest_path, embeddings)
        return embeddings

    def reindex(self) -> list[EmbeddingRecord]:
        self.vector_store.reset()
        return self.embed_chunks()

    def full_sync(self) -> dict[str, int]:
        self.sync_sources(Path("config/sources.yaml"))
        documents = self.extract_documents()
        chunks = self.classify_and_chunk_documents()
        training = self.build_training_dataset()
        embeddings = self.embed_chunks()
        return {
            "documents": len(documents),
            "chunks": len(chunks),
            "training_examples": len(training),
            "embeddings": len(embeddings),
        }
