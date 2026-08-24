import unittest

from rag.prompt_builder import build_prompt


class PromptBuilderTests(unittest.TestCase):
    def test_prompt_enables_general_knowledge_answers(self):
        prompt = build_prompt(
            query="日本史について教えて",
            history_text="user: 日本史について教えて",
            react_context="",
            rag_context="",
        )

        self.assertIn("親しみやすい会話調", prompt)
        self.assertIn("相談では、決めつけや説教をせず", prompt)


if __name__ == "__main__":
    unittest.main()
