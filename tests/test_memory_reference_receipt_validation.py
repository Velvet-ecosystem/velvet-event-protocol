import unittest

from memory_reference import MemoryReference


class MemoryReferenceReceiptValidationTests(unittest.TestCase):
    def test_blank_receipt_id_is_rejected(self):
        with self.assertRaises(ValueError):
            MemoryReference("memory-1", "fact", "accepted", receipt_id="").to_payload()


if __name__ == "__main__":
    unittest.main()
