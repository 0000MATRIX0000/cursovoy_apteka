import unittest
from unittest.mock import patch, mock_open, call
from game import save_result


class TestSaveResult(unittest.TestCase):
    def setUp(self):
        self.valid_cases = [
            # (name, score, minutes, seconds, expected_output)
            ("Иван", 500, 2, 30, "Иван: 500 очков, 02:30\n"),
            ("A", 0, 0, 0, "A: 0 очков, 00:00\n"),
            (" John ", 100, 1, 5, "John: 100 очков, 01:05\n")
        ]

        self.invalid_cases = [
            ("  ", 300, 1, 45),
            (None, 200, 0, 59),
            ("", 100, 0, 30),
            (123, 400, 0, 45),
            (["Name"], 500, 0, 0)
        ]

    @patch("builtins.open", new_callable=mock_open)
    def test_valid_names(self, mock_file):
        """Тестируем запись для корректных имен"""
        for name, score, m, s, expected in self.valid_cases:
            with self.subTest(name=name, score=score):
                save_result(name, score, m, s)
                mock_file().write.assert_has_calls([call(expected)])
                mock_file.reset_mock()

    @patch("builtins.open", new_callable=mock_open)
    def test_invalid_names(self, mock_file):
        """Тестируем пропуск некорректных данных"""
        for name, score, m, s in self.invalid_cases:
            with self.subTest(name=name, score=score):
                save_result(name, score, m, s)
                mock_file().write.assert_not_called()
                mock_file.reset_mock()

    @patch("builtins.open", side_effect=PermissionError("No write access"))
    def test_file_errors(self, mock_file):
        """Тестируем обработку ошибок файловой системы"""
        with self.assertLogs(level='ERROR') as cm:
            save_result("Test", 100, 0, 10)

        self.assertIn("Ошибка сохранения: No write access", cm.output[0])


if __name__ == "__main__":
    unittest.main()