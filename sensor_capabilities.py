# SPDX-License-Identifier: GPL-3.0-only
"""Read-only sensor capability declaration events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from event_schema import VelvetEvent

SENSOR_CAPABILITIES_REPORTED = "SENSOR_CAPABILITIES_REPORTED"
SENSOR_CAPABILITIES_CONTRACT = "velvet.sensor-capabilities.v0.1"


@dataclass(frozen=True)
class SensorCapabilities:
    sensor_id: str
    sensor_family: str
    measurements: tuple[str, ...]
    outputs: tuple[str, ...]
    diagnostics: Mapping[str, bool] = field(default_factory=dict)
    timing: Mapping[str, bool] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        _require_text("sensor_id", self.sensor_id)
        _require_text("sensor_family", self.sensor_family)
        measurements = _normalized_unique("measurements", self.measurements)
        outputs = _normalized_unique("outputs", self.outputs)
        if not measurements and not outputs:
            raise ValueError("at least one measurement or output capability is required")
        _validate_bool_map("diagnostics", self.diagnostics)
        _validate_bool_map("timing", self.timing)
        return {
            "sensor_id": self.sensor_id.strip(),
            "sensor_family": self.sensor_family.strip(),
            "measurements": measurements,
            "outputs": outputs,
            "diagnostics": dict(self.diagnostics),
            "timing": dict(self.timing),
            "status": "declaration-only",
            "read_only": True,
        }


def build_sensor_capabilities_event(*, source: str, capabilities: SensorCapabilities) -> VelvetEvent:
    _require_text("source", source)
    return VelvetEvent(
        source=source.strip(),
        event_type=SENSOR_CAPABILITIES_REPORTED,
        payload=capabilities.to_payload(),
        metadata={"contract": SENSOR_CAPABILITIES_CONTRACT, "authority": "none"},
    )


def _normalized_unique(name: str, values: tuple[str, ...]) -> list[str]:
    normalized = []
    for value in values:
        _require_text(name[:-1] if name.endswith("s") else name, value)
        normalized.append(value.strip())
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} must not contain duplicates")
    return normalized


def _validate_bool_map(name: str, values: Mapping[str, bool]) -> None:
    if not isinstance(values, Mapping):
        raise ValueError(f"{name} must be a mapping")
    for key, value in values.items():
        _require_text(f"{name} key", key)
        if not isinstance(value, bool):
            raise ValueError(f"{name} values must be boolean")


def _require_text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
