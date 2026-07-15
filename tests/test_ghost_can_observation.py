# SPDX-License-Identifier: GPL-3.0-only

import unittest

from ghost_can_observation import (
    GHOST_CAN_OBSERVATION_EVENT,
    GhostCanObservation,
    build_ghost_can_observation_event,
    validate_ghost_can_observation_event,
)


class TestGhostCanObservation(unittest.TestCase):
    def test_builds_public_safe_ghost_event(self):
        event = build_ghost_can_observation_event(
            source="velvet-runtime",
            observation=GhostCanObservation(
                can_id="0x120",
                data_hex="0000000000000000",
                signals={"vehicle_speed_kph": 0, "ignition_state": "off"},
                timestamp=1.0,
            ),
        )

        self.assertEqual(event.event_type, GHOST_CAN_OBSERVATION_EVENT)
        self.assertEqual(event.payload["route_id"], "can-ghost")
        self.assertEqual(event.payload["target"], "vehicle-can-ghost")
        self.assertTrue(event.payload["read_only"])
        self.assertTrue(event.payload["synthetic_fixture"])
        self.assertFalse(event.payload["physical_bus_opened"])
        self.assertFalse(event.payload["can_transmission_attempted"])
        self.assertFalse(event.payload["actuation_performed"])
        self.assertFalse(event.payload["authority_granted"])
        validate_ghost_can_observation_event(event)

    def test_rejects_authority_fields(self):
        event = build_ghost_can_observation_event(
            source="velvet-runtime",
            observation=GhostCanObservation(can_id=0x120, data_hex="00"),
        )
        event.payload["executor_name"] = "can-writer"

        with self.assertRaisesRegex(ValueError, "forbidden authority fields"):
            validate_ghost_can_observation_event(event)

    def test_rejects_bus_opened_claim(self):
        event = build_ghost_can_observation_event(
            source="velvet-runtime",
            observation=GhostCanObservation(can_id=0x120, data_hex="00"),
        )
        event.payload["physical_bus_opened"] = True

        with self.assertRaisesRegex(ValueError, "physical_bus_opened"):
            validate_ghost_can_observation_event(event)

    def test_rejects_bad_dlc(self):
        event = build_ghost_can_observation_event(
            source="velvet-runtime",
            observation=GhostCanObservation(can_id=0x120, data_hex="0000"),
        )
        event.payload["dlc"] = 8

        with self.assertRaisesRegex(ValueError, "dlc"):
            validate_ghost_can_observation_event(event)

    def test_rejects_bad_signal_value(self):
        event = build_ghost_can_observation_event(
            source="velvet-runtime",
            observation=GhostCanObservation(can_id=0x120, data_hex="00"),
        )
        event.payload["signals"] = {"nested": {"not": "scalar"}}

        with self.assertRaisesRegex(ValueError, "scalar"):
            validate_ghost_can_observation_event(event)


if __name__ == "__main__":
    unittest.main()
