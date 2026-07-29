# SPDX-License-Identifier: GPL-3.0-only
"""Distributed-node advertisement and workload lifecycle event contracts.

These events carry verified Runtime state between trusted local components. They
never select executors, grant Court authority, transfer capability tokens, or
permit actuation. An event describes what Runtime observed or decided; it is not
the decision mechanism itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple

from event_schema import VelvetEvent


NODE_ADVERTISEMENT_PUBLISHED = "NODE_ADVERTISEMENT_PUBLISHED"
WORK_OFFERED = "WORK_OFFERED"
WORK_ACCEPTED = "WORK_ACCEPTED"
WORK_REFUSED = "WORK_REFUSED"
WORK_HANDOFF_REQUESTED = "WORK_HANDOFF_REQUESTED"
WORK_COMPLETED = "WORK_COMPLETED"
WORK_DEGRADED = "WORK_DEGRADED"
WORK_RECOVERY_REASSIGNED = "WORK_RECOVERY_REASSIGNED"

DISTRIBUTED_WORK_EVENT_TYPES = {
    NODE_ADVERTISEMENT_PUBLISHED,
    WORK_OFFERED,
    WORK_ACCEPTED,
    WORK_REFUSED,
    WORK_HANDOFF_REQUESTED,
    WORK_COMPLETED,
    WORK_DEGRADED,
    WORK_RECOVERY_REASSIGNED,
}

_NODE_TIERS = {"microcontroller", "specialist_linux", "heavy_linux", "queen"}
_NODE_AVAILABILITY = {
    "available",
    "busy",
    "saturated",
    "degraded",
    "draining",
    "offline",
    "quarantined",
}
_PLACEMENT_MODES = {
    "primary",
    "overflow",
    "temporary_absorption",
    "queen_fallback",
    "partial",
    "observe_only",
}
_DEGRADATION_MODES = {
    "full_replacement",
    "partial_replacement",
    "observe_only",
    "capability_unavailable",
}
_RESULT_STATES = {"completed", "partial", "failed", "cancelled"}

_FORBIDDEN_AUTHORITY_KEYS = {
    "action",
    "actuate",
    "actuation",
    "authorized_by",
    "capability_token",
    "command",
    "court_token",
    "execution_token",
    "executor",
    "executor_name",
    "hardware_handle",
    "hardware_target",
    "permit",
    "shell",
    "token",
}

_TRANSPORT_FLAGS = {
    "transport_only": True,
    "canonical": False,
    "authority": "none",
    "grants_authority": False,
    "grants_execution": False,
    "grants_actuation": False,
}


@dataclass(frozen=True)
class NodeAdvertisement:
    """One node's body binding, capabilities, limits, and live condition."""

    node_id: str
    body_id: str
    organ: str
    tier: str
    capabilities: Tuple[str, ...]
    current_load: float
    health: float
    availability: str
    last_heartbeat: float
    max_concurrent_tasks: int
    current_tasks: int = 0
    accepted_work_classes: Tuple[str, ...] = ()
    refused_work_classes: Tuple[str, ...] = ()
    overflow_capabilities: Tuple[str, ...] = ()
    temporary_absorption_capabilities: Tuple[str, ...] = ()
    fallback_options: Tuple[str, ...] = ()
    body_verified: bool = True
    continuity_verified: bool = True

    def to_payload(self) -> dict[str, Any]:
        _validate_node_advertisement(self)
        return {
            "node_id": self.node_id.strip(),
            "body_id": self.body_id.strip(),
            "organ": self.organ.strip(),
            "tier": self.tier,
            "capabilities": list(self.capabilities),
            "current_load": float(self.current_load),
            "health": float(self.health),
            "availability": self.availability,
            "last_heartbeat": float(self.last_heartbeat),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "current_tasks": self.current_tasks,
            "accepted_work_classes": list(self.accepted_work_classes),
            "refused_work_classes": list(self.refused_work_classes),
            "overflow_capabilities": list(self.overflow_capabilities),
            "temporary_absorption_capabilities": list(
                self.temporary_absorption_capabilities
            ),
            "fallback_options": list(self.fallback_options),
            "body_verified": self.body_verified,
            "continuity_verified": self.continuity_verified,
            **_TRANSPORT_FLAGS,
        }


