import unittest
from unittest.mock import patch

from rag.external_llm import ExternalLLMClient


class ExternalLLMTests(unittest.TestCase):
    @patch("rag.external_llm.requests.post")
    def test_generate_uses_external_api_when_configured(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "歴史についての回答"}}]
        }

        client = ExternalLLMClient(
            api_key="fake-key",
            base_url="https://example.com/v1",
            model="gpt-4o-mini",
        )

        result = client.generate("歴史について教えて")

        self.assertEqual(result, "歴史についての回答")
        self.assertEqual(mock_post.call_count, 1)


if __name__ == "__main__":
    unittest.main()
