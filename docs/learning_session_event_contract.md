# Learning Mode Session Event Contract

`velvet.learning-session-events.v1` carries bounded lifecycle evidence for Velvet Learning Mode sessions.

The event family reports that a study session was proposed, checked for eligibility, opened, progressed, paused, degraded, moved to review, completed, aborted, or ended for insufficient evidence. It does not perform the study and it does not promote what was learned.

## Event family

- `learning.session.proposed`
- `learning.session.eligibility_checked`
- `learning.session.opened`
- `learning.session.studying`
- `learning.session.review_pending`
- `learning.session.paused`
- `learning.session.degraded`
- `learning.session.insufficient_evidence`
- `learning.session.completed`
- `learning.session.aborted`

## Payload boundary

The contract carries references and lifecycle facts only:

- Learning Session ID
- body and node binding
- stable study-subject reference
- state
- evidence references
- eligibility-source references
- cognitive workspace references
- distributed-work references
- candidate references
- explicitly simulated evidence references
- degraded reason codes
- bounded step count
- compact lifecycle reason code

It deliberately does not copy raw study material, prompts, queries, web pages, Library content, transcripts, model output, capability tokens, Court decisions, executor handles, commands, hardware targets, or actuation claims.

## Ghost boundary

Ghost remains the fake-car and simulated-vehicle fixture path. Learning Mode may consume Ghost-backed evidence only when that evidence is explicitly identified as simulated. `simulated_evidence_refs` must be a subset of the session's ordinary `evidence_refs` so simulated vehicle evidence cannot lose provenance while moving through Learning Mode.

Ghost is not a general-purpose Learning Mode sandbox, worker class, or cognition engine.

## Authority boundary

Every Learning Mode lifecycle payload declares:

```text
transport_only: true
canonical: false
learning_evidence_only: true
authority: none
grants_authority: false
grants_memory_write: false
grants_runtime_placement: false
grants_execution: false
grants_actuation: false
applies_learning_change: false
```

A valid Learning Mode event proves that a bounded lifecycle transition was reported. It does not prove that a conclusion is true, grant permission to promote memory, choose Runtime placement, authorize execution, or change behavior.

## Ownership

AI Core owns Learning Session meaning and cognitive coordination. Runtime/body policy supplies eligibility and may place separately proposed bounded work. Event Protocol transports lifecycle evidence. Velvet Receipts may normalize accepted events into canonical append-only evidence. Persona Continuity and Core memory admission remain separate from session transport.
