# Distributed Work Event Contract

Velvet's distributed body needs a shared, versioned way to report which organs exist, what work is available, where Runtime placed it, and how the body degraded or recovered.

This contract is the nervous-system transport for that truth.

It is not the scheduler, Court, an executor, a capability token, or canonical memory.

> Events communicate. Runtime places and leases. Court authorizes. Executors perform. Receipts preserve evidence. Riven preserves lineage.

## Contract

```text
velvet.distributed-work-events.v1
```

Every event carries:

```text
transport_only: true
canonical: false
authority: none
grants_authority: false
grants_execution: false
grants_actuation: false
```

A valid event can describe a Runtime workload lease. It cannot create one.

A valid event can report that consequential work requires Court. It cannot satisfy Court.

A valid event can report completion. It cannot retroactively authorize the work.

## Event family

### `NODE_ADVERTISEMENT_PUBLISHED`

Reports one verified Runtime registry view of an organ:

- node and body identity;
- named organ;
- node tier;
- capabilities;
- current load and health;
- availability;
- heartbeat;
- concurrent-task limits;
- accepted and refused work classes;
- overflow capabilities;
- temporary duty-absorption capabilities;
- fallback options;
- body and continuity verification status.

The Event Protocol transports these assertions. Runtime remains responsible for verifying and trusting them.

### `WORK_OFFERED`

Reports a bounded work requirement and its required capabilities. It may state whether Court authorization will be required and which degraded fallbacks are useful.

It does not name or select an executor.

### `WORK_ACCEPTED`

Reports that Runtime selected an organ and issued a short-lived workload lease. It carries the selected node, organ, placement mode, lease ID, and expiry.

The workload lease is placement evidence only. It is not an execution grant.

### `WORK_REFUSED`

Reports that a node refused work outside its limits or present availability. Refusal is healthy bounded behaviour, not an authority failure.

### `WORK_HANDOFF_REQUESTED`

Reports that active work should be moved because of load, health, availability, task limits, or another explicit reason.

The request cannot transfer authority, tokens, or executor identity to the replacement node.

### `WORK_COMPLETED`

Reports completion, partial completion, failure, or cancellation. Important results remain marked for escalation to the Queen so whole-body awareness is preserved.

### `WORK_DEGRADED`

Reports one explicit degradation mode:

```text
full_replacement
partial_replacement
observe_only
capability_unavailable
```

Degradation must name the known loss and available fallback rather than pretending the body is fully healthy.

### `WORK_RECOVERY_REASSIGNED`

Reports that Runtime moved work from a stale, offline, or failed node to another verified organ. It carries both node identities, the new placement mode, the replacement lease, and the recovery reason.

## Layered body

The event family supports Velvet's physical hierarchy:

- microcontrollers carry deterministic reflexes, timing, sensors, relays, and actuators;
- small specialist Linux nodes carry focused services;
- heavier Linux nodes carry demanding local cognition and service groups;
- the Queen carries whole-system awareness, reasoning, planning, authority context, and final coordination.

Hardware size does not determine importance. Advertised suitability, timing, health, task limits, and capacity determine placement.

## Unified-Organ boundary

These events do not create independent agents.

All participating organs remain bound to:

- one verified body registry;
- one continuity lineage;
- one Event Protocol;
- one Runtime placement system;
- one Court authority path;
- one accountable Queen.

> Velvet rejects the agent swarm. She is built as Unified-Organ AI: distributed specialties, shared concrete reality, dynamic workload cooperation, one authorization spine, and one accountable body.

## Forbidden authority fields

The validator rejects authority-bearing fields anywhere in the payload, including nested values. Examples include:

```text
capability_token
court_token
execution_token
executor_name
command
shell
hardware_target
permit
```

A future contract that needs to report authorization evidence must use a separate, explicit Court or execution outcome event. It must not smuggle authority through this workload family.

## Receipts and continuity

Placement, refusal, handoff, recovery, and degraded-state events may later be receipted when policy requires durable evidence.

Receipts prove that the event was preserved. They do not create permission.

Riven may preserve node replacement and duty-absorption lineage where those changes affect the body's continuing identity. Ordinary short-lived load balancing does not automatically become canonical lineage.

## Current boundary

This contract adds no network listener, remote executor, scheduling algorithm, capability token, CAN transmission, actuator path, or physical authority.

Current physical authority remains **none**.
