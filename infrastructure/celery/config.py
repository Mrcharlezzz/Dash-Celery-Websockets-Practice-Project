"""Celery configuration using a class-based approach."""

from __future__ import annotations

import os
from typing import Any


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class CeleryConfig:
    """Configuration class for Celery application."""

    def __init__(self) -> None:
        self.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        self.result_backend = os.getenv(
            "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
        )
        default_include = "infrastructure.celery.tasks"
        self.include_modules = [
            module.strip()
            for module in os.getenv("CELERY_INCLUDE", default_include).split(",")
            if module.strip()
        ]

    @property
    def config_dict(self) -> dict[str, Any]:
        """Return configuration as a dictionary."""
        return {
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": os.getenv("CELERY_TIMEZONE", "UTC"),
            "enable_utc": _bool_env("CELERY_ENABLE_UTC", True),
            "broker_transport_options": {
                "visibility_timeout": _int_env("CELERY_BROKER_VISIBILITY_TIMEOUT", 3600)
            },
            "result_backend_transport_options": {
                "visibility_timeout": _int_env("CELERY_RESULT_VISIBILITY_TIMEOUT", 3600)
            },
        }
