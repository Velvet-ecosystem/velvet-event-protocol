# SPDX-License-Identifier: GPL-3.0-only
"""Public package surface for Velvet Event Protocol."""

from .cognitive_events import (
    ACTION_TRACKING_FINISHED,
    ACTION_TRACKING_STARTED,
    BOUNDARY_PROPOSED,
    CONNECTION_HEALTH_CHANGED,
    CONTRACT as COGNITIVE_EVENT_CONTRACT,
    EPISODE_PROPOSED,
    EVENT_CLOSED,
    EVENT_OPENED,
    EVENT_TYPES as COGNITIVE_EVENT_TYPES,
    EVENT_UPDATED,
    HEALTH_CHANGED,
    INTERRUPT_ACCEPTED,
    INTERRUPT_CANDIDATE,
    MODULATORS_SNAPSHOTTED,
    PREDICTION_CREATED,
    PREDICTION_ERROR,
    PREDICTION_RESOLVED,
    PROPOSAL_CONTEXT,
    CognitiveEventRecord,
    build_cognitive_event,
    validate_cognitive_event,
)
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
    "COGNITIVE_EVENT_CONTRACT",
    "COGNITIVE_EVENT_TYPES",
    "EVENT_OPENED",
    "EVENT_UPDATED",
    "BOUNDARY_PROPOSED",
    "EVENT_CLOSED",
    "PREDICTION_CREATED",
    "PREDICTION_RESOLVED",
    "PREDICTION_ERROR",
    "INTERRUPT_CANDIDATE",
    "INTERRUPT_ACCEPTED",
    "PROPOSAL_CONTEXT",
    "ACTION_TRACKING_STARTED",
    "ACTION_TRACKING_FINISHED",
    "EPISODE_PROPOSED",
    "MODULATORS_SNAPSHOTTED",
    "CONNECTION_HEALTH_CHANGED",
    "HEALTH_CHANGED",
    "CognitiveEventRecord",
    "build_cognitive_event",
    "validate_cognitive_event",
]
