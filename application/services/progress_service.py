"""Progress queries aggregating domain formatting."""

from __future__ import annotations

import logging
from typing import Any

from domain.progress import NOT_FOUND_STATE, build_progress_state

from .task_service import TaskCommandService

logger = logging.getLogger(__name__)


class ProgressQueryService:
    """Read model exposing task progress and results."""

    def __init__(self, task_service: TaskCommandService | None = None) -> None:
        self._task_service = task_service or TaskCommandService()

    def get_progress_update(self, task_id: str) -> dict[str, Any]:
        """Return the progress payload for the given task."""
        task_result = self._task_service.get_task_result(task_id)
        if not task_result:
            return {**NOT_FOUND_STATE}
        return build_progress_state(task_result.state, task_result.info)

    def get_task_output(self, task_id: str) -> dict[str, Any]:
        """Return task completion payload along with result data if available."""
        task_result = self._task_service.get_task_result(task_id)
        if not task_result:
            return {**NOT_FOUND_STATE}

        payload = build_progress_state(task_result.state, task_result.info)
        if payload["state"] != "SUCCESS":
            return payload

        try:
            payload["result"] = task_result.get()
        except Exception as exc:
            logger.error(
                "Failed to fetch task result for task_id=%s: %s",
                task_id,
                str(exc),
                exc_info=True,
            )
            payload["state"] = "ERROR"
            payload["progress"] = 0
            payload["status"] = f"Failed to load result: {exc}"
        return payload
