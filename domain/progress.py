"""Domain helpers for progress tracking semantics."""

from __future__ import annotations

from typing import Any

from models.task_models import ProgressUpdate

NOT_FOUND_STATE: dict[str, Any] = {
    "state": "NOT_FOUND",
    "progress": 0,
    "status": "Task not found",
}


def build_progress_state(state: str, info: Any) -> dict[str, Any]:
    """Return a normalized progress payload for the given task state."""
    normalized_state = state or "PENDING"

    if normalized_state == "PROGRESS":
        progress_meta = info or {}
        progress_update = ProgressUpdate(
            current=int(progress_meta.get("current", 0)),
            total=int(progress_meta.get("total", 1)),
            progress=int(progress_meta.get("progress", 0)),
            status=str(progress_meta.get("status", "Processing...")),
        )
        return {
            "state": normalized_state,
            **progress_update.model_dump(),
        }

    if normalized_state == "PENDING":
        return {
            "state": normalized_state,
            "progress": 0,
            "status": "Task is pending...",
        }

    if normalized_state == "SUCCESS":
        return {
            "state": normalized_state,
            "progress": 100,
            "status": "Task completed!",
        }

    if normalized_state == "FAILURE":
        failure_info = str(info) if info is not None else "Unknown reason"
        return {
            "state": normalized_state,
            "progress": 0,
            "status": f"Task failed: {failure_info}",
        }

    return {
        "state": normalized_state,
        "progress": 0,
        "status": f"State: {normalized_state}",
    }
