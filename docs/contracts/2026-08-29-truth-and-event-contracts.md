# Truth and event contract set

Date: 2026-08-29
Status: contract draft
Owner repo: velvet-event-protocol

## Purpose

These contracts define how Velvet preserves sensor truth, clock truth, trust aging, contradiction evidence, and event escalation before higher-level reasoning turns observations into decisions.

Event Protocol should preserve what the body actually sensed. Fusion and reasoning may derive cleaner interpretations, but they must not overwrite raw timing, provenance, confidence, or uncertainty.

## 1. Time Integrity Contract

Every node that emits events should report time health separately from ordinary module health.

Required fields:

```yaml
clock_source: gnss | rtc | monotonic | network_sync | supervisor | unknown
source_clock_id: string
expected_frequency_hz: number | null
measured_frequency_hz: number | null
frequency_deviation_ppm: number | null
monotonic_clock_ok: boolean
sync_source_available: boolean
timestamp_confidence: 0.0-1.0
drift_suspected: boolean
throttling_suspected: boolean
oscillator_fault_suspected: boolean
last_sync_timestamp: string | null
receipt_id: string | null
```

Rule: an organ can be online while its time is degraded. Any fusion, receipt, CAN interpretation, audio alignment, or replay that uses degraded time must carry that confidence forward.

## 2. Holdover Contract

When preferred time sync disappears, the node reports how long its time remains trustworthy.

Required fields:

```yaml
preferred_time_source: string
holdover_source: rtc | local_oscillator | monotonic | supervisor | none
holdover_started_at: string | null
estimated_drift_ppm: number | null
holdover_confidence: 0.0-1.0
confidence_decay_model: fixed | measured | unknown
max_trusted_holdover_ms: integer | null
holdover_expired: boolean
```

Rule: `time_source_available=false` does not mean time is immediately worthless. It means confidence must begin decaying honestly.

## 3. Asynchronous Sensor Truth Contract

Sensors keep native timing first. Synchronized observations are derived products.

Canonical path:

```text
native sample -> normalized packet -> optional synchronized observation -> belief/world state
```

Required packet additions:

```yaml
native_timestamp: string
source_clock_id: string
source_clock_confidence: 0.0-1.0
capture_rate_hz: number | null
native_sequence_id: string | null
normalized_timestamp: string
normalization_method: passthrough | converted | estimated | interpolated
interpolation_used: boolean
raw_packet_reference: string | null
derived_from_packet_ids: [string]
```

Rules:

- Do not silently invent synchronized timestamps.
- Fusion may request a synchronized view, but raw events keep original timing.
- Any interpolation, resampling, or dropped sample is recorded.
- Replay must support native timing and synchronized timing.

## 4. Sensor Trust Aging Contract

A sensor answering is not proof that the sensor deserves full belief.

Suggested fields:

```yaml
sensor_id: string
installed_at: string | null
operating_hours: number | null
thermal_cycles: integer | null
fault_exposure_count: integer | null
calibration_version: string | null
calibration_age_hours: number | null
signal_quality: 0.0-1.0
service_life_confidence: 0.0-1.0
current_trust: 0.0-1.0
trust_derating_reason: string | null
replacement_recommended: boolean
```

Trust should combine:

```text
online status + current signal quality + calibration validity + environmental stress + accumulated service history
```

## 5. Health Trend Contract

Health is not only a snapshot. Velvet should know whether an organ is improving, stable, or slowly degrading.

Suggested fields:

```yaml
module_id: string
current_state: online | ready | degraded | failed | offline | unknown
new_faults_window: integer
resolved_faults_window: integer
recurring_faults_window: integer
net_health_direction: improving | stable | worsening | unknown
trend_window_hours: integer
recurring_offender: boolean
trend_reason: string | null
```

## 6. Telemetry Reconciliation Contract

Some measurements should agree. When they do not, the contradiction is itself an event.

Examples:

```text
branch current sum <-> supply current
network packets sent <-> packets received
camera frames generated <-> frames processed
storage writes reported <-> filesystem growth
node uptime <-> heartbeat history
```

Suggested event fields:

```yaml
reconciliation_id: string
left_measurement: string
right_measurement: string
expected_relation: equals | sum_equals | within_tolerance | monotonic | custom
observed_left: any
observed_right: any
tolerance: any
confidence: 0.0-1.0
contradiction_detected: boolean
likely_fault_domain: sensor | transport | storage | clock | software | unknown
receipt_id: string
```

## 7. Sensor Escalation Contract

Sensors may operate in energy modes rather than roaring at full rate all the time.

Modes:

```text
sentinel -> normal -> diagnostic -> evidence capture -> central escalation -> return to sentinel
```

Suggested fields:

```yaml
sensor_id: string
energy_mode: sentinel | normal | diagnostic
escalation_reason: string | null
sample_rate_hz: number
local_threshold_crossed: boolean
corroborating_sources: [string]
evidence_capture_started: boolean
return_to_sentinel_condition: string
```

## 8. Distributed Measurement Cluster Pattern

A cluster is a local monitor that validates nearby sensors before central escalation.

Pattern:

```text
sensors -> local monitor -> validated summary + raw-on-demand -> central organ
```

Use cases:

- seat clusters
- camera pods
- power distribution
- engine sensing
- Home rooms
- workshop machines

Cluster summary should include:

```yaml
cluster_id: string
local_monitor_id: string
sensor_ids: [string]
summary_confidence: 0.0-1.0
raw_available_on_demand: boolean
local_sanity_checks_passed: boolean
degraded_sources: [string]
escalation_required: boolean
```

## 9. Event Evidence Trigger Link

Event Protocol should allow receipts to request bounded evidence capture when an anomaly occurs.

Suggested trigger fields:

```yaml
trigger_condition: string
trigger_confidence: 0.0-1.0
pre_buffer_ms: integer
post_buffer_ms: integer
raw_sources_requested: [string]
derived_state_requested: [string]
privacy_class: public | internal | private | sensitive
storage_budget_bytes: integer | null
reason: string
receipt_id: string
```

## Non-authority rule

These events describe truth, uncertainty, contradiction, and escalation. They do not grant physical control. Any action remains gated by Runtime and Court.
