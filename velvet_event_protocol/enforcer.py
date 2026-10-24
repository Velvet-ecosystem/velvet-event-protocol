# SPDX-License-Identifier: GPL-3.0-only

from typing import Any, Callable, Dict, Optional, Set

from .event_bus import EventBus
from .event_schema import VelvetEvent


class UnauthorizedEventError(Exception):
    pass


class EventEnforcer:
    """Publish evidence and requests, never physical execution authority.

    ACTUATION is reserved and always rejected here. Receipt lookup and source
    allowlists cannot replace Runtime Court, capability verification, safety,
    replay protection, and its approved executor. The legacy constructor
    arguments remain accepted for migrating callers; neither can enable
    consequential publishing.
    """

    def __init__(
        self,
        bus: Optional[EventBus] = None,
        publish_fn: Optional[Callable[[VelvetEvent], None]] = None,
        receipt_validator: Optional[Callable[[str], bool]] = None,
        allowed_actuation_sources: Optional[Set[str]] = None,
        default_source: str = "velvet-runtime",
    ) -> None:
        if bus is None and publish_fn is None:
            raise ValueError("EventEnforcer requires bus or publish_fn")
        if bus is not None and publish_fn is not None:
            raise ValueError("EventEnforcer accepts bus or publish_fn, not both")

        self.bus = bus
        self._publish_fn = bus._publish if bus is not None else publish_fn
        self._default_source = default_source

    def publish(
        self,
        event: Optional[VelvetEvent] = None,
        *,
        event_type: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        receipt_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> VelvetEvent:
        if event is not None and event_type is not None:
            raise ValueError("provide event or event_type, not both")
        if event is None:
            if not event_type:
                raise ValueError("event_type is required")
            event = VelvetEvent(
                event_type=event_type,
                source=source or self._default_source,
                payload=payload or {},
                receipt_id=receipt_id,
            )

        self._enforce(event)
        assert self._publish_fn is not None
        self._publish_fn(event)
        return event

    def _enforce(self, event: VelvetEvent) -> None:
        if isinstance(event.event_type, str) and event.event_type.strip().upper() == "ACTUATION":
            raise UnauthorizedEventError(
                "ACTUATION is not accepted by generic event publishing; "
                "submit an intent through the Velvet Runtime Court and approved executor"
            )
