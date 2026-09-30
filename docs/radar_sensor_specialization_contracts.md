# Radar and Sensor Specialization Contracts v0.1

Status: proposed specialization layer on top of `velvet.sensor-envelope.v0.1`.

## Purpose

These contracts define vendor-neutral radar payloads and the first common sensor coordination events. They remain evidence-only. They do not grant actuation authority, select executors, or create a direct sensor-to-actuator path.

## Radar detection frame

`radar_detection_frame` reports normalized radar measurements such as:

- range in metres
- radial velocity in metres per second
- azimuth and optional elevation
- signal-to-noise ratio and radar cross-section when available
- per-measurement uncertainty
- quality flags
- optional sensor-local classification with explicit source and confidence

A classification is interpretation produced by the sensor or adapter. It is not equivalent to the underlying range, velocity, or angle measurement.

## Radar local track

`radar_local_track` preserves a track maintained by one radar or radar adapter. A sensor-local track identifier must not be treated as a world-model track identifier. Fusion software may associate the local track with a separate world-model track and may maintain that world track across sensor restarts or local-track renumbering.

## Radar health

The common sensor envelope already carries health states suitable for radar, including:

- healthy
- degraded
- blocked
- misaligned_suspected
- interference
- overtemperature
- communication_fault
- timing_fault
- calibration_invalid
- offline

Radar-specific reasons may be carried in quality or lifecycle evidence, for example suspected multipath, surface contamination, or installation blockage.

## Sensor lifecycle

Lifecycle evidence reports state changes such as:

`discovered -> online -> calibration_loaded -> ready`

and degraded conditions such as:

- degraded
- blocked
- calibration_invalid
- offline
- recovered

Lifecycle events are read-only evidence. A state change may influence higher-level policy, but the lifecycle event itself cannot command hardware.

## Sensor disagreement

A disagreement event records that two or more sensors produced materially different observations for an associated property. It carries the sources, observed values, severity, optional numeric difference, and optional association identifier.

The contract deliberately sets `fault_assignment` to null. A disagreement is evidence that requires investigation; it does not declare one sensor wrong. Possible causes include timing skew, bad association, calibration error, occlusion, multipath, depth-estimation error, blockage, or genuine ambiguity.

## Sensor capabilities

Capability declarations let consumers subscribe to normalized measurements and outputs rather than hardware models. Examples include:

Measurements:

- range
- radial_velocity
- azimuth
- elevation
- presence
- temperature

Outputs:

- detections
- local_tracks
- health
- diagnostic_maps

Diagnostics and timing support are declared independently, for example raw capture, self-test, hardware timestamping, and external synchronization.

## Authority boundary

The commissioning ladder in the common sensor envelope remains:

`observe -> trust -> advise -> authorize`

`authorize` means the evidence is mature enough for an approved use profile. It does not turn the sensor into an executor. Consumers and Court remain responsible for any later decision that could lead to actuation.

## Integration order

1. Publish normalized sensor evidence.
2. Validate timing, mounting, calibration, health, and uncertainty.
3. Compare independent sensors and record disagreements.
4. Advance commissioning per use profile only after evidence supports the change.
5. Add sensor-fabric runtime routing only after the message contracts are stable.
