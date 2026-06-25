# SPDX-License-Identifier: GPL-3.0-only

from typing import Iterable

from event_schema import VelvetEvent
from memory_event_types import MEMORY_RECALL_RESULTS, MEMORY_REFERENCE_OBSERVED
from memory_recall_result import MemoryRecallResult
from memory_reference import MemoryReference


def build_memory_reference_event(source: str, reference: MemoryReference) -> VelvetEvent:
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")
    payload = reference.to_payload()
    payload["truth_claimed"] = False
    return VelvetEvent(
        source=source.strip(),
        event_type=MEMORY_REFERENCE_OBSERVED,
        payload=payload,
        metadata={"contract": "velvet.memory-reference.v1"},
        receipt_id=reference.receipt_id,
    )


def build_memory_recall_event(
    source: str,
    query_event_id: str,
    results: Iterable[MemoryRecallResult],
) -> VelvetEvent:
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")
    if not isinstance(query_event_id, str) or not query_event_id.strip():
        raise ValueError("query_event_id must be a non-empty string")
    rows = [result.to_payload() for result in results]
    return VelvetEvent(
        source=source.strip(),
        event_type=MEMORY_RECALL_RESULTS,
        payload={
            "query_event_id": query_event_id,
            "results": rows,
            "result_count": len(rows),
            "read_only": True,
            "truth_claimed": False,
        },
        metadata={"contract": "velvet.memory-recall-results.v1"},
    )
