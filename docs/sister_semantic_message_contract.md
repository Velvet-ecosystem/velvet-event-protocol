# Sister Semantic Message Contract

Status: Phase 1 draft, additive and non-production

## Purpose

Velvet already has event contracts for observations, cognition, proposals, truth, distributed work, handoff, and receipts. What was missing was a bounded way for one named identity to tell another what she found, ask a question, propose an interpretation, correct a prior statement, or acknowledge receipt without turning that exchange into a work-transfer protocol or a hidden reasoning channel.

This contract fills that gap.

Example shape:

- Iris observes visual evidence and asks Sarah to evaluate security significance.
- Velour finds a historical record and sends Ruby the evidence reference for diagnostic interpretation.
- Anna identifies an acoustic event and asks Iris whether there is matching visual evidence.
- Nancy proposes route context to Charlotte without gaining driving authority.

## Semantic messages are not raw reasoning

A semantic message carries a concise, externally reviewable statement, question, proposal, correction, or acknowledgement.

It must not carry raw chain-of-thought, hidden scratchpads, private reasoning traces, shell commands, execution tokens, Court tokens, hardware targets, or capability grants.

The allowed speech acts are:

- `statement`
- `question`
- `proposal`
- `correction`
- `acknowledgement`

The message is the conclusion or question that another organ needs, not the sender's private internal reasoning transcript.

## Required identity fields

Each message identifies:

- `sender_identity_id`
- one or more `recipient_identity_ids`
- `message_id`
- `purpose`
- `semantic_content`
- `source_refs`

A sender cannot address the same message to herself. Identity references are descriptive and do not establish that a running process has proven lineage. Riven / Continuity Spine remains responsible for identity continuity proof.

## Evidence and confidence

Messages may include `evidence_refs`, `confidence`, and `correlation_ids`.

Evidence references make testimony inspectable. They do not become canonical truth merely because a sister sent them.

A receiving organ may disagree, request more evidence, or send a correction. Testimony is evidence, not identity instruction and not authority.

## Privacy scope

Phase 1 reuses the existing Persona Continuity vocabulary:

- `shared`
- `role_local`
- `private`
- `working`

The event only labels the intended scope. It does not grant access to that scope. Runtime, profile/session policy, Persona Continuity, and the relevant source custodian still decide whether a sender may disclose and a recipient may receive the referenced information.

A private label is therefore not a bypass token.

## Urgency and requested response

Urgency is descriptive:

- `routine`
- `elevated`
- `urgent`

It may affect prioritization in a future consumer, but it grants no authority and cannot trigger physical action by itself.

The sender may request:

- `none`
- `acknowledge`
- `answer`
- `evaluate`
- `propose`

A requested response is not an instruction to execute work. Existing distributed-work events remain the path for governed work offers, handoffs, acceptance, refusal, degradation, and recovery reassignment.

## Replies

A semantic reply uses the same event contract and may include `reply_to_message_id`.

This gives sister exchanges a reviewable thread without creating a second conversation engine or transport.

## Authority invariants

Every message is fixed to:

```text
semantic_only: true
transport_only: true
canonical_evidence: false
authority: none
grants_authority: false
grants_execution: false
grants_actuation: false
memory_write: false
```

Therefore:

- Nancy cannot authorize Charlotte to drive.
- Sarah cannot unlock a door through a semantic message.
- Ruby cannot gain ECU write access because another sister asked her to inspect something.
- A sister cannot promote her own role or capability by saying she is qualified.
- A message cannot write itself into canonical memory.

## Relationship to existing Event Protocol contracts

Use semantic messages for bounded sister-to-sister meaning.

Use Cognitive Events for a cognitive episode, prediction, interruption candidate, proposal context, and cognitive health state.

Use Distributed Work Events when work is being offered, accepted, refused, handed off, degraded, completed, or reassigned.

Use Truth Events and source observations for evidence/truth assertions.

Use Runtime/Court for authority and execution governance.

Use Communications only as a carrier when an approved event crosses nodes/bodies. This contract does not add a new transport.

## Phase 1 examples

### Iris to Sarah

Iris may send:

> visual-perception found an unknown person remaining near the driver door; evaluate security significance.

The message references the visual observation and carries a confidence value. It does not mark the person hostile and does not authorize a response.

### Velour to Ruby

Velour may send:

> archive record shows this fault code previously occurred after low system voltage; evaluate whether that history is relevant to the current diagnostic evidence.

Ruby receives provenance, not a command.

### Nancy to Charlotte

Nancy may send:

> current route context indicates the planned turn is 400 m ahead; evaluate against current driving context.

That is navigation context. Charlotte's motion proposals and any consequential execution remain separately governed.

## Hard boundaries

This branch does not modify:

- existing event type registries;
- existing Cognitive Event behavior;
- existing Distributed Work behavior;
- Runtime or Court;
- Communications transport;
- AI Core;
- Persona Continuity;
- Riven;
- Language;
- Interface;
- physical execution or hardware control.

The new contract is additive and can be reviewed/rebased after Astra's repair sequence without patching Repair 2 CI work.
