import unittest
from unittest.mock import patch, MagicMock
import requests

from cleanse_library_data import generate_book_description_local


class TestGenerateBookDescriptionLocal(unittest.TestCase):

    @patch("cleanse_library_data.requests.post")
    def test_generate_book_description_success(self, mock_post):
        # Arrange: fake successful Ollama response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "response": "A classic novel about ambition and unintended consequences."
        }
        mock_post.return_value = mock_response

        # Act
        result = generate_book_description_local("Frankenstein")

        # Assert result
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 10)
        self.assertIn("novel", result.lower())

        # Assert request (robust: don’t lock to exact prompt wording)
        self.assertEqual(mock_post.call_count, 1)
        called_args, called_kwargs = mock_post.call_args

        # URL
        self.assertEqual(called_args[0], "http://ai_model:11434/api/generate")

        # Timeout
        self.assertEqual(called_kwargs.get("timeout"), 30)

        # JSON body
        body = called_kwargs.get("json")
        self.assertIsInstance(body, dict)

        self.assertEqual(body.get("model"), "llama3.2:1b")
        self.assertEqual(body.get("stream"), False)

        prompt = body.get("prompt", "")
        self.assertIn("Frankenstein", prompt)

        # Options are expected in the newer implementation; if you later remove them,
        # change this to conditional asserts.
        self.assertIn("options", body)
        self.assertIn("num_predict", body["options"])

    @patch("cleanse_library_data.requests.post")
    def test_generate_book_description_http_error(self, mock_post):
        # Arrange: simulate HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response

        # Act / Assert
        with self.assertRaises(requests.HTTPError):
            generate_book_description_local("1984")


if __name__ == "__main__":
    unittest.main()
