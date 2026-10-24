# Court Authority Boundary

Velvet Event Protocol transports structured meaning. It does not grant authority.

A valid event, a valid source, and a valid receipt are still insufficient to authorize physical or write-capable behavior.

The only approved execution path is:

```text
strict intent
  -> verified identity context
  -> capability policy
  -> Court authorization
  -> signed capability token
  -> matching safety gate
  -> approved executor
  -> replay consumption
  -> execution receipts
```

Event Protocol may carry observations and requests into Runtime, then distribute decisions and outcomes after Runtime has completed its checks.

Receipt-aware event enforcement remains useful for accountability and transport integrity, but it must never be interpreted as a substitute for Court authorization.

The former receipt-only actuation helper is retired. Generic `EventEnforcer.publish`
unconditionally rejects `ACTUATION`, including case/whitespace variants, regardless
of receipt identifiers, verifier callbacks or source allowlists. Missing verification
cannot create an exception. The root legacy enforcer delegates to the same gate.

There is no trusted-source escape hatch. Submit consequential intent to Runtime;
its approved executor invokes the handler after all required gates. Publish
`EXECUTION_STARTED`, `EXECUTION_COMPLETED`, `EXECUTION_FAILED` or other evidence
as observations, never as commands for another subscriber to execute.

Constructor parameters `receipt_validator` and `allowed_actuation_sources` remain
accepted for source compatibility but cannot enable actuation and are not called
as execution verifiers. Existing callers that used receipt-backed ACTUATION must
migrate to Runtime. No new capability/token format is introduced.
