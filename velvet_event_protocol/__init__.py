# SPDX-License-Identifier: GPL-3.0-only
"""Public package surface for Velvet Event Protocol."""

from .enforcer import EventEnforcer, UnauthorizedEventError
from .event_bus import EventBus
from .event_schema import VelvetEvent
from .ghost_can_observation import (
    GHOST_CAN_OBSERVATION_EVENT,
    GhostCanObservation,
    build_ghost_can_observation_event,
    validate_ghost_can_observation_event,
)

__all__ = [
    "EventBus",
    "EventEnforcer",
    "UnauthorizedEventError",
    "VelvetEvent",
    "GHOST_CAN_OBSERVATION_EVENT",
    "GhostCanObservation",
    "build_ghost_can_observation_event",
    "validate_ghost_can_observation_event",
]
