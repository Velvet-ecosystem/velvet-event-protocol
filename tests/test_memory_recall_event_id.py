import unittest

from memory_recall_result import MemoryRecallResult


class MemoryRecallEventIdTests(unittest.TestCase):
    def test_event_id_is_preserved(self):
        payload = MemoryRecallResult("memory-1", 0.8, 1.0, 0.9, 0.7, 1.0).to_payload()
        self.assertEqual(payload["event_id"], "memory-1")


if __name__ == "__main__":
    unittest.main()
