import unittest

from memory_reference import MemoryReference


class MemoryReferenceOptionalFieldTests(unittest.TestCase):
    def test_optional_fields_can_be_absent(self):
        payload = MemoryReference("memory-1", "fact", "accepted").to_payload()
        self.assertNotIn("confidence", payload)
        self.assertNotIn("receipt_id", payload)


if __name__ == "__main__":
    unittest.main()
