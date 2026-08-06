# SPDX-License-Identifier: GPL-3.0-only

import json
import unittest
from pathlib import Path

from cognitive_events import (
    ACTION_TRACKING_FINISHED,
    ACTION_TRACKING_STARTED,
    EPISODE_PROPOSED,
    EVENT_CLOSED,
    EVENT_OPENED,
    EVENT_UPDATED,
    PREDICTION_CREATED,
    PREDICTION_RESOLVED,
    PROPOSAL_CONTEXT,
    validate_cognitive_event,
)


class VehicleEntryFixtureTests(unittest.TestCase):
    def fixture(self):
        path = Path(__file__).parent / "fixtures" / "cognitive_vehicle_entry_v1.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_fixed_sequence_validates_without_authority(self):
        fixture = self.fixture()
        self.assertEqual(fixture, self.fixture())
        self.assertFalse(fixture["physical_execution_permitted"])
        expected = [
            EVENT_OPENED,
            EVENT_UPDATED,
            PROPOSAL_CONTEXT,
            PREDICTION_CREATED,
            ACTION_TRACKING_STARTED,
            PREDICTION_RESOLVED,
            ACTION_TRACKING_FINISHED,
            EVENT_CLOSED,
            EPISODE_PROPOSED,
        ]
        events = fixture["events"]
        self.assertEqual([event["event_type"] for event in events], expected)
        self.assertEqual(len({event["event_id"] for event in events}), len(events))
        for event in events:
            self.assertEqual(event["payload"]["replay_state"], "fixture")
            self.assertTrue(event["payload"]["replay_safe"])
            self.assertFalse(event["payload"]["grants_authority"])
            self.assertFalse(event["payload"]["grants_execution"])
            self.assertFalse(event["payload"]["grants_actuation"])
            validate_cognitive_event(event)

    def test_tracking_only_references_external_authority(self):
        tracking = self.fixture()["events"][4]
        self.assertEqual(tracking["payload"]["authorization_ref"], "court-decision-001")
        self.assertEqual(tracking["payload"]["execution_ref"], "execution-contract-001")
        self.assertTrue(tracking["payload"]["tracking_only"])
        self.assertNotIn("executor", tracking["payload"])
        self.assertNotIn("capability_token", tracking["payload"])

    def test_episode_stays_below_sources_and_receipts(self):
        episode = self.fixture()["events"][-1]
        self.assertTrue(episode["payload"]["memory_navigation_only"])
        self.assertFalse(episode["payload"]["canonical_evidence"])
        self.assertIn("receipt-execution-001", episode["payload"]["receipt_refs"])
        self.assertIn("obs-lock-unlocked-001", episode["payload"]["source_refs"])


if __name__ == "__main__":
    unittest.main()
