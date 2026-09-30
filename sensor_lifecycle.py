# SPDX-License-Identifier: GPL-3.0-only
"""Read-only sensor lifecycle evidence events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from event_schema import VelvetEvent

SENSOR_LIFECYCLE_REPORTED = "SENSOR_LIFECYCLE_REPORTED"
SENSOR_LIFECYCLE_CONTRACT = "velvet.sensor-lifecycle.v0.1"

LIFECYCLE_STATES = {
    "discovered",
    "online",
    "calibration_loaded",
    "ready",
    "degraded",
    "blocked",
    "offline",
    "recovered",
    "calibration_invalid",
}


@dataclass(frozen=True)
class SensorLifecycleEvent:
    sensor_id: str
    sensor_family: str
    state: str
    occurred_at: float
    reasons: tuple[str, ...] = field(default_factory=tuple)
    calibration_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        _require_text("sensor_id", self.sensor_id)
        _require_text("sensor_family", self.sensor_family)
        if self.state not in LIFECYCLE_STATES:
            raise ValueError("invalid lifecycle state")
        if isinstance(self.occurred_at, bool) or not isinstance(self.occurred_at, (int, float)):
            raise ValueError("occurred_at must be numeric")
        if float(self.occurred_at) < 0:
            raise ValueError("occurred_at cannot be negative")
        for reason in self.reasons:
            _require_text("reason", reason)
        if self.calibration_id is not None:
            _require_text("calibration_id", self.calibration_id)

        payload: dict[str, Any] = {
            "sensor_id": self.sensor_id.strip(),
            "sensor_family": self.sensor_family.strip(),
            "state": self.state,
            "occurred_at": float(self.occurred_at),
            "reasons": list(self.reasons),
            "status": "evidence-only",
            "read_only": True,
        }
        if self.calibration_id is not None:
            payload["calibration_id"] = self.calibration_id.strip()
        return payload


def build_sensor_lifecycle_event(*, source: str, lifecycle: SensorLifecycleEvent) -> VelvetEvent:
    _require_text("source", source)
    return VelvetEvent(
        source=source.strip(),
        event_type=SENSOR_LIFECYCLE_REPORTED,
        payload=lifecycle.to_payload(),
        metadata={"contract": SENSOR_LIFECYCLE_CONTRACT, "authority": "none"},
    )


def _require_text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
