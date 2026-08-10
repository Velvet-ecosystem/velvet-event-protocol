# SPDX-License-Identifier: GPL-3.0-only
"""Authority-free transport contract for Audio Studio output evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple, Union

from .event_schema import VelvetEvent

CONTRACT = "velvet.audio-output-evidence.v1"
SCHEMA_VERSION = "1.0"

AUDIO_OUTPUT_BOOKED = "audio.output.booked"
AUDIO_OUTPUT_STARTED = "audio.output.started"
AUDIO_OUTPUT_COMPLETED = "audio.output.completed"
AUDIO_OUTPUT_PREEMPTED = "audio.output.preempted"
AUDIO_OUTPUT_FAILED = "audio.output.failed"
AUDIO_OUTPUT_RECOVERED = "audio.output.recovered"

AUDIO_OUTPUT_EVENT_TYPES = {
    AUDIO_OUTPUT_BOOKED,
    AUDIO_OUTPUT_STARTED,
    AUDIO_OUTPUT_COMPLETED,
    AUDIO_OUTPUT_PREEMPTED,
    AUDIO_OUTPUT_FAILED,
    AUDIO_OUTPUT_RECOVERED,
}

_FAILURE_STAGES = {"synthesis", "booking", "playback"}
_FIXED_FLAGS = {
    "evidence_only": True,
    "authority": "none",
    "grants_authority": False,
    "grants_execution": False,
    "grants_actuation": False,
    "audio_output_only": True,
}
_FORBIDDEN_KEYS = {
    "text",
    "transcript",
    "pcm_bytes",
    "raw_audio",
    "alsa_device",
    "model_path",
    "config_path",
    "capability",
    "capability_token",
    "command",
    "court_token",
    "execution_token",
    "executor",
    "hardware_handle",
    "hardware_target",
    "authorization",
    "authorized",
    "authorized_by",
    "actuation",
    "actuate",
}

EventLike = Union[VelvetEvent, Mapping[str, Any]]


@dataclass(frozen=True)
class AudioOutputEvidenceRecord:
    output_event_id: str
    request_id: str
    node_id: str
    priority: int
    output_channels: Tuple[int, ...] = ()
    expression_id: Optional[str] = None
    profile_id: Optional[str] = None
    model_id: Optional[str] = None
    data: Mapping[str, Any] = None  # type: ignore[assignment]

    def to_payload(self, event_type: str) -> Dict[str, Any]:
        data = {} if self.data is None else dict(self.data)
        collisions = set(data).intersection(
            {
                "schema_version",
                "output_event_id",
                "request_id",
                "node_id",
                "priority",
                "output_channels",
                "expression_id",
                "profile_id",
                "model_id",
                *_FIXED_FLAGS,
            }
        )
        if collisions:
            raise ValueError("audio output data collides with reserved fields: %s" % sorted(collisions))
        payload: Dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "output_event_id": self.output_event_id.strip(),
            "request_id": self.request_id.strip(),
            "node_id": self.node_id.strip(),
            "priority": self.priority,
            "output_channels": list(self.output_channels),
            **_FIXED_FLAGS,
            **data,
        }
        if self.expression_id is not None:
            payload["expression_id"] = self.expression_id.strip()
        if self.profile_id is not None:
            payload["profile_id"] = self.profile_id.strip()
        if self.model_id is not None:
            payload["model_id"] = self.model_id.strip()
        _validate_payload(event_type, payload)
        return payload


def build_audio_output_event(
    *,
    source: str,
    event_type: str,
    record: AudioOutputEvidenceRecord,
    parent_event_id: Optional[str] = None,
    receipt_id: Optional[str] = None,
) -> VelvetEvent:
    _text("source", source)
    if event_type not in AUDIO_OUTPUT_EVENT_TYPES:
        raise ValueError("unexpected audio output event type")
    event = VelvetEvent(
        source=source.strip(),
        event_type=event_type,
        payload=record.to_payload(event_type),
        metadata={
            "contract": CONTRACT,
            "schema_version": SCHEMA_VERSION,
            "family": "audio-output-evidence",
            "authority": "none",
            "evidence_only": True,
        },
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )
    validate_audio_output_event(event)
    return event


def validate_audio_output_event(event: EventLike) -> None:
    document = event.to_dict() if isinstance(event, VelvetEvent) else dict(event)
    event_type = document.get("event_type")
    if event_type not in AUDIO_OUTPUT_EVENT_TYPES:
        raise ValueError("unexpected audio output event type")

    metadata = document.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, Mapping):
            raise ValueError("audio output metadata must be a mapping")
        if metadata.get("contract") != CONTRACT:
            raise ValueError("unexpected audio output contract")
        if metadata.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unexpected audio output schema version")
        if metadata.get("family") != "audio-output-evidence":
            raise ValueError("unexpected audio output event family")
        if metadata.get("authority") != "none":
            raise ValueError("audio output metadata cannot carry authority")
        if metadata.get("evidence_only") is not True:
            raise ValueError("audio output metadata must remain evidence-only")

    payload = document.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("audio output payload must be a mapping")
    _validate_payload(event_type, payload)


def _validate_payload(event_type: str, payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("audio output payload schema mismatch")
    for key in ("output_event_id", "request_id", "node_id"):
        _text(key, payload.get(key))
    priority = payload.get("priority")
    if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 100:
        raise ValueError("audio output priority must be an integer from 0 to 100")
    channels = _channels(payload.get("output_channels"))
    for key in ("expression_id", "profile_id", "model_id"):
        if key in payload:
            _text(key, payload.get(key))
    for key, expected in _FIXED_FLAGS.items():
        if payload.get(key) != expected:
            raise ValueError("audio output payload %s must be %r" % (key, expected))
    forbidden = _find_forbidden(payload)
    if forbidden:
        raise ValueError("audio output payload contains forbidden fields: %s" % sorted(forbidden))

    if event_type == AUDIO_OUTPUT_BOOKED:
        if not channels:
            raise ValueError("booked audio output requires output channels")
    elif event_type == AUDIO_OUTPUT_STARTED:
        if not channels:
            raise ValueError("started audio output requires output channels")
        _positive_int(payload, "source_sample_rate_hz")
        _positive_int(payload, "playback_sample_rate_hz")
        _nonnegative_int(payload, "source_frames")
    elif event_type in {AUDIO_OUTPUT_COMPLETED, AUDIO_OUTPUT_PREEMPTED}:
        if not channels:
            raise ValueError("finished audio output requires output channels")
        _positive_int(payload, "playback_sample_rate_hz")
        _nonnegative_int(payload, "frames_written")
        _nonnegative_number(payload, "playback_duration_ms")
        if event_type == AUDIO_OUTPUT_PREEMPTED:
            _text("preempted_by_request_id", payload.get("preempted_by_request_id"))
    elif event_type == AUDIO_OUTPUT_FAILED:
        stage = _text("failure_stage", payload.get("failure_stage"))
        if stage not in _FAILURE_STAGES:
            raise ValueError("invalid audio output failure stage")
        _text("error_class", payload.get("error_class"))
        _text("reason", payload.get("reason"))
        if payload.get("recovery_required") is not True:
            raise ValueError("audio output failure must require recovery")
    elif event_type == AUDIO_OUTPUT_RECOVERED:
        _text("recovered_from_event_id", payload.get("recovered_from_event_id"))
        _text("recovered_from_stage", payload.get("recovered_from_stage"))


def _find_forbidden(value: Any, path: str = "payload") -> set:
    found = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text in _FORBIDDEN_KEYS:
                found.add("%s.%s" % (path, key_text))
            found.update(_find_forbidden(child, "%s.%s" % (path, key_text)))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found.update(_find_forbidden(child, "%s[%s]" % (path, index)))
    return found


def _channels(value: Any) -> Tuple[int, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("output_channels must be a list")
    channels = tuple(value)
    if len(set(channels)) != len(channels):
        raise ValueError("output_channels must be unique")
    if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in channels):
        raise ValueError("output_channels must contain non-negative integers")
    return channels


def _text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be a non-empty string" % name)
    return value.strip()


def _positive_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("%s must be a positive integer" % key)
    return value


def _nonnegative_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("%s must be a non-negative integer" % key)
    return value


def _nonnegative_number(payload: Mapping[str, Any], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError("%s must be a non-negative number" % key)
    return float(value)
