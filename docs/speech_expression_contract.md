# Speech Expression Event Contract

`language.expression.speech_requested` carries already-approved human-facing wording from Velvet Language toward an audio organ through the shared Event Protocol.

It is an expression request, not authority and not a hardware command.

## Path

```text
verified meaning
  -> Velvet Language
  -> RenderedExpression
  -> language.expression.speech_requested
  -> Runtime/Event Protocol routing
  -> Velvet Audio Studio
  -> bounded delivery profile
  -> local TTS
  -> Studio lease and mixer/playback
  -> accepted sound device
```

## Language-owned fields

The event may carry:

- expression identifier
- approved text
- severity
- audience
- requested named delivery profile
- driving-load context
- quiet/social presentation hints
- whether the expression is intended to interrupt presentation
- generator and language policy version

The event always declares:

- `speech_approved: true`
- `command_authority: false`
- `actuation_authority: false`
- `hardware_selected: false`
- `synthesis_selected: false`

## Forbidden fields

Language must not use this event to choose:

- ALSA devices or binaries
- output channel numbers or speaker slots
- TTS speaker IDs or voice model paths
- gain, volume, pitch, rate, Piper controls, or other synthesis implementation details
- capabilities, tokens, executors, hardware targets, Court decisions, or authorization

Those choices belong to Audio Studio, Runtime, Court, or the owning hardware organ.

## Safety posture

Severity and presentation intent are information. Audio Studio independently maps them to its own minimum playback priority and preemption policy. A speech-expression event therefore cannot grant itself a safety capability or directly seize a speaker.

Critical and emergency language should remain deterministic upstream. Audio may additionally force bounded acoustic profiles for warning, critical, emergency, or high-driving-load delivery.

## Replay

Replaying this event remains an expression request only. Replay must not be interpreted as renewed operational authorization. Physical playback policy may suppress, deduplicate, simulate, or route replayed speech according to Runtime and Audio Studio policy.
