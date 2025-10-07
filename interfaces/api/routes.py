"""REST API endpoints exposing task orchestration."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from application.services import ProgressQueryService, TaskCommandService

router = APIRouter(prefix="/tasks", tags=["tasks"])

_task_service = TaskCommandService()
_progress_service = ProgressQueryService(_task_service)


def get_task_service() -> TaskCommandService:
    return _task_service


def get_progress_service() -> ProgressQueryService:
    return _progress_service


class TaskRequest(BaseModel):
    text: str


@router.post("/process", status_code=status.HTTP_202_ACCEPTED)
def start_process_task(
    payload: TaskRequest,
    task_service: TaskCommandService = Depends(get_task_service),
) -> dict[str, str]:
    """Start the long-running text processing workflow."""
    try:
        task_id = task_service.start_text_processing(payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"task_id": task_id}


@router.post("/quick-analysis", status_code=status.HTTP_202_ACCEPTED)
def start_quick_analysis(
    payload: TaskRequest,
    task_service: TaskCommandService = Depends(get_task_service),
) -> dict[str, str]:
    """Start the quick analysis workflow."""
    try:
        task_id = task_service.start_quick_analysis(payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"task_id": task_id}


@router.get("/{task_id}/status")
def get_task_status(
    task_id: str,
    progress_service: ProgressQueryService = Depends(get_progress_service),
) -> dict[str, str | int]:
    """Retrieve task progress status."""
    return progress_service.get_progress_update(task_id)


@router.get("/{task_id}/result")
def get_task_result(
    task_id: str,
    progress_service: ProgressQueryService = Depends(get_progress_service),
) -> dict[str, str | int]:
    """Retrieve task result details."""
    return progress_service.get_task_output(task_id)


# TODO: Introduce WebSocket endpoints that push task progress updates to clients,
# enabling streaming updates per the PostTagger reimagined specification.
