# SPDX-License-Identifier: GPL-3.0-only
"""Truth-layer event contracts for Velvet.

These events preserve timing truth, sensor trust, telemetry contradictions, and
sensor escalation state. They describe observation quality only. They do not
grant authority, select executors, identify hardware handles, or request
actuation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from event_schema import VelvetEvent

TIME_INTEGRITY_OBSERVED = "TIME_INTEGRITY_OBSERVED"
HOLDOVER_STATE_OBSERVED = "HOLDOVER_STATE_OBSERVED"
ASYNC_SENSOR_SAMPLE_OBSERVED = "ASYNC_SENSOR_SAMPLE_OBSERVED"
SENSOR_TRUST_AGING_OBSERVED = "SENSOR_TRUST_AGING_OBSERVED"
HEALTH_TREND_OBSERVED = "HEALTH_TREND_OBSERVED"
TELEMETRY_RECONCILIATION_OBSERVED = "TELEMETRY_RECONCILIATION_OBSERVED"
SENSOR_ESCALATION_OBSERVED = "SENSOR_ESCALATION_OBSERVED"

_CONTRACT_VERSION = "velvet.truth-events.v1"

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

_VALID_CLOCK_SOURCES = {
    "gnss",
    "rtc",
    "monotonic",
    "network_sync",
    "supervisor",
    "unknown",
}

_VALID_HEALTH_TRENDS = {"improving", "stable", "worsening", "unknown"}
_VALID_ENERGY_MODES = {"sentinel", "normal", "diagnostic"}


@dataclass(frozen=True)
class TimeIntegrityObservation:
    node_id: str
    clock_source: str
    source_clock_id: str
    timestamp_confidence: float
    monotonic_clock_ok: bool
    sync_source_available: bool
    expected_frequency_hz: float | None = None
    measured_frequency_hz: float | None = None
    frequency_deviation_ppm: float | None = None
    drift_suspected: bool = False
    throttling_suspected: bool = False
    oscillator_fault_suspected: bool = False
    last_sync_timestamp: float | None = None

    def to_payload(self) -> dict[str, Any]:
        _validate_time_integrity(self)
        payload: dict[str, Any] = {
            "node_id": self.node_id.strip(),
            "clock_source": self.clock_source,
            "source_clock_id": self.source_clock_id.strip(),
            "timestamp_confidence": float(self.timestamp_confidence),
            "monotonic_clock_ok": bool(self.monotonic_clock_ok),
            "sync_source_available": bool(self.sync_source_available),
            "drift_suspected": bool(self.drift_suspected),
            "throttling_suspected": bool(self.throttling_suspected),
            "oscillator_fault_suspected": bool(self.oscillator_fault_suspected),
            "status": "observation-only",
            "actuation_granted": False,
        }
        _optional_number(payload, "expected_frequency_hz", self.expected_frequency_hz)
        _optional_number(payload, "measured_frequency_hz", self.measured_frequency_hz)
        _optional_number(payload, "frequency_deviation_ppm", self.frequency_deviation_ppm)
        _optional_number(payload, "last_sync_timestamp", self.last_sync_timestamp)
        return payload


@dataclass(frozen=True)
class HoldoverStateObservation:
    node_id: str
    preferred_time_source: str
    holdover_source: str
    holdover_confidence: float
    holdover_expired: bool
    holdover_started_at: float | None = None
    estimated_drift_ppm: float | None = None
    max_trusted_holdover_ms: int | None = None

    def to_payload(self) -> dict[str, Any]:
        _validate_non_empty("node_id", self.node_id)
        _validate_non_empty("preferred_time_source", self.preferred_time_source)
        _validate_non_empty("holdover_source", self.holdover_source)
        _validate_confidence("holdover_confidence", self.holdover_confidence)
        if self.max_trusted_holdover_ms is not None:
            _validate_non_negative_int("max_trusted_holdover_ms", self.max_trusted_holdover_ms)
        payload: dict[str, Any] = {
            "node_id": self.node_id.strip(),
            "preferred_time_source": self.preferred_time_source.strip(),
            "holdover_source": self.holdover_source.strip(),
            "holdover_confidence": float(self.holdover_confidence),
            "holdover_expired": bool(self.holdover_expired),
            "status": "observation-only",
            "actuation_granted": False,
        }
        _optional_number(payload, "holdover_started_at", self.holdover_started_at)
        _optional_number(payload, "estimated_drift_ppm", self.estimated_drift_ppm)
        if self.max_trusted_holdover_ms is not None:
            payload["max_trusted_holdover_ms"] = int(self.max_trusted_holdover_ms)
        return payload


@dataclass(frozen=True)
class AsyncSensorSampleObservation:
    sensor_id: str
    native_timestamp: float
    source_clock_id: str
    source_clock_confidence: float
    normalized_timestamp: float
    normalization_method: str
    interpolation_used: bool
    derived_from_packet_ids: tuple[str, ...] = ()
    native_sequence_id: str | None = None
    raw_packet_reference: str | None = None
    capture_rate_hz: float | None = None

    def to_payload(self) -> dict[str, Any]:
        _validate_non_empty("sensor_id", self.sensor_id)
        _validate_non_negative_number("native_timestamp", self.native_timestamp)
        _validate_non_empty("source_clock_id", self.source_clock_id)
        _validate_confidence("source_clock_confidence", self.source_clock_confidence)
        _validate_non_negative_number("normalized_timestamp", self.normalized_timestamp)
        _validate_non_empty("normalization_method", self.normalization_method)
        for packet_id in self.derived_from_packet_ids:
            _validate_non_empty("derived_from_packet_ids[]", packet_id)
        payload: dict[str, Any] = {
            "sensor_id": self.sensor_id.strip(),
            "native_timestamp": float(self.native_timestamp),
            "source_clock_id": self.source_clock_id.strip(),
            "source_clock_confidence": float(self.source_clock_confidence),
            "normalized_timestamp": float(self.normalized_timestamp),
            "normalization_method": self.normalization_method.strip(),
            "interpolation_used": bool(self.interpolation_used),
            "derived_from_packet_ids": [packet_id.strip() for packet_id in self.derived_from_packet_ids],
            "status": "observation-only",
            "actuation_granted": False,
        }
        _optional_string(payload, "native_sequence_id", self.native_sequence_id)
        _optional_string(payload, "raw_packet_reference", self.raw_packet_reference)
        _optional_number(payload, "capture_rate_hz", self.capture_rate_hz)
        return payload


@dataclass(frozen=True)
class SensorTrustAgingObservation:
    sensor_id: str
    signal_quality: float
    service_life_confidence: float
    current_trust: float
    replacement_recommended: bool = False
    installed_at: float | None = None
    operating_hours: float | None = None
    thermal_cycles: int | None = None
    fault_exposure_count: int | None = None
    calibration_version: str | None = None
    calibration_age_hours: float | None = None
    trust_derating_reason: str | None = None

    def to_payload(self) -> dict[str, Any]:
        _validate_non_empty("sensor_id", self.sensor_id)
        _validate_confidence("signal_quality", self.signal_quality)
        _validate_confidence("service_life_confidence", self.service_life_confidence)
        _validate_confidence("current_trust", self.current_trust)
        payload: dict[str, Any] = {
            "sensor_id": self.sensor_id.strip(),
            "signal_quality": float(self.signal_quality),
            "service_life_confidence": float(self.service_life_confidence),
            "current_trust": float(self.current_trust),
            "replacement_recommended": bool(self.replacement_recommended),
            "status": "observation-only",
            "actuation_granted": False,
        }
        _optional_number(payload, "installed_at", self.installed_at)
        _optional_number(payload, "operating_hours", self.operating_hours)
        _optional_int(payload, "thermal_cycles", self.thermal_cycles)
        _optional_int(payload, "fault_exposure_count", self.fault_exposure_count)
        _optional_string(payload, "calibration_version", self.calibration_version)
        _optional_number(payload, "calibration_age_hours", self.calibration_age_hours)
        _optional_string(payload, "trust_derating_reason", self.trust_derating_reason)
        return payload


@dataclass(frozen=True)
class HealthTrendObservation:
    module_id: str
    current_state: str
    net_health_direction: str
    trend_window_hours: int
    new_faults_window: int = 0
    resolved_faults_window: int = 0
    recurring_faults_window: int = 0
    recurring_offender: bool = False
    trend_reason: str | None = None

    def to_payload(self) -> dict[str, Any]:
        _validate_non_empty("module_id", self.module_id)
        _validate_non_empty("current_state", self.current_state)
        if self.net_health_direction not in _VALID_HEALTH_TRENDS:
            raise ValueError("net_health_direction must be one of improving, stable, worsening, unknown")
        _validate_non_negative_int("trend_window_hours", self.trend_window_hours)
        _validate_non_negative_int("new_faults_window", self.new_faults_window)
        _validate_non_negative_int("resolved_faults_window", self.resolved_faults_window)
        _validate_non_negative_int("recurring_faults_window", self.recurring_faults_window)
        payload: dict[str, Any] = {
            "module_id": self.module_id.strip(),
            "current_state": self.current_state.strip(),
            "net_health_direction": self.net_health_direction,
            "trend_window_hours": int(self.trend_window_hours),
            "new_faults_window": int(self.new_faults_window),
            "resolved_faults_window": int(self.resolved_faults_window),
            "recurring_faults_window": int(self.recurring_faults_window),
            "recurring_offender": bool(self.recurring_offender),
            "status": "observation-only",
            "actuation_granted": False,
        }
        _optional_string(payload, "trend_reason", self.trend_reason)
        return payload


@dataclass(frozen=True)
class TelemetryReconciliationObservation:
    reconciliation_id: str
    left_measurement: str
    right_measurement: str
    expected_relation: str
    contradiction_detected: bool
    confidence: float
    observed_left: Any = None
    observed_right: Any = None
    tolerance: Any = None
    likely_fault_domain: str = "unknown"

    def to_payload(self) -> dict[str, Any]:
        _validate_non_empty("reconciliation_id", self.reconciliation_id)
        _validate_non_empty("left_measurement", self.left_measurement)
        _validate_non_empty("right_measurement", self.right_measurement)
        _validate_non_empty("expected_relation", self.expected_relation)
        _validate_confidence("confidence", self.confidence)
        _validate_non_empty("likely_fault_domain", self.likely_fault_domain)
        return {
            "reconciliation_id": self.reconciliation_id.strip(),
            "left_measurement": self.left_measurement.strip(),
            "right_measurement": self.right_measurement.strip(),
            "expected_relation": self.expected_relation.strip(),
            "observed_left": self.observed_left,
            "observed_right": self.observed_right,
            "tolerance": self.tolerance,
            "contradiction_detected": bool(self.contradiction_detected),
            "confidence": float(self.confidence),
            "likely_fault_domain": self.likely_fault_domain.strip(),
            "status": "observation-only",
            "actuation_granted": False,
        }


@dataclass(frozen=True)
class SensorEscalationObservation:
    sensor_id: str
    energy_mode: str
    sample_rate_hz: float
    local_threshold_crossed: bool
    evidence_capture_started: bool
    return_to_sentinel_condition: str
    escalation_reason: str | None = None
    corroborating_sources: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        _validate_non_empty("sensor_id", self.sensor_id)
        if self.energy_mode not in _VALID_ENERGY_MODES:
            raise ValueError("energy_mode must be sentinel, normal, or diagnostic")
        _validate_non_negative_number("sample_rate_hz", self.sample_rate_hz)
        _validate_non_empty("return_to_sentinel_condition", self.return_to_sentinel_condition)
        for source in self.corroborating_sources:
            _validate_non_empty("corroborating_sources[]", source)
        payload: dict[str, Any] = {
            "sensor_id": self.sensor_id.strip(),
            "energy_mode": self.energy_mode,
            "sample_rate_hz": float(self.sample_rate_hz),
            "local_threshold_crossed": bool(self.local_threshold_crossed),
            "evidence_capture_started": bool(self.evidence_capture_started),
            "return_to_sentinel_condition": self.return_to_sentinel_condition.strip(),
            "corroborating_sources": [source.strip() for source in self.corroborating_sources],
            "status": "observation-only",
            "actuation_granted": False,
        }
        _optional_string(payload, "escalation_reason", self.escalation_reason)
        return payload


def build_truth_event(
    *,
    source: str,
    event_type: str,
    observation: TimeIntegrityObservation
    | HoldoverStateObservation
    | AsyncSensorSampleObservation
    | SensorTrustAgingObservation
    | HealthTrendObservation
    | TelemetryReconciliationObservation
    | SensorEscalationObservation,
    parent_event_id: str | None = None,
    receipt_id: str | None = None,
) -> VelvetEvent:
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")
    if event_type not in _VALID_EVENT_TYPES:
        raise ValueError("unsupported truth event type")
    payload = observation.to_payload()
    return VelvetEvent(
        source=source.strip(),
        event_type=event_type,
        payload=payload,
        metadata={"contract": _CONTRACT_VERSION, "authority": "none"},
        parent_event_id=parent_event_id,
        receipt_id=receipt_id,
    )


def validate_truth_event(event: VelvetEvent | Mapping[str, Any]) -> None:
    document = event.to_dict() if isinstance(event, VelvetEvent) else dict(event)
    event_type = document.get("event_type")
    if event_type not in _VALID_EVENT_TYPES:
        raise ValueError("unsupported truth event type")

    payload = document.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("truth event payload must be a mapping")

    forbidden = _FORBIDDEN_PAYLOAD_KEYS.intersection(payload)
    if forbidden:
        raise ValueError(f"truth event contains forbidden authority fields: {sorted(forbidden)}")

    if payload.get("status") != "observation-only":
        raise ValueError("truth event status must be observation-only")
    if payload.get("actuation_granted") is not False:
        raise ValueError("truth event cannot grant actuation")

    if event_type == TIME_INTEGRITY_OBSERVED:
        _validate_time_integrity_payload(payload)
    elif event_type == HOLDOVER_STATE_OBSERVED:
        _validate_required(payload, {"node_id", "preferred_time_source", "holdover_source", "holdover_confidence", "holdover_expired"})
        _validate_confidence("holdover_confidence", payload["holdover_confidence"])
    elif event_type == ASYNC_SENSOR_SAMPLE_OBSERVED:
        _validate_required(payload, {"sensor_id", "native_timestamp", "source_clock_id", "source_clock_confidence", "normalized_timestamp", "normalization_method", "interpolation_used", "derived_from_packet_ids"})
        _validate_confidence("source_clock_confidence", payload["source_clock_confidence"])
    elif event_type == SENSOR_TRUST_AGING_OBSERVED:
        _validate_required(payload, {"sensor_id", "signal_quality", "service_life_confidence", "current_trust", "replacement_recommended"})
        _validate_confidence("signal_quality", payload["signal_quality"])
        _validate_confidence("service_life_confidence", payload["service_life_confidence"])
        _validate_confidence("current_trust", payload["current_trust"])
    elif event_type == HEALTH_TREND_OBSERVED:
        _validate_required(payload, {"module_id", "current_state", "net_health_direction", "trend_window_hours"})
        if payload["net_health_direction"] not in _VALID_HEALTH_TRENDS:
            raise ValueError("invalid net_health_direction")
    elif event_type == TELEMETRY_RECONCILIATION_OBSERVED:
        _validate_required(payload, {"reconciliation_id", "left_measurement", "right_measurement", "expected_relation", "contradiction_detected", "confidence"})
        _validate_confidence("confidence", payload["confidence"])
    elif event_type == SENSOR_ESCALATION_OBSERVED:
        _validate_required(payload, {"sensor_id", "energy_mode", "sample_rate_hz", "local_threshold_crossed", "evidence_capture_started", "return_to_sentinel_condition"})
        if payload["energy_mode"] not in _VALID_ENERGY_MODES:
            raise ValueError("invalid energy_mode")


def _validate_time_integrity_payload(payload: Mapping[str, Any]) -> None:
    _validate_required(payload, {"node_id", "clock_source", "source_clock_id", "timestamp_confidence", "monotonic_clock_ok", "sync_source_available"})
    if payload["clock_source"] not in _VALID_CLOCK_SOURCES:
        raise ValueError("invalid clock_source")
    _validate_confidence("timestamp_confidence", payload["timestamp_confidence"])


def _validate_time_integrity(observation: TimeIntegrityObservation) -> None:
    _validate_non_empty("node_id", observation.node_id)
    if observation.clock_source not in _VALID_CLOCK_SOURCES:
        raise ValueError("clock_source must be a known source")
    _validate_non_empty("source_clock_id", observation.source_clock_id)
    _validate_confidence("timestamp_confidence", observation.timestamp_confidence)
    if observation.expected_frequency_hz is not None:
        _validate_non_negative_number("expected_frequency_hz", observation.expected_frequency_hz)
    if observation.measured_frequency_hz is not None:
        _validate_non_negative_number("measured_frequency_hz", observation.measured_frequency_hz)
    if observation.last_sync_timestamp is not None:
        _validate_non_negative_number("last_sync_timestamp", observation.last_sync_timestamp)


def _validate_required(payload: Mapping[str, Any], required: set[str]) -> None:
    missing = required - set(payload)
    if missing:
        raise ValueError(f"truth event is missing fields: {sorted(missing)}")


def _validate_non_empty(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _validate_confidence(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


def _validate_non_negative_number(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if float(value) < 0:
        raise ValueError(f"{name} cannot be negative")


def _validate_non_negative_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")


def _optional_number(payload: dict[str, Any], name: str, value: float | int | None) -> None:
    if value is not None:
        _validate_non_negative_number(name, value)
        payload[name] = float(value)


def _optional_int(payload: dict[str, Any], name: str, value: int | None) -> None:
    if value is not None:
        _validate_non_negative_int(name, value)
        payload[name] = int(value)


def _optional_string(payload: dict[str, Any], name: str, value: str | None) -> None:
    if value is not None:
        _validate_non_empty(name, value)
        payload[name] = value.strip()


_VALID_EVENT_TYPES = {
    TIME_INTEGRITY_OBSERVED,
    HOLDOVER_STATE_OBSERVED,
    ASYNC_SENSOR_SAMPLE_OBSERVED,
    SENSOR_TRUST_AGING_OBSERVED,
    HEALTH_TREND_OBSERVED,
    TELEMETRY_RECONCILIATION_OBSERVED,
    SENSOR_ESCALATION_OBSERVED,
}
