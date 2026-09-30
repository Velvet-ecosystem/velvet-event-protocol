# Velvet Sensor Envelope Contract v0.1

Status: foundation contract.

## Purpose

The Sensor Envelope gives all Velvet sensors a shared outer message shape while keeping each sensor's measurement payload independent. It is intended for radar, cameras, IMUs, GNSS, cabin sensors, presence sensors, and future sensor families.

The contract is evidence-only. A sensor reports what it measured, when it measured it, its health, calibration references, quality, provenance, and current evidence-maturity profile. Consumers decide how to interpret that evidence.

## Common envelope

Each message carries:

- sensor identity and family
- sequence identifier
- measurement, monotonic, and receive timestamps when available
- clock synchronization state and estimated synchronization error
- reference frame, mount identifier, and calibration identifier
- sensor health state
- message quality and reasons
- per-use evidence maturity
- producer/firmware provenance
- sensor-specific payload type and payload data

## Evidence maturity

Each use profile advances independently through:

`observe -> trust -> advise -> authorize`

These states describe how mature the sensor evidence is for a named use. `authorize` means the evidence has passed the validation required for that use; it does not make the sensor an executor and does not turn a measurement message into a command.

Example profiles include security detection, camera assistance, navigation, road-world modelling, and parking assistance.

## Health and quality are separate

Health describes the sensor or link. Quality describes the current observation. A healthy sensor can produce a degraded observation because of glare, blockage, multipath, timing uncertainty, occlusion, or environmental conditions.

Suggested health states:

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
- unknown

Suggested quality states:

- valid
- degraded
- invalid
- unknown

## Time

Consumers should prefer measurement time over receive time. Where available, a sensor should also publish a monotonic timestamp, synchronization state, and synchronization uncertainty. This allows fusion code to distinguish real motion from late or skewed delivery.

## Coordinate frames

Sensors identify the frame in which their measurements are expressed and reference a mount/calibration record. A vehicle installation should maintain transforms from each sensor frame into the common vehicle-body frame rather than scattering mount offsets through consumer code.

## Confidence and uncertainty

Envelope-level confidence only describes broad message usability. It must not replace sensor-specific uncertainty. A radar payload may expose separate uncertainty for range, radial velocity, azimuth, and elevation. A camera payload may expose different quantities.

## Provenance

Messages should identify the adapter/driver and, when available, firmware or model version. This lets evidence consumers reconstruct which software and calibration produced an observation.

## Sensor-specific payloads

The shared envelope does not force all sensors into one measurement model. Payloads remain specialized, for example:

- radar_detection_frame
- radar_local_track
- camera_detection_frame
- imu_sample
- gnss_fix
- seat_presence
- cabin_environment

Consumers should subscribe to normalized measurements and capabilities rather than vendor-specific packet formats.

## Specialization contracts

The first specialization layer defines radar detections and local tracks, sensor lifecycle evidence, cross-sensor disagreement evidence, and sensor capability declarations. See `docs/radar_sensor_specialization_contracts.md`.
