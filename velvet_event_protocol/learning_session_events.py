# SPDX-License-Identifier: GPL-3.0-only
"""Authority-free transport contracts for Learning Mode session lifecycle evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple, Union

from .event_schema import VelvetEvent

CONTRACT = "velvet.learning-session-events.v1"
SCHEMA_VERSION = "1.0"

SESSION_PROPOSED = "learning.session.proposed"
ELIGIBILITY_CHECKED = "learning.session.eligibility_checked"
SESSION_OPENED = "learning.session.opened"
SESSION_STUDYING = "learning.session.studying"
REVIEW_PENDING = "learning.session.review_pending"
SESSION_PAUSED = "learning.session.paused"
SESSION_DEGRADED = "learning.session.degraded"
INSUFFICIENT_EVIDENCE = "learning.session.insufficient_evidence"
SESSION_COMPLETED = "learning.session.completed"
SESSION_ABORTED = "learning.session.aborted"

EVENT_TYPES = {
    SESSION_PROPOSED,
    ELIGIBILITY_CHECKED,
    SESSION_OPENED,
    SESSION_STUDYING,
    REVIEW_PENDING,
    SESSION_PAUSED,
    SESSION_DEGRADED,
    INSUFFICIENT_EVIDENCE,
    SESSION_COMPLETED,
    SESSION_ABORTED,
}

STATES = {
    "PROPOSED",
    "ELIGIBILITY_CHECK",
    "OPEN",
    "STUDYING",
    "REVIEW_PENDING",
    "PAUSED",
    "DEGRADED",
    "INSUFFICIENT_EVIDENCE",
    "COMPLETED",
    "ABORTED",
}

_EVENT_STATE = {
    SESSION_PROPOSED: "PROPOSED",
    ELIGIBILITY_CHECKED: "ELIGIBILITY_CHECK",
    SESSION_OPENED: "OPEN",
    SESSION_STUDYING: "STUDYING",
    REVIEW_PENDING: "REVIEW_PENDING",
    SESSION_PAUSED: "PAUSED",
    SESSION_DEGRADED: "DEGRADED",
    INSUFFICIENT_EVIDENCE: "INSUFFICIENT_EVIDENCE",
    SESSION_COMPLETED: "COMPLETED",
    SESSION_ABORTED: "ABORTED",
}

_FLAGS = {
    "transport_only": True,
    "canonical": False,
    "learning_evidence_only": True,
    "authority": "none",
    "grants_authority": False,
    "grants_memory_write": False,
    "grants_runtime_placement": False,
    "grants_execution": False,
    "grants_actuation": False,
    "applies_learning_change": False,
}

_RESERVED = {
    "schema_version",
    "session_id",
    "body_id",
    "node_id",
    "subject_ref",
    "state",
    "evidence_refs",
    "eligibility_refs",
    "workspace_refs",
    "distributed_work_refs",
    "candidate_refs",
    "simulated_evidence_refs",
    "degraded_reasons",
    "steps_used",
    "reason_code",
    *_FLAGS,
}

_FORBIDDEN_KEYS = {
    "objective",
    "prompt",
    "query",
    "content",
    "text",
    "transcript",
    "raw_content",
    "raw_document",
    "raw_audio",
    "raw_image",
    "web_page",
    "url",
    "network_request",
    "capability",
    "capability_token",
    "command",
    "court_decision",
    "court_token",
    "execution_token",
    "executor",
    "executor_handle",
    "hardware_handle",
    "hardware_target",
    "authorization",
    "authorized",
    "authorized_by",
    "policy_override",
    "safety_override",
    "actuation",
    "actuate",
    "shell",
}

EventLike = Union[VelvetEvent, Mapping[str, Any]]


@dataclass(frozen=True)
class LearningSessionEventRecord:
    session_id: str
    body_id: str
    node_id: str
    subject_ref: str
    state: str
    evidence_refs: Tuple[str, ...]
    eligibility_refs: Tuple[str, ...] = ()
    workspace_refs: Tuple[str, ...] = ()
    distributed_work_refs: Tuple[str, ...] = ()
    candidate_refs: Tuple[str, ...] = ()
    simulated_evidence_refs: Tuple[str, ...] = ()
    degraded_reasons: Tuple[str, ...] = ()
    steps_used: int = 0
    reason_code: str = "unspecified"
    data: Mapping[str, Any] = field(default_factory=dict)

    def to_payload(self, event_type: str) -> Dict[str, Any]:
        if event_type not in EVENT_TYPES:
            raise ValueError("unexpected learning session event type")
        _text("session_id", self.session_id)
        _text("body_id", self.body_id)
        _text("node_id", self.node_id)
        _text("subject_ref", self.subject_ref)
        if self.state not in STATES:
            raise ValueError("invalid learning session state")
        if self.state != _EVENT_STATE[event_type]:
            raise ValueError("learning session state does not match event type")
        _text_tuple("evidence_refs", self.evidence_refs, required=True)
        _text_tuple("eligibility_refs", self.eligibility_refs)
        _text_tuple("workspace_refs", self.workspace_refs)
        _text_tuple("distributed_work_refs", self.distributed_work_refs)
        _text_tuple("candidate_refs", self.candidate_refs)
        _text_tuple("simulated_evidence_refs", self.simulated_evidence_refs)
        _text_tuple("degraded_reasons", self.degraded_reasons)
        _reason_code(self.reason_code)
        if isinstance(self.steps_used, bool) or not isinstance(self.steps_used, int) or self.steps_used < 0:
            raise ValueError("steps_used must be a non-negative integer")
        if not set(self.simulated_evidence_refs).issubset(set(self.evidence_refs)):
            raise ValueError("simulated evidence refs must also be session evidence refs")
        if not isinstance(self.data, Mapping):
            raise ValueError("data must be a mapping")
        collisions = set(self.data).intersection(_RESERVED)
        if collisions:
            raise ValueError("learning session data collides with reserved fields: %s" % sorted(collisions))
        forbidden = _find_forbidden(self.data)
        if forbidden:
            raise ValueError("learning session data contains forbidden fields: %s" % sorted(forbidden))

        payload: Dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "session_id": self.session_id.strip(),
            "body_id": self.body_id.strip(),
            "node_id": self.node_id.strip(),
            "subject_ref": self.subject_ref.strip(),
            "state": self.state,
            "evidence_refs": list(self.evidence_refs),
            "eligibility_refs": list(self.eligibility_refs),
            "workspace_refs": list(self.workspace_refs),
            "distributed_work_refs": list(self.distributed_work_refs),
            "candidate_refs": list(self.candidate_refs),
            "simulated_evidence_refs": list(self.simulated_evidence_refs),
            "degraded_reasons": list(self.degraded_reasons),
            "steps_used": self.steps_used,
            "reason_code": self.reason_code.strip(),
            **_FLAGS,
            **dict(self.data),
        }
        _validate_payload(event_type, payload)
        return payload


def build_learning_session_event(
    *,
    source: str,
    event_type: str,
    record: LearningSessionEventRecord,
    parent_event_id: Optional[str] = None,
    receipt_id: Optional[str] = None,
) -> VelvetEvent:
    _text("source", source)
    event = VelvetEvent(
        source=source.strip(),
        event_type=event_type,
        payload=record.to_payload(event_type),
        metadata={
            "contract": CONTRACT,
            "schema_version": SCHEMA_VERSION,
            "family": "learning-session",
            "authority": "none",
            "learning_evidence_only": True,
        },
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )
    validate_learning_session_event(event)
    return event


def validate_learning_session_event(event: EventLike) -> None:
    document = event.to_dict() if isinstance(event, VelvetEvent) else dict(event)
    event_type = document.get("event_type")
    if event_type not in EVENT_TYPES:
        raise ValueError("unexpected learning session event type")
    metadata = document.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, Mapping):
            raise ValueError("learning session metadata must be a mapping")
        if metadata.get("contract") != CONTRACT:
            raise ValueError("unexpected learning session contract")
        if metadata.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unexpected learning session schema version")
        if metadata.get("family") != "learning-session":
            raise ValueError("unexpected learning session event family")
        if metadata.get("authority") != "none":
            raise ValueError("learning session metadata cannot carry authority")
        if metadata.get("learning_evidence_only") is not True:
            raise ValueError("learning session metadata must remain evidence-only")
    payload = document.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("learning session payload must be a mapping")
    _validate_payload(event_type, payload)


def _validate_payload(event_type: str, payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("learning session payload schema mismatch")
    for key in ("session_id", "body_id", "node_id", "subject_ref"):
        _text(key, payload.get(key))
    state = payload.get("state")
    if state not in STATES or state != _EVENT_STATE[event_type]:
        raise ValueError("learning session payload state mismatch")
    evidence = _text_list("evidence_refs", payload.get("evidence_refs"), required=True)
    _text_list("eligibility_refs", payload.get("eligibility_refs", []))
    _text_list("workspace_refs", payload.get("workspace_refs", []))
    _text_list("distributed_work_refs", payload.get("distributed_work_refs", []))
    _text_list("candidate_refs", payload.get("candidate_refs", []))
    simulated = _text_list("simulated_evidence_refs", payload.get("simulated_evidence_refs", []))
    _text_list("degraded_reasons", payload.get("degraded_reasons", []))
    if not set(simulated).issubset(set(evidence)):
        raise ValueError("simulated evidence refs must also be session evidence refs")
    steps = payload.get("steps_used")
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError("steps_used must be a non-negative integer")
    _reason_code(payload.get("reason_code"))
    for key, expected in _FLAGS.items():
        if payload.get(key) != expected:
            raise ValueError("learning session payload %s must be %r" % (key, expected))
    forbidden = _find_forbidden(payload)
    if forbidden:
        raise ValueError("learning session payload contains forbidden fields: %s" % sorted(forbidden))


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


def _text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be a non-empty string" % name)
    return value.strip()


def _reason_code(value: Any) -> str:
    text = _text("reason_code", value)
    if len(text) > 96 or any(character.isspace() for character in text):
        raise ValueError("reason_code must be a compact non-whitespace code")
    return text


def _text_tuple(name: str, values: Tuple[str, ...], required: bool = False) -> Tuple[str, ...]:
    if not isinstance(values, tuple):
        raise ValueError("%s must be a tuple" % name)
    normalized = tuple(_text(name, value) for value in values)
    if required and not normalized:
        raise ValueError("%s must not be empty" % name)
    if len(set(normalized)) != len(normalized):
        raise ValueError("%s must not contain duplicates" % name)
    return normalized


def _text_list(name: str, values: Any, required: bool = False) -> Tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        raise ValueError("%s must be a list" % name)
    normalized = tuple(_text(name, value) for value in values)
    if required and not normalized:
        raise ValueError("%s must not be empty" % name)
    if len(set(normalized)) != len(normalized):
        raise ValueError("%s must not contain duplicates" % name)
    return normalized
