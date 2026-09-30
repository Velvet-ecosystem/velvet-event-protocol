# SPDX-License-Identifier: GPL-3.0-only

import unittest

from radar_observation import (
    RADAR_DETECTION_FRAME,
    RADAR_LOCAL_TRACK,
    RadarClassification,
    RadarDetection,
    RadarDetectionFrame,
    RadarLocalTrack,
)
from sensor_capabilities import SensorCapabilities, build_sensor_capabilities_event
from sensor_disagreement import SensorDisagreement, build_sensor_disagreement_event
from sensor_lifecycle import SensorLifecycleEvent, build_sensor_lifecycle_event


class TestRadarObservation(unittest.TestCase):
    def test_detection_frame_preserves_measurement_uncertainty(self):
        frame = RadarDetectionFrame(
            frame_id="184291",
            detections=(
                RadarDetection(
                    detection_id="31",
                    range_m=42.71,
                    radial_velocity_mps=-11.34,
                    azimuth_deg=-3.8,
                    elevation_deg=0.6,
                    snr_db=18.2,
                    rcs_dbsm=7.1,
                    uncertainty={"range_m": 0.09, "radial_velocity_mps": 0.14, "azimuth_deg": 0.7},
                    quality_flags=("valid",),
                    classification=RadarClassification("vehicle", 0.73),
                ),
            ),
        )
        payload = frame.to_payload()
        self.assertEqual(payload["detections"][0]["range_m"], 42.71)
        self.assertEqual(payload["detections"][0]["classification"]["source"], "sensor_local_model")
        self.assertEqual(RADAR_DETECTION_FRAME, "radar_detection_frame")

    def test_rejects_negative_range(self):
        with self.assertRaisesRegex(ValueError, "range_m"):
            RadarDetection("bad", -1.0, 0.0, 0.0).to_payload()

    def test_local_track_remains_sensor_local(self):
        track = RadarLocalTrack(
            sensor_track_id="17",
            range_m=38.4,
            radial_velocity_mps=-4.6,
            azimuth_deg=2.7,
            age_ms=830,
            measurement_count=19,
            track_quality=0.91,
        )
        payload = track.to_payload()
        self.assertEqual(payload["sensor_track_id"], "17")
        self.assertNotIn("world_track_id", payload)
        self.assertEqual(RADAR_LOCAL_TRACK, "radar_local_track")


class TestSensorLifecycle(unittest.TestCase):
    def test_lifecycle_is_evidence_only(self):
        event = build_sensor_lifecycle_event(
            source="velvet-sensor-adapter",
            lifecycle=SensorLifecycleEvent(
                sensor_id="radar_front_center",
                sensor_family="radar",
                state="blocked",
                occurred_at=1234.5,
                reasons=("possible_surface_contamination",),
            ),
        )
        self.assertEqual(event.metadata["authority"], "none")
        self.assertTrue(event.payload["read_only"])
        self.assertEqual(event.payload["state"], "blocked")

    def test_rejects_unknown_lifecycle_state(self):
        with self.assertRaisesRegex(ValueError, "lifecycle"):
            SensorLifecycleEvent("r", "radar", "command_brakes", 1.0).to_payload()


class TestSensorDisagreement(unittest.TestCase):
    def test_disagreement_does_not_assign_fault(self):
        event = build_sensor_disagreement_event(
            source="sensor-fusion",
            disagreement=SensorDisagreement(
                sources=("camera_front", "radar_front_center"),
                property_name="longitudinal_range_m",
                observations={"camera_front": 31.8, "radar_front_center": 50.9},
                observed_at=10.0,
                severity="high",
                difference=19.1,
                association_id="track-candidate-42",
            ),
        )
        self.assertIsNone(event.payload["fault_assignment"])
        self.assertEqual(event.metadata["authority"], "none")

    def test_requires_matching_sources_and_observations(self):
        with self.assertRaisesRegex(ValueError, "exactly"):
            SensorDisagreement(
                sources=("a", "b"),
                property_name="range",
                observations={"a": 1.0},
                observed_at=1.0,
            ).to_payload()


class TestSensorCapabilities(unittest.TestCase):
    def test_capabilities_are_vendor_neutral(self):
        event = build_sensor_capabilities_event(
            source="velvet-radar-adapter",
            capabilities=SensorCapabilities(
                sensor_id="radar_front_center",
                sensor_family="radar",
                measurements=("range", "radial_velocity", "azimuth"),
                outputs=("detections", "local_tracks", "health"),
                diagnostics={"raw_capture": True, "self_test": True},
                timing={"hardware_timestamp": True, "external_sync": False},
            ),
        )
        self.assertIn("radial_velocity", event.payload["measurements"])
        self.assertEqual(event.metadata["authority"], "none")
        self.assertTrue(event.payload["read_only"])

    def test_rejects_duplicate_capabilities(self):
        with self.assertRaisesRegex(ValueError, "duplicates"):
            SensorCapabilities("r", "radar", ("range", "range"), ()).to_payload()


if __name__ == "__main__":
    unittest.main()
