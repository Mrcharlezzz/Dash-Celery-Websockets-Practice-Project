"""Task command/query services leveraging Celery workers."""

from __future__ import annotations

import logging

from celery.result import AsyncResult

from domain.text_processing import validate_text_input
from infrastructure.celery.app import get_celery_application
from infrastructure.celery.tasks import process_text_task, quick_analysis_task

logger = logging.getLogger(__name__)


class TaskCommandService:
    """Facade offering task orchestration commands."""

    def __init__(self):
        self._celery_app = get_celery_application()

    def start_text_processing(self, text: str) -> str:
        """Submit the long-running text processing workflow."""
        validated_text = validate_text_input(text)
        task = process_text_task.delay(validated_text)
        return task.id

    def start_quick_analysis(self, text: str) -> str:
        """Submit the quick analysis shortcut."""
        validated_text = validate_text_input(text)
        task = quick_analysis_task.delay(validated_text)
        return task.id

    def get_task_result(self, task_id: str) -> AsyncResult | None:
        """Access the raw Celery result."""
        try:
            return AsyncResult(task_id, app=self._celery_app)
        except Exception as exc:
            logger.error(
                "Failed to retrieve task result for task_id=%s: %s",
                task_id,
                str(exc),
                exc_info=True,
            )
            return None
