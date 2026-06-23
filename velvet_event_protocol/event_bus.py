# SPDX-License-Identifier: GPL-3.0-only

from typing import Callable, List

from .event_schema import VelvetEvent


class EventBus:
    """Internal event transport. Publishing must pass through EventEnforcer."""

    def __init__(self) -> None:
        self.subscribers: List[Callable[[VelvetEvent], None]] = []

    def subscribe(self, handler: Callable[[VelvetEvent], None]) -> None:
        self.subscribers.append(handler)

    def _publish(self, event: VelvetEvent) -> None:
        for handler in tuple(self.subscribers):
            handler(event)
