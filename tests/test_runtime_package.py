# SPDX-License-Identifier: GPL-3.0-only

import ast
import unittest
from pathlib import Path

from velvet_event_protocol import EventBus, EventEnforcer, UnauthorizedEventError, VelvetEvent


ROOT = Path(__file__).resolve().parents[1]


class RuntimePackageTests(unittest.TestCase):
    def test_runtime_keyword_publish_reaches_subscriber(self):
        bus = EventBus()
        received = []
        bus.subscribe(received.append)
        enforcer = EventEnforcer(bus=bus, receipt_validator=lambda receipt_id: True)

        event = enforcer.publish(event_type="TEST_PING", payload={"value": 1})

        self.assertEqual(received, [event])
        self.assertEqual(event.source, "velvet-runtime")
        self.assertEqual(event.payload, {"value": 1})

    def test_actuation_without_receipt_fails_closed(self):
        bus = EventBus()
        enforcer = EventEnforcer(bus=bus, receipt_validator=lambda receipt_id: True)

        with self.assertRaises(UnauthorizedEventError):
            enforcer.publish(event_type="ACTUATION", payload={})

    def test_invalid_actuation_receipt_fails_closed(self):
        bus = EventBus()
        enforcer = EventEnforcer(bus=bus, receipt_validator=lambda receipt_id: False)

        with self.assertRaises(UnauthorizedEventError):
            enforcer.publish(
                event_type="ACTUATION",
                payload={},
                receipt_id="receipt_invalid",
            )

    def test_existing_event_publish_shape_remains_supported(self):
        published = []
        enforcer = EventEnforcer(publish_fn=published.append)
        event = VelvetEvent(event_type="OBSERVATION", source="test", payload={})

        self.assertIs(enforcer.publish(event), event)
        self.assertEqual(published, [event])

    def test_package_parses_as_python38(self):
        for relative_path in (
            "velvet_event_protocol/__init__.py",
            "velvet_event_protocol/event_schema.py",
            "velvet_event_protocol/event_bus.py",
            "velvet_event_protocol/enforcer.py",
        ):
            source = (ROOT / relative_path).read_text(encoding="utf-8")
            ast.parse(source, filename=relative_path, feature_version=8)


if __name__ == "__main__":
    unittest.main()
