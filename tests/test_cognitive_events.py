# SPDX-License-Identifier: GPL-3.0-only

import copy
import unittest

from cognitive_events import (
    ACTION_TRACKING_FINISHED,
    ACTION_TRACKING_STARTED,
    BOUNDARY_PROPOSED,
    CONNECTION_HEALTH_CHANGED,
    EPISODE_PROPOSED,
    EVENT_CLOSED,
    EVENT_OPENED,
    EVENT_UPDATED,
    HEALTH_CHANGED,
    INTERRUPT_ACCEPTED,
    INTERRUPT_CANDIDATE,
    MODULATORS_SNAPSHOTTED,
    PREDICTION_CREATED,
    PREDICTION_ERROR,
    PREDICTION_RESOLVED,
    PROPOSAL_CONTEXT,
    CognitiveEventRecord,
    build_cognitive_event,
    validate_cognitive_event,
)


class CognitiveEventTests(unittest.TestCase):
    def record(self, data, **overrides):
        values = {
            "cognitive_event_id": "cog-entry-001",
            "node_id": "queen-01",
            "body_id": "tiburon-01",
            "source_refs": ("obs-presence-001",),
            "correlation_ids": ("trace-entry-001",),
            "monotonic_time": 100.0,
            "data": data,
        }
        values.update(overrides)
        return CognitiveEventRecord(**values)

    def event(self, event_type, data, **overrides):
        return build_cognitive_event(
            source="velvet-ai-core",
            event_type=event_type,
            record=self.record(data, **overrides),
        )

    def test_open_event_is_interpretation_only(self):
        event = self.event(EVENT_OPENED, {
            "mode": "OBSERVE",
            "lifecycle_state": "OPEN",
            "event_kind": "vehicle_entry",
            "confidence": 0.72,
            "freshness_state": "fresh",
            "observation_refs": ["obs-presence-001"],
        })
        self.assertTrue(event.payload["interpretation_only"])
        self.assertFalse(event.payload["canonical_evidence"])
        self.assertFalse(event.payload["grants_authority"])
        validate_cognitive_event(event)

    def test_terminal_state_requires_closed_event_and_reason(self):
        with self.assertRaisesRegex(ValueError, "terminal lifecycle_state"):
            self.event(EVENT_UPDATED, {
                "mode": "OBSERVE",
                "lifecycle_state": "COMPLETED",
                "event_kind": "vehicle_entry",
                "confidence": 0.9,
                "freshness_state": "fresh",
            })
        with self.assertRaisesRegex(ValueError, "completion_reason"):
            self.event(EVENT_CLOSED, {
                "mode": "TRACK_ACTION",
                "lifecycle_state": "COMPLETED",
                "event_kind": "vehicle_entry",
                "confidence": 0.9,
                "freshness_state": "fresh",
            })

    def test_boundary_is_evidence_linked(self):
        event = self.event(BOUNDARY_PROPOSED, {
            "boundary_id": "boundary-001",
            "boundary_type": "completion",
            "recommended_terminal_state": "COMPLETED",
            "evidence_refs": ["obs-unlocked-001"],
            "confidence": 0.94,
        })
        validate_cognitive_event(event)

    def test_prediction_is_pending_and_falsifiable(self):
        event = self.event(PREDICTION_CREATED, {
            "prediction_id": "prediction-001",
            "subject": "driver_door_lock",
            "expected_state": {"lock_state": "unlocked"},
            "expected_by": 100.7,
            "tolerance": {"late_ms": 50},
            "confidence": 0.91,
            "source_model": "door-state-rules",
            "source_version": "1.0",
            "observation_refs": ["obs-auth-ok"],
            "status": "pending",
        })
        self.assertEqual(event.payload["status"], "pending")
        validate_cognitive_event(event)

    def test_nested_authority_field_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "forbidden authority fields"):
            self.event(PREDICTION_CREATED, {
                "prediction_id": "prediction-001",
                "subject": "driver_door_lock",
                "expected_state": {"result": {"executor_name": "lock-writer"}},
                "expected_by": 100.7,
                "confidence": 0.91,
                "source_model": "door-state-rules",
                "source_version": "1.0",
                "status": "pending",
            })

    def test_unknown_prediction_resolution_is_preserved(self):
        event = self.event(PREDICTION_RESOLVED, {
            "prediction_id": "prediction-001",
            "status": "unknown",
            "observed_state": {},
            "confidence": 0.4,
            "observation_refs": [],
            "receipt_refs": [],
        })
        self.assertEqual(event.payload["status"], "unknown")
        validate_cognitive_event(event)

    def test_prediction_error_cannot_retry(self):
        event = self.event(PREDICTION_ERROR, {
            "prediction_error_id": "error-001",
            "prediction_id": "prediction-001",
            "error_class": "timeout",
            "observed_state": {"lock_state": "unobserved"},
            "confidence": 0.99,
            "receipt_refs": [],
            "automatic_retry_requested": False,
        })
        tampered = event.to_dict()
        tampered["payload"] = copy.deepcopy(event.payload)
        tampered["payload"]["automatic_retry_requested"] = True
        with self.assertRaisesRegex(ValueError, "automatic retry"):
            validate_cognitive_event(tampered)

    def test_interrupt_never_authorizes_safeing(self):
        event = self.event(INTERRUPT_CANDIDATE, {
            "interrupt_id": "interrupt-001",
            "priority": 0.8,
            "reason": "impact-like acceleration",
            "accumulated_score": 0.75,
            "threshold": 0.8,
            "requires_immediate_safeing": True,
            "safe_state_reached": "unknown",
            "safeing_authorized": False,
            "safeing_performed": False,
            "outstanding_effect_refs": [],
        })
        validate_cognitive_event(event)

    def test_accepted_interrupt_requires_threshold_and_target(self):
        with self.assertRaisesRegex(ValueError, "meet threshold"):
            self.event(INTERRUPT_ACCEPTED, {
                "interrupt_id": "interrupt-001",
                "priority": 0.9,
                "reason": "medical distress",
                "accumulated_score": 0.7,
                "threshold": 0.8,
                "requires_immediate_safeing": True,
                "safe_state_reached": "unknown",
                "safeing_authorized": False,
                "safeing_performed": False,
                "outstanding_effect_refs": [],
                "interrupted_event_id": "cog-entry-001",
            })

    def test_proposal_context_is_not_permission(self):
        event = self.event(PROPOSAL_CONTEXT, {
            "proposal_ref": "intent-unlock-001",
            "confidence": 0.95,
            "observation_refs": ["obs-auth-ok"],
            "prediction_refs": [],
            "interruption_refs": [],
            "proposal_only": True,
        })
        self.assertTrue(event.payload["proposal_only"])
        validate_cognitive_event(event)

    def test_action_tracking_requires_external_refs(self):
        with self.assertRaisesRegex(ValueError, "authorization_ref"):
            self.event(ACTION_TRACKING_STARTED, {
                "tracking_id": "track-001",
                "state": "started",
                "authorization_ref": "",
                "execution_ref": "execution-001",
                "tracking_only": True,
            })
        event = self.event(ACTION_TRACKING_STARTED, {
            "tracking_id": "track-001",
            "state": "started",
            "authorization_ref": "court-decision-001",
            "execution_ref": "execution-001",
            "tracking_only": True,
            "observation_refs": [],
            "receipt_refs": [],
            "outstanding_effect_refs": [],
        })
        validate_cognitive_event(event)

    def test_finished_tracking_cannot_still_be_started(self):
        with self.assertRaisesRegex(ValueError, "terminal state"):
            self.event(ACTION_TRACKING_FINISHED, {
                "tracking_id": "track-001",
                "state": "started",
                "authorization_ref": "court-decision-001",
                "execution_ref": "execution-001",
                "tracking_only": True,
            })

    def test_episode_remains_navigation_only(self):
        event = self.event(EPISODE_PROPOSED, {
            "episode_id": "episode-001",
            "summary": "Owner approached and the unlock was confirmed.",
            "retention_class": "operational",
            "confidence": 0.93,
            "receipt_refs": ["receipt-exec-001"],
            "actors": ["owner"],
            "locations": ["driver_door"],
            "what_changed": ["lock became unlocked"],
            "proposal_refs": ["intent-unlock-001"],
            "authorization_refs": ["court-decision-001"],
            "execution_refs": ["execution-001"],
            "outcome_refs": ["obs-unlocked-001"],
            "prediction_error_refs": [],
            "interruption_refs": [],
            "memory_navigation_only": True,
        })
        self.assertFalse(event.payload["canonical_evidence"])
        validate_cognitive_event(event)

    def test_modulators_are_allowlisted_and_bounded(self):
        event = self.event(MODULATORS_SNAPSHOTTED, {
            "snapshot_id": "mod-001",
            "values": {"uncertainty": 0.7, "urgency": 0.2},
            "trust_context": "owner-local-verified",
            "cannot_change_authority": True,
        })
        validate_cognitive_event(event)
        with self.assertRaisesRegex(ValueError, "unknown modulators"):
            self.event(MODULATORS_SNAPSHOTTED, {
                "snapshot_id": "mod-002",
                "values": {"curiosity": 1.0},
                "trust_context": "owner-local-verified",
                "cannot_change_authority": True,
            })

    def test_connection_health_exposes_degradation(self):
        event = self.event(CONNECTION_HEALTH_CHANGED, {
            "connection_id": "camera-to-segmenter",
            "source_component": "camera-observer",
            "destination_component": "event-segmenter",
            "signal_type": "visual.observation",
            "maximum_latency_ms": 100.0,
            "stale_after_ms": 250.0,
            "observed_latency_ms": 180.0,
        }, health_state="degraded", degraded_reasons=("latency-over-budget",))
        validate_cognitive_event(event)

    def test_component_health_is_transport_only(self):
        event = self.event(HEALTH_CHANGED, {
            "component": "event-segmenter",
            "latency_ms": 350.0,
        }, health_state="degraded", degraded_reasons=("fixture-delay",))
        self.assertFalse(event.payload["grants_execution"])
        validate_cognitive_event(event)

    def test_fixture_and_replay_states_are_explicit(self):
        event = self.event(EVENT_OPENED, {
            "mode": "OBSERVE",
            "lifecycle_state": "OPEN",
            "event_kind": "vehicle_entry",
            "confidence": 0.72,
            "freshness_state": "fresh",
        }, replay_state="fixture")
        self.assertEqual(event.payload["replay_state"], "fixture")
        self.assertTrue(event.payload["replay_safe"])

    def test_metadata_authority_escalation_is_rejected(self):
        event = self.event(EVENT_OPENED, {
            "mode": "OBSERVE",
            "lifecycle_state": "OPEN",
            "event_kind": "vehicle_entry",
            "confidence": 0.72,
            "freshness_state": "fresh",
        })
        document = event.to_dict()
        document["metadata"] = copy.deepcopy(event.metadata)
        document["metadata"]["authority"] = "court"
        with self.assertRaisesRegex(ValueError, "metadata cannot carry authority"):
            validate_cognitive_event(document)

    def test_same_record_produces_same_payload(self):
        record = self.record({
            "prediction_id": "prediction-001",
            "subject": "driver_door_lock",
            "expected_state": {"lock_state": "unlocked"},
            "expected_by": 100.7,
            "confidence": 0.91,
            "source_model": "door-state-rules",
            "source_version": "1.0",
            "status": "pending",
        })
        first = build_cognitive_event(source="core", event_type=PREDICTION_CREATED, record=record)
        second = build_cognitive_event(source="core", event_type=PREDICTION_CREATED, record=record)
        self.assertEqual(first.payload, second.payload)
        self.assertEqual(first.metadata, second.metadata)


if __name__ == "__main__":
    unittest.main()
