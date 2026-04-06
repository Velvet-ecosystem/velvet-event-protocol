from typing import Callable, Optional, Set
from velvet_event_protocol.event_schema import VelvetEvent

# Example validator (to be connected to velvet-receipts later):
# def validate_receipt(receipt_id: str) -> bool:
#     # lookup in receipt chain
#     return receipt_id in known_receipts


class UnauthorizedEventError(Exception):
    pass


class EventEnforcer:
    """
    Minimal enforcement layer for Velvet events.

    Responsibilities:
    - Block unauthorized ACTUATION events
    - Provide a wrapper around EventBus._publish
    - Keep enforcement separate from transport (event_bus)
    """

    def __init__(
        self,
        publish_fn: Callable[[VelvetEvent], None],
        receipt_validator: Callable[[str], bool] = None,
        allowed_actuation_sources: Optional[Set[str]] = None,
    ):
        self._publish = publish_fn
        self._receipt_validator = receipt_validator
        self._allowed_sources = allowed_actuation_sources

    def publish(self, event: VelvetEvent):
        self._enforce(event)
        self._publish(event)

    def _enforce(self, event: VelvetEvent):
        # RULE 1: No ACTUATION without receipt
        if event.event_type == "ACTUATION":
            if not event.receipt_id:
                raise UnauthorizedEventError(
                    "ACTUATION event blocked: missing receipt_id"
                )

            # RULE 2: Receipt must be valid (if validator provided)
            if self._receipt_validator:
                if not self._receipt_validator(event.receipt_id):
                    raise UnauthorizedEventError(
                        "ACTUATION event blocked: invalid receipt_id"
                    )

            # RULE 3: Source restriction (if configured)
            if self._allowed_sources:
                if event.source not in self._allowed_sources:
                    raise UnauthorizedEventError(
                        f"ACTUATION event blocked: unauthorized source '{event.source}'"
                    )

        # Future rules go here
