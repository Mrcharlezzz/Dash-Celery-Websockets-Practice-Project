"""Celery integration package."""

from __future__ import annotations

from .app import get_celery_application

__all__ = ["get_celery_application"]
