from typing import Callable, Optional, Dict, Any
from velvet_event_protocol.event_schema import VelvetEvent

from receipt import Receipt
from receipt_logger import ReceiptLogger


def publish_receipted_event(
    *,
    enforcer_publish: Callable[[VelvetEvent], None],
    receipt_logger: ReceiptLogger,
    event_type: str,
    source: str,
    payload: Optional[Dict[str, Any]] = None,
    parent_event_id: Optional[str] = None,
    policy: str,
    authorized_by: str,
    domain: Optional[str] = None,
    notes: Optional[str] = None,
    confidence: Optional[float] = None,
) -> VelvetEvent:
    """Publish a receipted observation or lifecycle event.

    This helper records and distributes events. It is not an authorization
    mechanism and refuses ACTUATION events. Physical or write-capable actions
    must pass through Velvet Runtime Court authorization, a signed capability
    token, a matching safety gate, and an approved executor.
    """

    if event_type == "ACTUATION":
        raise RuntimeError(
            "ACTUATION events cannot be created by receipt-only helpers; "
            "use the Velvet Runtime Court and approved-executor pipeline"
        )

    receipt = Receipt(
        policy=policy,
        authorized_by=authorized_by,
        domain=domain,
        notes=notes,
        confidence=confidence,
    )
    logged = receipt_logger.log(receipt)

    event = VelvetEvent(
        event_type=event_type,
        source=source,
        payload=payload or {},
        parent_event_id=parent_event_id,
        receipt_id=logged.receipt_id,
    )
    enforcer_publish(event)
    return event


def execute_authorized_action(**kwargs):
    """Deprecated and intentionally blocked.

    A receipt proves a decision or result was recorded. It does not create
    authority. This former shortcut could publish an ACTUATION event after
    receipt creation without a Court token, safety gate, or approved executor.
    """

    raise RuntimeError(
        "execute_authorized_action is retired; submit a strict intent through "
        "Velvet Runtime so Court authorization, safety, replay protection, "
        "approved execution, and final receipts remain mandatory"
    )
