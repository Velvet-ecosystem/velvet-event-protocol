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

The former receipt-only actuation helper is retired. `ACTUATION` events must originate from trusted Runtime execution wiring after the approved executor path has completed its required gates.
