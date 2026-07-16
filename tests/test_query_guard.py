import unittest

from rag.query_guard import normalize_query


class QueryGuardTests(unittest.TestCase):
    def test_normalizes_historical_question(self):
        result = normalize_query("本能寺の変は何年に起きた出来事？")
        self.assertIn("本能寺の変", result)
        self.assertIn("何年", result)


if __name__ == "__main__":
    unittest.main()
