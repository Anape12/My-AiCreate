import os
import re
import threading

from providers import create_llm_provider
from prompt_repository import PromptRepository


class CharacterConversationService:
    """Fast, character-focused conversation path with cached model providers."""

    def __init__(self, registry, prompt_repository=None):
        self.registry = registry
        self.prompts = prompt_repository or PromptRepository()
        self.default_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self._providers = {}
        self._locks = {}
        self._cache_lock = threading.Lock()

    def _provider(self, model_name):
        model = model_name or self.default_model
        with self._cache_lock:
            if model not in self._providers:
                self._providers[model] = create_llm_provider(model)
                self._locks[model] = threading.Lock()
            return model, self._providers[model], self._locks[model]

    def warmup(self):
        self.prompts.preload_all()
        _, provider, _ = self._provider(None)
        provider.warmup()

    def _tool_names(self, message):
        text = message.lower()
        selected = []
        needs_rag = any(word in text for word in ("社内資料", "ナレッジ", "規程", "手順書", "ドキュメント"))
        if needs_rag:
            selected.append("rag_search")
        if any(word in text for word in ("計算して", "計算お願い", "合計して")):
            selected.append("calculator")
        if any(word in text for word in ("天気", "降水", "傘いる")):
            selected.append("weather")
        if any(word in text for word in ("電車", "列車", "運行状況")):
            selected.append("train")
        if not needs_rag and any(word in text for word in ("検索して", "調べて", "最新情報")):
            selected.append("web_search")
        return [name for name in dict.fromkeys(selected) if name in self.registry.names()]

    def _tool_context(self, message):
        names = self._tool_names(message)
        if not names:
            return ""
        return "\n\n".join(f"[{name}]\n{self.registry.execute(name, message)}" for name in names)

    @staticmethod
    def _naturalize_answer(answer, character_name, message):
        """Remove model-generated speaker labels and repetitive self-introductions."""
        text = answer.strip()
        name = re.escape(character_name)
        text = re.sub(rf"^(?:AI住人)?[「『]?{name}[」』]?\s*[:：]\s*", "", text)
        introduction = re.compile(
            rf"^(?:(おはよう(?:ございます)?|こんにちは|こんばんは)[、,!！。　\s]*)?"
            rf"(?:私は|僕は|こちらは)?[「『]?{name}[」』]?(?:です|だよ|といいます|と申します)[,!！。、\s]*"
        )
        match = introduction.match(text)
        if match:
            remainder = text[match.end():].strip()
            user_greeted = any(word in message for word in ("おはよう", "こんにちは", "こんばんは"))
            if user_greeted and match.group(1):
                greeting = match.group(1)
                return f"{greeting}！{remainder}" if remainder else f"{greeting}！"
            if remainder:
                return remainder
        return text

    def respond(self, *, character_name, prompt_key, model_name,
                conversation_type, context, message):
        _, provider, lock = self._provider(model_name)
        tool_context = self._tool_context(message)
        character_prompt = self.prompts.load(prompt_key, conversation_type)
        user_prompt = f"""以下の会話履歴は、今回の発言を理解するための補助情報です。
履歴に別の話題があっても、必ず「今回の発言」の内容に対して返答してください。

<conversation_history type="{conversation_type}">
{(context or '')[-3000:]}
</conversation_history>

<current_user_message>
{message}
</current_user_message>

<tool_result>
{tool_context or 'なし'}
</tool_result>

今回の発言にかみ合う「{character_name}」の返答本文だけを出力してください。"""
        # Ollama clients are reused; serialize calls per model to keep local inference stable.
        with lock:
            answer = provider.invoke_chat(character_prompt, user_prompt)
        return self._naturalize_answer(answer, character_name, message)
