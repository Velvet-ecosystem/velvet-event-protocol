from typing import Callable, Optional, Set
from velvet_event_protocol.event_bus import EventBus
from velvet_event_protocol.event_enforcer import EventEnforcer


def build_event_runtime(
    *,
    receipt_validator: Optional[Callable[[str], bool]] = None,
    allowed_actuation_sources: Optional[Set[str]] = None,
) -> dict:
    """
    Sole authorized assembly point for the Velvet event runtime.

    This is the ONLY place permitted to touch EventBus._publish directly.
    Modules must never receive bus or raw publish callable.
    Modules receive only the 'publish' key from this dict (enforcer.publish).

    Returns:
        {
            "bus":      EventBus       — for subscribe() wiring only
            "enforcer": EventEnforcer  — for inspection/testing only
            "publish":  Callable       — the ONLY publish path for modules
        }
    """
    bus = EventBus()
    enforcer = EventEnforcer(
        bus._publish,
        receipt_validator=receipt_validator,
        allowed_actuation_sources=allowed_actuation_sources,
    )
    return {
        "bus": bus,
        "enforcer": enforcer,
        "publish": enforcer.publish,
    }
