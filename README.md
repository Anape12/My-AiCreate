## venc
- Start
  - Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  - .\venv\Scripts\Activate.ps1

  - $env:LLM_PROVIDER = "ollama"
  - $env:OLLAMA_MODEL = "qwen2.5:7b"
  - $env:AI_ONLINE = "true"
  - $env:OLLAMA_KEEP_ALIVE = "-1m"
  - uvicorn app:app --reload

## Model switching

The general-purpose default is `qwen2.5:7b`.  It is better suited to Japanese
conversation and technical explanations than the smaller 3B model, while
remaining runnable on a typical local machine.

After starting the API, an installed Ollama model can also be checked and
switched without restarting the server:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/models"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/models/select" -Method Post -ContentType "application/json" -Body '{"model_name":"qwen2.5:7b"}'
```

The switch is first warmed up.  Only after that succeeds is it saved as the
active local model, so the same model is retained after the next restart.

## NWProject integration

`POST /internal/respond` accepts a character definition, conversation identifier,
recent conversation context, and the latest message. Set `AI_SERVICE_TOKEN` to
require the same value in the `X-Internal-Token` request header. Each call uses
isolated short-term memory; the caller owns conversation-scoped persistence.
