import unittest

from memory_reference import MemoryReference


class MemoryReferenceValidationTests(unittest.TestCase):
    def test_invalid_reference_is_rejected(self):
        with self.assertRaises(ValueError):
            MemoryReference("", "fact", "accepted").to_payload()


if __name__ == "__main__":
    unittest.main()
