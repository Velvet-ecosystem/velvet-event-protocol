# Decoded CAN Observation Contract

`DECODED_CAN_SIGNAL_OBSERVED` carries one interpreted vehicle telemetry value from a trusted local producer such as Velvet Runtime.

It is information, not permission.

Required payload fields:

```text
signal_name
value
confidence
observed_at
source_profile
status: observation-only
read_only: true
actuation_granted: false
actuation_performed: false
```

Optional payload field:

```text
unit
```

Forbidden payload concepts include:

```text
executor or executor_name
route_id
capability or token
target or hardware_target
command or shell
action, actuate, or actuation
```

The event may be displayed, logged, correlated, or used as input to later reasoning. It may not directly select an executor, authorize control, or touch vehicle hardware.

A consumer must treat confidence as evidence quality, not authority level. Low-confidence values should remain visibly provisional and may be filtered by the producing Runtime route.

Canonical flow:

```text
listen-only CAN frame
  -> approved local vehicle profile
  -> conservative decoder
  -> Runtime read-only executor
  -> DECODED_CAN_SIGNAL_OBSERVED
  -> receipt-aware event delivery
  -> UI, logs, or bounded reasoning
```

Any transition from this event into a physical action must start a new strict intent and pass through identity, Court authorization, capability-token checks, a matching safety gate, an approved executor, and receipts.
