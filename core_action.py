from typing import Callable, Optional, Dict, Any
from velvet_event_protocol.event_schema import VelvetEvent

# We assume these imports exist in velvet-receipts
# (do not modify their implementation)
from receipt import Receipt
from receipt_logger import ReceiptLogger


def execute_authorized_action(
    *,
    enforcer_publish: Callable[[VelvetEvent], None],
    receipt_logger: ReceiptLogger,
    policy: str,
    authorized_by: str,
    domain: Optional[str],
    notes: Optional[str],
    action_event_type: str = "ACTUATION",
    source: str = "core",
    payload: Optional[Dict[str, Any]] = None,
    parent_event_id: Optional[str] = None,
    confidence: Optional[float] = None,
) -> VelvetEvent:
    """
    Creates a receipt, logs it, and publishes an ACTUATION event
    that is guaranteed to carry a valid receipt_id.

    This enforces:
    - No actuation without receipt
    - Receipts precede actions
    """

    # 1. Create receipt (inert)
    receipt = Receipt(
        policy=policy,
        authorized_by=authorized_by,
        domain=domain,
        notes=notes,
        confidence=confidence,
    )

    # 2. Log receipt (this assigns receipt_id + hash chain)
    logged = receipt_logger.log(receipt)

    # 3. Create ACTUATION event with receipt_id attached
    event = VelvetEvent(
        event_type=action_event_type,
        source=source,
        payload=payload or {},
        parent_event_id=parent_event_id,
        receipt_id=logged.receipt_id,
    )

    # 4. Publish through enforcer (will validate receipt)
    enforcer_publish(event)

    return event


# from event_bus import EventBus
# from event_enforcer import EventEnforcer
# from receipt_logger import ReceiptLogger
# from receipt_bridge import make_receipt_validator
# from core_action import execute_authorized_action
#
# bus = EventBus()
# logger = ReceiptLogger("receipts.log")
# validator = make_receipt_validator("receipts.log")
#
# enforcer = EventEnforcer(
#     bus.publish,
#     receipt_validator=validator,
#     allowed_actuation_sources={"core"},
# )
#
# execute_authorized_action(
#     enforcer_publish=enforcer.publish,
#     receipt_logger=logger,
#     policy="AutoHeadlightPolicy",
#     authorized_by="core",
#     domain="lighting",
#     notes="Low light detected",
#     payload={"headlights": "ON"},
# )
