# SPDX-License-Identifier: GPL-3.0-only

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MemoryRecallResult:
    event_id: str
    score: float
    association: float
    confidence: float
    salience: float
    status_weight: float

    def to_payload(self) -> Dict[str, float]:
        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise ValueError("event_id must be a non-empty string")
        values = {
            "score": self.score,
            "association": self.association,
            "confidence": self.confidence,
            "salience": self.salience,
            "status_weight": self.status_weight,
        }
        for name, value in values.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("{} must be numeric".format(name))
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError("{} must be between 0 and 1".format(name))
        payload = {name: float(value) for name, value in values.items()}
        payload["event_id"] = self.event_id
        return payload
