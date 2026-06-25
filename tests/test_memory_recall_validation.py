import unittest

from memory_recall_result import MemoryRecallResult


class MemoryRecallValidationTests(unittest.TestCase):
    def test_invalid_score_is_rejected(self):
        with self.assertRaises(ValueError):
            MemoryRecallResult("memory-1", 1.1, 1.0, 1.0, 1.0, 1.0).to_payload()


if __name__ == "__main__":
    unittest.main()
