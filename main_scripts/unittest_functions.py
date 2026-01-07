import unittest
import os
from cleanse_library_data import calculate_date_difference, generate_book_description


class TestOperations(unittest.TestCase):
    def setUp(self):
        api_key = os.getenv("AI_API_KEY")
        self.assertGreater(len(api_key), 5)

    def test_date_difference(self):
        diff = calculate_date_difference("01/01/2024", "05/01/2024")
        print(f"the answer was {diff}")
        self.assertEqual(diff, 4, 'the answer was not 4')

    def test_book_description(self):
        response = generate_book_description("The Highikers Guide to the Galaxy", os.getenv("AI_API_KEY"))
        print(f"The answer was {response}")
        self.assertEqual(type(response), str, 'the result was not a string type')
        self.assertGreater(len(response), 10, 'the result was not greater than 10 characters.')

if __name__ == '__main__':
    unittest.main()