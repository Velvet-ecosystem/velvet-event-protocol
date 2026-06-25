import unittest

from memory_reference import MemoryReference


class MemoryReferenceTextValidationTests(unittest.TestCase):
    def test_blank_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            MemoryReference("memory-1", "", "accepted").to_payload()


if __name__ == "__main__":
    unittest.main()