@dataclass(frozen=True)
class WorkLifecycleRecord:
    """One bounded distributed-work state transition."""

    event_type: str
    work_id: str
    work_class: str
    required_capabilities: Tuple[str, ...] = ()
    node_id: Optional[str] = None
    organ: Optional[str] = None
    placement_mode: Optional[str] = None
    lease_id: Optional[str] = None
    lease_expires_at: Optional[float] = None
    reason: Optional[str] = None
    fallback_options: Tuple[str, ...] = ()
    degradation_mode: Optional[str] = None
    result_status: Optional[str] = None
    from_node_id: Optional[str] = None
    to_node_id: Optional[str] = None
    important_result: bool = False
    escalate_to_queen: bool = True
    court_authorization_required: bool = False

    def to_payload(self) -> dict[str, Any]:
        _validate_work_record(self)
        payload: dict[str, Any] = {
            "work_id": self.work_id.strip(),
            "work_class": self.work_class.strip(),
            "required_capabilities": list(self.required_capabilities),
            "fallback_options": list(self.fallback_options),
            "important_result": self.important_result,
            "escalate_to_queen": self.escalate_to_queen,
            "court_authorization_required": self.court_authorization_required,
            **_TRANSPORT_FLAGS,
        }
        optional = {
            "node_id": self.node_id,
            "organ": self.organ,
            "placement_mode": self.placement_mode,
            "lease_id": self.lease_id,
            "lease_expires_at": self.lease_expires_at,
            "reason": self.reason,
            "degradation_mode": self.degradation_mode,
            "result_status": self.result_status,
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
        }
        for key, value in optional.items():
            if value is not None:
                payload[key] = value.strip() if isinstance(value, str) else float(value)
        return payload


def build_node_advertisement_event(
    *,
    source: str,
    advertisement: NodeAdvertisement,
    parent_event_id: Optional[str] = None,
    receipt_id: Optional[str] = None,
) -> VelvetEvent:
    return _build_event(
        source=source,
        event_type=NODE_ADVERTISEMENT_PUBLISHED,
        payload=advertisement.to_payload(),
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )


def build_distributed_work_event(
    *,
    source: str,
    record: WorkLifecycleRecord,
    parent_event_id: Optional[str] = None,
    receipt_id: Optional[str] = None,
) -> VelvetEvent:
    return _build_event(
        source=source,
        event_type=record.event_type,
        payload=record.to_payload(),
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )


