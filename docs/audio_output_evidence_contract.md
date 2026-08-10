# Audio Output Evidence Contract

`velvet.audio-output-evidence.v1` carries evidence about local Audio Studio output activity. It records what the audio organ booked, started, completed, preempted, failed, and later recovered from. It never grants permission to speak, execute, actuate, or seize hardware.

## Event family

- `audio.output.booked`
- `audio.output.started`
- `audio.output.completed`
- `audio.output.preempted`
- `audio.output.failed`
- `audio.output.recovered`

Every payload declares that it is evidence-only, authority-free, non-executing, non-actuating, and audio-output-only.

## Privacy boundary

The contract intentionally excludes the spoken text and raw audio. Canonical output evidence may identify the expression/request, profile/model identifiers, priority, logical output channels, sample rates, frame counts, duration, preemption relationship, and bounded failure/recovery details.

It rejects:

- spoken text and transcripts
- raw or encoded PCM
- ALSA device paths
- voice model/config filesystem paths
- capability or Court/execution tokens
- executor or hardware handles
- authorization or actuation claims

This lets the body prove that speech was attempted or played without turning the evidence stream into a duplicate conversation archive.

## Lifecycle

A normal successful path is:

```text
audio.output.booked
  -> audio.output.started
  -> audio.output.completed
```

A lower-priority clip displaced by a higher-priority request ends with `audio.output.preempted` and names the request that displaced it.

A synthesis, booking, or playback failure emits `audio.output.failed` with a bounded error class/reason and `recovery_required: true`. The first later successful output after that failure may emit `audio.output.recovered` referencing the prior failure evidence.

## Ownership

Audio Studio owns the observations because it owns the local booking, synthesis delivery, and speaker path. Event Protocol owns only the transport contract. Velvet Receipts may normalize these events into canonical append-only evidence. Runtime/Court authority remains independent.

A valid event is evidence, not permission.
