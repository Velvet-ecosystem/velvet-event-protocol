# Velvet Event Protocol

**Enforcement layer for event-driven actuation in the Velvet ecosystem.**

This repository defines the internal event law of the Velvet runtime. It governs how decisions become actions — ensuring no actuation occurs without authorization, logging, and validation.

> **This module enforces behavior. It does not trust it.**

---

## Core Doctrine

- **No ACTUATION without a valid receipt.**
- **Cognition proposes. Court decides. Executors act.**
- **All actions must be logged before execution.**

These are not conventions. They are enforced structurally by `EventEnforcer` and `runtime_wiring`.

---

## Flow

```
decision → receipt → validation → enforcer → bus → handlers
```

1. A decision is made upstream (brain adapter / policy layer).
2. A receipt is created and logged via `velvet-receipts`.
3. The receipt ID is attached to the event.
4. `EventEnforcer` validates the receipt before allowing publish.
5. `EventBus` delivers the event to registered handlers.

---

## Usage

```python
from velvet_event_protocol.runtime_wiring import build_event_runtime

rt = build_event_runtime(
    receipt_validator=...,
    allowed_actuation_sources={"core"}
)

rt["publish"](event)
```

Subscribe handlers before publishing:

```python
rt["bus"].subscribe(my_handler)
```

For authorized actuation with receipt creation, use `core_action`:

```python
from velvet_event_protocol.core_action import execute_authorized_action

execute_authorized_action(
    enforcer_publish=rt["publish"],
    receipt_logger=logger,
    policy="AutoHeadlightPolicy",
    authorized_by="core",
    domain="lighting",
    notes="Low light detected",
    payload={"headlights": "ON"},
)
```

---

## Receipt Validation

By default, the protocol enforces the presence of a `receipt_id`.

To enforce that the receipt exists in the ledger, a validator must be provided:

```python
from velvet_event_protocol.receipt_bridge import make_receipt_validator

rt = build_event_runtime(
    receipt_validator=make_receipt_validator("receipts.log"),
    allowed_actuation_sources={"core"}
)
```

**Without a validator:**
- ACTUATION without `receipt_id` is blocked
- ACTUATION with any `receipt_id` is allowed

**With a validator:**
- Only receipts present in the ledger are accepted

---

## Event Types

Event types are case-sensitive.

```
"ACTUATION"   → valid, enforced
"actuation"   → NOT enforced
```

Always use the defined constants from `event_types.py`:

```python
from velvet_event_protocol.event_types import ACTION_EVENTS
```

---

## Critical Rule

Modules must **never**:

- Access `EventBus` directly
- Call `_publish`
- Bypass `runtime_wiring`

All event publishing must go through:

```
rt["publish"] → EventEnforcer → EventBus
```

Violating this breaks the enforcement model.

---

## ⚠ Warnings

```
DO NOT bypass runtime_wiring.
DO NOT access EventBus directly.
DO NOT attempt to publish without enforcer.
```

Direct use of `EventBus._publish` outside of `runtime_wiring` is a doctrine violation and will not be supported.

---

## Version

`v1.5.1` — documentation polish release.
Part of the Velvet ecosystem. Requires `velvet-receipts` for full actuation path.
