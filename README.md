# Dash-Celery-Websockets-Practice-Project

Practice project inspired by JetBrains' PostTagger reimagined description. The codebase now follows a layered architecture with clear separation between the domain, application, infrastructure, and interface layers. A FastAPI backend exposes task orchestration APIs, a Dash frontend consumes those APIs, and Celery workers handle background jobs.

> **WebSockets roadmap:** the backend and frontend contain TODO markers where live progress streaming will be introduced next. Polling via Dash intervals remains the default until that iteration.

## Project structure

```
├── api_main.py                    # FastAPI entrypoint
├── application/                   # Application services (thin facades)
├── domain/                        # Pure business logic
├── infrastructure/celery/         # Celery app & task definitions
├── interfaces/
│   ├── api/                       # FastAPI routes
│   └── web/                       # Dash UI consuming the HTTP API
├── models/                        # Pydantic DTOs
├── requirements/                  # Shared dependency locks for containers
└── docker/                        # Service-specific Dockerfiles
```

## Running locally (without Docker)

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements/base.txt
   ```
2. Start Redis (required by Celery).
3. Run the backend API:
   ```bash
   uvicorn api_main:app --reload
   ```
4. In a separate terminal start the Celery worker:
   ```bash
   celery -A infrastructure.celery.tasks worker --loglevel=info
   ```
5. Launch the Dash frontend:
   ```bash
   python -m interfaces.web.dash_app
   ```

## Dockerised deployment

The repository includes a multi-service setup with isolated containers for the API, frontend, Celery worker, and Redis broker.

```bash
docker compose up --build
```

Published ports:
- `8000` – FastAPI backend
- `8050` – Dash frontend
- `6379` – Redis broker (exposed for local debugging)

The containers share a codebase snapshot. Adjust the `docker-compose.yml` file for production concerns such as mounting volumes, configuring secrets, or scaling workers.

## Environment configuration

Key variables (all optional with sensible defaults):
- `API_BASE_URL` – Base URL the Dash frontend uses to talk to the backend (`http://api:8000/api` in Docker, `http://localhost:8000/api` locally).
- `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` – Broker and result backend URLs.
- `DASH_HOST`, `DASH_PORT`, `DASH_DEBUG` – Override Dash server host, port, and debug flag.

## Next steps

- Implement the WebSocket channel alluded to in the PostTagger specification to broadcast task progress without polling.
- Add integration tests covering the FastAPI routes and Dash callbacks.
- Harden Docker images (non-root user, slimmer base image, separated dependency layers) once the architecture stabilises.
