import unittest
from calculator import Calculator

class TestOperations(unittest.TestCase):

    def setUp(self):
        self.calc = Calculator(8,2)
    def test_sum(self):
        answer = self.calc.get_sum()
        print(f'The answer was from test_sum with 8,2 input was: {answer}')
        self.assertEqual(calc.get_sum(), 10, 'The answer was not 10')

    def test_diff(self):
        calc = Calculator(8,2)
        answer = calc.get_difference()
        print(f'The answer from test_diff was: {answer}')
        self.assertEqual(answer, 6, 'The answer was not 6')

    def test_product(self):
        calc = Calculator(8,2)
        answer = calc.get_product()
        print(f'The answer from test_product was: {answer}')
        self.assertEqual(answer, 16, 'The answer was not 16')

    def test_quotient(self):
        calc = Calculator(8,2)
        answer = calc.get_quotient()
        print(f'The answer is: {answer}')
        self.assertEqual(answer, 4, 'The answer was not 4' )

if __name__ == "__main__":
    unittest.main()
