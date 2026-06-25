import unittest

from memory_event_types import MEMORY_RECALL_RESULTS, MEMORY_REFERENCE_OBSERVED


class MemoryEventTypeTests(unittest.TestCase):
    def test_constants_are_stable(self):
        self.assertEqual(MEMORY_REFERENCE_OBSERVED, "MEMORY_REFERENCE_OBSERVED")
        self.assertEqual(MEMORY_RECALL_RESULTS, "MEMORY_RECALL_RESULTS")


if __name__ == "__main__":
    unittest.main()
