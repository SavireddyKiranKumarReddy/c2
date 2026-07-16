#!/usr/bin/env python3
"""Compatibility launcher for the consent-based simulation agent."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from windows_manager_sim.cli import agent_main  # noqa: E402


if __name__ == "__main__":
    agent_main()

