import unittest

from memory_event_builders import build_memory_reference_event
from memory_reference import MemoryReference


class MemoryEventMetadataTests(unittest.TestCase):
    def test_contract_metadata(self):
        event = build_memory_reference_event(
            "velvet-runtime",
            MemoryReference("memory-1", "fact", "accepted"),
        )
        self.assertEqual(event.metadata["contract"], "velvet.memory-reference.v1")


if __name__ == "__main__":
    unittest.main()
