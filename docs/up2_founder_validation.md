# UP² Founder Event Protocol Validation

## Scope

This note records the role of `velvet-event-protocol` during Velvet's first verified Founder Runtime boot on physical UP Squared hardware.

It records package presence, compatibility, and architectural boundaries. It does not claim that the complete live cross-component event stream, cross-node delivery, or physical-event execution path has been validated.

## Verified visible posture

```text
Continuity        VERIFIED
Court             READY
Runtime           ACTIVE
Routes            READ-ONLY
Physical Control  DISABLED

Waiting for Mister
```

The Event Protocol package was installed in the same explicit Python 3.10.20 environment as the other public Velvet packages and was detected by Runtime during the verified boot path.

## What this validates

The physical UP² session validates that:

- the `velvet-event-protocol` distribution can be installed on the Founder platform
- Runtime can discover the installed package in the selected interpreter
- Event Protocol remains compatible with the verified read-only Runtime boot
- the ecosystem can preserve the distinction between observation, proposal, authorization, execution, receipt, continuity, and presentation
- no event was treated as authority merely because the package was present
- no CAN transmission, relay action, actuator command, or other physical control was enabled

## What this does not validate

This milestone does not yet prove:

- a complete live EventBus stream between all organs
- sustained event throughput or back-pressure behavior
- deterministic replay across a full physical session
- correction-event handling under real degraded conditions
- cross-node delivery to Luckfox nodes
- privacy-aware subscriptions and retention
- event-family compatibility across every supported repository version
- any physical executor triggered by an event

Package presence is not the same as a live nervous-system exercise.

## Authority boundary preserved

The validated boot preserved the core Event Laws:

```text
events communicate
Runtime verifies and coordinates
Court authorizes
executors act
Receipts preserve evidence
Riven preserves lineage
Interface presents state
```

A valid event shape remains transport acceptance, not action approval.

A valid receipt reference remains evidence, not authority.

Direct `EventBus` access remains prohibited outside trusted Runtime wiring.

## Installation lesson

Use one explicit interpreter for installation, diagnostics, snapshot generation, and launch.

```bash
PYTHON=/home/coyote/.pyenv/versions/3.10.20/bin/python3

$PYTHON -m pip install -e ~/velvet/velvet-event-protocol
$PYTHON -m pip list | grep velvet
```

A package installed under another interpreter may exist on disk while remaining invisible to Runtime.

## Snapshot lesson

The Founder Interface displayed a generated Runtime snapshot. After package, state, or environment changes, the snapshot must be regenerated in the same shell that has the intended Runtime environment loaded.

A stale snapshot can truthfully display old failure state even after the underlying package problem has been corrected.

## Fail-closed interpretation

The bring-up sequence reinforced a useful diagnostic law:

1. missing package is reported as missing package
2. installed package with absent state advances to the state failure
3. verified state advances to the next real gate
4. no presentation layer may promote package presence into a claim of active authority

The system should expose the next truthful blocker rather than flattening every failure into a generic error.

## Next validation milestones

1. Exercise a live local event stream during unattended Founder boot.
2. Capture deterministic observation, Court, execution-status, receipt, continuity, and Interface events in one bounded timeline.
3. Add cross-repository compatibility tests for Runtime, Receipts, Interface, AI Core, CAN, and Continuity.
4. Validate deterministic replay and correction events from preserved physical-session fixtures.
5. Define bounded cross-node delivery contracts for the Luckfox organs.
6. Test degraded transport, subscriber failure, and recovery without creating hidden authority lanes.

## Security conclusion

The first verified Founder boot confirms that the nervous-system package can participate in the physical body without becoming its sovereign controller.

The rule remains simple:

> An event is information, not authority.
