# Public Ghost Event Protocol Patch Notes

This patch adds the canonical public event contract for the jarred-car CAN demo.

## Added

- `ghost_can_observation.py`
- `velvet_event_protocol/ghost_can_observation.py`
- `tests/test_ghost_can_observation.py`
- `tests/test_package_ghost_can_observation.py`
- `examples/ghost_can_observation.py`
- `docs/ghost_can_observation_contract.md`

## Event type

```text
vehicle.can.ghost_observation
```

## Purpose

The event carries synthetic/read-only CAN observations between the public ghost-system repos:

```text
velvet-vehicle-can -> velvet-runtime -> velvet-receipts -> velvet-interface
```

## Safety boundary

The validator requires explicit flags proving:

- read-only observation
- committed/synthetic fixture source
- no physical CAN bus opened
- no CAN transmission attempted or performed
- no actuation granted or performed
- no vehicle authority granted

It rejects payload authority fields such as executor names, commands, capabilities, hardware targets, shell handles, and tokens.
