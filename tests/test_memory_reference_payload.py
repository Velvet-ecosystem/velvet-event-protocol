import unittest

from memory_reference import MemoryReference


class MemoryReferencePayloadTests(unittest.TestCase):
    def test_payload_contains_expected_fields(self):
        payload = MemoryReference("memory-1", "fact", "accepted").to_payload()
        self.assertIn("event_id", payload)
        self.assertIn("kind", payload)
        self.assertIn("status", payload)


if __name__ == "__main__":
    unittest.main()
