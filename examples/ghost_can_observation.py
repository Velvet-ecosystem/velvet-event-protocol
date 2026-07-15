# SPDX-License-Identifier: GPL-3.0-only
"""Print a public-safe ghost CAN observation event."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from velvet_event_protocol import GhostCanObservation, build_ghost_can_observation_event


def main() -> None:
    event = build_ghost_can_observation_event(
        source="velvet-runtime",
        observation=GhostCanObservation(
            can_id="0x120",
            data_hex="0000000000000000",
            signals={"vehicle_speed_kph": 0, "ignition_state": "off"},
            timestamp=1.0,
        ),
    )
    print(json.dumps(event.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
