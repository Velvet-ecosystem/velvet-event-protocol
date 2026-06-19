# Intent Event Contract

This repo defines Velvet's event protocol, event validation, enforcement boundaries, and safe event flow.

The canonical doctrine lives in:

- `velvet-ai-core/docs/scene_doctrine.md`
- `velvet-ai-core/docs/room_body_interface.md`
- `velvet-ai-core/docs/boot_identity_sequence.md`
- `velvet-ai-core/docs/retrofit_body_registry.md`
- `velvet-ai-core/docs/naming_and_binding.md`

This document defines the event protocol repo's local contract.

Events may carry intent, observations, status, requests, confirmations, degraded-state reports, and receipt references.

Events do not grant authority by themselves.

An event is not permission.

## Event Responsibilities

The event protocol layer may:

- define event structure
- validate event shape
- classify event type
- preserve source identity
- require receipt references where appropriate
- enforce event immutability where required
- reject malformed events
- distinguish observation from request
- distinguish request from actuation
- support safe publish boundaries
- prevent unsafe event routing patterns

The event protocol layer may not:

- treat event presence as authorization
- allow direct source-to-executor shortcuts
- allow scene objects to actuate hardware directly
- allow CAN-discovered signals to become trusted actions directly
- allow modules to bypass safe publish
- allow write-capable events without enforcement context
- silently upgrade observations into commands
- silently upgrade requests into executions

## Intent Is Not Execution

A user interface scene may emit an intent event.

A CAN module may emit an observation event.

A runtime module may emit a degraded-state event.

A profile module may emit a session-context event.

None of these events execute hardware by themselves.

Correct flow:

    event emitted
      -> event validation
      -> identity / context check
      -> policy authorization
      -> capability token check
      -> safety gate
      -> executor
      -> receipt

Forbidden flow:

    event emitted
      -> actuator

## Observation Events

Observation events report what the system sees.

Examples:

- sensor state
- CAN frame interpretation
- passenger presence signal
- body fingerprint status
- degraded hardware state
- module heartbeat
- environmental condition
- profile context signal

Observation events may inform policy, but they do not authorize action.

## Request Events

Request events describe a desired action or transition.

Examples:

- request door lock
- request HVAC change
- request scene transition
- request profile switch
- request maintenance mode
- request body registry update
- request boot identity review

Request events require authorization before execution.

## Actuation Events

Actuation events represent write-capable behavior or execution intent.

Examples:

- relay command
- CAN command
- actuator command
- body registry mutation
- profile binding mutation
- capability policy change
- restricted scene access change

Actuation events require stricter validation, authorization, capability checks, safety gates, and receipts.

## Source Identity

Events should preserve source identity.

Examples:

- interface scene
- runtime module
- CAN observer
- body registry loader
- profile manager
- receipt validator
- maintenance tool
- emergency policy module

Source identity helps determine trust level, routing, and enforcement requirements.

Source identity does not replace authorization.

## Event Type Boundaries

Suggested event classes:

    OBSERVATION
    INTENT
    REQUEST
    CONFIRMATION
    AUTHORIZATION_RESULT
    ACTUATION
    DEGRADED_STATE
    RECEIPT_REFERENCE
    BOOT_IDENTITY
    BODY_REGISTRY_UPDATE
    PROFILE_BINDING_UPDATE

Event classes should not be casually upgraded.

A malformed or ambiguous event should fail closed.

## Public Rule

Events carry meaning.

Policy grants permission.

Gates enforce permission.

Executors perform action.

Receipts preserve accountability.