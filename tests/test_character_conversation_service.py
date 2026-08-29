import unittest
from unittest.mock import Mock, patch

from character_conversation_service import CharacterConversationService


class CharacterConversationServiceTests(unittest.TestCase):
    def setUp(self):
        self.registry = Mock()
        self.registry.names.return_value = ["rag_search", "calculator", "weather", "train", "web_search"]
        self.provider = Mock()
        self.provider.invoke_chat.return_value = "自然な返答"
        self.prompts = Mock()
        self.prompts.load.return_value = "ミアの人格定義"
        provider_patch = patch("character_conversation_service.create_llm_provider", return_value=self.provider)
        self.addCleanup(provider_patch.stop)
        self.create_provider = provider_patch.start()
        self.service = CharacterConversationService(self.registry, self.prompts)

    def respond(self, message="こんにちは"):
        return self.service.respond(
            character_name="ミア", prompt_key="mia", model_name=None, conversation_type="CHAT",
            context="tmng: 先週スマホを買い替えた", message=message,
        )

    def test_casual_chat_uses_one_model_call_without_tools(self):
        self.assertEqual("自然な返答", self.respond())
        self.provider.invoke_chat.assert_called_once()
        self.registry.execute.assert_not_called()

    def test_explicit_document_request_uses_rag(self):
        self.registry.execute.return_value = "検索結果"
        self.respond("社内資料から手順を調べて")
        self.registry.execute.assert_called_with("rag_search", "社内資料から手順を調べて")

    def test_provider_is_cached_between_responses(self):
        self.respond()
        self.respond("もう少し教えて")
        self.create_provider.assert_called_once_with("qwen2.5:3b")

    def test_loads_prompt_for_conversation_type(self):
        self.respond()
        self.prompts.load.assert_called_once_with("mia", "CHAT")

    def test_sends_persona_as_system_and_latest_message_as_current_user_message(self):
        self.respond("今日の夜ご飯は焼き鳥で胃もたれした笑")
        system_prompt, user_prompt = self.provider.invoke_chat.call_args.args
        self.assertEqual("ミアの人格定義", system_prompt)
        self.assertIn("<current_user_message>\n今日の夜ご飯は焼き鳥で胃もたれした笑", user_prompt)
        self.assertIn("必ず「今回の発言」の内容に対して返答", user_prompt)

    def test_warmup_preloads_prompts_before_model(self):
        self.service.warmup()
        self.prompts.preload_all.assert_called_once_with()
        self.provider.warmup.assert_called_once_with()

    def test_removes_repetitive_greeting_and_self_introduction(self):
        self.provider.invoke_chat.return_value = "おはよう、「ミア」です。カメラの差は大きそうだね。"
        self.assertEqual("カメラの差は大きそうだね。", self.respond("スマホを買い替えた"))

    def test_keeps_a_natural_greeting_when_user_greets_first(self):
        self.provider.invoke_chat.return_value = "おはよう、ミアです。今日もよろしくね。"
        self.assertEqual("おはよう！今日もよろしくね。", self.respond("おはよう"))


if __name__ == "__main__":
    unittest.main()
