# SPDX-License-Identifier: GPL-3.0-only

from typing import Any, Callable, Dict, Optional, Set

from .event_bus import EventBus
from .event_schema import VelvetEvent


class UnauthorizedEventError(Exception):
    pass


class EventEnforcer:
    """Enforce transport rules before publishing onto the internal EventBus."""

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
        self._receipt_validator = receipt_validator
        self._allowed_sources = allowed_actuation_sources
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
        if event.event_type != "ACTUATION":
            return

        if not event.receipt_id:
            raise UnauthorizedEventError("ACTUATION event blocked: missing receipt_id")

        if self._receipt_validator and not self._receipt_validator(event.receipt_id):
            raise UnauthorizedEventError("ACTUATION event blocked: invalid receipt_id")

        if self._allowed_sources and event.source not in self._allowed_sources:
            raise UnauthorizedEventError(
                "ACTUATION event blocked: unauthorized source {!r}".format(event.source)
            )
