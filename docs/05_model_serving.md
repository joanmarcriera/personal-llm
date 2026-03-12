# 05 Model Serving

## API surface

The FastAPI service exposes:

- `POST /v1/chat/completions`
- `POST /v1/embeddings`
- `GET /health`
- `GET /metrics`
- `POST /admin/reindex`

## Serving modes

- MLX backend for Apple Silicon local inference
- Ollama backend for managed local model lifecycle
- llama.cpp backend for GGUF-centric deployments
- Mock backend for offline smoke tests

## Plain-English differences

- `MLX`: runs the model directly through Apple-Silicon-native libraries. This is the default local path in this repo.
- `Ollama`: runs the model through a local server with a simple API. It is easier to operate if you prefer a model manager over direct runtime wiring.
- `llama.cpp`: useful when you want tight control over GGUF-based local inference.

If you are unsure, start with `MLX`. Move to `Ollama` later only if you want a cleaner local serving layer or easier model switching outside the Python process.

## Backend selection recommendation

For first-time use, keep backend selection profile-driven:

- set the model profile
- let the repository choose the matching backend
- use the backend override only when you are intentionally testing a different runtime

## Guardrail selection recommendation

For first-time use, keep:

- `PERSONAL_LLM_GUARDRAIL_PROFILE=standard`

Then move to:

- `strict` if you want stronger professional-only refusal behavior
- `relaxed` if you want fewer refusals
- `original_model` if you want near-base-model behavior

Guardrail profiles change:

- which system prompt is used
- whether runtime policy refuses requests
- whether disallowed retrieval is filtered out automatically

The actual prompt files live in [prompts/README.md](../prompts/README.md). They already exist for `strict`, `standard`, `relaxed`, and `original_model`, and are selected by [config/guardrails.yaml](../config/guardrails.yaml).

For first-time tuning, keep this mental model:

- `knowledge/persona.md` defines how you want the assistant to sound
- `prompts/*.md` translate that into runtime behavior
- LoRA examples make the behavior more stable over time

## Request flow

1. Classify the user query.
2. Refuse if the topic is outside the professional domain.
3. Retrieve relevant chunks using the configured vector backend.
4. Build the final prompt with system policy, retrieved context, and citations.
5. Generate the answer through the selected backend.
6. Validate the output policy before returning the response.
