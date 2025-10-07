"""Celery tasks binding domain workflows to asynchronous execution."""

from __future__ import annotations

import logging
import time
from typing import Any

from domain.text_processing import TextProcessor, iterate_processing_chunks
from infrastructure.celery.app import get_celery_application
from models.task_models import ProgressUpdate, TextProcessingResult

logger = logging.getLogger(__name__)

celery_app = get_celery_application()


@celery_app.task(bind=True)
def process_text_task(self, text: str) -> dict[str, Any]:
    """Main text processing task."""
    logger.debug("Starting text processing task with text length: %s", len(text))
    processor = TextProcessor()
    results: list[str] = []

    for step, processed_chunk in iterate_processing_chunks(text, processor):
        time.sleep(2)  # Simulate processing

        logger.debug(
            "Processing step %s/%s: %s",
            step.index,
            step.total_steps,
            step.description,
        )
        progress_update = ProgressUpdate(
            current=step.index,
            total=step.total_steps,
            progress=step.progress,
            status=f"{step.description}: {step.progress}%",
        )
        self.update_state(
            state="PROGRESS",
            meta=progress_update.model_dump(),
        )

        results.append(processed_chunk)

    logger.debug("Text processing task completed successfully")
    result = TextProcessingResult(
        task_id=self.request.id or "",
        status="SUCCESS",
        processed_text="\n".join(results),
        original_text=text,
        word_count=len(text.split()),
        char_count=len(text),
        steps_completed=len(results),
    )
    return result.model_dump()


@celery_app.task
def quick_analysis_task(text: str) -> dict[str, Any]:
    """Quick analysis task."""
    return {
        "word_count": len(text.split()),
        "char_count": len(text),
        "contains_letters": any(c.isalpha() for c in text),
        "analysis_type": "quick",
    }
