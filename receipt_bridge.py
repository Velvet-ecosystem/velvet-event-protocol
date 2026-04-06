import json
from typing import Callable


def make_receipt_validator(receipt_log_path: str) -> Callable[[str], bool]:
    """
    Returns a validator function that checks whether a receipt_id
    exists in the given JSONL receipt log.

    Policy:
    - missing file returns False
    - malformed lines are skipped
    - any matching receipt_id returns True
    """

    def validate(receipt_id: str) -> bool:
        if not receipt_id:
            return False

        try:
            with open(receipt_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if entry.get("receipt_id") == receipt_id:
                        return True

        except FileNotFoundError:
            return False
        except OSError:
            return False

        return False

    return validate


# from event_bus import EventBus
# from event_enforcer import EventEnforcer
# from receipt_bridge import make_receipt_validator
#
# bus = EventBus()
# validator = make_receipt_validator("receipts.log")
# enforcer = EventEnforcer(
#     bus.publish,
#     receipt_validator=validator,
#     allowed_actuation_sources={"core"},
# )
