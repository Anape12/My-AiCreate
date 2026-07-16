import unittest

from rag.calculator import calculate


class CalculatorTests(unittest.TestCase):
    def test_calculates_yearly_amount_from_daily_cost(self):
        result = calculate("一日の利用料金が56円の場合、年間いくら？")
        self.assertEqual(result, 20440.0)


if __name__ == "__main__":
    unittest.main()
