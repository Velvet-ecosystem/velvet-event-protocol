"""Generic event transport cannot turn receipt evidence into execution authority."""

import importlib
import unittest
from unittest.mock import Mock

from velvet_event_protocol import (
    EventBus, EventEnforcer, UnauthorizedEventError, VelvetEvent,
)


class ActuationBoundaryTests(unittest.TestCase):
    def test_receipts_and_source_allowlists_never_authorize_actuation(self):
        for receipt in (None, "", "denied", "unrelated", "expired", "replayed",
                        "tampered", "wrong-target", "apparently-valid"):
            for event_type in ("ACTUATION", "actuation", " ACTUATION "):
                with self.subTest(receipt=receipt, event_type=event_type):
                    published = []
                    verifier = Mock(return_value=True)
                    enforcer = EventEnforcer(
                        publish_fn=published.append,
                        receipt_validator=verifier,
                        allowed_actuation_sources={"velvet-runtime"},
                    )
                    with self.assertRaises(UnauthorizedEventError):
                        enforcer.publish(event_type=event_type, receipt_id=receipt,
                                         source="velvet-runtime", payload={"target": "bench"})
                    self.assertEqual(published, [])
                    verifier.assert_not_called()

    def test_missing_or_failed_verifier_cannot_admit_existing_event(self):
        for verifier in (None, Mock(return_value=False), Mock(side_effect=OSError("offline"))):
            with self.subTest(verifier=verifier):
                bus = EventBus()
                received = []
                bus.subscribe(received.append)
                enforcer = EventEnforcer(bus=bus, receipt_validator=verifier)
                event = VelvetEvent(event_type="ACTUATION", receipt_id="forged",
                                    source="velvet-runtime", payload={})
                with self.assertRaises(UnauthorizedEventError):
                    enforcer.publish(event)
                self.assertEqual(received, [])

    def test_same_event_is_rejected_on_every_replay(self):
        published = []
        enforcer = EventEnforcer(publish_fn=published.append)
        event = VelvetEvent(event_type="ACTUATION", receipt_id="reused")
        for _ in range(2):
            with self.assertRaises(UnauthorizedEventError):
                enforcer.publish(event)
        self.assertEqual(published, [])

    def test_observations_and_outcomes_keep_receipt_linkage(self):
        bus = EventBus()
        received = []
        bus.subscribe(received.append)
        enforcer = EventEnforcer(bus=bus)
        for name in ("OBSERVATION", "TELEMETRY", "COURT_DENIED", "EXECUTION_COMPLETED"):
            event = enforcer.publish(event_type=name, payload={"value": 1}, receipt_id="evidence")
            self.assertIs(received[-1], event)
            self.assertEqual(event.receipt_id, "evidence")
        self.assertEqual(len(received), 4)

    def test_legacy_enforcer_has_the_same_fail_closed_policy(self):
        legacy = importlib.import_module("event_enforcer")
        published = []
        enforcer = legacy.EventEnforcer(published.append, receipt_validator=lambda _: True,
                                       allowed_actuation_sources={"legacy"})
        with self.assertRaises(legacy.UnauthorizedEventError):
            enforcer.publish(VelvetEvent(event_type="ACTUATION", source="legacy",
                                        receipt_id="unrelated"))
        self.assertEqual(published, [])
        observation = VelvetEvent(event_type="OBSERVATION")
        enforcer.publish(observation)
        self.assertEqual(published, [observation])

    def test_legacy_wiring_uses_the_packaged_gate(self):
        wiring = importlib.import_module("runtime_wiring")
        runtime = wiring.build_event_runtime(receipt_validator=lambda _: True)
        received = []
        runtime["bus"].subscribe(received.append)
        with self.assertRaises(UnauthorizedEventError):
            runtime["publish"](VelvetEvent(event_type="ACTUATION", receipt_id="unrelated"))
        self.assertEqual(received, [])
        runtime["publish"](VelvetEvent(event_type="OBSERVATION"))
        self.assertEqual(len(received), 1)


if __name__ == "__main__":
    unittest.main()
