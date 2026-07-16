import unittest

from rag.quick_answers import get_quick_answer


class QuickAnswerTests(unittest.TestCase):
    def test_returns_local_answer_for_known_keyword(self):
        answer = get_quick_answer("if文とは？")
        self.assertIsNotNone(answer)
        self.assertIn("条件", answer)

    def test_returns_none_for_unknown_query(self):
        answer = get_quick_answer("今日は何をしますか？")
        self.assertIsNone(answer)


if __name__ == "__main__":
    unittest.main()
