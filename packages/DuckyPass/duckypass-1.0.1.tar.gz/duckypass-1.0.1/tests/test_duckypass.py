import unittest
from unittest.mock import patch
from duckypassapi.duckypass import DuckyPassAPI

class TestDuckyPassAPI(unittest.TestCase):

    @patch('duckypassapi.duckypass.requests.get')
    def test_generate_simple_password(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'simple_password'
        
        result = DuckyPassAPI('simple', 1)
        self.assertEqual(result, 'simple_password')

    @patch('duckypassapi.duckypass.requests.get')
    def test_generate_secure_password(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'passwords': ['secure_password1', 'secure_password2']}
        
        result = DuckyPassAPI('secure', 2)
        self.assertEqual(result, ['secure_password1', 'secure_password2'])

    @patch('duckypassapi.duckypass.requests.get')
    def test_invalid_password_type(self, mock_get):
        with self.assertRaises(ValueError):
            DuckyPassAPI('invalid_type', 1)

    @patch('duckypassapi.duckypass.requests.get')
    def test_invalid_count(self, mock_get):
        with self.assertRaises(ValueError):
            DuckyPassAPI('simple', 0)

    @patch('duckypassapi.duckypass.requests.get')
    def test_api_failure(self, mock_get):
        mock_get.return_value.status_code = 500
        mock_get.return_value.text = 'Internal Server Error'
        
        with self.assertRaises(Exception) as context:
            DuckyPassAPI('simple', 1)
        self.assertIn('Failed to generate password(s)', str(context.exception))

if __name__ == '__main__':
    unittest.main()