def validate_distributed_work_event(event: VelvetEvent | Mapping[str, Any]) -> None:
    document = event.to_dict() if isinstance(event, VelvetEvent) else dict(event)
    event_type = document.get("event_type")
    if event_type not in DISTRIBUTED_WORK_EVENT_TYPES:
        raise ValueError("unexpected distributed-work event type")

    payload = document.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("distributed-work payload must be a mapping")
    _validate_transport_flags(payload)
    forbidden = _find_forbidden_keys(payload)
    if forbidden:
        raise ValueError(
            "distributed-work event contains forbidden authority fields: "
            f"{sorted(forbidden)}"
        )

    metadata = document.get("metadata")
    if not isinstance(metadata, Mapping):
        raise ValueError("distributed-work metadata must be a mapping")
    if metadata.get("contract") != "velvet.distributed-work-events.v1":
        raise ValueError("unexpected distributed-work contract version")
    if metadata.get("authority") != "none":
        raise ValueError("distributed-work event metadata cannot carry authority")

    if event_type == NODE_ADVERTISEMENT_PUBLISHED:
        advertisement = NodeAdvertisement(
            node_id=payload.get("node_id"),
            body_id=payload.get("body_id"),
            organ=payload.get("organ"),
            tier=payload.get("tier"),
            capabilities=_tuple_field(payload, "capabilities"),
            current_load=payload.get("current_load"),
            health=payload.get("health"),
            availability=payload.get("availability"),
            last_heartbeat=payload.get("last_heartbeat"),
            max_concurrent_tasks=payload.get("max_concurrent_tasks"),
            current_tasks=payload.get("current_tasks"),
            accepted_work_classes=_tuple_field(payload, "accepted_work_classes"),
            refused_work_classes=_tuple_field(payload, "refused_work_classes"),
            overflow_capabilities=_tuple_field(payload, "overflow_capabilities"),
            temporary_absorption_capabilities=_tuple_field(
                payload, "temporary_absorption_capabilities"
            ),
            fallback_options=_tuple_field(payload, "fallback_options"),
            body_verified=payload.get("body_verified"),
            continuity_verified=payload.get("continuity_verified"),
        )
        _validate_node_advertisement(advertisement)
        return

    record = WorkLifecycleRecord(
        event_type=event_type,
        work_id=payload.get("work_id"),
        work_class=payload.get("work_class"),
        required_capabilities=_tuple_field(payload, "required_capabilities"),
        node_id=payload.get("node_id"),
        organ=payload.get("organ"),
        placement_mode=payload.get("placement_mode"),
        lease_id=payload.get("lease_id"),
        lease_expires_at=payload.get("lease_expires_at"),
        reason=payload.get("reason"),
        fallback_options=_tuple_field(payload, "fallback_options"),
        degradation_mode=payload.get("degradation_mode"),
        result_status=payload.get("result_status"),
        from_node_id=payload.get("from_node_id"),
        to_node_id=payload.get("to_node_id"),
        important_result=payload.get("important_result"),
        escalate_to_queen=payload.get("escalate_to_queen"),
        court_authorization_required=payload.get("court_authorization_required"),
    )
    _validate_work_record(record)


def _build_event(
    *,
    source: str,
    event_type: str,
    payload: dict[str, Any],
    parent_event_id: Optional[str],
    receipt_id: Optional[str],
) -> VelvetEvent:
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")
    event = VelvetEvent(
        source=source.strip(),
        event_type=event_type,
        payload=payload,
        metadata={
            "contract": "velvet.distributed-work-events.v1",
            "family": "distributed-work",
            "authority": "none",
        },
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )
    validate_distributed_work_event(event)
    return event


def _validate_node_advertisement(advertisement: NodeAdvertisement) -> None:
    for name, value in (
        ("node_id", advertisement.node_id),
        ("body_id", advertisement.body_id),
        ("organ", advertisement.organ),
    ):
        _require_text(name, value)
    if advertisement.tier not in _NODE_TIERS:
        raise ValueError("invalid node tier")
    if advertisement.availability not in _NODE_AVAILABILITY:
        raise ValueError("invalid node availability")
    _require_text_tuple("capabilities", advertisement.capabilities, required=True)
    for name, values in (
        ("accepted_work_classes", advertisement.accepted_work_classes),
        ("refused_work_classes", advertisement.refused_work_classes),
        ("overflow_capabilities", advertisement.overflow_capabilities),
        (
            "temporary_absorption_capabilities",
            advertisement.temporary_absorption_capabilities,
        ),
        ("fallback_options", advertisement.fallback_options),
    ):
        _require_text_tuple(name, values)
    _require_ratio("current_load", advertisement.current_load)
    _require_ratio("health", advertisement.health)
    _require_non_negative_number("last_heartbeat", advertisement.last_heartbeat)
    if isinstance(advertisement.max_concurrent_tasks, bool) or not isinstance(
        advertisement.max_concurrent_tasks, int
    ):
        raise ValueError("max_concurrent_tasks must be an integer")
    if advertisement.max_concurrent_tasks < 1:
        raise ValueError("max_concurrent_tasks must be at least one")
    if isinstance(advertisement.current_tasks, bool) or not isinstance(
        advertisement.current_tasks, int
    ):
        raise ValueError("current_tasks must be an integer")
    if not 0 <= advertisement.current_tasks <= advertisement.max_concurrent_tasks:
        raise ValueError("current_tasks must fit the declared task limit")
    if not isinstance(advertisement.body_verified, bool):
        raise ValueError("body_verified must be boolean")
    if not isinstance(advertisement.continuity_verified, bool):
        raise ValueError("continuity_verified must be boolean")


