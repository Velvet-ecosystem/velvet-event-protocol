import unittest

from memory_event_builders import build_memory_recall_event
from memory_recall_result import MemoryRecallResult


class MemoryEventBuilderMinimalTests(unittest.TestCase):
    def test_recall_event_count(self):
        event = build_memory_recall_event(
            "velvet-runtime",
            "query-1",
            [MemoryRecallResult("memory-1", 0.8, 1.0, 0.9, 0.7, 1.0)],
        )
        self.assertEqual(event.payload["result_count"], 1)


if __name__ == "__main__":
    unittest.main()
