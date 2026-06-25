import unittest

from memory_reference import MemoryReference


class MemoryReferenceNumericValidationTests(unittest.TestCase):
    def test_non_numeric_confidence_is_rejected(self):
        with self.assertRaises(ValueError):
            MemoryReference("memory-1", "fact", "accepted", "high").to_payload()


if __name__ == "__main__":
    unittest.main()
