import os
import unittest
from unittest.mock import patch

os.environ.setdefault("AI_SERVICE_TOKEN", "test-token")

from fastapi.testclient import TestClient
import app


class InternalApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app.app)
        self.payload = {
            "character_id": "1", "character_name": "ミア", "prompt_key": "mia", "model_name": None,
            "conversation_type": "CHAT", "conversation_id": "room-1",
            "context": None, "message": "こんにちは",
        }

    @patch.object(app.character_service, "respond", return_value="ミアの応答")
    def test_accepts_nullable_optional_character_fields(self, _service):
        response = self.client.post("/internal/respond", json=self.payload,
                                    headers={"X-Internal-Token": "test-token"})
        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual("ミアの応答", response.json()["answer"])

    def test_rejects_invalid_internal_token(self):
        response = self.client.post("/internal/respond", json=self.payload)
        self.assertEqual(401, response.status_code)
