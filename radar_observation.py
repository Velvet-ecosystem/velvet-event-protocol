# SPDX-License-Identifier: GPL-3.0-only
"""Normalized radar evidence payloads for the Velvet sensor envelope."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


RADAR_DETECTION_FRAME = "radar_detection_frame"
RADAR_LOCAL_TRACK = "radar_local_track"


@dataclass(frozen=True)
class RadarClassification:
    label: str
    confidence: float
    source: str = "sensor_local_model"

    def to_payload(self) -> dict[str, Any]:
        _require_text("classification.label", self.label)
        _require_text("classification.source", self.source)
        _require_probability("classification.confidence", self.confidence)
        return {
            "label": self.label.strip(),
            "confidence": float(self.confidence),
            "source": self.source.strip(),
        }


@dataclass(frozen=True)
class RadarDetection:
    detection_id: str
    range_m: float
    radial_velocity_mps: float
    azimuth_deg: float
    elevation_deg: float | None = None
    snr_db: float | None = None
    rcs_dbsm: float | None = None
    uncertainty: Mapping[str, float] = field(default_factory=dict)
    quality_flags: tuple[str, ...] = field(default_factory=tuple)
    classification: RadarClassification | None = None

    def to_payload(self) -> dict[str, Any]:
        _require_text("detection_id", self.detection_id)
        _require_nonnegative("range_m", self.range_m)
        _require_number("radial_velocity_mps", self.radial_velocity_mps)
        _require_angle("azimuth_deg", self.azimuth_deg, -180.0, 180.0)
        if self.elevation_deg is not None:
            _require_angle("elevation_deg", self.elevation_deg, -90.0, 90.0)
        for key, value in self.uncertainty.items():
            _require_text("uncertainty key", key)
            _require_nonnegative(f"uncertainty.{key}", value)
        for flag in self.quality_flags:
            _require_text("quality flag", flag)

        payload: dict[str, Any] = {
            "detection_id": self.detection_id.strip(),
            "range_m": float(self.range_m),
            "radial_velocity_mps": float(self.radial_velocity_mps),
            "azimuth_deg": float(self.azimuth_deg),
            "uncertainty": {key: float(value) for key, value in self.uncertainty.items()},
            "quality_flags": list(self.quality_flags),
        }
        if self.elevation_deg is not None:
            payload["elevation_deg"] = float(self.elevation_deg)
        if self.snr_db is not None:
            _require_number("snr_db", self.snr_db)
            payload["snr_db"] = float(self.snr_db)
        if self.rcs_dbsm is not None:
            _require_number("rcs_dbsm", self.rcs_dbsm)
            payload["rcs_dbsm"] = float(self.rcs_dbsm)
        if self.classification is not None:
            payload["classification"] = self.classification.to_payload()
        return payload


@dataclass(frozen=True)
class RadarDetectionFrame:
    frame_id: str
    detections: tuple[RadarDetection, ...]

    def to_payload(self) -> dict[str, Any]:
        _require_text("frame_id", self.frame_id)
        return {
            "frame_id": self.frame_id.strip(),
            "detections": [detection.to_payload() for detection in self.detections],
        }


@dataclass(frozen=True)
class RadarLocalTrack:
    sensor_track_id: str
    range_m: float
    radial_velocity_mps: float
    azimuth_deg: float
    elevation_deg: float | None = None
    age_ms: float | None = None
    measurement_count: int | None = None
    track_quality: float | None = None
    uncertainty: Mapping[str, float] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        _require_text("sensor_track_id", self.sensor_track_id)
        _require_nonnegative("range_m", self.range_m)
        _require_number("radial_velocity_mps", self.radial_velocity_mps)
        _require_angle("azimuth_deg", self.azimuth_deg, -180.0, 180.0)
        if self.elevation_deg is not None:
            _require_angle("elevation_deg", self.elevation_deg, -90.0, 90.0)
        if self.age_ms is not None:
            _require_nonnegative("age_ms", self.age_ms)
        if self.measurement_count is not None:
            if isinstance(self.measurement_count, bool) or not isinstance(self.measurement_count, int) or self.measurement_count < 0:
                raise ValueError("measurement_count must be a non-negative integer")
        if self.track_quality is not None:
            _require_probability("track_quality", self.track_quality)
        for key, value in self.uncertainty.items():
            _require_text("uncertainty key", key)
            _require_nonnegative(f"uncertainty.{key}", value)

        payload: dict[str, Any] = {
            "sensor_track_id": self.sensor_track_id.strip(),
            "range_m": float(self.range_m),
            "radial_velocity_mps": float(self.radial_velocity_mps),
            "azimuth_deg": float(self.azimuth_deg),
            "uncertainty": {key: float(value) for key, value in self.uncertainty.items()},
        }
        if self.elevation_deg is not None:
            payload["elevation_deg"] = float(self.elevation_deg)
        if self.age_ms is not None:
            payload["age_ms"] = float(self.age_ms)
        if self.measurement_count is not None:
            payload["measurement_count"] = self.measurement_count
        if self.track_quality is not None:
            payload["track_quality"] = float(self.track_quality)
        return payload


def _require_text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _require_number(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")


def _require_nonnegative(name: str, value: object) -> None:
    _require_number(name, value)
    if float(value) < 0:
        raise ValueError(f"{name} cannot be negative")


def _require_probability(name: str, value: object) -> None:
    _require_number(name, value)
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


def _require_angle(name: str, value: object, low: float, high: float) -> None:
    _require_number(name, value)
    if not low <= float(value) <= high:
        raise ValueError(f"{name} must be between {low} and {high}")
