from copy import deepcopy

import pytest

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


def test_builds_expression_only_event_without_authority_or_hardware_selection() -> None:
    event = _event()

    assert event.event_type == SPEECH_EXPRESSION_REQUESTED
    assert event.metadata == {
        "contract": CONTRACT,
        "schema_version": SCHEMA_VERSION,
        "family": "speech-expression",
        "authority": "none",
        "expression_only": True,
    }
    assert event.payload["text"] == "Mister, systems nominal."
    assert event.payload["speech_approved"] is True
    assert event.payload["command_authority"] is False
    assert event.payload["actuation_authority"] is False
    assert event.payload["hardware_selected"] is False
    assert event.payload["synthesis_selected"] is False
    assert "output_channels" not in event.payload
    assert "model_path" not in event.payload

    validate_speech_expression_event(event)


def test_rejects_authority_or_physical_implementation_fields() -> None:
    document = _event().to_dict()
    for field, value in (
        ("capability_token", "not-allowed"),
        ("output_channels", [4]),
        ("gain_db", 6.0),
        ("model_path", "/tmp/voice.onnx"),
    ):
        candidate = deepcopy(document)
        candidate["payload"][field] = value
        with pytest.raises(ValueError, match="forbidden implementation or authority"):
            validate_speech_expression_event(candidate)


def test_rejects_false_speech_approval_or_claimed_authority() -> None:
    document = _event().to_dict()
    candidate = deepcopy(document)
    candidate["payload"]["speech_approved"] = False
    with pytest.raises(ValueError, match="speech_approved"):
        validate_speech_expression_event(candidate)

    candidate = deepcopy(document)
    candidate["payload"]["command_authority"] = True
    with pytest.raises(ValueError, match="command_authority"):
        validate_speech_expression_event(candidate)


def test_rejects_invalid_severity_load_and_oversized_text() -> None:
    with pytest.raises(ValueError, match="severity"):
        SpeechExpressionRecord(
            expression_id="x",
            text="hello",
            severity="dramatic",
        ).to_payload()

    with pytest.raises(ValueError, match="driving_load"):
        SpeechExpressionRecord(
            expression_id="x",
            text="hello",
            severity="informational",
            driving_load="maximum",
        ).to_payload()

    with pytest.raises(ValueError, match="4096"):
        SpeechExpressionRecord(
            expression_id="x",
            text="x" * 4097,
            severity="informational",
        ).to_payload()
