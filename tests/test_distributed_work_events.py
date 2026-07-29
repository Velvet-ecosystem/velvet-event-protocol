# SPDX-License-Identifier: GPL-3.0-only

import unittest

from distributed_work_events import (
    NODE_ADVERTISEMENT_PUBLISHED,
    WORK_ACCEPTED,
    WORK_COMPLETED,
    WORK_DEGRADED,
    WORK_HANDOFF_REQUESTED,
    WORK_OFFERED,
    WORK_RECOVERY_REASSIGNED,
    WORK_REFUSED,
    NodeAdvertisement,
    WorkLifecycleRecord,
    build_distributed_work_event,
    build_node_advertisement_event,
    validate_distributed_work_event,
)


class DistributedWorkEventTests(unittest.TestCase):
    def advertisement(self, **overrides):
        values = {
            "node_id": "velour-01",
            "body_id": "velvet-founder",
            "organ": "velour",
            "tier": "specialist_linux",
            "capabilities": ("logging", "receipt-indexing"),
            "current_load": 0.25,
            "health": 0.96,
            "availability": "available",
            "last_heartbeat": 100.0,
            "max_concurrent_tasks": 3,
            "current_tasks": 1,
            "accepted_work_classes": ("logging", "indexing"),
            "overflow_capabilities": ("sensor-filtering",),
            "temporary_absorption_capabilities": ("security-log",),
            "fallback_options": ("queen",),
        }
        values.update(overrides)
        return NodeAdvertisement(**values)

    def record(self, event_type, **overrides):
        values = {
            "event_type": event_type,
            "work_id": "work-001",
            "work_class": "logging",
            "required_capabilities": ("logging",),
        }
        values.update(overrides)
        return WorkLifecycleRecord(**values)

    def test_builds_transport_only_node_advertisement(self):
        event = build_node_advertisement_event(
            source="velvet-runtime",
            advertisement=self.advertisement(),
        )
        self.assertEqual(event.event_type, NODE_ADVERTISEMENT_PUBLISHED)
        self.assertEqual(event.payload["authority"], "none")
        self.assertTrue(event.payload["transport_only"])
        self.assertFalse(event.payload["grants_authority"])
        self.assertFalse(event.payload["grants_execution"])
        self.assertFalse(event.payload["grants_actuation"])
        validate_distributed_work_event(event)

    def test_advertisement_carries_small_node_limits_without_reducing_importance(self):
        event = build_node_advertisement_event(
            source="velvet-runtime",
            advertisement=self.advertisement(
                node_id="audio-tiny",
                organ="audio",
                capabilities=("wake-word",),
                max_concurrent_tasks=1,
                current_tasks=0,
            ),
        )
        self.assertEqual(event.payload["max_concurrent_tasks"], 1)
        self.assertEqual(event.payload["capabilities"], ["wake-word"])
        validate_distributed_work_event(event)

    def test_rejects_invalid_advertised_load(self):
        with self.assertRaisesRegex(ValueError, "current_load"):
            self.advertisement(current_load=1.1).to_payload()

    def test_work_offer_requires_capabilities(self):
        with self.assertRaisesRegex(ValueError, "requires capabilities"):
            self.record(WORK_OFFERED, required_capabilities=()).to_payload()

    def test_builds_work_offer_without_selecting_executor(self):
        event = build_distributed_work_event(
            source="velvet-native-brain",
            record=self.record(
                WORK_OFFERED,
                court_authorization_required=True,
                fallback_options=("partial", "observe-only"),
            ),
        )
        self.assertTrue(event.payload["court_authorization_required"])
        self.assertNotIn("executor_name", event.payload)
        self.assertFalse(event.payload["grants_execution"])
        validate_distributed_work_event(event)

    def test_acceptance_carries_runtime_lease_but_no_authority(self):
        event = build_distributed_work_event(
            source="velvet-runtime",
            record=self.record(
                WORK_ACCEPTED,
                node_id="velour-01",
                organ="velour",
                placement_mode="primary",
                lease_id="work-001:velour-01",
                lease_expires_at=160.0,
                important_result=True,
            ),
        )
        self.assertEqual(event.payload["lease_id"], "work-001:velour-01")
        self.assertTrue(event.payload["escalate_to_queen"])
        self.assertEqual(event.payload["authority"], "none")
        validate_distributed_work_event(event)

    def test_refusal_requires_clear_reason(self):
        with self.assertRaisesRegex(ValueError, "missing fields"):
            self.record(
                WORK_REFUSED,
                node_id="velour-01",
                organ="velour",
            ).to_payload()

    def test_handoff_names_source_and_reason(self):
        event = build_distributed_work_event(
            source="velvet-runtime",
            record=self.record(
                WORK_HANDOFF_REQUESTED,
                from_node_id="audio-01",
                reason="load-limit-reached",
                fallback_options=("audio-02", "queen"),
            ),
        )
        self.assertEqual(event.payload["from_node_id"], "audio-01")
        self.assertEqual(event.payload["fallback_options"], ["audio-02", "queen"])
        validate_distributed_work_event(event)

    def test_completion_escalates_important_result_to_queen(self):
        event = build_distributed_work_event(
            source="velvet-runtime",
            record=self.record(
                WORK_COMPLETED,
                node_id="security-01",
                organ="security",
                result_status="completed",
                important_result=True,
            ),
        )
        self.assertTrue(event.payload["important_result"])
        self.assertTrue(event.payload["escalate_to_queen"])
        validate_distributed_work_event(event)

    def test_degradation_is_explicit_not_hidden(self):
        event = build_distributed_work_event(
            source="velvet-runtime",
            record=self.record(
                WORK_DEGRADED,
                degradation_mode="observe_only",
                reason="full-audio-pipeline-unavailable",
                fallback_options=("push-to-talk",),
            ),
        )
        self.assertEqual(event.payload["degradation_mode"], "observe_only")
        self.assertEqual(event.payload["fallback_options"], ["push-to-talk"])
        validate_distributed_work_event(event)

    def test_recovery_reassignment_names_both_organs(self):
        event = build_distributed_work_event(
            source="velvet-runtime",
            record=self.record(
                WORK_RECOVERY_REASSIGNED,
                from_node_id="velour-01",
                to_node_id="queen-01",
                placement_mode="queen_fallback",
                lease_id="work-001:queen-01",
                lease_expires_at=240.0,
                reason="stale-heartbeat",
            ),
        )
        self.assertEqual(event.payload["from_node_id"], "velour-01")
        self.assertEqual(event.payload["to_node_id"], "queen-01")
        self.assertFalse(event.payload["grants_authority"])
        validate_distributed_work_event(event)

    def test_rejects_nested_authority_field(self):
        event = build_distributed_work_event(
            source="velvet-runtime",
            record=self.record(WORK_OFFERED),
        )
        event.payload["fallback_options"] = [{"executor_name": "can-writer"}]
        with self.assertRaisesRegex(ValueError, "forbidden authority fields"):
            validate_distributed_work_event(event)

    def test_rejects_transport_flag_escalation(self):
        event = build_distributed_work_event(
            source="velvet-runtime",
            record=self.record(WORK_OFFERED),
        )
        event.payload["grants_execution"] = True
        with self.assertRaisesRegex(ValueError, "grants_execution"):
            validate_distributed_work_event(event)

    def test_rejects_authority_in_metadata(self):
        event = build_distributed_work_event(
            source="velvet-runtime",
            record=self.record(WORK_OFFERED),
        )
        event.metadata["authority"] = "runtime"
        with self.assertRaisesRegex(ValueError, "metadata cannot carry authority"):
            validate_distributed_work_event(event)

    def test_same_record_produces_same_contract_payload(self):
        record = self.record(
            WORK_ACCEPTED,
            node_id="velour-01",
            organ="velour",
            placement_mode="overflow",
            lease_id="work-001:velour-01",
            lease_expires_at=180.0,
        )
        first = build_distributed_work_event(source="velvet-runtime", record=record)
        second = build_distributed_work_event(source="velvet-runtime", record=record)
        self.assertEqual(first.payload, second.payload)
        self.assertEqual(first.metadata, second.metadata)


if __name__ == "__main__":
    unittest.main()
