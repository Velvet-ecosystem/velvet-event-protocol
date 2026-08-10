import unittest

from velvet_event_protocol.audio_output_evidence import (
    AUDIO_OUTPUT_BOOKED,
    AUDIO_OUTPUT_COMPLETED,
    AUDIO_OUTPUT_FAILED,
    AUDIO_OUTPUT_PREEMPTED,
    AUDIO_OUTPUT_RECOVERED,
    AUDIO_OUTPUT_STARTED,
    AudioOutputEvidenceRecord,
    build_audio_output_event,
    validate_audio_output_event,
)


class AudioOutputEvidenceTests(unittest.TestCase):
    def _record(self, **changes):
        values = {
            "output_event_id": "audio-out-1",
            "request_id": "request-1",
            "node_id": "velvet-audio-pi3-01",
            "priority": 70,
            "output_channels": (4,),
            "expression_id": "response-42",
            "profile_id": "owner_default",
            "model_id": "velvet",
            "data": {},
        }
        values.update(changes)
        return AudioOutputEvidenceRecord(**values)

    def test_booked_event_is_evidence_only(self):
        event = build_audio_output_event(
            source="velvet-audio-studio",
            event_type=AUDIO_OUTPUT_BOOKED,
            record=self._record(),
        )
        self.assertEqual(event.payload["authority"], "none")
        self.assertTrue(event.payload["evidence_only"])
        self.assertFalse(event.payload["grants_authority"])
        self.assertFalse(event.payload["grants_execution"])
        self.assertFalse(event.payload["grants_actuation"])
        validate_audio_output_event(event)

    def test_started_and_completed_require_bounded_playback_evidence(self):
        started = build_audio_output_event(
            source="velvet-audio-studio",
            event_type=AUDIO_OUTPUT_STARTED,
            record=self._record(data={
                "source_sample_rate_hz": 22050,
                "playback_sample_rate_hz": 48000,
                "source_frames": 4410,
            }),
        )
        validate_audio_output_event(started)

        completed = build_audio_output_event(
            source="velvet-audio-studio",
            event_type=AUDIO_OUTPUT_COMPLETED,
            record=self._record(data={
                "playback_sample_rate_hz": 48000,
                "frames_written": 9600,
                "playback_duration_ms": 200.0,
            }),
        )
        validate_audio_output_event(completed)

    def test_preemption_names_the_higher_priority_request(self):
        event = build_audio_output_event(
            source="velvet-audio-studio",
            event_type=AUDIO_OUTPUT_PREEMPTED,
            record=self._record(data={
                "playback_sample_rate_hz": 48000,
                "frames_written": 480,
                "playback_duration_ms": 10.0,
                "preempted_by_request_id": "safety-request",
            }),
        )
        self.assertEqual(event.payload["preempted_by_request_id"], "safety-request")

    def test_failure_and_recovery_are_explicit(self):
        failed = build_audio_output_event(
            source="velvet-audio-studio",
            event_type=AUDIO_OUTPUT_FAILED,
            record=self._record(
                output_channels=(),
                data={
                    "failure_stage": "synthesis",
                    "error_class": "SpeechSynthesisError",
                    "reason": "local voice unavailable",
                    "recovery_required": True,
                },
            ),
        )
        validate_audio_output_event(failed)

        recovered = build_audio_output_event(
            source="velvet-audio-studio",
            event_type=AUDIO_OUTPUT_RECOVERED,
            record=self._record(data={
                "recovered_from_event_id": failed.payload["output_event_id"],
                "recovered_from_stage": "synthesis",
            }),
        )
        validate_audio_output_event(recovered)

    def test_rejects_spoken_text_raw_audio_and_authority(self):
        for field, value in (
            ("text", "secret speech"),
            ("pcm_bytes", "00ff"),
            ("capability_token", "nope"),
            ("authorized_by", "Court"),
        ):
            record = self._record(data={field: value})
            with self.assertRaisesRegex(ValueError, "forbidden"):
                record.to_payload(AUDIO_OUTPUT_BOOKED)

    def test_plain_transport_envelope_without_metadata_is_supported(self):
        payload = self._record().to_payload(AUDIO_OUTPUT_BOOKED)
        validate_audio_output_event({
            "event_type": AUDIO_OUTPUT_BOOKED,
            "source_id": "octo.playback.primary",
            "sequence": 1,
            "occurred_at_monotonic_ns": 10,
            "payload": payload,
        })


if __name__ == "__main__":
    unittest.main()
