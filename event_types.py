# Core system event types

SYSTEM_EVENTS = {
    "SYSTEM_START",
    "SYSTEM_STOP",
    "ERROR",
}

USER_EVENTS = {
    "USER_INPUT",
    "VOICE_COMMAND",
    "TOUCH_INPUT",
}

DECISION_EVENTS = {
    "INTENT_DETECTED",
    "POLICY_CHECK",
    "AUTHORIZATION_GRANTED",
    "AUTHORIZATION_DENIED",
}

ACTION_EVENTS = {
    "COMMAND_DISPATCH",
    "ACTUATION",
}

OBSERVATION_EVENTS = {
    "DECODED_CAN_SIGNAL_OBSERVED",
}

COGNITIVE_EVENTS = {
    "cognitive.event.opened",
    "cognitive.event.updated",
    "cognitive.event.boundary_proposed",
    "cognitive.event.closed",
    "cognitive.prediction.created",
    "cognitive.prediction.resolved",
    "cognitive.prediction.error",
    "cognitive.interrupt.candidate",
    "cognitive.interrupt.accepted",
    "cognitive.proposal.context",
    "cognitive.action.tracking_started",
    "cognitive.action.tracking_finished",
    "cognitive.episode.proposed",
    "cognitive.modulators.snapshotted",
    "cognitive.connection.health_changed",
    "cognitive.health.changed",
}

DISTRIBUTED_WORK_EVENTS = {
    "NODE_ADVERTISEMENT_PUBLISHED",
    "WORK_OFFERED",
    "WORK_ACCEPTED",
    "WORK_REFUSED",
    "WORK_HANDOFF_REQUESTED",
    "WORK_COMPLETED",
    "WORK_DEGRADED",
    "WORK_RECOVERY_REASSIGNED",
}

MEMORY_EVENTS = {
    "RECEIPT_CREATED",
    "RECEIPT_VERIFIED",
}
