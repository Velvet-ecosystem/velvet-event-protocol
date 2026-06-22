# SPDX-License-Identifier: GPL-3.0-only
"""Decoded CAN observation event contract.

Decoded signal events carry interpreted telemetry only. They never grant authority,
select executors, identify hardware handles, or request actuation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from event_schema import VelvetEvent

DECODED_CAN_SIGNAL_OBSERVED = "DECODED_CAN_SIGNAL_OBSERVED"

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
    "route_id",
    "shell",
    "target",
    "token",
}


@dataclass(frozen=True)
class DecodedCanSignalObservation:
    signal_name: str
    value: int | float | str | bool
    confidence: float
    observed_at: float
    source_profile: str
    unit: str | None = None

    def to_payload(self) -> dict[str, Any]:
        _validate_observation(self)
        payload: dict[str, Any] = {
            "signal_name": self.signal_name,
            "value": self.value,
            "confidence": float(self.confidence),
            "observed_at": float(self.observed_at),
            "source_profile": self.source_profile,
            "status": "observation-only",
            "read_only": True,
            "actuation_granted": False,
            "actuation_performed": False,
        }
        if self.unit is not None:
            payload["unit"] = self.unit
        return payload


def build_decoded_can_signal_event(
    *,
    source: str,
    observation: DecodedCanSignalObservation,
    parent_event_id: str | None = None,
    receipt_id: str | None = None,
) -> VelvetEvent:
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")
    return VelvetEvent(
        source=source.strip(),
        event_type=DECODED_CAN_SIGNAL_OBSERVED,
        payload=observation.to_payload(),
        metadata={
            "contract": "velvet.decoded-can-observation.v1",
            "authority": "none",
        },
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )


def validate_decoded_can_signal_event(event: VelvetEvent | Mapping[str, Any]) -> None:
    document = event.to_dict() if isinstance(event, VelvetEvent) else dict(event)
    if document.get("event_type") != DECODED_CAN_SIGNAL_OBSERVED:
        raise ValueError("unexpected event type for decoded CAN observation")

    payload = document.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("decoded CAN observation payload must be a mapping")

    forbidden = _FORBIDDEN_PAYLOAD_KEYS.intersection(payload)
    if forbidden:
        raise ValueError(f"decoded CAN observation contains forbidden authority fields: {sorted(forbidden)}")

    required = {
        "signal_name",
        "value",
        "confidence",
        "observed_at",
        "source_profile",
        "status",
        "read_only",
        "actuation_granted",
        "actuation_performed",
    }
    missing = required - set(payload)
    if missing:
        raise ValueError(f"decoded CAN observation is missing fields: {sorted(missing)}")

    observation = DecodedCanSignalObservation(
        signal_name=payload["signal_name"],
        value=payload["value"],
        confidence=payload["confidence"],
        observed_at=payload["observed_at"],
        source_profile=payload["source_profile"],
        unit=payload.get("unit"),
    )
    _validate_observation(observation)

    if payload.get("status") != "observation-only":
        raise ValueError("decoded CAN observation status must be observation-only")
    if payload.get("read_only") is not True:
        raise ValueError("decoded CAN observation must be read_only")
    if payload.get("actuation_granted") is not False:
        raise ValueError("decoded CAN observation cannot grant actuation")
    if payload.get("actuation_performed") is not False:
        raise ValueError("decoded CAN observation cannot claim actuation")


def _validate_observation(observation: DecodedCanSignalObservation) -> None:
    if not isinstance(observation.signal_name, str) or not observation.signal_name.strip():
        raise ValueError("signal_name must be a non-empty string")
    if isinstance(observation.value, (dict, list, tuple, set)) or observation.value is None:
        raise ValueError("value must be a scalar")
    if isinstance(observation.confidence, bool) or not isinstance(observation.confidence, (int, float)):
        raise ValueError("confidence must be numeric")
    if not 0.0 <= float(observation.confidence) <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if isinstance(observation.observed_at, bool) or not isinstance(observation.observed_at, (int, float)):
        raise ValueError("observed_at must be numeric")
    if float(observation.observed_at) < 0:
        raise ValueError("observed_at cannot be negative")
    if not isinstance(observation.source_profile, str) or not observation.source_profile.strip():
        raise ValueError("source_profile must be a non-empty string")
    if observation.unit is not None and (not isinstance(observation.unit, str) or not observation.unit.strip()):
        raise ValueError("unit must be a non-empty string when provided")