def _validate_work_record(record: WorkLifecycleRecord) -> None:
    if record.event_type not in DISTRIBUTED_WORK_EVENT_TYPES - {
        NODE_ADVERTISEMENT_PUBLISHED
    }:
        raise ValueError("invalid workload lifecycle event type")
    _require_text("work_id", record.work_id)
    _require_text("work_class", record.work_class)
    _require_text_tuple("required_capabilities", record.required_capabilities)
    _require_text_tuple("fallback_options", record.fallback_options)
    for name, value in (
        ("node_id", record.node_id),
        ("organ", record.organ),
        ("lease_id", record.lease_id),
        ("reason", record.reason),
        ("from_node_id", record.from_node_id),
        ("to_node_id", record.to_node_id),
    ):
        if value is not None:
            _require_text(name, value)
    if record.placement_mode is not None and record.placement_mode not in _PLACEMENT_MODES:
        raise ValueError("invalid placement mode")
    if record.degradation_mode is not None and record.degradation_mode not in _DEGRADATION_MODES:
        raise ValueError("invalid degradation mode")
    if record.result_status is not None and record.result_status not in _RESULT_STATES:
        raise ValueError("invalid result status")
    if record.lease_expires_at is not None:
        _require_non_negative_number("lease_expires_at", record.lease_expires_at)
    for name, value in (
        ("important_result", record.important_result),
        ("escalate_to_queen", record.escalate_to_queen),
        ("court_authorization_required", record.court_authorization_required),
    ):
        if not isinstance(value, bool):
            raise ValueError(f"{name} must be boolean")

    if record.event_type == WORK_OFFERED:
        if not record.required_capabilities:
            raise ValueError("work offer requires capabilities")
    elif record.event_type == WORK_ACCEPTED:
        _require_fields(
            record,
            "node_id",
            "organ",
            "placement_mode",
            "lease_id",
            "lease_expires_at",
        )
    elif record.event_type == WORK_REFUSED:
        _require_fields(record, "node_id", "organ", "reason")
    elif record.event_type == WORK_HANDOFF_REQUESTED:
        if record.from_node_id is None and record.node_id is None:
            raise ValueError("handoff requires a source node")
        _require_fields(record, "reason")
    elif record.event_type == WORK_COMPLETED:
        _require_fields(record, "node_id", "organ", "result_status")
    elif record.event_type == WORK_DEGRADED:
        _require_fields(record, "degradation_mode", "reason")
    elif record.event_type == WORK_RECOVERY_REASSIGNED:
        _require_fields(
            record,
            "from_node_id",
            "to_node_id",
            "placement_mode",
            "lease_id",
            "lease_expires_at",
            "reason",
        )


def _validate_transport_flags(payload: Mapping[str, Any]) -> None:
    for key, expected in _TRANSPORT_FLAGS.items():
        if payload.get(key) != expected:
            raise ValueError(f"distributed-work payload must set {key}={expected!r}")


def _find_forbidden_keys(value: Any, path: str = "payload") -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in _FORBIDDEN_AUTHORITY_KEYS:
                found.add(f"{path}.{key}")
            found.update(_find_forbidden_keys(child, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found.update(_find_forbidden_keys(child, f"{path}[{index}]"))
    return found


def _tuple_field(payload: Mapping[str, Any], key: str) -> Tuple[str, ...]:
    value = payload.get(key)
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{key} must be a list")
    return tuple(value)


def _require_fields(record: WorkLifecycleRecord, *names: str) -> None:
    missing = [name for name in names if getattr(record, name) is None]
    if missing:
        raise ValueError(f"{record.event_type} is missing fields: {sorted(missing)}")


def _require_text(name: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _require_text_tuple(name: str, values: Any, required: bool = False) -> None:
    if not isinstance(values, tuple):
        raise ValueError(f"{name} must be a tuple")
    if required and not values:
        raise ValueError(f"{name} cannot be empty")
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{name} must contain non-empty strings")


def _require_ratio(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


def _require_non_negative_number(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if float(value) < 0.0:
        raise ValueError(f"{name} cannot be negative")
