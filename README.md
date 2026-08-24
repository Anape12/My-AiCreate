## venc
- Start
  - Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  - .\venv\Scripts\Activate.ps1

  - $env:LLM_PROVIDER = "ollama"
  - $env:OLLAMA_MODEL = "mistral"
  - $env:AI_ONLINE = "true"
  - $env:OLLAMA_KEEP_ALIVE = "-1"
  - uvicorn app:app --reload
