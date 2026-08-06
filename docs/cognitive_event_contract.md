# Cognitive Event Transport Contract

Status: Gate 1 schema contract  
Contract: `velvet.cognitive-events.v1`  
Schema version: `1.0`

## Purpose

The Cognitive Event family carries Velvet's temporary interpretation of an unfolding situation across trusted local components.

It can transport:

- current-event snapshots
- boundary proposals
- predictions and prediction outcomes
- prediction errors
- interruption candidates and accepted interruptions
- proposal context
- authorized-action tracking references
- evidence-linked episode proposals
- bounded internal-modulator snapshots
- cognitive connection and component health

These messages are not Court decisions, capabilities, execution contracts, executor handles, commands, receipts, or identity proof.

> The layer connects moments. It does not command the body.

## Contract Flags

Every cognitive payload must declare:

```yaml
schema_version: "1.0"
interpretation_only: true
transport_only: true
canonical_evidence: false
authority: none
grants_authority: false
grants_execution: false
grants_actuation: false
replay_safe: true
replay_state: live | fixture | replay
```

A message that changes any of these flags is invalid.

## Common Fields

Every cognitive payload carries:

```yaml
cognitive_event_id: string
node_id: string
body_id: string
source_refs: [string]
correlation_ids: [string]
monotonic_time: number | omitted
replay_state: live | fixture | replay
health_state: healthy | degraded | failed | unknown
degraded_reasons: [string]
```

`source_refs` must not be empty. Cognitive interpretation must remain traceable to observations, Runtime decisions, execution lifecycle records, receipts, or other named inputs.

## Event Types

### Current event

- `cognitive.event.opened`
- `cognitive.event.updated`
- `cognitive.event.boundary_proposed`
- `cognitive.event.closed`

Modes are:

```text
OBSERVE
PROPOSE_ACTION
TRACK_ACTION
```

A mode is cognitive posture, not authorization.

Terminal states are:

```text
COMPLETED
INTERRUPTED
STALE
CONTRADICTED
ABANDONED
UNKNOWN_OUTCOME
DEGRADED_COMPLETION
```

Only `cognitive.event.closed` may carry a terminal lifecycle state, and it must name a completion reason.

### Prediction

- `cognitive.prediction.created`
- `cognitive.prediction.resolved`
- `cognitive.prediction.error`

A prediction must name a subject, expected state, deadline, confidence, and producing model/version. It begins as `pending` and must later resolve as `confirmed`, `contradicted`, `expired`, or `unknown`.

Prediction error is evidence. It must not request an automatic retry.

### Interruption

- `cognitive.interrupt.candidate`
- `cognitive.interrupt.accepted`

An accepted interrupt must meet its declared threshold and identify the event it interrupted. The cognitive message may request attention or a normal authority-path proposal, but it cannot authorize or claim that safeing occurred.

### Proposal and action tracking

- `cognitive.proposal.context`
- `cognitive.action.tracking_started`
- `cognitive.action.tracking_finished`

Proposal context remains proposal-only.

Action tracking may start only after references to an external Court authorization and external execution lifecycle record are available. Those references do not become authority inside the cognitive layer.

### Memory navigation

- `cognitive.episode.proposed`

An episode is a navigational interpretation over source events and receipts. It is not canonical evidence and cannot replace or rewrite a receipt.

### Internal and connection state

- `cognitive.modulators.snapshotted`
- `cognitive.connection.health_changed`
- `cognitive.health.changed`

Initial bounded modulators are:

```text
arousal
novelty
uncertainty
urgency
social_engagement
resource_pressure
prediction_stability
```

Each value is between `0.0` and `1.0`. `trust_context` is a named policy state, not a numeric modulator. Modulator snapshots explicitly declare that they cannot change authority.

Connection-health messages expose source, destination, signal type, latency limits, stale limits, observed latency, expected rate, fallback path, health, and degradation. A healthy endpoint must not hide a degraded nerve.

## Forbidden Authority Fields

Cognitive payloads are recursively checked for authority-bearing keys, including:

- capability or Court tokens
- executor names or handles
- commands or shell requests
- hardware targets or handles
- authorization claims
- policy or safety overrides
- retry authorization
- actuation claims

References such as `authorization_ref`, `execution_ref`, and `receipt_refs` are allowed because they point to externally owned records. They do not reproduce or grant the referenced authority.

## Replay Boundary

The deterministic fixture at:

```text
tests/fixtures/cognitive_vehicle_entry_v1.json
```

covers:

```text
presence observation
  -> current event opened
  -> local authentication reference
  -> bounded unlock proposal context
  -> explicit unlock prediction
  -> external Court and execution references
  -> action tracking
  -> observed unlock outcome
  -> prediction resolution
  -> event closure
  -> episode proposal
```

Every event in the fixture is marked `replay_state: fixture`, `replay_safe: true`, and grants no authority, execution, or actuation. Replaying it must never touch hardware.

## Repository Boundary

This repository owns the transport schema and validation rules.

It does not own:

- event association or segmentation logic
- prediction models
- interruption policy
- Court authorization
- capabilities or execution contracts
- executors
- receipt truth
- Riven identity lineage
- interface presentation

Those responsibilities remain with their existing repositories.

## Promotion Gate

Gate 1 passes when:

1. all cognitive event types validate deterministically
2. nested authority-bearing fields are rejected
3. replay state is explicit
4. fixed replay events validate without physical authority
5. action tracking requires external authorization and execution references
6. episode proposals remain subordinate to source events and receipts
7. modulators cannot alter authority
8. package and source-tree imports expose the same contract

Passing Gate 1 permits work on the read-only current-event workspace. It does not permit physical execution or learning.
