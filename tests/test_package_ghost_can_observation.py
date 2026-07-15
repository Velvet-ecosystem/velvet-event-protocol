# SPDX-License-Identifier: GPL-3.0-only

import unittest

from velvet_event_protocol import (
    GHOST_CAN_OBSERVATION_EVENT,
    GhostCanObservation,
    build_ghost_can_observation_event,
    validate_ghost_can_observation_event,
)


class PackageGhostCanObservationTests(unittest.TestCase):
    def test_package_exports_ghost_helpers(self):
        event = build_ghost_can_observation_event(
            source="velvet-runtime",
            observation=GhostCanObservation(
                can_id="0x130",
                data_hex="9001000000000000",
                signals={"engine_rpm": 400, "o2_fault": True},
            ),
        )
        self.assertEqual(event.event_type, GHOST_CAN_OBSERVATION_EVENT)
        validate_ghost_can_observation_event(event)


if __name__ == "__main__":
    unittest.main()
