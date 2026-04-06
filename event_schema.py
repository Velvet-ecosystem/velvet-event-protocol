from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import uuid
import time


def generate_event_id() -> str:
    return str(uuid.uuid4())


def current_timestamp() -> float:
    return time.time()


@dataclass(frozen=True)
class VelvetEvent:
    event_id: str = field(default_factory=generate_event_id)
    timestamp: float = field(default_factory=current_timestamp)

    source: str = ""          # module or surface
    event_type: str = ""      # canonical type
    intent: Optional[str] = None

    payload: Dict[str, Any] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)

    # Optional linkage
    parent_event_id: Optional[str] = None
    receipt_id: Optional[str] = None  # filled AFTER authorization


    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "source": self.source,
            "event_type": self.event_type,
            "intent": self.intent,
            "payload": self.payload,
            "metadata": self.metadata,
            "parent_event_id": self.parent_event_id,
            "receipt_id": self.receipt_id,
        }
