from typing import Callable, List
from velvet_event_protocol.event_schema import VelvetEvent


class EventBus:
    """
    EventBus is an internal transport layer.

    Publishing MUST go through EventEnforcer.
    Wiring MUST go through runtime_wiring.build_event_runtime().

    Direct access to EventBus._publish bypasses doctrine
    and is considered invalid usage outside of runtime_wiring.
    EventBus instances must never be distributed to modules.
    """

    def __init__(self):
        self.subscribers: List[Callable[[VelvetEvent], None]] = []

    def subscribe(self, handler: Callable[[VelvetEvent], None]):
        self.subscribers.append(handler)

    def _publish(self, event: VelvetEvent):
        for handler in self.subscribers:
            handler(event)
