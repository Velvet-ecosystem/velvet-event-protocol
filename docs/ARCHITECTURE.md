# Velvet Event Protocol — Architecture

## Overview

The Velvet Event Protocol is the enforcement layer between cognition and actuation. It ensures that every action taken by the Velvet runtime is authorized, receipted, and delivered through a controlled path. No module may actuate by circumventing this layer.

---

## Component Roles

**`event_schema.py`**
Defines `VelvetEvent` — a frozen dataclass representing a single immutable event. All events carry a source, type, payload, and optionally a `receipt_id`. Immutability is structural: `frozen=True` prevents modification after creation.

**`event_types.py`**
Canonical registry of event type strings, grouped by domain: SYSTEM, USER, DECISION, ACTION, MEMORY. Used for consistency across the runtime. Not enforced programmatically — consumed by convention.

**`event_bus.py`**
Internal transport layer only. Maintains a list of subscribers and delivers events to them via `_publish`. The leading underscore is intentional — `_publish` is not a public interface. `EventBus` instances must never be passed to external modules. Wiring is exclusively the responsibility of `runtime_wiring`.

**`event_enforcer.py`**
The enforcement gate. Wraps `_publish` and intercepts every event before delivery. Enforces three rules for ACTUATION events: receipt presence, receipt validity (if a validator is provided), and source authorization (if a source allowlist is configured). Raises `UnauthorizedEventError` on any violation. Future enforcement rules are added here only.

**`receipt_bridge.py`**
Constructs a receipt validator callable from a JSONL receipt log file. Bridges the file-based receipt chain from `velvet-receipts` into the enforcer's validator interface. Stateless — returns a function, holds no state itself.

**`core_action.py`**
The canonical actuation path. Combines receipt creation, logging, event construction, and enforcer publication into a single authorized call. This is the correct way to trigger an ACTUATION event. Depends on `Receipt` and `ReceiptLogger` from the `velvet-receipts` repo.

**`runtime_wiring.py`**
The sole authorized assembly point for the event runtime. The only location permitted to pass `EventBus._publish` directly to `EventEnforcer`. Returns a dict with three keys: `bus` (for subscribe wiring), `enforcer` (for inspection/testing), and `publish` (the only callable modules may hold). Modules must never receive `bus` or a raw publish callable.

---

## Enforcement Chain

```
Event → Enforcer → Validation → Publish → Handlers
```

Every event passes through `EventEnforcer.publish`. For ACTUATION events, the enforcer checks receipt presence, receipt validity, and source authorization — in that order — before forwarding to `EventBus._publish`. Non-ACTUATION events pass through without restriction (future rules may change this).

---

## Security Model

**No direct bus publishing.** `EventBus._publish` is intentionally named with a leading underscore. The only legitimate caller is `runtime_wiring`. Any module calling it directly is bypassing enforcement.

**Immutable events.** `VelvetEvent` is a frozen dataclass. Once constructed, it cannot be altered. There is no path to retroactively attach a receipt ID to an event — the receipt must be obtained before the event is created.

**Receipt-backed actuation only.** An ACTUATION event without a `receipt_id` is rejected unconditionally. An ACTUATION event with a `receipt_id` that fails validation is also rejected. There is no override path.

**Source allowlisting.** `EventEnforcer` accepts an optional `allowed_actuation_sources` set. When configured, only events from listed sources may actuate. Events from unlisted sources raise `UnauthorizedEventError` regardless of receipt validity.

---

## Known Constraint

Python's import system and introspection capabilities mean that a malicious or compromised module could access `EventBus._publish` directly, bypassing `EventEnforcer`. This system does not defend against that scenario.

**The system assumes all loaded modules are trusted.** Module-level trust is a runtime and deployment concern, outside the scope of this package. Enforcement here is structural, not adversarial.

---

## External Dependencies

`core_action.py` imports `Receipt` and `ReceiptLogger` from `velvet-receipts`. These are not bundled in this repository. The event protocol is intentionally decoupled from the receipt implementation — the bridge is `receipt_bridge.py`, which accepts any JSONL log path.
