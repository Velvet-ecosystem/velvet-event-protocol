"""Legacy positional adapter for the canonical, non-authorizing event gate."""

from typing import Callable, Optional, Set

from velvet_event_protocol.enforcer import (
    EventEnforcer as _EventEnforcer,
    UnauthorizedEventError,
)
from velvet_event_protocol.event_schema import VelvetEvent


class EventEnforcer(_EventEnforcer):
    """Preserve the old callback constructor without a second enforcement policy."""

    def __init__(
        self,
        publish_fn: Callable[[VelvetEvent], None],
        receipt_validator: Optional[Callable[[str], bool]] = None,
        allowed_actuation_sources: Optional[Set[str]] = None,
    ) -> None:
        super().__init__(
            publish_fn=publish_fn,
            receipt_validator=receipt_validator,
            allowed_actuation_sources=allowed_actuation_sources,
        )
