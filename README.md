## venc
- Start
  - Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  - .\venv\Scripts\Activate.ps1

  - $env:LLM_PROVIDER = "ollama"
  - $env:OLLAMA_MODEL = "qwen2.5:3b"
  - $env:AI_ONLINE = "true"
  - $env:OLLAMA_KEEP_ALIVE = "-1"
  - uvicorn app:app --reload

## NWProject integration

`POST /internal/respond` accepts a character definition, conversation identifier,
recent conversation context, and the latest message. Set `AI_SERVICE_TOKEN` to
require the same value in the `X-Internal-Token` request header. Each call uses
isolated short-term memory; the caller owns conversation-scoped persistence.
