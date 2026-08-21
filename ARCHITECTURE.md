# My-AI Architecture

```
FastAPI (app.py)
  -> AIService
     -> ConversationMemory / ExperienceMemory / EvaluationGate
     -> Planner
        -> ToolRegistry
           -> rag_search / calculator / weather / train / web_search / export_training_data
     -> LLM Provider (Ollama or external API)
```

## Modes

- Default (`AI_ONLINE=false`): `rag_search`, `calculator`, and `export_training_data` are available.
- Online (`AI_ONLINE=true`): adds `weather`, `train`, and `web_search`. Set `TRAIN_STATUS_URL` to a compatible transit-status endpoint to enable live train data.

## Memory

- Conversation memory holds the latest six messages in process memory.
- Knowledge memory is accessed through the `rag_search` tool.
- Online search evidence is cached in `data/sourced_knowledge.jsonl` with its source URL and capture time. Offline RAG can reuse that evidence while showing its provenance.
- Successful problem-solving traces are appended to `data/experiences.jsonl` as `pending` records.
- The chat response includes `X-Experience-ID`. Review it through `POST /experiences/{id}/review` with `approved` or `rejected`; only approved records with a score of 4 or 5 can enter the training dataset.

## LLM providers

- `LLM_PROVIDER=ollama` (default) uses the local Ollama runtime and `OLLAMA_MODEL`.
- `LLM_PROVIDER=external` uses the existing OpenAI-compatible external endpoint settings.
- Learning, evaluation, and the model registry do not depend on either provider.

## Training preparation

The `export_training_data` tool exports successful experiences to `data/training/experiences.jsonl`.
Before export, the pipeline rejects incomplete answers and failed tool calls, then writes `data/training/manifest.json` for review. The manifest contains the exact LoRA training command.

## Fine-tuning and model promotion

1. Accumulate and review successful experiences.
2. Ask for `export_training_data`; review the generated dataset and manifest.
3. In a dedicated GPU environment, install `requirements-training.txt` and execute the command in the manifest.
4. Evaluate the adapter, convert or import it into the local model runtime, and register it as `ready` in `data/models.json`.
5. Activate only a `ready` model. `AIService` then uses that active model instead of the default `OLLAMA_MODEL` on its next start.

Fine-tuning is intentionally never started from a chat request: it can be expensive and should happen only after the dataset has been reviewed.
