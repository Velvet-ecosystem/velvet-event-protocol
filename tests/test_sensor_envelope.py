# SPDX-License-Identifier: GPL-3.0-only

import unittest

from sensor_envelope import (
    SENSOR_OBSERVATION_REPORTED,
    SensorEnvelope,
    build_sensor_observation_event,
)


class TestSensorEnvelope(unittest.TestCase):
    def _example(self, **overrides):
        values = {
            "sensor_id": "radar_front_center",
            "sensor_family": "radar",
            "payload_type": "radar_detection_frame",
            "sensor_payload": {"detection_count": 1},
            "measured_at": 10.0,
            "received_at": 10.01,
            "health_state": "healthy",
            "quality_state": "valid",
            "message_confidence": 0.95,
            "commissioning": {
                "security": "authorize",
                "road_world_model": "trust",
                "physical_control": "observe",
            },
            "provenance": {
                "driver": "velvet-radar-adapter",
                "driver_version": "0.1.0",
            },
            "sequence": 42,
            "monotonic_ns": 123456789,
            "time_sync_state": "synchronized",
            "estimated_sync_error_us": 150.0,
            "mount_id": "tibby_front_center_v1",
            "calibration_id": "cal-rfc-0024",
        }
        values.update(overrides)
        return SensorEnvelope(**values)

    def test_builds_common_read_only_sensor_event(self):
        event = build_sensor_observation_event(
            source="velvet-sensor-fabric",
            envelope=self._example(),
        )

        self.assertEqual(event.event_type, SENSOR_OBSERVATION_REPORTED)
        self.assertEqual(event.metadata["contract"], "velvet.sensor-envelope.v0.1")
        self.assertEqual(event.metadata["authority"], "none")
        self.assertEqual(event.payload["status"], "observation-only")
        self.assertTrue(event.payload["read_only"])
        self.assertEqual(event.payload["sensor"]["id"], "radar_front_center")
        self.assertEqual(event.payload["sensor_payload"]["type"], "radar_detection_frame")

    def test_profiles_mature_independently(self):
        payload = self._example().to_payload()
        self.assertEqual(payload["commissioning"]["security"], "authorize")
        self.assertEqual(payload["commissioning"]["road_world_model"], "trust")
        self.assertEqual(payload["commissioning"]["physical_control"], "observe")

    def test_keeps_health_separate_from_quality(self):
        payload = self._example(
            health_state="healthy",
            quality_state="degraded",
            quality_reasons=("multipath_suspected",),
        ).to_payload()
        self.assertEqual(payload["health"]["state"], "healthy")
        self.assertEqual(payload["quality"]["state"], "degraded")
        self.assertEqual(payload["quality"]["reasons"], ["multipath_suspected"])

    def test_rejects_invalid_message_confidence(self):
        with self.assertRaisesRegex(ValueError, "message_confidence"):
            self._example(message_confidence=1.1).to_payload()

    def test_rejects_unknown_commissioning_state(self):
        with self.assertRaisesRegex(ValueError, "commissioning"):
            self._example(commissioning={"security": "magic"}).to_payload()

    def test_rejects_negative_timestamp(self):
        with self.assertRaisesRegex(ValueError, "timestamps"):
            self._example(measured_at=-1.0).to_payload()


if __name__ == "__main__":
    unittest.main()
