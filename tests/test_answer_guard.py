import unittest

from rag.answer_guard import refine_answer


class AnswerGuardTests(unittest.TestCase):
    def test_refines_vague_answer_with_context(self):
        answer = refine_answer("分からないです", "本能寺の変は1582年に起きた")
        self.assertIn("参考情報の範囲では確認できませんでした", answer)


if __name__ == "__main__":
    unittest.main()
