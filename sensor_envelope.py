# SPDX-License-Identifier: GPL-3.0-only
"""Common read-only sensor observation envelope."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from event_schema import VelvetEvent

SENSOR_OBSERVATION_REPORTED = "SENSOR_OBSERVATION_REPORTED"
SENSOR_ENVELOPE_CONTRACT = "velvet.sensor-envelope.v0.1"

COMMISSIONING_STATES = {"observe", "trust", "advise", "authorize"}
HEALTH_STATES = {
    "healthy", "degraded", "blocked", "misaligned_suspected",
    "interference", "overtemperature", "communication_fault",
    "timing_fault", "calibration_invalid", "offline", "unknown",
}
QUALITY_STATES = {"valid", "degraded", "invalid", "unknown"}
TIME_SYNC_STATES = {"synchronized", "unsynchronized", "degraded", "unknown"}


@dataclass(frozen=True)
class SensorEnvelope:
    sensor_id: str
    sensor_family: str
    payload_type: str
    sensor_payload: Mapping[str, Any]
    measured_at: float
    received_at: float
    health_state: str
    quality_state: str
    message_confidence: float
    commissioning: Mapping[str, str]
    provenance: Mapping[str, str]
    sequence: int | None = None
    monotonic_ns: int | None = None
    time_sync_state: str = "unknown"
    estimated_sync_error_us: float | None = None
    mount_id: str | None = None
    calibration_id: str | None = None
    reference_frame: str = "vehicle_body"
    quality_reasons: tuple[str, ...] = field(default_factory=tuple)

    def to_payload(self) -> dict[str, Any]:
        _validate(self)
        result: dict[str, Any] = {
            "schema": "velvet.sensor-envelope",
            "version": "0.1.0",
            "sensor": {"id": self.sensor_id, "family": self.sensor_family},
            "time": {
                "measurement": float(self.measured_at),
                "received": float(self.received_at),
                "sync_state": self.time_sync_state,
            },
            "frame": {
                "reference": self.reference_frame,
                "mount_id": self.mount_id,
                "calibration_id": self.calibration_id,
            },
            "health": {"state": self.health_state},
            "quality": {
                "state": self.quality_state,
                "message_confidence": float(self.message_confidence),
                "reasons": list(self.quality_reasons),
            },
            "commissioning": dict(self.commissioning),
            "provenance": dict(self.provenance),
            "sensor_payload": {"type": self.payload_type, "data": dict(self.sensor_payload)},
            "status": "observation-only",
            "read_only": True,
        }
        if self.sequence is not None:
            result["sequence"] = self.sequence
        if self.monotonic_ns is not None:
            result["time"]["monotonic_ns"] = self.monotonic_ns
        if self.estimated_sync_error_us is not None:
            result["time"]["estimated_sync_error_us"] = float(self.estimated_sync_error_us)
        return result


def build_sensor_observation_event(*, source: str, envelope: SensorEnvelope) -> VelvetEvent:
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")
    return VelvetEvent(
        source=source.strip(),
        event_type=SENSOR_OBSERVATION_REPORTED,
        payload=envelope.to_payload(),
        metadata={"contract": SENSOR_ENVELOPE_CONTRACT, "authority": "none"},
    )


def _validate(envelope: SensorEnvelope) -> None:
    for name, value in (
        ("sensor_id", envelope.sensor_id),
        ("sensor_family", envelope.sensor_family),
        ("payload_type", envelope.payload_type),
        ("reference_frame", envelope.reference_frame),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    if not isinstance(envelope.sensor_payload, Mapping):
        raise ValueError("sensor_payload must be a mapping")
    if envelope.health_state not in HEALTH_STATES:
        raise ValueError("invalid health_state")
    if envelope.quality_state not in QUALITY_STATES:
        raise ValueError("invalid quality_state")
    if envelope.time_sync_state not in TIME_SYNC_STATES:
        raise ValueError("invalid time_sync_state")
    if not 0.0 <= float(envelope.message_confidence) <= 1.0:
        raise ValueError("message_confidence must be between 0 and 1")
    if not envelope.commissioning:
        raise ValueError("commissioning must not be empty")
    if any(state not in COMMISSIONING_STATES for state in envelope.commissioning.values()):
        raise ValueError("invalid commissioning state")
    if not envelope.provenance:
        raise ValueError("provenance must not be empty")
    if envelope.measured_at < 0 or envelope.received_at < 0:
        raise ValueError("timestamps cannot be negative")
