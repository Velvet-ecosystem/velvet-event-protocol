# SPDX-License-Identifier: GPL-3.0-only

import copy
import unittest

from semantic_messages import (
    SEMANTIC_MESSAGE,
    SemanticMessageRecord,
    build_semantic_message,
    validate_semantic_message,
)


class SemanticMessageTests(unittest.TestCase):
    def record(self, **overrides):
        values = {
            "message_id": "msg-001",
            "sender_identity_id": "iris",
            "recipient_identity_ids": ("sarah",),
            "purpose": "request security interpretation",
            "speech_act": "question",
            "semantic_content": "Unknown person remains near the driver door; evaluate security significance.",
            "source_refs": ("identity:iris", "obs-camera-001"),
            "evidence_refs": ("obs-camera-001",),
            "confidence": 0.84,
            "urgency": "elevated",
            "privacy_scope": "role_local",
            "requested_response": "evaluate",
            "correlation_ids": ("incident-001",),
        }
        values.update(overrides)
        return SemanticMessageRecord(**values)

    def event(self, **overrides):
        return build_semantic_message(source="velvet-ai-core", record=self.record(**overrides))

    def test_semantic_message_is_authority_free(self):
        event = self.event()
        self.assertEqual(event.event_type, SEMANTIC_MESSAGE)
        self.assertTrue(event.payload["semantic_only"])
        self.assertTrue(event.payload["transport_only"])
        self.assertFalse(event.payload["canonical_evidence"])
        self.assertFalse(event.payload["grants_authority"])
        self.assertFalse(event.payload["grants_execution"])
        self.assertFalse(event.payload["grants_actuation"])
        self.assertFalse(event.payload["memory_write"])
        validate_semantic_message(event)

    def test_nancy_can_advise_charlotte_without_driving_authority(self):
        event = self.event(
            sender_identity_id="nancy",
            recipient_identity_ids=("charlotte",),
            purpose="share route context",
            speech_act="proposal",
            semantic_content="Planned turn is approximately 400 m ahead; evaluate against current driving context.",
            source_refs=("identity:nancy", "gnss-fix-001", "route-001"),
            evidence_refs=("gnss-fix-001", "route-001"),
            requested_response="evaluate",
        )
        self.assertEqual(event.payload["sender_identity_id"], "nancy")
        self.assertEqual(event.payload["recipient_identity_ids"], ["charlotte"])
        self.assertEqual(event.payload["authority"], "none")

    def test_sender_cannot_be_recipient(self):
        with self.assertRaisesRegex(ValueError, "sender cannot be a recipient"):
            self.event(recipient_identity_ids=("iris",))

    def test_multiple_recipients_are_supported(self):
        event = self.event(recipient_identity_ids=("sarah", "nyx"))
        self.assertEqual(event.payload["recipient_identity_ids"], ["sarah", "nyx"])

    def test_duplicate_recipients_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicates"):
            self.event(recipient_identity_ids=("sarah", "sarah"))

    def test_invalid_speech_act_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "speech_act"):
            self.event(speech_act="command")

    def test_invalid_privacy_scope_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "privacy_scope"):
            self.event(privacy_scope="secret_override")

    def test_invalid_requested_response_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "requested_response"):
            self.event(requested_response="execute")

    def test_confidence_is_bounded(self):
        with self.assertRaisesRegex(ValueError, "confidence"):
            self.event(confidence=1.1)

    def test_reply_links_without_changing_authority(self):
        event = self.event(
            message_id="msg-002",
            sender_identity_id="sarah",
            recipient_identity_ids=("iris",),
            purpose="answer visual security question",
            speech_act="statement",
            semantic_content="Current evidence is insufficient to classify the person as a security threat.",
            source_refs=("identity:sarah", "msg-001"),
            evidence_refs=("obs-camera-001",),
            confidence=0.61,
            urgency="routine",
            privacy_scope="role_local",
            requested_response="none",
            reply_to_message_id="msg-001",
        )
        self.assertEqual(event.payload["reply_to_message_id"], "msg-001")
        self.assertEqual(event.payload["authority"], "none")

    def test_tampered_capability_grant_is_rejected(self):
        event = self.event()
        document = event.to_dict()
        document["payload"] = copy.deepcopy(event.payload)
        document["payload"]["capability_grant"] = "vehicle.write"
        with self.assertRaisesRegex(ValueError, "forbidden fields"):
            validate_semantic_message(document)

    def test_nested_authority_field_is_rejected(self):
        event = self.event()
        document = event.to_dict()
        document["payload"] = copy.deepcopy(event.payload)
        document["payload"]["evidence_bundle"] = {"executor_name": "lock-writer"}
        with self.assertRaisesRegex(ValueError, "forbidden fields"):
            validate_semantic_message(document)

    def test_raw_chain_of_thought_field_is_rejected(self):
        event = self.event()
        document = event.to_dict()
        document["payload"] = copy.deepcopy(event.payload)
        document["payload"]["chain_of_thought"] = "hidden internal reasoning"
        with self.assertRaisesRegex(ValueError, "forbidden fields"):
            validate_semantic_message(document)

    def test_raw_reasoning_trace_nested_field_is_rejected(self):
        event = self.event()
        document = event.to_dict()
        document["payload"] = copy.deepcopy(event.payload)
        document["payload"]["debug"] = {"reasoning_trace": "private scratch state"}
        with self.assertRaisesRegex(ValueError, "forbidden fields"):
            validate_semantic_message(document)

    def test_memory_write_cannot_be_flipped(self):
        event = self.event()
        document = event.to_dict()
        document["payload"] = copy.deepcopy(event.payload)
        document["payload"]["memory_write"] = True
        with self.assertRaisesRegex(ValueError, "memory_write"):
            validate_semantic_message(document)

    def test_canonical_evidence_cannot_be_flipped(self):
        event = self.event()
        document = event.to_dict()
        document["payload"] = copy.deepcopy(event.payload)
        document["payload"]["canonical_evidence"] = True
        with self.assertRaisesRegex(ValueError, "canonical_evidence"):
            validate_semantic_message(document)

    def test_source_refs_are_required(self):
        with self.assertRaisesRegex(ValueError, "source_refs"):
            self.event(source_refs=())

    def test_semantic_content_is_bounded(self):
        with self.assertRaisesRegex(ValueError, "maximum length"):
            self.event(semantic_content="x" * 4097)

    def test_message_does_not_require_work_handoff_fields(self):
        event = self.event()
        self.assertNotIn("required_capabilities", event.payload)
        self.assertNotIn("work_id", event.payload)
        self.assertNotIn("executor_name", event.payload)


if __name__ == "__main__":
    unittest.main()
