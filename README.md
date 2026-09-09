# Velvet Event Protocol

**Velvet's versioned nervous system and trusted local message bus.**

Velvet Event Protocol carries structured observations, proposals, Court decisions, resource changes, execution outcomes, receipts, continuity updates, diagnostics, and degraded-state notifications between trusted local components.

It does not grant authority. It does not execute hardware. It does not remember by itself.

> A healthy nervous system carries information faithfully. It does not decide, command, or remember by itself. It exists so the body can remain one body.

## The Nervous System (Message Bus)

Engineering-wise, this repository defines a versioned, deterministic message bus.

Within Velvet's Unified-Organ architecture, it is the nervous system connecting one accountable body:

```text
sensors and observers
  -> structured events
  -> hardened publish boundary
  -> EventEnforcer
  -> EventBus
  -> permitted subscribers
  -> receipts and continuity where required
```

The organs do not shout across private wires. They communicate through shared contracts that can be validated, observed, replayed, and receipted.

**Modules connect to the nervous system. They do not wire directly into other organs.**

That rule keeps optional capabilities pluggable above the stable system without creating hidden dependencies or private authority lanes.

## Biological and Engineering Map

| Velvet body concept | Engineering component |
|---|---|
| Unified body | Velvet ecosystem |
| Brain and interpretation | `velvet-ai-core` |
| Constitution and authority | `velvet-runtime` and Court |
| Nervous system | `velvet-event-protocol` message bus |
| Eyes, ears, and senses | CAN observers, sensors, cameras, microphones |
| Memory and evidence | `velvet-receipts` and Continuity Spine |
| Organs | Named handmaidens and pluggable modules |
| Presence | `velvet-interface` |

The metaphor does not replace the engineering boundary. It makes the boundary easier to understand.

## Event Laws

Every event contract should follow six laws.

### 1. One event, one truth

An event should describe one bounded fact or state transition, not a bundle of assumptions.

### 2. Events describe reality

An observation says what was observed. A proposal says what was proposed. A Court event says what was authorized or denied. An execution event says what actually happened.

These truths must not be collapsed into one ambiguous message.

### 3. Events are immutable

Once published, an event is not rewritten. Corrections arrive as new events with explicit references to the earlier record.

### 4. Events are replayable

A preserved event sequence should reconstruct the same shared history without silently creating new authority or physical action.

### 5. Events are observable

Events are visible only to components permitted by local policy, but they should not disappear into private side channels.

### 6. Events are versioned

Schemas evolve through explicit versions, additive compatibility where possible, and clear deprecation rather than surprise breakage.

## Event Families

Velvet separates event families because each answers a different question.

### Observation events

What was sensed or measured?

Examples include decoded CAN signals, occupancy, temperature, microphone state, camera observations, and Ghost CAN fixtures.

### Proposal and intent events

What action or interpretation was requested?

These may carry a public route ID and bounded parameters. They do not carry executor authority, raw capability selection, shell commands, hardware handles, or capability tokens.

### Court decision events

Was the request authorized or denied, under which policies, and for what reason?

Court events report authority decisions. They do not perform the action.

### Resource events

Were exclusive resources acquired, denied, released, or left degraded?

These events describe Runtime traffic control. They do not grant authorization by themselves.

### Execution events

Did an approved executor start, complete, fail, or receive a denial?

Execution events must preserve whether physical or logical work actually occurred.

### Receipt events

Was evidence persisted, linked, verified, or degraded?

A receipt proves that evidence exists. It does not create permission.

### Continuity events

What changed in lineage, body binding, surface identity, successor state, or verified history?

Continuity events preserve identity through time without becoming execution authority.

### Diagnostic and recovery events

What failed, degraded, recovered, or requires attention?

These events should name the known state rather than pretending the system is healthy.

## Reality Pipeline

```text
sensor or trusted producer
  -> observation event
  -> Core interpretation or structured proposal
  -> Runtime identity and context verification
  -> Court authorization or denial
  -> execution contract
  -> resource coordination
  -> safety gate
  -> replay protection
  -> approved executor
  -> execution outcome event
  -> receipt evidence
  -> continuity and interface presentation
```

The Event Protocol participates throughout this path, but it never substitutes for Runtime, Court, safety, replay protection, executors, Receipts, or Continuity.

## Authority Boundary

Events communicate. Runtime coordinates. Court authorizes. Executors act. Receipts remember.

An event must never be treated as permission to:

- select an executor
- choose raw capabilities or hardware targets
- invoke shell commands
- import arbitrary modules
- access relays or CAN writers
- steer, brake, accelerate, unlock, heat, cool, or actuate hardware
- bypass replay protection or resource coordination

A valid receipt ID is evidence, not authority.

A valid event shape is transport acceptance, not action approval.

## Event Delivery Path

```text
producer
  -> hardened publish interface
  -> schema and source validation
  -> receipt validation where required
  -> EventEnforcer
  -> EventBus
  -> permitted handlers
```

