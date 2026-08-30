import pytest

from event_schema import VelvetEvent
from truth_events import (
    ASYNC_SENSOR_SAMPLE_OBSERVED,
    SENSOR_ESCALATION_OBSERVED,
    TELEMETRY_RECONCILIATION_OBSERVED,
    TIME_INTEGRITY_OBSERVED,
    AsyncSensorSampleObservation,
    SensorEscalationObservation,
    TelemetryReconciliationObservation,
    TimeIntegrityObservation,
    build_truth_event,
    validate_truth_event,
)


def test_time_integrity_event_is_observation_only():
    event = build_truth_event(
        source="clock.supervisor",
        event_type=TIME_INTEGRITY_OBSERVED,
        observation=TimeIntegrityObservation(
            node_id="queen-up2",
            clock_source="gnss",
            source_clock_id="gnss-main",
            timestamp_confidence=0.93,
            monotonic_clock_ok=True,
            sync_source_available=True,
            expected_frequency_hz=10.0,
            measured_frequency_hz=9.99,
        ),
    )

    validate_truth_event(event)
    assert event.metadata["authority"] == "none"
    assert event.payload["status"] == "observation-only"
    assert event.payload["actuation_granted"] is False


def test_async_sensor_sample_preserves_native_and_normalized_time():
    event = build_truth_event(
        source="seat.left.cluster",
        event_type=ASYNC_SENSOR_SAMPLE_OBSERVED,
        observation=AsyncSensorSampleObservation(
            sensor_id="seat-left-pressure",
            native_timestamp=123.4,
            source_clock_id="seat-left-mcu-clock",
            source_clock_confidence=0.82,
            normalized_timestamp=124.0,
            normalization_method="converted",
            interpolation_used=False,
            derived_from_packet_ids=("raw-1", "raw-2"),
        ),
    )

    validate_truth_event(event)
    assert event.payload["native_timestamp"] == 123.4
    assert event.payload["normalized_timestamp"] == 124.0
    assert event.payload["derived_from_packet_ids"] == ["raw-1", "raw-2"]


def test_telemetry_reconciliation_reports_contradiction_without_authority():
    event = build_truth_event(
        source="velour.telemetry",
        event_type=TELEMETRY_RECONCILIATION_OBSERVED,
        observation=TelemetryReconciliationObservation(
            reconciliation_id="power-branch-sum-1",
            left_measurement="branch_current_sum",
            right_measurement="supply_current",
            expected_relation="within_tolerance",
            contradiction_detected=True,
            confidence=0.76,
            observed_left=8.2,
            observed_right=5.0,
            tolerance=0.5,
            likely_fault_domain="sensor",
        ),
    )

    validate_truth_event(event)
    assert event.payload["contradiction_detected"] is True
    assert event.payload["actuation_granted"] is False


def test_sensor_escalation_records_energy_mode():
    event = build_truth_event(
        source="perimeter.pod",
        event_type=SENSOR_ESCALATION_OBSERVED,
        observation=SensorEscalationObservation(
            sensor_id="garage-door-vibe",
            energy_mode="diagnostic",
            sample_rate_hz=400.0,
            local_threshold_crossed=True,
            evidence_capture_started=True,
            return_to_sentinel_condition="quiet_for_30_seconds",
            escalation_reason="vibration spike",
            corroborating_sources=("door-contact",),
        ),
    )

    validate_truth_event(event)
    assert event.payload["energy_mode"] == "diagnostic"
    assert event.payload["corroborating_sources"] == ["door-contact"]


def test_truth_event_rejects_forbidden_authority_fields():
    event = VelvetEvent(
        source="bad.actor",
        event_type=TIME_INTEGRITY_OBSERVED,
        payload={
            "node_id": "queen-up2",
            "clock_source": "gnss",
            "source_clock_id": "clock",
            "timestamp_confidence": 1.0,
            "monotonic_clock_ok": True,
            "sync_source_available": True,
            "status": "observation-only",
            "actuation_granted": False,
            "command": "unlock",
        },
    )

    with pytest.raises(ValueError, match="forbidden authority"):
        validate_truth_event(event)


def test_truth_event_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="timestamp_confidence"):
        TimeIntegrityObservation(
            node_id="queen-up2",
            clock_source="gnss",
            source_clock_id="clock",
            timestamp_confidence=1.5,
            monotonic_clock_ok=True,
            sync_source_available=True,
        ).to_payload()
