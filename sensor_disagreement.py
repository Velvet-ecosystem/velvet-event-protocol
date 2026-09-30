# SPDX-License-Identifier: GPL-3.0-only
"""Cross-sensor disagreement evidence without assigning blame or authority."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Union

from event_schema import VelvetEvent

SENSOR_DISAGREEMENT_REPORTED = "SENSOR_DISAGREEMENT_REPORTED"
SENSOR_DISAGREEMENT_CONTRACT = "velvet.sensor-disagreement.v0.1"
DISAGREEMENT_SEVERITIES = {"info", "low", "medium", "high", "critical"}
_SCALAR = Union[int, float, str, bool]


@dataclass(frozen=True)
class SensorDisagreement:
    sources: tuple[str, ...]
    property_name: str
    observations: Mapping[str, _SCALAR]
    observed_at: float
    severity: str = "medium"
    difference: float | None = None
    association_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        if len(self.sources) < 2:
            raise ValueError("sources must contain at least two sensors")
        normalized_sources = []
        for source in self.sources:
            _require_text("source", source)
            normalized_sources.append(source.strip())
        if len(set(normalized_sources)) != len(normalized_sources):
            raise ValueError("sources must be unique")

        _require_text("property_name", self.property_name)
        if set(self.observations) != set(normalized_sources):
            raise ValueError("observations must contain exactly the declared sources")
        for source, value in self.observations.items():
            _require_text("observation source", source)
            if value is None or isinstance(value, (dict, list, tuple, set)):
                raise ValueError("observation values must be scalar")

        if isinstance(self.observed_at, bool) or not isinstance(self.observed_at, (int, float)):
            raise ValueError("observed_at must be numeric")
        if float(self.observed_at) < 0:
            raise ValueError("observed_at cannot be negative")
        if self.severity not in DISAGREEMENT_SEVERITIES:
            raise ValueError("invalid disagreement severity")
        if self.difference is not None:
            if isinstance(self.difference, bool) or not isinstance(self.difference, (int, float)):
                raise ValueError("difference must be numeric")
        if self.association_id is not None:
            _require_text("association_id", self.association_id)

        payload: dict[str, Any] = {
            "sources": normalized_sources,
            "property": self.property_name.strip(),
            "observations": dict(self.observations),
            "observed_at": float(self.observed_at),
            "severity": self.severity,
            "status": "evidence-only",
            "read_only": True,
            "fault_assignment": None,
        }
        if self.difference is not None:
            payload["difference"] = float(self.difference)
        if self.association_id is not None:
            payload["association_id"] = self.association_id.strip()
        return payload


def build_sensor_disagreement_event(*, source: str, disagreement: SensorDisagreement) -> VelvetEvent:
    _require_text("source", source)
    return VelvetEvent(
        source=source.strip(),
        event_type=SENSOR_DISAGREEMENT_REPORTED,
        payload=disagreement.to_payload(),
        metadata={"contract": SENSOR_DISAGREEMENT_CONTRACT, "authority": "none"},
    )


def _require_text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
