import importlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


class VelvetEvent:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestCoreActionBoundary(unittest.TestCase):
    def load_module(self):
        event_schema = MagicMock()
        event_schema.VelvetEvent = VelvetEvent
        receipt_module = MagicMock()
        receipt_module.Receipt = MagicMock
        receipt_logger_module = MagicMock()
        receipt_logger_module.ReceiptLogger = object
        modules = {
            "velvet_event_protocol": MagicMock(),
            "velvet_event_protocol.event_schema": event_schema,
            "receipt": receipt_module,
            "receipt_logger": receipt_logger_module,
        }
        with patch.dict(sys.modules, modules):
            sys.modules.pop("core_action", None)
            return importlib.import_module("core_action")

    def test_retired_action_helper_fails_closed(self):
        module = self.load_module()
        with self.assertRaises(RuntimeError):
            module.execute_authorized_action()

    def test_receipted_event_helper_refuses_actuation(self):
        module = self.load_module()
        with self.assertRaises(RuntimeError):
            module.publish_receipted_event(
                enforcer_publish=lambda event: None,
                receipt_logger=MagicMock(),
                event_type="ACTUATION",
                source="core",
                policy="LegacyPolicy",
                authorized_by="core",
            )

    def test_receipted_observation_may_be_published(self):
        module = self.load_module()
        logged_receipt = SimpleNamespace(receipt_id="receipt-1")
        logger = MagicMock()
        logger.log.return_value = logged_receipt
        published = []

        event = module.publish_receipted_event(
            enforcer_publish=published.append,
            receipt_logger=logger,
            event_type="EXECUTION_COMPLETED",
            source="velvet-runtime",
            policy="RuntimeExecutionContract",
            authorized_by="ApprovedExecutor",
            payload={"executor_name": "runtime-status"},
        )

        self.assertEqual(event.receipt_id, "receipt-1")
        self.assertEqual(event.event_type, "EXECUTION_COMPLETED")
        self.assertEqual(published, [event])


if __name__ == "__main__":
    unittest.main()
