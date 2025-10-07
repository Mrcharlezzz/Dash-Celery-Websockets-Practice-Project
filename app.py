"""Backwards-compatible entry-point for deployment environments."""

from main import DashApplication, main

__all__ = ["DashApplication", "main"]


if __name__ == "__main__":
    main()
