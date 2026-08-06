# SPDX-License-Identifier: GPL-3.0-only
"""Versioned transport contracts for Velvet's Cognitive Event Layer.

Cognitive events carry bounded interpretation, prediction, interruption,
action-tracking references, and episode proposals. They never authorize,
execute, retry, or replace receipts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple, Union

from .event_schema import VelvetEvent

CONTRACT = "velvet.cognitive-events.v1"
SCHEMA_VERSION = "1.0"

EVENT_OPENED = "cognitive.event.opened"
EVENT_UPDATED = "cognitive.event.updated"
BOUNDARY_PROPOSED = "cognitive.event.boundary_proposed"
EVENT_CLOSED = "cognitive.event.closed"
PREDICTION_CREATED = "cognitive.prediction.created"
PREDICTION_RESOLVED = "cognitive.prediction.resolved"
PREDICTION_ERROR = "cognitive.prediction.error"
INTERRUPT_CANDIDATE = "cognitive.interrupt.candidate"
INTERRUPT_ACCEPTED = "cognitive.interrupt.accepted"
PROPOSAL_CONTEXT = "cognitive.proposal.context"
ACTION_TRACKING_STARTED = "cognitive.action.tracking_started"
ACTION_TRACKING_FINISHED = "cognitive.action.tracking_finished"
EPISODE_PROPOSED = "cognitive.episode.proposed"
MODULATORS_SNAPSHOTTED = "cognitive.modulators.snapshotted"
CONNECTION_HEALTH_CHANGED = "cognitive.connection.health_changed"
HEALTH_CHANGED = "cognitive.health.changed"

EVENT_TYPES = {
    EVENT_OPENED,
    EVENT_UPDATED,
    BOUNDARY_PROPOSED,
    EVENT_CLOSED,
    PREDICTION_CREATED,
    PREDICTION_RESOLVED,
    PREDICTION_ERROR,
    INTERRUPT_CANDIDATE,
    INTERRUPT_ACCEPTED,
    PROPOSAL_CONTEXT,
    ACTION_TRACKING_STARTED,
    ACTION_TRACKING_FINISHED,
    EPISODE_PROPOSED,
    MODULATORS_SNAPSHOTTED,
    CONNECTION_HEALTH_CHANGED,
    HEALTH_CHANGED,
}

MODES = {"OBSERVE", "PROPOSE_ACTION", "TRACK_ACTION"}
LIFECYCLE_STATES = {
    "OPEN",
    "DEVELOPING",
    "PROPOSAL_PENDING",
    "ACTION_TRACKING",
    "COMPLETED",
    "INTERRUPTED",
    "STALE",
    "CONTRADICTED",
    "ABANDONED",
    "UNKNOWN_OUTCOME",
    "DEGRADED_COMPLETION",
}
TERMINAL_STATES = {
    "COMPLETED",
    "INTERRUPTED",
    "STALE",
    "CONTRADICTED",
    "ABANDONED",
    "UNKNOWN_OUTCOME",
    "DEGRADED_COMPLETION",
}
REPLAY_STATES = {"live", "fixture", "replay"}
HEALTH_STATES = {"healthy", "degraded", "failed", "unknown"}

_FLAGS = {
    "interpretation_only": True,
    "transport_only": True,
    "canonical_evidence": False,
    "authority": "none",
    "grants_authority": False,
    "grants_execution": False,
    "grants_actuation": False,
    "replay_safe": True,
}
_COMMON_KEYS = {
    "schema_version",
    "cognitive_event_id",
    "node_id",
    "body_id",
    "source_refs",
    "correlation_ids",
    "monotonic_time",
    "replay_state",
    "health_state",
    "degraded_reasons",
    *_FLAGS,
}
_FORBIDDEN_KEYS = {
    "actuate",
    "actuation",
    "authorization",
    "authorized",
    "authorized_by",
    "capability",
    "capability_token",
    "command",
    "court_decision",
    "court_token",
    "execution_token",
    "executor",
    "executor_handle",
    "executor_name",
    "hardware_handle",
    "hardware_target",
    "permit",
    "policy_override",
    "retry_authorized",
    "safety_override",
    "shell",
    "token",
}
_ALLOWED_MODULATORS = {
    "arousal",
    "novelty",
    "uncertainty",
    "urgency",
    "social_engagement",
    "resource_pressure",
    "prediction_stability",
}

EventLike = Union[VelvetEvent, Mapping[str, Any]]


@dataclass(frozen=True)
class CognitiveEventRecord:
    cognitive_event_id: str
    node_id: str
    body_id: str
    source_refs: Tuple[str, ...]
    data: Mapping[str, Any]
    correlation_ids: Tuple[str, ...] = ()
    monotonic_time: Optional[float] = None
    replay_state: str = "live"
    health_state: str = "healthy"
    degraded_reasons: Tuple[str, ...] = ()

    def to_payload(self, event_type: str) -> Dict[str, Any]:
        _validate_common_record(self)
        if not isinstance(self.data, Mapping):
            raise ValueError("data must be a mapping")
        collisions = set(self.data).intersection(_COMMON_KEYS)
        if collisions:
            raise ValueError("data collides with reserved fields: {}".format(sorted(collisions)))
        payload: Dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "cognitive_event_id": self.cognitive_event_id.strip(),
            "node_id": self.node_id.strip(),
            "body_id": self.body_id.strip(),
            "source_refs": list(self.source_refs),
            "correlation_ids": list(self.correlation_ids),
            "replay_state": self.replay_state,
            "health_state": self.health_state,
            "degraded_reasons": list(self.degraded_reasons),
            **_FLAGS,
            **dict(self.data),
        }
        if self.monotonic_time is not None:
            payload["monotonic_time"] = float(self.monotonic_time)
        _validate_payload(event_type, payload)
        return payload


def build_cognitive_event(
    *,
    source: str,
    event_type: str,
    record: CognitiveEventRecord,
    parent_event_id: Optional[str] = None,
    receipt_id: Optional[str] = None,
) -> VelvetEvent:
    _text("source", source)
    if event_type not in EVENT_TYPES:
        raise ValueError("unexpected cognitive event type")
    event = VelvetEvent(
        source=source.strip(),
        event_type=event_type,
        payload=record.to_payload(event_type),
        metadata={
            "contract": CONTRACT,
            "schema_version": SCHEMA_VERSION,
            "family": "cognitive-event",
            "authority": "none",
            "interpretation_only": True,
        },
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )
    validate_cognitive_event(event)
    return event


def validate_cognitive_event(event: EventLike) -> None:
    document = event.to_dict() if isinstance(event, VelvetEvent) else dict(event)
    event_type = document.get("event_type")
    if event_type not in EVENT_TYPES:
        raise ValueError("unexpected cognitive event type")
    payload = document.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("cognitive payload must be a mapping")
    metadata = document.get("metadata")
    if not isinstance(metadata, Mapping):
        raise ValueError("cognitive metadata must be a mapping")
    if metadata.get("contract") != CONTRACT:
        raise ValueError("unexpected cognitive event contract")
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected cognitive schema version")
    if metadata.get("family") != "cognitive-event":
        raise ValueError("unexpected cognitive event family")
    if metadata.get("authority") != "none":
        raise ValueError("cognitive metadata cannot carry authority")
    if metadata.get("interpretation_only") is not True:
        raise ValueError("cognitive metadata must remain interpretation-only")
    _validate_payload(event_type, payload)


def _validate_common_record(record: CognitiveEventRecord) -> None:
    _text("cognitive_event_id", record.cognitive_event_id)
    _text("node_id", record.node_id)
    _text("body_id", record.body_id)
    _text_tuple("source_refs", record.source_refs, required=True)
    _text_tuple("correlation_ids", record.correlation_ids)
    _text_tuple("degraded_reasons", record.degraded_reasons)
    if record.monotonic_time is not None:
        _non_negative("monotonic_time", record.monotonic_time)
    if record.replay_state not in REPLAY_STATES:
        raise ValueError("invalid replay_state")
    if record.health_state not in HEALTH_STATES:
        raise ValueError("invalid health_state")
    if record.health_state == "healthy" and record.degraded_reasons:
        raise ValueError("healthy record cannot declare degraded reasons")


def _validate_payload(event_type: str, payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("cognitive payload schema mismatch")
    for name in ("cognitive_event_id", "node_id", "body_id"):
        _text(name, payload.get(name))
    _text_list("source_refs", payload.get("source_refs"), required=True)
    _text_list("correlation_ids", payload.get("correlation_ids", []))
    _text_list("degraded_reasons", payload.get("degraded_reasons", []))
    if payload.get("replay_state") not in REPLAY_STATES:
        raise ValueError("invalid replay_state")
    health = payload.get("health_state")
    if health not in HEALTH_STATES:
        raise ValueError("invalid health_state")
    if health == "healthy" and payload.get("degraded_reasons"):
        raise ValueError("healthy record cannot declare degraded reasons")
    if "monotonic_time" in payload:
        _non_negative("monotonic_time", payload.get("monotonic_time"))
    for key, expected in _FLAGS.items():
        if payload.get(key) != expected:
            raise ValueError("cognitive payload {} must be {!r}".format(key, expected))
    forbidden = _forbidden(payload)
    if forbidden:
        raise ValueError("cognitive payload contains forbidden authority fields: {}".format(sorted(forbidden)))

    if event_type in {EVENT_OPENED, EVENT_UPDATED, EVENT_CLOSED}:
        _snapshot(event_type, payload)
    elif event_type == BOUNDARY_PROPOSED:
        _boundary(payload)
    elif event_type == PREDICTION_CREATED:
        _prediction_created(payload)
    elif event_type == PREDICTION_RESOLVED:
        _prediction_resolved(payload)
    elif event_type == PREDICTION_ERROR:
        _prediction_error(payload)
    elif event_type in {INTERRUPT_CANDIDATE, INTERRUPT_ACCEPTED}:
        _interrupt(event_type, payload)
    elif event_type == PROPOSAL_CONTEXT:
        _proposal(payload)
    elif event_type in {ACTION_TRACKING_STARTED, ACTION_TRACKING_FINISHED}:
        _tracking(event_type, payload)
    elif event_type == EPISODE_PROPOSED:
        _episode(payload)
    elif event_type == MODULATORS_SNAPSHOTTED:
        _modulators(payload)
    elif event_type == CONNECTION_HEALTH_CHANGED:
        _connection(payload)
    elif event_type == HEALTH_CHANGED:
        _text("component", payload.get("component"))
        if "latency_ms" in payload:
            _non_negative("latency_ms", payload.get("latency_ms"))


def _snapshot(event_type: str, p: Mapping[str, Any]) -> None:
    if p.get("mode") not in MODES:
        raise ValueError("invalid cognitive mode")
    state = p.get("lifecycle_state")
    if state not in LIFECYCLE_STATES:
        raise ValueError("invalid lifecycle_state")
    if event_type == EVENT_CLOSED:
        if state not in TERMINAL_STATES:
            raise ValueError("closed event requires terminal lifecycle_state")
        _text("completion_reason", p.get("completion_reason"))
    elif state in TERMINAL_STATES:
        raise ValueError("terminal lifecycle_state requires cognitive.event.closed")
    _text("event_kind", p.get("event_kind"))
    _ratio("confidence", p.get("confidence"))
    if p.get("freshness_state") not in {"fresh", "aging", "stale"}:
        raise ValueError("invalid freshness_state")
    _lists(p, "observation_refs", "organ_contribution_refs", "proposal_refs", "authorization_refs", "execution_refs", "receipt_refs", "prediction_refs", "interruption_refs", "nested_event_ids")


def _boundary(p: Mapping[str, Any]) -> None:
    _text("boundary_id", p.get("boundary_id"))
    if p.get("boundary_type") not in {"completion", "interruption", "context_shift", "timeout", "contradiction"}:
        raise ValueError("invalid boundary_type")
    if p.get("recommended_terminal_state") not in TERMINAL_STATES:
        raise ValueError("boundary requires terminal state")
    _text_list("evidence_refs", p.get("evidence_refs"), required=True)
    _ratio("confidence", p.get("confidence"))


def _prediction_created(p: Mapping[str, Any]) -> None:
    _text("prediction_id", p.get("prediction_id"))
    _text("subject", p.get("subject"))
    _mapping("expected_state", p.get("expected_state"), required=True)
    _mapping("tolerance", p.get("tolerance", {}))
    _non_negative("expected_by", p.get("expected_by"))
    _ratio("confidence", p.get("confidence"))
    _text("source_model", p.get("source_model"))
    _text("source_version", p.get("source_version"))
    _text_list("observation_refs", p.get("observation_refs", []))
    if p.get("status") != "pending":
        raise ValueError("created prediction must be pending")


def _prediction_resolved(p: Mapping[str, Any]) -> None:
    _text("prediction_id", p.get("prediction_id"))
    if p.get("status") not in {"confirmed", "contradicted", "expired", "unknown"}:
        raise ValueError("invalid prediction resolution")
    _mapping("observed_state", p.get("observed_state"))
    _ratio("confidence", p.get("confidence"))
    _lists(p, "observation_refs", "receipt_refs")


def _prediction_error(p: Mapping[str, Any]) -> None:
    _text("prediction_error_id", p.get("prediction_error_id"))
    _text("prediction_id", p.get("prediction_id"))
    if p.get("error_class") not in {"mismatch", "timeout", "partial", "impossible", "unobservable"}:
        raise ValueError("invalid prediction error_class")
    _mapping("observed_state", p.get("observed_state"))
    _ratio("confidence", p.get("confidence"))
    _text_list("receipt_refs", p.get("receipt_refs", []))
    if p.get("automatic_retry_requested") is not False:
        raise ValueError("prediction error cannot request automatic retry")


def _interrupt(event_type: str, p: Mapping[str, Any]) -> None:
    _text("interrupt_id", p.get("interrupt_id"))
    _ratio("priority", p.get("priority"))
    _text("reason", p.get("reason"))
    _non_negative("accumulated_score", p.get("accumulated_score"))
    _non_negative("threshold", p.get("threshold"))
    _boolean("requires_immediate_safeing", p.get("requires_immediate_safeing"))
    if p.get("safe_state_reached") not in {"true", "false", "unknown"}:
        raise ValueError("invalid safe_state_reached")
    if p.get("safeing_authorized") is not False or p.get("safeing_performed") is not False:
        raise ValueError("cognitive interrupt cannot authorize or claim safeing")
    _text_list("outstanding_effect_refs", p.get("outstanding_effect_refs", []))
    if event_type == INTERRUPT_ACCEPTED:
        if p.get("accumulated_score") < p.get("threshold"):
            raise ValueError("accepted interrupt must meet threshold")
        _text("interrupted_event_id", p.get("interrupted_event_id"))


def _proposal(p: Mapping[str, Any]) -> None:
    _text("proposal_ref", p.get("proposal_ref"))
    _ratio("confidence", p.get("confidence"))
    _lists(p, "observation_refs", "prediction_refs", "interruption_refs")
    if p.get("proposal_only") is not True:
        raise ValueError("proposal context must remain proposal-only")


def _tracking(event_type: str, p: Mapping[str, Any]) -> None:
    _text("tracking_id", p.get("tracking_id"))
    state = p.get("state")
    if state not in {"started", "completed", "failed", "denied", "unknown", "interrupted"}:
        raise ValueError("invalid tracking state")
    if event_type == ACTION_TRACKING_STARTED and state != "started":
        raise ValueError("tracking_started requires started state")
    if event_type == ACTION_TRACKING_FINISHED and state == "started":
        raise ValueError("tracking_finished requires terminal state")
    _text("authorization_ref", p.get("authorization_ref"))
    _text("execution_ref", p.get("execution_ref"))
    _lists(p, "observation_refs", "receipt_refs", "outstanding_effect_refs")
    if p.get("tracking_only") is not True:
        raise ValueError("action tracking must remain tracking-only")


def _episode(p: Mapping[str, Any]) -> None:
    _text("episode_id", p.get("episode_id"))
    _text("summary", p.get("summary"))
    if p.get("retention_class") not in {"transient", "operational", "significant", "protected"}:
        raise ValueError("invalid retention_class")
    _ratio("confidence", p.get("confidence"))
    _lists(p, "receipt_refs", "actors", "locations", "what_changed", "proposal_refs", "authorization_refs", "execution_refs", "outcome_refs", "prediction_error_refs", "interruption_refs")
    if p.get("memory_navigation_only") is not True:
        raise ValueError("episode must remain memory-navigation-only")


def _modulators(p: Mapping[str, Any]) -> None:
    _text("snapshot_id", p.get("snapshot_id"))
    _text("trust_context", p.get("trust_context"))
    values = p.get("values")
    _mapping("values", values, required=True)
    unknown = set(values) - _ALLOWED_MODULATORS
    if unknown:
        raise ValueError("unknown modulators: {}".format(sorted(unknown)))
    for name, value in values.items():
        _ratio(name, value)
    if p.get("cannot_change_authority") is not True:
        raise ValueError("modulators cannot change authority")


def _connection(p: Mapping[str, Any]) -> None:
    for name in ("connection_id", "source_component", "destination_component", "signal_type"):
        _text(name, p.get(name))
    _non_negative("maximum_latency_ms", p.get("maximum_latency_ms"))
    _non_negative("stale_after_ms", p.get("stale_after_ms"))
    if "observed_latency_ms" in p:
        _non_negative("observed_latency_ms", p.get("observed_latency_ms"))


def _forbidden(value: Any) -> set:
    found = set()
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if isinstance(key, str) and key.lower() in _FORBIDDEN_KEYS:
                found.add(key.lower())
            found.update(_forbidden(nested))
    elif isinstance(value, (list, tuple, set)):
        for nested in value:
            found.update(_forbidden(nested))
    return found


def _lists(p: Mapping[str, Any], *names: str) -> None:
    for name in names:
        _text_list(name, p.get(name, []))


def _text(name: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))


def _text_tuple(name: str, values: Any, required: bool = False) -> None:
    if not isinstance(values, tuple) or (required and not values):
        raise ValueError("{} must be a{} tuple".format(name, " non-empty" if required else ""))
    for value in values:
        _text(name, value)


def _text_list(name: str, values: Any, required: bool = False) -> None:
    if not isinstance(values, list) or (required and not values):
        raise ValueError("{} must be a{} list".format(name, " non-empty" if required else ""))
    for value in values:
        _text(name, value)


def _ratio(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
        raise ValueError("{} must be between 0 and 1".format(name))


def _non_negative(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) < 0:
        raise ValueError("{} must be non-negative".format(name))


def _mapping(name: str, value: Any, required: bool = False) -> None:
    if not isinstance(value, Mapping) or (required and not value):
        raise ValueError("{} must be a{} mapping".format(name, " non-empty" if required else ""))


def _boolean(name: str, value: Any) -> None:
    if not isinstance(value, bool):
        raise ValueError("{} must be boolean".format(name))


__all__ = [
    "CONTRACT",
    "SCHEMA_VERSION",
    "EVENT_TYPES",
    "EVENT_OPENED",
    "EVENT_UPDATED",
    "BOUNDARY_PROPOSED",
    "EVENT_CLOSED",
    "PREDICTION_CREATED",
    "PREDICTION_RESOLVED",
    "PREDICTION_ERROR",
    "INTERRUPT_CANDIDATE",
    "INTERRUPT_ACCEPTED",
    "PROPOSAL_CONTEXT",
    "ACTION_TRACKING_STARTED",
    "ACTION_TRACKING_FINISHED",
    "EPISODE_PROPOSED",
    "MODULATORS_SNAPSHOTTED",
    "CONNECTION_HEALTH_CHANGED",
    "HEALTH_CHANGED",
    "CognitiveEventRecord",
    "build_cognitive_event",
    "validate_cognitive_event",
]
