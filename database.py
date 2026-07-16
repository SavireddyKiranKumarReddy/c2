"""Compatibility export for the local SQLite simulation storage."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from windows_manager_sim.storage import Storage  # noqa: E402,F401

__all__ = ["Storage"]

