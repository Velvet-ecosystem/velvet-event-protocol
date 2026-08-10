# SPDX-License-Identifier: GPL-3.0-only
"""Transport contract for approved language expressions destined for speech.

The event carries wording and bounded presentation context from Language to the
audio organ. It never selects hardware, synthesis implementation, authority, or
actuation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Union

from .event_schema import VelvetEvent

CONTRACT = "velvet.speech-expression.v1"
SCHEMA_VERSION = "1.0"
SPEECH_EXPRESSION_REQUESTED = "language.expression.speech_requested"

SEVERITIES = {"casual", "informational", "warning", "critical", "emergency"}
DRIVING_LOADS = {"low", "medium", "high"}

_FIXED_FLAGS = {
    "speech_approved": True,
    "command_authority": False,
    "actuation_authority": False,
    "hardware_selected": False,
    "synthesis_selected": False,
}

_FORBIDDEN_KEYS = {
    "alsa_device",
    "aplay_binary",
    "output_channel",
    "output_channels",
    "speaker_id",
    "speaker_slot",
    "speaker_slots",
    "voice_model",
    "model_path",
    "config_path",
    "volume",
    "gain",
    "gain_db",
    "pitch",
    "rate",
    "length_scale",
    "noise_scale",
    "noise_w_scale",
    "capability",
    "capability_token",
    "command",
    "court_token",
    "execution_token",
    "executor",
    "hardware_target",
    "authorization",
    "authorized",
    "authorized_by",
    "actuation",
    "actuate",
}

EventLike = Union[VelvetEvent, Mapping[str, Any]]


@dataclass(frozen=True)
class SpeechExpressionRecord:
    expression_id: str
    text: str
    severity: str
    audience: str = "owner"
    requested_profile: str = "owner_default"
    driving_load: str = "low"
    emergency_context: bool = False
    quiet_requested: bool = False
    social_allowed: bool = False
    interrupt: bool = False
    generator: str = "unknown"
    policy_version: str = "0.1"

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "expression_id": self.expression_id.strip(),
            "text": _normalized_text(self.text),
            "severity": self.severity.strip().casefold(),
            "audience": self.audience.strip().casefold(),
            "requested_profile": self.requested_profile.strip(),
            "driving_load": self.driving_load.strip().casefold(),
            "emergency_context": self.emergency_context,
            "quiet_requested": self.quiet_requested,
            "social_allowed": self.social_allowed,
            "interrupt": self.interrupt,
            "generator": self.generator.strip(),
            "policy_version": self.policy_version.strip(),
            **_FIXED_FLAGS,
        }
        _validate_payload(payload)
        return payload


def build_speech_expression_event(
    *,
    source: str,
    record: SpeechExpressionRecord,
    parent_event_id: Optional[str] = None,
    receipt_id: Optional[str] = None,
) -> VelvetEvent:
    _text("source", source)
    event = VelvetEvent(
        source=source.strip(),
        event_type=SPEECH_EXPRESSION_REQUESTED,
        payload=record.to_payload(),
        metadata={
            "contract": CONTRACT,
            "schema_version": SCHEMA_VERSION,
            "family": "speech-expression",
            "authority": "none",
            "expression_only": True,
        },
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )
    validate_speech_expression_event(event)
    return event


def validate_speech_expression_event(event: EventLike) -> None:
    document = event.to_dict() if isinstance(event, VelvetEvent) else dict(event)
    if document.get("event_type") != SPEECH_EXPRESSION_REQUESTED:
        raise ValueError("unexpected speech expression event type")

    metadata = document.get("metadata")
    if not isinstance(metadata, Mapping):
        raise ValueError("speech expression metadata must be a mapping")
    if metadata.get("contract") != CONTRACT:
        raise ValueError("unexpected speech expression contract")
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected speech expression schema version")
    if metadata.get("family") != "speech-expression":
        raise ValueError("unexpected speech expression family")
    if metadata.get("authority") != "none":
        raise ValueError("speech expression metadata cannot carry authority")
    if metadata.get("expression_only") is not True:
        raise ValueError("speech expression metadata must remain expression-only")

    payload = document.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("speech expression payload must be a mapping")
    _validate_payload(payload)


def _validate_payload(payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("speech expression payload schema mismatch")

    _text("expression_id", payload.get("expression_id"))
    text = _normalized_text(payload.get("text"))
    if len(text) > 4096:
        raise ValueError("speech expression text exceeds 4096 characters")

    severity = _text("severity", payload.get("severity")).casefold()
    if severity not in SEVERITIES:
        raise ValueError("invalid speech expression severity")
    driving_load = _text("driving_load", payload.get("driving_load")).casefold()
    if driving_load not in DRIVING_LOADS:
        raise ValueError("invalid speech expression driving_load")

    for name in ("audience", "requested_profile", "generator", "policy_version"):
        _text(name, payload.get(name))
    for name in (
        "emergency_context",
        "quiet_requested",
        "social_allowed",
        "interrupt",
    ):
        _boolean(name, payload.get(name))
    for name, expected in _FIXED_FLAGS.items():
        if payload.get(name) is not expected:
            raise ValueError("speech expression {} must be {!r}".format(name, expected))

    forbidden = _find_forbidden_keys(payload)
    if forbidden:
        raise ValueError(
            "speech expression contains forbidden implementation or authority fields: {}".format(
                sorted(forbidden)
            )
        )


def _find_forbidden_keys(value: Any) -> set:
    found = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) in _FORBIDDEN_KEYS:
                found.add(str(key))
            found.update(_find_forbidden_keys(child))
    elif isinstance(value, (list, tuple)):
        for child in value:
            found.update(_find_forbidden_keys(child))
    return found


def _normalized_text(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("text must be a string")
    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError("text must be non-empty")
    return normalized


def _text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))
    return value.strip()


def _boolean(name: str, value: Any) -> None:
    if not isinstance(value, bool):
        raise ValueError("{} must be true or false".format(name))
