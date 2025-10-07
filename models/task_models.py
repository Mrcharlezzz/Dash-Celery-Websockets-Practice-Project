"""Data Transfer Objects supporting Celery task orchestration."""

from __future__ import annotations

from pydantic import BaseModel


class TextProcessingResult(BaseModel):
    """DTO representing the aggregated text processing output."""

    task_id: str
    processed_text: str
    original_text: str
    word_count: int
    char_count: int
    steps_completed: int
    progress: int = 100
    error: str | None = None


class ProgressUpdate(BaseModel):
    """DTO describing progress metadata for long-running tasks."""

    current: int
    total: int
    progress: int
    status: str
