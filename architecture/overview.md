# Architecture Overview

## Design principles

- Keep the first-run experience simple on Apple Silicon.
- Preserve stable interfaces so the local quickstart can evolve into a more production-style deployment.
- Keep training adapter-based and retrieval-grounded.
- Bias the system strongly toward professional domains through multiple independent control layers.
- Keep raw data private and minimize unnecessary export to external compute.

## Diagrams

- [system-overview.mmd](system-overview.mmd)
- [ingestion-flow.mmd](ingestion-flow.mmd)
- [training-flow.mmd](training-flow.mmd)
- [serving-sequence.mmd](serving-sequence.mmd)
- [security-boundaries.mmd](security-boundaries.mmd)

## System overview

```mermaid
flowchart TD
    user["User / Agent Client"] --> api["FastAPI Orchestrator"]
    api --> router["Topic Router + Policy Validator"]
    router -->|allowed| retriever["Retriever"]
    router -->|disallowed| refusal["Refusal Policy"]
    retriever --> vectordb["Chroma or Qdrant"]
    vectordb --> chunks["Allowed Domain Chunks"]
    api --> backend["MLX / Ollama / llama.cpp"]
    backend --> adapters["LoRA Adapters"]
    connectors["Drive / Email / Linkwarden / Files / Code"] --> ingest["Ingestion Pipelines"]
    ingest --> processed["Processed JSONL + Parquet"]
    processed --> vectordb
    processed --> training["Training Dataset Builder"]
    training --> adapters
```

## Ingestion flow

```mermaid
flowchart LR
    source["Source Connectors"] --> raw["data/raw"]
    raw --> extract["Text Extraction"]
    extract --> dedup["Checksum + Near-Duplicate Detection"]
    dedup --> classify["Domain Classification"]
    classify --> chunk["Chunking + Metadata Tags"]
    chunk --> manifest["JSONL Manifest"]
    chunk --> parquet["Parquet Export"]
    manifest --> embed["Embedding Jobs"]
    embed --> vector["Vector Store"]
```

## Training flow

```mermaid
flowchart TD
    corpus["Processed Chunks"] --> curate["Dataset Curation"]
    prompts["Refusal + Professional Prompt Assets"] --> curate
    curate --> sft["SFT JSONL"]
    curate --> eval["Eval JSONL"]
    sft --> mlx["Local MLX LoRA"]
    sft --> runpod["Remote RunPod Axolotl/PEFT"]
    mlx --> adapters["Adapters + Metrics"]
    runpod --> adapters
```

## Serving sequence

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant P as Policy
    participant R as Retriever
    participant V as Vector DB
    participant M as Model Backend
    C->>A: chat.completions
    A->>P: classify query
    alt disallowed
        P-->>A: refuse + redirect
        A-->>C: refusal response
    else allowed
        A->>R: retrieve context
        R->>V: semantic search + metadata filter
        V-->>R: top chunks
        R-->>A: citations + context
        A->>M: final prompt
        M-->>A: answer
        A->>P: validate output
        A-->>C: grounded response
    end
```

## Security boundaries

```mermaid
flowchart TD
    raw["Raw Personal Documents"] --> secure["Encrypted Local Storage"]
    secure --> process["Local Processing"]
    process --> filtered["Approved Training / Retrieval Corpus"]
    filtered --> local["Local MLX / Chroma / API"]
    filtered --> remote["Optional Remote GPU Export"]
    remote --> review["Explicit Approval + Redaction Review"]
    review --> adapter["Remote LoRA Job"]
    classDef sensitive fill:#fbe9e7,stroke:#bf360c,color:#000;
    classDef controlled fill:#e8f5e9,stroke:#1b5e20,color:#000;
    class raw,secure sensitive;
    class process,filtered,local,remote,review,adapter controlled;
```

## Components

- Connectors acquire or scan sources and write immutable raw artifacts plus normalized source manifests.
- Pipelines extract text, deduplicate, chunk, and classify domains before exporting processed corpora.
- Training builds SFT and refusal datasets for MLX or remote Axolotl/PEFT jobs.
- RAG indexes allowed-domain chunks and filters disallowed or sensitive data by policy.
- The API orchestrator classifies every query before retrieval or generation.
