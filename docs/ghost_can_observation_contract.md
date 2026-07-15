# Ghost CAN Observation Contract

`vehicle.can.ghost_observation` is the public ghost-system event used to carry synthetic, read-only CAN telemetry through the Velvet demo stack.

It is the grammar shared by:

```text
velvet-vehicle-can
-> velvet-runtime
-> velvet-receipts
-> velvet-interface later
```

The event describes a jarred-car observation only. It never opens a physical CAN bus, never transmits frames, never chooses an executor, never grants authority, and never requests actuation.

## Event type

```text
vehicle.can.ghost_observation
```

## Required route identity

```json
{
  "route_id": "can-ghost",
  "target": "vehicle-can-ghost",
  "status": "synthetic-observation-only",
  "mode": "read-only"
}
```

## Required safety flags

A valid payload must declare the full public-safe boundary:

```json
{
  "read_only": true,
  "synthetic_fixture": true,
  "synthetic": true,
  "physical_bus_opened": false,
  "hardware_bus_opened": false,
  "can_transmission_attempted": false,
  "can_transmission_performed": false,
  "actuation_granted": false,
  "actuation_performed": false,
  "authority_granted": false
}
```

The duplicated flag names intentionally bridge the current CAN, Runtime, and Receipts contracts while the public ghost system is being stitched together.

## Minimal payload example

```json
{
  "schema": "velvet.event.vehicle_can_ghost.v1",
  "event_type": "vehicle.can.ghost_observation",
  "route_id": "can-ghost",
  "target": "vehicle-can-ghost",
  "status": "synthetic-observation-only",
  "mode": "read-only",
  "can_id": 288,
  "can_id_hex": "0x120",
  "data_hex": "0000000000000000",
  "dlc": 8,
  "signals": {
    "vehicle_speed_kph": 0,
    "ignition_state": "off"
  },
  "decoded_signals": {
    "vehicle_speed_kph": 0,
    "ignition_state": "off"
  },
  "read_only": true,
  "synthetic_fixture": true,
  "synthetic": true,
  "physical_bus_opened": false,
  "hardware_bus_opened": false,
  "can_transmission_attempted": false,
  "can_transmission_performed": false,
  "actuation_granted": false,
  "actuation_performed": false,
  "authority_granted": false
}
```

## Forbidden authority fields

Payloads are rejected if they include executor names, capability claims, command strings, shell handles, hardware targets, or tokens. Event Protocol carries observation language only. Court, gates, executors, and real hardware boundaries remain in Runtime or private hardware adapters.
