"""Celery application class following a Singleton pattern."""

from __future__ import annotations

from celery import Celery

from infrastructure.celery.config import CeleryConfig
from logging_config import configure_logging


class CeleryApplication:
    """Singleton class for Celery application instance."""

    _instance: CeleryApplication | None = None

    def __new__(cls) -> CeleryApplication:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize Celery application."""
        configure_logging()

        config = CeleryConfig()

        self.app = Celery(
            "text_processor",
            broker=config.broker_url,
            backend=config.result_backend,
            include=config.include_modules,
        )

        self.app.config_from_object(config.config_dict)

    def get_app(self) -> Celery:
        """Get a Celery application instance."""
        return self.app


def get_celery_application() -> Celery:
    """Module-level accessor."""
    return CeleryApplication().get_app()
