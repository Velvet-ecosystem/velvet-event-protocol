# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class MemoryReference:
    event_id: str
    kind: str
    status: str
    confidence: Optional[float] = None
    receipt_id: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        _text(self.event_id, "event_id")
        _text(self.kind, "kind")
        _text(self.status, "status")
        if self.confidence is not None:
            _unit(self.confidence, "confidence")
        if self.receipt_id is not None:
            _text(self.receipt_id, "receipt_id")

        payload = {
            "event_id": self.event_id,
            "kind": self.kind,
            "status": self.status,
            "read_only": True,
        }
        if self.confidence is not None:
            payload["confidence"] = float(self.confidence)
        if self.receipt_id is not None:
            payload["receipt_id"] = self.receipt_id
        return payload


def _unit(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("{} must be numeric".format(name))
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError("{} must be between 0 and 1".format(name))


def _text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))