Direct `EventBus` access remains prohibited outside trusted Runtime wiring.

Modules must never:

- call private publish methods
- bypass Runtime wiring
- create private control buses to other organs
- originate actuation events outside an approved Runtime executor path
- convert observations directly into hardware actions

## Receipted Events

Use `publish_receipted_event()` for observations, lifecycle changes, decisions, and results that require persisted evidence.

```python
from core_action import publish_receipted_event

publish_receipted_event(
    enforcer_publish=runtime_publish,
    receipt_logger=logger,
    event_type="EXECUTION_COMPLETED",
    source="velvet-runtime",
    policy="runtime.execution.v1",
    authorized_by="court",
    domain="execution",
    payload={
        "executor_name": "runtime-status",
        "execution_performed": True,
        "actuation_performed": False,
    },
)
```

`publish_receipted_event()` refuses `ACTUATION` events. The retired `execute_authorized_action()` helper fails closed.

## CAN Observation Contracts

### Decoded CAN observations

`DECODED_CAN_SIGNAL_OBSERVED` carries one confidence-scored interpreted vehicle value from a trusted local producer.

It is observation-only and forbids executor names, direct routes, capabilities, tokens, commands, hardware targets, and actuation claims.

### Ghost CAN observations

`vehicle.can.ghost_observation` carries synthetic read-only CAN telemetry for the public Ghost Car loop.

A valid Ghost event must declare that it is fixture-backed, read-only, has not opened a physical bus, has not attempted or performed CAN transmission, has not performed actuation, and has not granted authority.

Ghost events may be replayed for demonstration and testing. Replay does not become physical execution.

See:

- [Intent Event Contract](docs/intent_event_contract.md)
- [Court Authority Boundary](docs/court_authority_boundary.md)
- [Decoded CAN Observation Contract](docs/decoded_can_observation_contract.md)
- [Ghost CAN Observation Contract](docs/ghost_can_observation_contract.md)

## Plugin and Module Doctrine

Velvet's stable main system should remain small and reviewable. Optional capabilities arrive as pluggable modules above that foundation.

A future dedicated Modules repository may catalogue optional capabilities, but it is not currently a dependency of this package.

Every module should:

- publish and subscribe through documented event contracts
- declare compatible schema versions
- consume only events it is permitted to see
- avoid private organ-to-organ protocols
- preserve observation, proposal, authorization, execution, and receipt distinctions
- gain no authority merely because it is installed

## Versioning and Compatibility

Event types are case-sensitive. Use constants from `event_types.py` where available.

Schema evolution should prefer:

- additive fields with safe defaults
- explicit schema-version fields
- compatibility tests across supported repositories
- documented deprecation windows
- replay tests using preserved fixtures
- rejection of unknown authority-bearing fields

Breaking changes require a new contract version rather than silent reinterpretation.

## What This Repository Owns

- event schemas and family definitions
- deterministic local event delivery
- source and receipt enforcement
- observation and lifecycle contracts
- request, decision, result, and degraded-state transport
- versioning and compatibility rules for the message bus

## What This Repository Does Not Own

- identity or continuity verification
- capability policy or authority hierarchy
- Court authorization
- capability-token signing
- execution-contract enforcement
- resource coordination
- safety-gate selection
- replay-ledger ownership
- executor registration
- hardware execution
- long-term evidence retention
- interface presentation

Those responsibilities belong to the corresponding Velvet repositories.

## Current Status

Current physical authority: **none**.

Implemented foundations include:

- hardened local publish path
- EventEnforcer and EventBus separation
- receipt-aware publishing
- retired direct-action helper
- intent event boundary
- decoded CAN observation contract
- Ghost CAN observation contract
- public Ghost event path

## Next Milestones

1. Build a shared schema registry with explicit event-family versions.
2. Add compatibility tests across Runtime, Receipts, Interface, Core, CAN, and Continuity.
3. Expand deterministic replay tooling and correction-event support.
4. Add bounded cross-node delivery contracts for trusted local machines.
5. Define module certification checks against the Event Laws.
6. Add privacy-aware subscription and retention guidance.

## Tests

From the repository root:

```bash
python -m pip install -e . 'pytest>=7.4,<8.4'
python -m pytest tests -q -ra
```

Pytest is the supported complete-suite runner for both `TestCase` methods and
module-level functions, including the truth-event tests. Installing pytest
while keeping `unittest discover` would still omit those functions. The test
dependency range preserves Python 3.8 support; CI runs on Python 3.8, 3.10,
and 3.12, prints the executed result/count, and retains JUnit XML for each run.

## Security Warning

A bus event is information, not authority.

A receipt is evidence, not permission.

Any path that turns either directly into hardware action is a doctrine violation.

## Version

`v1.6.2` public Ghost CAN protocol phase.

## License

GPLv3. Part of the Velvet ecosystem.
