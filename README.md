# Velvet Event Protocol

**Structured event transport and receipt-aware delivery for the Velvet ecosystem.**

**Depends on:** `velvet-receipts >= v1.0.0`

Velvet Event Protocol carries observations, lifecycle changes, requests, decisions, and execution results between trusted local components.

It does not grant authority and it does not execute hardware.

> Events describe. Court authorizes. Safety gates approve conditions. Executors act. Receipts remember.

## Core Doctrine

- Events are structured meaning, not permission.
- A receipt proves that a decision or result was recorded. It does not create authority.
- Physical and write-capable actions must pass through Velvet Runtime.
- Direct event-bus access remains prohibited outside trusted runtime wiring.
- No event helper may create an alternate actuation path around Court.

## Authoritative Execution Path

```text
input
  -> verified identity context
  -> strict intent
  -> capability context
  -> Court authorization
  -> signed capability token
  -> matching safety gate
  -> approved executor
  -> execution receipts
  -> result and observation events
```

The event protocol participates before and after execution:

- before execution, it may carry observations or route requests
- after execution, it may distribute Court decisions, denials, execution outcomes, and state changes

It never substitutes for Court, safety, replay protection, or the approved executor.

## Event Delivery Path

```text
producer
  -> hardened publish interface
  -> receipt validation where required
  -> EventEnforcer
  -> EventBus
  -> registered handlers
```

The enforcer validates event shape, source restrictions, and receipt requirements. Those checks are transport enforcement, not action authorization.

## Receipted Events

Use `publish_receipted_event()` for observations and lifecycle events that require a receipt:

```python
from core_action import publish_receipted_event

publish_receipted_event(
    enforcer_publish=runtime_publish,
    receipt_logger=logger,
    event_type="EXECUTION_COMPLETED",
    source="velvet-runtime",
    policy="RuntimeExecutionContract",
    authorized_by="ApprovedExecutor",
    domain="execution",
    payload={"executor_name": "runtime-status"},
)
```

`publish_receipted_event()` refuses `ACTUATION` events.

The former `execute_authorized_action()` helper is retired and fails closed. Receipt creation by itself is not enough to authorize an action.

## Intent Event Contract

Scenes, modules, CAN observers, and runtime services may emit structured intent or observation events. Such events may include a public route ID and bounded parameters, but they must not carry direct executor authority.

Events must not be treated as permission to:

- select an executor
- choose raw capabilities or hardware targets
- invoke shell commands
- import arbitrary modules
- touch relays, CAN writers, actuators, or other hardware

See:

- [Intent Event Contract](docs/intent_event_contract.md)
- [Court Authority Boundary](docs/court_authority_boundary.md)
- [Decoded CAN Observation Contract](docs/decoded_can_observation_contract.md)
- [Ghost CAN Observation Contract](docs/ghost_can_observation_contract.md)

## Decoded CAN Observations

`DECODED_CAN_SIGNAL_OBSERVED` carries one confidence-scored, interpreted vehicle telemetry value from a trusted local producer.

It is always observation-only. The contract forbids executor names, routes, capabilities, hardware targets, commands, tokens, and actuation claims inside the payload.

Use the helpers in `decoded_can_observation.py` to build and validate these events.

## Ghost CAN Observations

`vehicle.can.ghost_observation` carries synthetic/read-only CAN telemetry for the public jarred-car demo loop.

Use the helpers in `ghost_can_observation.py` or `velvet_event_protocol.ghost_can_observation` to build and validate the event before passing it between `velvet-vehicle-can`, `velvet-runtime`, `velvet-receipts`, and future UI surfaces.

A valid ghost CAN event must declare that it is read-only, fixture-backed, has not opened a physical bus, has not attempted or performed CAN transmission, has not performed actuation, and has not granted authority.

## Event Types

Event types are case-sensitive.

```text
ACTUATION   valid event type, but only approved Runtime executors may originate it
actuation   different string and not equivalent
```

Use constants from `event_types.py` rather than handwritten event names where available.

## Critical Boundary

Modules must never:

- access `EventBus` directly
- call `_publish`
- bypass runtime wiring
- treat a valid receipt ID as authority
- create ACTUATION events outside the approved Runtime executor path

All publishing must pass through the hardened publish interface supplied by Runtime.

## What This Repository Owns

- event schemas
- event delivery
- source and receipt enforcement
- observation and lifecycle event contracts
- request and result transport

## What This Repository Does Not Own

- identity verification
- continuity verification
- capability policy
- Court authorization
- capability-token signing
- safety-gate selection
- executor registration
- replay protection
- hardware execution

Those responsibilities belong to `velvet-runtime` and their supporting ecosystem contracts.

## Security Warning

A receipt is evidence, not permission.

A bus event is information, not authority.

Any code path that turns either directly into hardware action is a doctrine violation.

## Version

`v1.6.2` public ghost CAN protocol phase.

## License

GPLv3. Part of the Velvet ecosystem.
