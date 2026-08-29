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
            num_predict=180,
            temperature=0.7,
        )
