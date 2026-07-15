# SPDX-License-Identifier: GPL-3.0-only
"""Ghost CAN observation event contract.

This contract carries synthetic, read-only CAN observations for the public
Velvet ghost system. It describes a jarred-car telemetry event only. It never
opens hardware, transmits CAN frames, grants authority, or requests actuation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from event_schema import VelvetEvent

GHOST_CAN_OBSERVATION_EVENT = "vehicle.can.ghost_observation"
GHOST_CAN_OBSERVATION_CONTRACT = "velvet.event.vehicle_can_ghost.v1"

_FORBIDDEN_PAYLOAD_KEYS = {
    "action",
    "actuate",
    "actuation",
    "capability",
    "command",
    "executor",
    "executor_name",
    "hardware",
    "hardware_target",
    "shell",
    "token",
}

_REQUIRED_FLAGS = {
    "read_only": True,
    "synthetic_fixture": True,
    "synthetic": True,
    "physical_bus_opened": False,
    "hardware_bus_opened": False,
    "can_transmission_attempted": False,
    "can_transmission_performed": False,
    "actuation_granted": False,
    "actuation_performed": False,
    "authority_granted": False,
}


@dataclass(frozen=True)
class GhostCanObservation:
    can_id: int | str
    data_hex: str
    signals: Mapping[str, int | float | str | bool] = field(default_factory=dict)
    timestamp: float | None = None
    source_profile: str = "tiburon-public-ghost"

    def to_payload(self) -> dict[str, Any]:
        _validate_observation(self)
        can_id = _normalize_can_id(self.can_id)
        data_hex = self.data_hex.upper()
        payload: dict[str, Any] = {
            "schema": GHOST_CAN_OBSERVATION_CONTRACT,
            "event_type": GHOST_CAN_OBSERVATION_EVENT,
            "route_id": "can-ghost",
            "target": "vehicle-can-ghost",
            "status": "synthetic-observation-only",
            "mode": "read-only",
            "can_id": can_id,
            "can_id_hex": f"0x{can_id:X}",
            "data_hex": data_hex,
            "dlc": len(data_hex) // 2,
            "signals": dict(self.signals),
            "decoded_signals": dict(self.signals),
            "source_profile": self.source_profile,
            **_REQUIRED_FLAGS,
        }
        if self.timestamp is not None:
            payload["timestamp"] = float(self.timestamp)
        return payload


def build_ghost_can_observation_event(
    *,
    source: str,
    observation: GhostCanObservation,
    parent_event_id: str | None = None,
    receipt_id: str | None = None,
) -> VelvetEvent:
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")
    return VelvetEvent(
        source=source.strip(),
        event_type=GHOST_CAN_OBSERVATION_EVENT,
        payload=observation.to_payload(),
        metadata={
            "contract": GHOST_CAN_OBSERVATION_CONTRACT,
            "authority": "none",
            "public_demo": True,
        },
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )


def validate_ghost_can_observation_event(event: VelvetEvent | Mapping[str, Any]) -> None:
    document = event.to_dict() if isinstance(event, VelvetEvent) else dict(event)
    if document.get("event_type") != GHOST_CAN_OBSERVATION_EVENT:
        raise ValueError("unexpected event type for ghost CAN observation")

    payload = document.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("ghost CAN observation payload must be a mapping")

    forbidden = _FORBIDDEN_PAYLOAD_KEYS.intersection(payload)
    if forbidden:
        raise ValueError(f"ghost CAN observation contains forbidden authority fields: {sorted(forbidden)}")

    for key, expected in _REQUIRED_FLAGS.items():
        if payload.get(key) is not expected:
            raise ValueError(f"ghost CAN payload {key} must be {expected!r}")

    if payload.get("event_type") != GHOST_CAN_OBSERVATION_EVENT:
        raise ValueError("ghost CAN payload event_type mismatch")
    if payload.get("route_id") != "can-ghost":
        raise ValueError("ghost CAN payload route_id must be can-ghost")
    if payload.get("target") != "vehicle-can-ghost":
        raise ValueError("ghost CAN payload target must be vehicle-can-ghost")
    if payload.get("status") != "synthetic-observation-only":
        raise ValueError("ghost CAN status must be synthetic-observation-only")
    if payload.get("mode") != "read-only":
        raise ValueError("ghost CAN mode must be read-only")

    can_id = payload.get("can_id")
    if isinstance(can_id, str):
        can_id = _normalize_can_id(can_id)
    if isinstance(can_id, bool) or not isinstance(can_id, int) or can_id < 0:
        raise ValueError("ghost CAN payload can_id must be a non-negative integer")

    data_hex = payload.get("data_hex")
    if not isinstance(data_hex, str) or len(data_hex) % 2 != 0:
        raise ValueError("ghost CAN payload data_hex must be an even-length hex string")
    try:
        int(data_hex or "0", 16)
    except ValueError as exc:
        raise ValueError("ghost CAN payload data_hex must be hexadecimal") from exc

    dlc = payload.get("dlc")
    if isinstance(dlc, bool) or not isinstance(dlc, int) or dlc != len(data_hex) // 2:
        raise ValueError("ghost CAN payload dlc must match data_hex length")

    signals = payload.get("signals", {})
    if not isinstance(signals, Mapping):
        raise ValueError("ghost CAN payload signals must be a mapping")
    for key, value in signals.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("ghost CAN signal names must be non-empty strings")
        if isinstance(value, (dict, list, tuple, set)) or value is None:
            raise ValueError("ghost CAN signal values must be scalar")


def _validate_observation(observation: GhostCanObservation) -> None:
    _normalize_can_id(observation.can_id)
    if not isinstance(observation.data_hex, str) or len(observation.data_hex) % 2 != 0:
        raise ValueError("data_hex must be an even-length hex string")
    try:
        int(observation.data_hex or "0", 16)
    except ValueError as exc:
        raise ValueError("data_hex must be hexadecimal") from exc
    if not isinstance(observation.signals, Mapping):
        raise ValueError("signals must be a mapping")
    if observation.timestamp is not None:
        if isinstance(observation.timestamp, bool) or not isinstance(observation.timestamp, (int, float)):
            raise ValueError("timestamp must be numeric when provided")
        if float(observation.timestamp) < 0:
            raise ValueError("timestamp cannot be negative")
    if not isinstance(observation.source_profile, str) or not observation.source_profile.strip():
        raise ValueError("source_profile must be a non-empty string")


def _normalize_can_id(can_id: int | str) -> int:
    if isinstance(can_id, bool):
        raise ValueError("can_id must be an integer or hex string")
    if isinstance(can_id, int):
        value = can_id
    elif isinstance(can_id, str) and can_id.strip():
        stripped = can_id.strip()
        value = int(stripped, 16) if stripped.lower().startswith("0x") else int(stripped)
    else:
        raise ValueError("can_id must be an integer or hex string")
    if value < 0:
        raise ValueError("can_id cannot be negative")
    return value
