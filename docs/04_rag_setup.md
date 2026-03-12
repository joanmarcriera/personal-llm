# 04 RAG Setup

## Default backend

Chroma is the easiest local default and requires minimal setup.

## Upgrade backend

Qdrant provides stronger metadata filtering, larger-scale indexing, and better parity with production-style deployments.

In plain language:

- `Chroma` is the simple starter vector store.
- `Qdrant` is the more serious vector database when you need more control and better filtering.

You do not need Qdrant for the first local version. Use it when you want retrieval to behave more like a production service.

## Workflow

1. Ingest and normalize source documents.
2. Classify domains and drop or quarantine disallowed material.
3. Chunk documents with metadata.
4. Generate embeddings.
5. Upsert embeddings and metadata into Chroma or Qdrant.
6. At query time, classify the question, filter by allowed domains, retrieve relevant chunks, and add citations.

## Metadata filters

The retrieval layer supports:

- domain allow lists
- sensitivity labels
- source IDs
- date ranges
- connector/source-type filters

Qdrant is especially useful when those metadata filters become important, because its indexing model is designed to combine vector similarity with payload filtering efficiently.
