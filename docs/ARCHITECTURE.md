# Velvet Event Protocol — Architecture

Event Protocol transports observations, proposals, decisions and outcome evidence.
It does not authorize consequential execution. The authoritative boundary is
Velvet Runtime Court → verified capability token → safety/replay/persistence gates
→ approved executor. See [Court authority boundary](court_authority_boundary.md).

## Components

- `velvet_event_protocol/event_schema.py`: event envelope with optional receipt
  linkage. Frozen fields do not make nested payload dictionaries immutable.
- `velvet_event_protocol/event_bus.py`: trusted internal subscriber transport;
  ordinary publishers use the enforcer rather than `_publish`.
- `velvet_event_protocol/enforcer.py`: generic publisher. Rejects `ACTUATION`
  unconditionally, before any subscriber/callback, including when a receipt ID or
  source allowlist is supplied. Observation and outcome events remain available.
- Root `event_enforcer.py`: legacy positional-constructor adapter to the same
  packaged gate; it contains no separate authorization policy.
- Root `runtime_wiring.py`: legacy assembly example using the packaged enforcer.
  Production Runtime owns its private wiring; modules receive only its publisher.
- `receipt_bridge.py`: observational receipt-ID lookup, not execution verification.
- `core_action.py`: `publish_receipted_event` refuses ACTUATION;
  `execute_authorized_action` is retired and raises rather than executing.

## Migration

A caller cannot enable ACTUATION by omitting a verifier, supplying an always-true
verifier, forging a receipt or calling from a trusted-looking source. Constructor
arguments for the earlier receipt/source checks remain accepted only to avoid
breaking observation-only call sites. They no longer grant publishing permission.

Consequential callers must submit strict intent to Runtime. Approved executors
invoke their handlers directly after Runtime verification and record outcomes.
`EXECUTION_COMPLETED` is evidence about an invocation, not permission for a
subscriber to invoke again. Historical ACTUATION records may be inspected as data;
they cannot be republished through this live generic boundary.

## Trust model

This is not an adversarial in-process Python sandbox. Trusted wiring owns the bus;
a malicious same-process plugin can use introspection/private imports. Privileged
device access must be isolated where protection from hostile plugins is required.
This change closes the supported generic APIs; it does not claim process isolation.
