#!/usr/bin/env python3
"""Deprecated compatibility launcher.

The former global keyboard hook has intentionally been replaced by explicit,
synthetic telemetry. Use ``python agent.py --once`` for a one-cycle demo.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from windows_manager_sim.cli import agent_main  # noqa: E402


if __name__ == "__main__":
    print("Simulation mode: no keyboard input is captured.")
    agent_main()

