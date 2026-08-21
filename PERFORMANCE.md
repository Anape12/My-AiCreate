# Performance settings

The application keeps an Ollama model loaded for 30 minutes by default. This reduces the delay before the first token after idle time without changing model quality.

Before starting the API, use this setting if a different keep-alive period is required:

```powershell
$env:OLLAMA_KEEP_ALIVE = "30m"
```

Use `-1m` only when there is enough memory to keep the model resident until Ollama is restarted.

```powershell
$env:OLLAMA_KEEP_ALIVE = "-1m"
```

The chat page calls `POST /models/warmup` automatically, so the model is loaded before the first question. This does not generate or cache an answer.

For more speed without lowering quality, use a GPU with enough VRAM for the model. Do not reduce model size, quantization, or context length when answer quality is the priority.
