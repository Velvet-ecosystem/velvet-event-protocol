# SPDX-License-Identifier: GPL-3.0-only

import unittest

import radar_observation as radar_shim
import sensor_capabilities as capabilities_shim
import sensor_disagreement as disagreement_shim
import sensor_envelope as envelope_shim
import sensor_lifecycle as lifecycle_shim
from velvet_event_protocol import (
    RADAR_DETECTION_FRAME,
    RADAR_LOCAL_TRACK,
    SENSOR_CAPABILITIES_CONTRACT,
    SENSOR_CAPABILITIES_REPORTED,
    SENSOR_DISAGREEMENT_CONTRACT,
    SENSOR_DISAGREEMENT_REPORTED,
    SENSOR_ENVELOPE_CONTRACT,
    SENSOR_LIFECYCLE_CONTRACT,
    SENSOR_LIFECYCLE_REPORTED,
    SENSOR_OBSERVATION_REPORTED,
    RadarDetection,
    RadarDetectionFrame,
    RadarLocalTrack,
    SensorCapabilities,
    SensorDisagreement,
    SensorEnvelope,
    SensorLifecycleEvent,
    build_sensor_capabilities_event,
    build_sensor_disagreement_event,
    build_sensor_lifecycle_event,
    build_sensor_observation_event,
)


class SensorPackageSurfaceTests(unittest.TestCase):
    def test_public_package_exports_sensor_contracts(self):
        envelope = SensorEnvelope(
            sensor_id="radar.front",
            sensor_family="radar",
            payload_type=RADAR_DETECTION_FRAME,
            sensor_payload=RadarDetectionFrame(
                frame_id="frame-1",
                detections=(
                    RadarDetection(
                        detection_id="d-1",
                        range_m=12.5,
                        radial_velocity_mps=-1.25,
                        azimuth_deg=3.0,
                    ),
                ),
            ).to_payload(),
            measured_at=10.0,
            received_at=10.01,
            health_state="healthy",
            quality_state="valid",
            message_confidence=0.95,
            commissioning={"road_world_model": "observe"},
            provenance={"adapter": "test"},
        )
        event = build_sensor_observation_event(source="test", envelope=envelope)

        self.assertEqual(event.event_type, SENSOR_OBSERVATION_REPORTED)
        self.assertEqual(event.metadata["contract"], SENSOR_ENVELOPE_CONTRACT)
        self.assertEqual(event.metadata["authority"], "none")

    def test_public_builders_keep_existing_contract_ids(self):
        capability_event = build_sensor_capabilities_event(
            source="test",
            capabilities=SensorCapabilities(
                sensor_id="radar.front",
                sensor_family="radar",
                measurements=("range",),
                outputs=(RADAR_LOCAL_TRACK,),
            ),
        )
        lifecycle_event = build_sensor_lifecycle_event(
            source="test",
            lifecycle=SensorLifecycleEvent(
                sensor_id="radar.front",
                sensor_family="radar",
                state="ready",
                occurred_at=11.0,
            ),
        )
        disagreement_event = build_sensor_disagreement_event(
            source="test",
            disagreement=SensorDisagreement(
                sources=("radar.front", "camera.front"),
                property_name="range_m",
                observations={"radar.front": 12.5, "camera.front": 13.0},
                observed_at=12.0,
            ),
        )

        self.assertEqual(capability_event.event_type, SENSOR_CAPABILITIES_REPORTED)
        self.assertEqual(capability_event.metadata["contract"], SENSOR_CAPABILITIES_CONTRACT)
        self.assertEqual(lifecycle_event.event_type, SENSOR_LIFECYCLE_REPORTED)
        self.assertEqual(lifecycle_event.metadata["contract"], SENSOR_LIFECYCLE_CONTRACT)
        self.assertEqual(disagreement_event.event_type, SENSOR_DISAGREEMENT_REPORTED)
        self.assertEqual(disagreement_event.metadata["contract"], SENSOR_DISAGREEMENT_CONTRACT)

    def test_root_modules_are_compatibility_reexports(self):
        self.assertIs(envelope_shim.SensorEnvelope, SensorEnvelope)
        self.assertIs(radar_shim.RadarDetection, RadarDetection)
        self.assertIs(radar_shim.RadarLocalTrack, RadarLocalTrack)
        self.assertIs(capabilities_shim.SensorCapabilities, SensorCapabilities)
        self.assertIs(lifecycle_shim.SensorLifecycleEvent, SensorLifecycleEvent)
        self.assertIs(disagreement_shim.SensorDisagreement, SensorDisagreement)


if __name__ == "__main__":
    unittest.main()
