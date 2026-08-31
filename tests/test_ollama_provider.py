import os
import unittest
from unittest.mock import patch

from providers.ollama_provider import OllamaProvider


class OllamaProviderTests(unittest.TestCase):
    @patch("providers.ollama_provider.OllamaLLM")
    def test_passes_configured_host_to_langchain_client(self, mock_llm):
        with patch.dict(os.environ, {"OLLAMA_HOST": "http://host.docker.internal:11434"}):
            OllamaProvider("mistral")

        mock_llm.assert_called_once_with(
            model="mistral",
            keep_alive="30m",
            base_url="http://host.docker.internal:11434",
            num_ctx=4096,
            num_predict=512,
            temperature=0.5,
        )

    @patch("providers.ollama_provider.requests.post")
    @patch("providers.ollama_provider.OllamaLLM")
    def test_chat_uses_native_system_and_user_roles(self, _mock_llm, mock_post):
        mock_post.return_value.json.return_value = {"message": {"content": "かなり居酒屋メニューだね！"}}
        provider = OllamaProvider("qwen2.5:3b")

        answer = provider.invoke_chat("ミアの人格", "焼き鳥食べた")

        self.assertEqual("かなり居酒屋メニューだね！", answer)
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual("system", payload["messages"][0]["role"])
        self.assertEqual("ミアの人格", payload["messages"][0]["content"])
        self.assertEqual("user", payload["messages"][1]["role"])
