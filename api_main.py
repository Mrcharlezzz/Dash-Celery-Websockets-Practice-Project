"""FastAPI entrypoint for backend services."""

from __future__ import annotations

from fastapi import FastAPI

from interfaces.api.routes import router as tasks_router
from logging_config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Text Processing Backend", version="0.1.0")
    app.include_router(tasks_router, prefix="/api")

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
