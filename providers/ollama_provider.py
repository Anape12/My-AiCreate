from collections.abc import Iterator
import os

import requests

from langchain_ollama import OllamaLLM

from .base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.keep_alive = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
        # Environment variables are strings; Ollama requires a duration unit for strings.
        if self.keep_alive == "-1":
            self.keep_alive = "-1m"
        self.host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "4096"))
        # 180 tokens often cuts off code samples and numbered explanations mid-sentence.
        self.num_predict = int(os.getenv("OLLAMA_NUM_PREDICT", "512"))
        self.temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.5"))
        self._client = OllamaLLM(
            model=model_name,
            keep_alive=self.keep_alive,
            base_url=self.host,
            num_ctx=self.num_ctx,
            num_predict=self.num_predict,
            temperature=self.temperature,
        )

    def invoke(self, prompt: str) -> str:
        return self._client.invoke(prompt)

    def stream(self, prompt: str) -> Iterator[str]:
        yield from self._client.stream(prompt)

    def invoke_chat(self, system_prompt: str, user_prompt: str) -> str:
        response = requests.post(
            f"{self.host.rstrip('/')}/api/chat",
            json={
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "keep_alive": self.keep_alive,
                "options": {
                    "num_ctx": self.num_ctx,
                    "num_predict": self.num_predict,
                    "temperature": self.temperature,
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        answer = response.json().get("message", {}).get("content", "").strip()
        if not answer:
            raise RuntimeError("Ollama returned an empty chat response")
        return answer

    def warmup(self) -> None:
        response = requests.post(
            f"{self.host.rstrip('/')}/api/generate",
            json={"model": self.model_name, "prompt": "", "stream": False, "keep_alive": self.keep_alive},
            timeout=120,
        )
        response.raise_for_status()
