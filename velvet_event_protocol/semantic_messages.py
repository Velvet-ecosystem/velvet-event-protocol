# SPDX-License-Identifier: GPL-3.0-only
"""Bounded semantic message contracts for named Velvet identities.

These events let one named organ/character send another a concise statement,
question, proposal, correction, or acknowledgement with provenance and
confidence. They are not raw reasoning traces, work handoffs, memory writes,
or authority/execution channels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple, Union

from .event_schema import VelvetEvent

CONTRACT = "velvet.semantic-messages.v1"
SCHEMA_VERSION = "1.0"
SEMANTIC_MESSAGE = "organ.semantic.message"
EVENT_TYPES = {SEMANTIC_MESSAGE}

SPEECH_ACTS = {"statement", "question", "proposal", "correction", "acknowledgement"}
URGENCY_LEVELS = {"routine", "elevated", "urgent"}
PRIVACY_SCOPES = {"shared", "role_local", "private", "working"}
REQUESTED_RESPONSES = {"none", "acknowledge", "answer", "evaluate", "propose"}

_FLAGS = {
    "semantic_only": True,
    "transport_only": True,
    "canonical_evidence": False,
    "authority": "none",
    "grants_authority": False,
    "grants_execution": False,
    "grants_actuation": False,
    "memory_write": False,
}

_ALLOWED_PAYLOAD_KEYS = {
    "schema_version",
    "message_id",
    "sender_identity_id",
    "recipient_identity_ids",
    "purpose",
    "speech_act",
    "semantic_content",
    "source_refs",
    "evidence_refs",
    "confidence",
    "urgency",
    "privacy_scope",
    "requested_response",
    "reply_to_message_id",
    "correlation_ids",
    *_FLAGS,
}

_FORBIDDEN_KEYS = {
    "actuate",
    "actuation",
    "authorization",
    "authorized",
    "authorized_by",
    "capability",
    "capabilities",
    "capability_grant",
    "capability_token",
    "command",
    "court_decision",
    "court_token",
    "execution_token",
    "executor",
    "executor_name",
    "hardware_target",
    "permit",
    "permission",
    "policy_override",
    "safety_override",
    "shell",
    "token",
    "chain_of_thought",
    "reasoning_trace",
    "scratchpad",
    "private_reasoning",
    "hidden_reasoning",
}

EventLike = Union[VelvetEvent, Mapping[str, Any]]


@dataclass(frozen=True)
class SemanticMessageRecord:
    message_id: str
    sender_identity_id: str
    recipient_identity_ids: Tuple[str, ...]
    purpose: str
    speech_act: str
    semantic_content: str
    source_refs: Tuple[str, ...]
    evidence_refs: Tuple[str, ...] = ()
    confidence: float = 1.0
    urgency: str = "routine"
    privacy_scope: str = "shared"
    requested_response: str = "none"
    reply_to_message_id: Optional[str] = None
    correlation_ids: Tuple[str, ...] = ()

    def to_payload(self) -> Dict[str, Any]:
        _text("message_id", self.message_id)
        _text("sender_identity_id", self.sender_identity_id)
        _text_tuple("recipient_identity_ids", self.recipient_identity_ids, required=True)
        if self.sender_identity_id.strip() in {value.strip() for value in self.recipient_identity_ids}:
            raise ValueError("sender cannot be a recipient of the same semantic message")
        _text("purpose", self.purpose, max_length=240)
        if self.speech_act not in SPEECH_ACTS:
            raise ValueError("invalid speech_act")
        _text("semantic_content", self.semantic_content, max_length=4096)
        _text_tuple("source_refs", self.source_refs, required=True)
        _text_tuple("evidence_refs", self.evidence_refs)
        _ratio("confidence", self.confidence)
        if self.urgency not in URGENCY_LEVELS:
            raise ValueError("invalid urgency")
        if self.privacy_scope not in PRIVACY_SCOPES:
            raise ValueError("invalid privacy_scope")
        if self.requested_response not in REQUESTED_RESPONSES:
            raise ValueError("invalid requested_response")
        if self.reply_to_message_id is not None:
            _text("reply_to_message_id", self.reply_to_message_id)
        _text_tuple("correlation_ids", self.correlation_ids)

        payload: Dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "message_id": self.message_id.strip(),
            "sender_identity_id": self.sender_identity_id.strip(),
            "recipient_identity_ids": [value.strip() for value in self.recipient_identity_ids],
            "purpose": self.purpose.strip(),
            "speech_act": self.speech_act,
            "semantic_content": self.semantic_content.strip(),
            "source_refs": list(self.source_refs),
            "evidence_refs": list(self.evidence_refs),
            "confidence": float(self.confidence),
            "urgency": self.urgency,
            "privacy_scope": self.privacy_scope,
            "requested_response": self.requested_response,
            "correlation_ids": list(self.correlation_ids),
            **_FLAGS,
        }
        if self.reply_to_message_id is not None:
            payload["reply_to_message_id"] = self.reply_to_message_id.strip()
        _validate_payload(payload)
        return payload


def build_semantic_message(
    *,
    source: str,
    record: SemanticMessageRecord,
    parent_event_id: Optional[str] = None,
    receipt_id: Optional[str] = None,
) -> VelvetEvent:
    _text("source", source)
    event = VelvetEvent(
        source=source.strip(),
        event_type=SEMANTIC_MESSAGE,
        payload=record.to_payload(),
        metadata={
            "contract": CONTRACT,
            "schema_version": SCHEMA_VERSION,
            "family": "semantic-message",
            "authority": "none",
            "semantic_only": True,
        },
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )
    validate_semantic_message(event)
    return event


def validate_semantic_message(event: EventLike) -> None:
    document = event.to_dict() if isinstance(event, VelvetEvent) else dict(event)
    if document.get("event_type") != SEMANTIC_MESSAGE:
        raise ValueError("unexpected semantic message event type")
    payload = document.get("payload")
    metadata = document.get("metadata")
    if not isinstance(payload, Mapping):
        raise ValueError("semantic message payload must be a mapping")
    if not isinstance(metadata, Mapping):
        raise ValueError("semantic message metadata must be a mapping")
    if metadata.get("contract") != CONTRACT:
        raise ValueError("unexpected semantic message contract")
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected semantic message schema version")
    if metadata.get("family") != "semantic-message":
        raise ValueError("unexpected semantic message family")
    if metadata.get("authority") != "none" or metadata.get("semantic_only") is not True:
        raise ValueError("semantic message metadata must remain authority-free and semantic-only")
    _validate_payload(payload)


def _validate_payload(payload: Mapping[str, Any]) -> None:
    forbidden = _forbidden(payload)
    if forbidden:
        raise ValueError("semantic message contains forbidden fields: {}".format(sorted(forbidden)))
    unknown = set(payload) - _ALLOWED_PAYLOAD_KEYS
    if unknown:
        raise ValueError("semantic message contains unknown fields: {}".format(sorted(unknown)))
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("semantic message payload schema mismatch")
    for name in ("message_id", "sender_identity_id", "purpose", "semantic_content"):
        _text(name, payload.get(name), max_length=4096 if name == "semantic_content" else 240)
    recipients = payload.get("recipient_identity_ids")
    _text_list("recipient_identity_ids", recipients, required=True)
    if payload.get("sender_identity_id") in recipients:
        raise ValueError("sender cannot be a recipient of the same semantic message")
    if payload.get("speech_act") not in SPEECH_ACTS:
        raise ValueError("invalid speech_act")
    _text_list("source_refs", payload.get("source_refs"), required=True)
    _text_list("evidence_refs", payload.get("evidence_refs", []))
    _text_list("correlation_ids", payload.get("correlation_ids", []))
    _ratio("confidence", payload.get("confidence"))
    if payload.get("urgency") not in URGENCY_LEVELS:
        raise ValueError("invalid urgency")
    if payload.get("privacy_scope") not in PRIVACY_SCOPES:
        raise ValueError("invalid privacy_scope")
    if payload.get("requested_response") not in REQUESTED_RESPONSES:
        raise ValueError("invalid requested_response")
    if "reply_to_message_id" in payload:
        _text("reply_to_message_id", payload.get("reply_to_message_id"))
    for key, expected in _FLAGS.items():
        if payload.get(key) != expected:
            raise ValueError("semantic message {} must be {!r}".format(key, expected))


def _forbidden(value: Any) -> set:
    found = set()
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in _FORBIDDEN_KEYS:
                found.add(str(key))
            found.update(_forbidden(nested))
    elif isinstance(value, (list, tuple)):
        for nested in value:
            found.update(_forbidden(nested))
    return found


def _text(name: str, value: Any, max_length: int = 240) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))
    if len(value.strip()) > max_length:
        raise ValueError("{} exceeds maximum length".format(name))


def _text_tuple(name: str, values: Any, required: bool = False) -> None:
    if not isinstance(values, tuple):
        raise ValueError("{} must be a tuple".format(name))
    if required and not values:
        raise ValueError("{} must not be empty".format(name))
    normalized = []
    for value in values:
        _text(name, value)
        normalized.append(value.strip())
    if len(normalized) != len(set(normalized)):
        raise ValueError("{} must not contain duplicates".format(name))


def _text_list(name: str, values: Any, required: bool = False) -> None:
    if not isinstance(values, list):
        raise ValueError("{} must be a list".format(name))
    if required and not values:
        raise ValueError("{} must not be empty".format(name))
    normalized = []
    for value in values:
        _text(name, value)
        normalized.append(value.strip())
    if len(normalized) != len(set(normalized)):
        raise ValueError("{} must not contain duplicates".format(name))


def _ratio(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
        raise ValueError("{} must be between 0 and 1".format(name))
