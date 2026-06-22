# SPDX-License-Identifier: GPL-3.0-only

import unittest

from decoded_can_observation import (
    DECODED_CAN_SIGNAL_OBSERVED,
    DecodedCanSignalObservation,
    build_decoded_can_signal_event,
    validate_decoded_can_signal_event,
)


class TestDecodedCanObservation(unittest.TestCase):
    def test_builds_observation_only_event(self):
        event = build_decoded_can_signal_event(
            source="velvet-runtime",
            observation=DecodedCanSignalObservation(
                signal_name="wheel_speed",
                value=42.3,
                confidence=0.91,
                observed_at=1234.5,
                source_profile="profile-abc",
                unit="km/h",
            ),
        )

        self.assertEqual(event.event_type, DECODED_CAN_SIGNAL_OBSERVED)
        self.assertEqual(event.payload["status"], "observation-only")
        self.assertTrue(event.payload["read_only"])
        self.assertFalse(event.payload["actuation_granted"])
        self.assertFalse(event.payload["actuation_performed"])
        validate_decoded_can_signal_event(event)

    def test_rejects_authority_fields(self):
        event = build_decoded_can_signal_event(
            source="velvet-runtime",
            observation=DecodedCanSignalObservation(
                signal_name="gear",
                value=3,
                confidence=1.0,
                observed_at=1.0,
                source_profile="profile-abc",
            ),
        )
        event.payload["executor_name"] = "can-writer"

        with self.assertRaisesRegex(ValueError, "forbidden authority fields"):
            validate_decoded_can_signal_event(event)

    def test_rejects_false_read_only_claim(self):
        event = build_decoded_can_signal_event(
            source="velvet-runtime",
            observation=DecodedCanSignalObservation(
                signal_name="steering_angle",
                value=-5.0,
                confidence=0.8,
                observed_at=1.0,
                source_profile="profile-abc",
            ),
        )
        event.payload["read_only"] = False

        with self.assertRaisesRegex(ValueError, "read_only"):
            validate_decoded_can_signal_event(event)

    def test_rejects_invalid_confidence(self):
        with self.assertRaisesRegex(ValueError, "confidence"):
            DecodedCanSignalObservation(
                signal_name="wheel_speed",
                value=1,
                confidence=1.2,
                observed_at=1.0,
                source_profile="profile-abc",
            ).to_payload()

    def test_rejects_non_scalar_value(self):
        with self.assertRaisesRegex(ValueError, "scalar"):
            DecodedCanSignalObservation(
                signal_name="wheel_speed",
                value={"speed": 1},
                confidence=0.9,
                observed_at=1.0,
                source_profile="profile-abc",
            ).to_payload()


if __name__ == "__main__":
    unittest.main()
