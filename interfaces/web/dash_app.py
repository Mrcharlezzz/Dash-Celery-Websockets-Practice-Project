"""Dash application consuming the HTTP API layer."""

from __future__ import annotations

import os
from typing import Any

import requests
from dash import Dash, Input, Output, State, ctx, dcc, html

from logging_config import configure_logging

DASH_HOST = os.getenv("DASH_HOST", "0.0.0.0")
DASH_PORT = int(os.getenv("DASH_PORT", "8050"))
DASH_DEBUG = os.getenv("DASH_DEBUG", "0") in {"1", "true", "True"}
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")


class DashApplication:
    """Dash application wired to the backend API."""

    def __init__(self) -> None:
        self.app: Dash = Dash(__name__)
        self.api_base_url = API_BASE_URL.rstrip("/")
        self.tasks_base_url = f"{self.api_base_url}/tasks"
        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self) -> None:
        """Configure the root layout."""
        self.app.layout = html.Div(
            [
                html.H1(
                    "Text Processor with Celery + Redis",
                    style={"textAlign": "center", "color": "#2c3e50"},
                ),
                html.Div(
                    [
                        dcc.Textarea(
                            id="text-input",
                            placeholder="Enter text to process...",
                            style={"width": "100%", "height": 100, "margin": "10px 0"},
                        ),
                        html.Button(
                            "Start Processing",
                            id="process-btn",
                            n_clicks=0,
                            style={
                                "backgroundColor": "#3498db",
                                "color": "white",
                            },
                        ),
                        html.Button(
                            "Quick Analysis",
                            id="quick-btn",
                            n_clicks=0,
                            style={
                                "backgroundColor": "#2ecc71",
                                "color": "white",
                                "marginLeft": "10px",
                            },
                        ),
                    ]
                ),
                html.Div(
                    id="task-id-display",
                    style={"margin": "10px 0", "fontSize": "12px"},
                ),
                html.Div(id="progress-container", style={"margin": "20px 0"}),
                html.Div(id="processing-result", style={"marginTop": "20px"}),
                # TODO: Replace polling interval with WebSocket-driven updates once backend streaming is available.
                dcc.Interval(id="progress-interval", interval=1000, n_intervals=0),
            ]
        )

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(f"{self.tasks_base_url}{path}", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def _get(self, path: str) -> dict[str, Any]:
        response = requests.get(f"{self.tasks_base_url}{path}", timeout=10)
        if response.status_code == 404:
            return {"state": "NOT_FOUND", "status": "Task not found", "progress": 0}
        response.raise_for_status()
        return response.json()

    def _setup_callbacks(self) -> None:
        """Wire Dash callbacks for task orchestration."""

        @self.app.callback(
            Output("task-id-display", "children"),
            Output("task-id-display", "style"),
            Input("process-btn", "n_clicks"),
            Input("quick-btn", "n_clicks"),
            State("text-input", "value"),
            prevent_initial_call=True,
        )
        def start_task(
            _process_clicks: int,
            _quick_clicks: int,
            text: str | None,
        ) -> tuple[str, dict[str, str]]:
            """Handle task start requests."""
            if not ctx.triggered_id or not text:
                return "Please enter text first!", {"color": "red"}

            button_id = ctx.triggered_id
            endpoint = "/process" if button_id == "process-btn" else "/quick-analysis"

            try:
                response = self._post(endpoint, {"text": text})
                task_id = response["task_id"]
                color = "#3498db" if button_id == "process-btn" else "#2ecc71"
                message = f"Task ID: {task_id}"
                return message, {
                    "color": color,
                    "fontFamily": "monospace",
                    "fontSize": "12px",
                }
            except requests.HTTPError as exc:
                detail = exc.response.json().get("detail", str(exc)) if exc.response else str(exc)
                return f"Error: {detail}", {"color": "red"}
            except requests.RequestException as exc:  # noqa: BLE001 - surface network errors
                return f"Network error: {exc}", {"color": "red"}

        @self.app.callback(
            Output("progress-container", "children"),
            Input("progress-interval", "n_intervals"),
            State("task-id-display", "children"),
        )
        def update_progress(
            _n_intervals: int,
            task_display: str | None,
        ) -> html.Div | str:
            """Update progress display."""
            if not task_display or "Task ID:" not in task_display:
                return ""

            task_id = task_display.split("Task ID: ")[1]
            progress_data = self._get(f"/{task_id}/status")

            if progress_data.get("state") == "PROGRESS":
                return html.Div(
                    [
                        html.Div(
                            f"Progress: {progress_data['progress']}% - {progress_data['status']}",
                            style={"marginBottom": "10px"},
                        ),
                        html.Progress(
                            value=progress_data["progress"],
                            max=100,
                            style={"width": "100%", "height": "20px"},
                        ),
                    ]
                )

            color = "#27ae60" if progress_data.get("state") == "SUCCESS" else "#f39c12"
            return html.Div(
                progress_data.get("status", "Awaiting status"),
                style={"color": color, "fontWeight": "bold"},
            )

        @self.app.callback(
            Output("processing-result", "children"),
            Input("progress-interval", "n_intervals"),
            State("task-id-display", "children"),
            prevent_initial_call=True,
        )
        def display_results(
            _n_intervals: int,
            task_display: str | None,
        ) -> html.Div | str:
            """Display task results once available."""
            if not task_display or "Task ID:" not in task_display:
                return ""

            task_id = task_display.split("Task ID: ")[1]
            result_payload = self._get(f"/{task_id}/result")

            if result_payload.get("state") != "SUCCESS":
                return ""

            result_data = result_payload.get("result", {})
            return html.Div(
                [
                    html.H3("🎉 Processing Complete!"),
                    html.Pre(
                        result_data.get("processed_text", "Analysis complete"),
                        style={
                            "background": "#f8f9fa",
                            "padding": "10px",
                            "borderRadius": "5px",
                        },
                    ),
                    html.P(f"Word count: {result_data.get('word_count')}") if "word_count" in result_data else "",
                    html.P(f"Character count: {result_data.get('char_count')}") if "char_count" in result_data else "",
                ]
            )

    def run(self, *, debug: bool = True) -> None:
        """Run the Dash development server."""
        self.app.run(host=DASH_HOST, port=DASH_PORT, debug=debug)


def main() -> None:
    """Entry point for running the Dash app."""
    configure_logging()
    DashApplication().run(debug=DASH_DEBUG)


if __name__ == "__main__":
    main()
