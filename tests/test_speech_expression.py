import unittest
from copy import deepcopy

from velvet_event_protocol.speech_expression import (
    CONTRACT,
    SCHEMA_VERSION,
    SPEECH_EXPRESSION_REQUESTED,
    SpeechExpressionRecord,
    build_speech_expression_event,
    validate_speech_expression_event,
)


def _event():
    return build_speech_expression_event(
        source="velvet-language",
        parent_event_id="meaning-123",
        record=SpeechExpressionRecord(
            expression_id="response-42",
            text="  Mister,   systems nominal.  ",
            severity="informational",
            audience="owner",
            requested_profile="playful_social",
            driving_load="low",
            social_allowed=True,
            generator="catalog",
            policy_version="0.1",
        ),
    )


class SpeechExpressionTests(unittest.TestCase):
    def test_builds_expression_only_event_without_authority_or_hardware_selection(self):
        event = _event()

        self.assertEqual(event.event_type, SPEECH_EXPRESSION_REQUESTED)
        self.assertEqual(
            event.metadata,
            {
                "contract": CONTRACT,
                "schema_version": SCHEMA_VERSION,
                "family": "speech-expression",
                "authority": "none",
                "expression_only": True,
            },
        )
        self.assertEqual(event.payload["text"], "Mister, systems nominal.")
        self.assertIs(event.payload["speech_approved"], True)
        self.assertIs(event.payload["command_authority"], False)
        self.assertIs(event.payload["actuation_authority"], False)
        self.assertIs(event.payload["hardware_selected"], False)
        self.assertIs(event.payload["synthesis_selected"], False)
        self.assertNotIn("output_channels", event.payload)
        self.assertNotIn("model_path", event.payload)

        validate_speech_expression_event(event)

    def test_rejects_authority_or_physical_implementation_fields(self):
        document = _event().to_dict()
        for field, value in (
            ("capability_token", "not-allowed"),
            ("output_channels", [4]),
            ("gain_db", 6.0),
            ("model_path", "/tmp/voice.onnx"),
        ):
            candidate = deepcopy(document)
            candidate["payload"][field] = value
            with self.assertRaisesRegex(ValueError, "forbidden implementation or authority"):
                validate_speech_expression_event(candidate)

    def test_rejects_false_speech_approval_or_claimed_authority(self):
        document = _event().to_dict()
        candidate = deepcopy(document)
        candidate["payload"]["speech_approved"] = False
        with self.assertRaisesRegex(ValueError, "speech_approved"):
            validate_speech_expression_event(candidate)

        candidate = deepcopy(document)
        candidate["payload"]["command_authority"] = True
        with self.assertRaisesRegex(ValueError, "command_authority"):
            validate_speech_expression_event(candidate)

    def test_rejects_invalid_severity_load_and_oversized_text(self):
        with self.assertRaisesRegex(ValueError, "severity"):
            SpeechExpressionRecord(
                expression_id="x",
                text="hello",
                severity="dramatic",
            ).to_payload()

        with self.assertRaisesRegex(ValueError, "driving_load"):
            SpeechExpressionRecord(
                expression_id="x",
                text="hello",
                severity="informational",
                driving_load="maximum",
            ).to_payload()

        with self.assertRaisesRegex(ValueError, "4096"):
            SpeechExpressionRecord(
                expression_id="x",
                text="x" * 4097,
                severity="informational",
            ).to_payload()


if __name__ == "__main__":
    unittest.main()
