import unittest

from memory_recall_result import MemoryRecallResult


class MemoryRecallResultTests(unittest.TestCase):
    def test_result_payload(self):
        payload = MemoryRecallResult(
            event_id="memory-1",
            score=0.8,
            association=1.0,
            confidence=0.9,
            salience=0.7,
            status_weight=1.0,
        ).to_payload()
        self.assertEqual(payload["event_id"], "memory-1")
        self.assertEqual(payload["score"], 0.8)


if __name__ == "__main__":
    unittest.main()
