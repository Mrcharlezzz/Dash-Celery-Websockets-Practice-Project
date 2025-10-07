"""Central logging configuration helpers."""

from __future__ import annotations

import logging


def configure_logging() -> None:
    """Configure root logging once for the application."""
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
