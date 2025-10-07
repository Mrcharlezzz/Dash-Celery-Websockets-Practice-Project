"""Main entry point delegating to the Dash web interface."""

from __future__ import annotations

from interfaces.web.dash_app import DashApplication, main as run_dash

__all__ = ["DashApplication", "run_dash", "main"]


def main() -> None:
    """CLI-style compatibility function."""
    run_dash()


if __name__ == "__main__":
    main()
