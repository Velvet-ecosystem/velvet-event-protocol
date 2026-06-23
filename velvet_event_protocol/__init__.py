# SPDX-License-Identifier: GPL-3.0-only
"""Public package surface for Velvet Event Protocol."""

from .enforcer import EventEnforcer, UnauthorizedEventError
from .event_bus import EventBus
from .event_schema import VelvetEvent

__all__ = [
    "EventBus",
    "EventEnforcer",
    "UnauthorizedEventError",
    "VelvetEvent",
]
