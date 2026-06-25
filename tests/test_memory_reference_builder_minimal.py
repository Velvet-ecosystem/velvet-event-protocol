import unittest

from memory_event_builders import build_memory_reference_event
from memory_reference import MemoryReference


class MemoryReferenceBuilderMinimalTests(unittest.TestCase):
    def test_reference_event_type(self):
        event = build_memory_reference_event(
            "velvet-runtime",
            MemoryReference("memory-1", "fact", "accepted", 0.9),
        )
        self.assertEqual(event.event_type, "MEMORY_REFERENCE_OBSERVED")


if __name__ == "__main__":
    unittest.main()
