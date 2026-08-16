# SPDX-License-Identifier: GPL-3.0-only

import unittest

from velvet_event_protocol.learning_session_events import (
    ELIGIBILITY_CHECKED,
    INSUFFICIENT_EVIDENCE,
    REVIEW_PENDING,
    SESSION_ABORTED,
    SESSION_COMPLETED,
    SESSION_DEGRADED,
    SESSION_OPENED,
    SESSION_PAUSED,
    SESSION_PROPOSED,
    SESSION_STUDYING,
    LearningSessionEventRecord,
    build_learning_session_event,
    validate_learning_session_event,
)


class LearningSessionEventTests(unittest.TestCase):
    def record(self, state="PROPOSED", **changes):
        values = {
            "session_id": "learning-session-001",
            "body_id": "founder",
            "node_id": "velvet-founder",
            "subject_ref": "study-subject-001",
            "state": state,
            "evidence_refs": ("evidence-001",),
            "reason_code": "owner_requested",
        }
        values.update(changes)
        return LearningSessionEventRecord(**values)

    def test_proposed_event_is_transport_only_and_non_authoritative(self):
        event = build_learning_session_event(
            source="velvet-ai-core",
            event_type=SESSION_PROPOSED,
            record=self.record(),
        )
        self.assertTrue(event.payload["transport_only"])
        self.assertFalse(event.payload["canonical"])
        self.assertEqual(event.payload["authority"], "none")
        self.assertFalse(event.payload["grants_memory_write"])
        self.assertFalse(event.payload["grants_runtime_placement"])
        self.assertFalse(event.payload["grants_execution"])
        self.assertFalse(event.payload["grants_actuation"])
        self.assertFalse(event.payload["applies_learning_change"])
        validate_learning_session_event(event)

    def test_state_must_match_event_type(self):
        with self.assertRaisesRegex(ValueError, "state does not match"):
            self.record(state="OPEN").to_payload(SESSION_PROPOSED)

    def test_simulated_evidence_provenance_is_preserved(self):
        event = build_learning_session_event(
            source="velvet-ai-core",
            event_type=SESSION_STUDYING,
            record=self.record(
                state="STUDYING",
                evidence_refs=("ghost-can-001", "manual-001"),
                simulated_evidence_refs=("ghost-can-001",),
                workspace_refs=("cog-001",),
                reason_code="bounded_study",
            ),
        )
        self.assertEqual(event.payload["simulated_evidence_refs"], ["ghost-can-001"])

    def test_simulated_refs_must_be_real_session_evidence_refs(self):
        with self.assertRaisesRegex(ValueError, "simulated evidence refs"):
            self.record(
                state="STUDYING",
                simulated_evidence_refs=("ghost-can-missing",),
            ).to_payload(SESSION_STUDYING)

    def test_raw_study_material_is_rejected(self):
        for key, value in (
            ("objective", "study the whole repair manual"),
            ("prompt", "explain this"),
            ("content", "copied library page"),
            ("url", "https://example.invalid"),
            ("capability_token", "forbidden"),
            ("executor", "also-forbidden"),
        ):
            with self.assertRaisesRegex(ValueError, "forbidden"):
                self.record(data={key: value}).to_payload(SESSION_PROPOSED)

    def test_compact_reason_codes_only(self):
        with self.assertRaisesRegex(ValueError, "reason_code"):
            self.record(reason_code="this is prose").to_payload(SESSION_PROPOSED)

    def test_plain_transport_envelope_is_supported(self):
        payload = self.record(state="PAUSED", reason_code="priority_work").to_payload(
            SESSION_PAUSED
        )
        validate_learning_session_event(
            {
                "event_type": SESSION_PAUSED,
                "source_id": "velvet-ai-core",
                "sequence": 7,
                "occurred_at_monotonic_ns": 10,
                "payload": payload,
            }
        )

    def test_all_lifecycle_events_have_fixed_state(self):
        cases = (
            (SESSION_PROPOSED, "PROPOSED"),
            (ELIGIBILITY_CHECKED, "ELIGIBILITY_CHECK"),
            (SESSION_OPENED, "OPEN"),
            (SESSION_STUDYING, "STUDYING"),
            (REVIEW_PENDING, "REVIEW_PENDING"),
            (SESSION_PAUSED, "PAUSED"),
            (SESSION_DEGRADED, "DEGRADED"),
            (INSUFFICIENT_EVIDENCE, "INSUFFICIENT_EVIDENCE"),
            (SESSION_COMPLETED, "COMPLETED"),
            (SESSION_ABORTED, "ABORTED"),
        )
        for event_type, state in cases:
            with self.subTest(event_type=event_type):
                event = build_learning_session_event(
                    source="velvet-ai-core",
                    event_type=event_type,
                    record=self.record(state=state, reason_code="lifecycle_transition"),
                )
                self.assertEqual(event.payload["state"], state)


if __name__ == "__main__":
    unittest.main()
