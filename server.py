#!/usr/bin/env python3
"""Compatibility launcher for the local simulation server."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from windows_manager_sim.cli import server_main  # noqa: E402


if __name__ == "__main__":
    server_main()

