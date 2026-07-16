"""Environment-backed application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings shared by the server and simulation agent."""

    token: str
    host: str = "127.0.0.1"
    port: int = 8443
    database: Path = Path("runtime/simulation.sqlite3")

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("WM_SIM_TOKEN", "").strip()
        if len(token) < 16:
            raise ValueError("WM_SIM_TOKEN must contain at least 16 characters")

        port_text = os.getenv("WM_SIM_PORT", "8443")
        try:
            port = int(port_text)
        except ValueError as exc:
            raise ValueError("WM_SIM_PORT must be an integer") from exc
        if not 1 <= port <= 65535:
            raise ValueError("WM_SIM_PORT must be between 1 and 65535")

        return cls(
            token=token,
            host=os.getenv("WM_SIM_HOST", "127.0.0.1"),
            port=port,
            database=Path(os.getenv("WM_SIM_DATABASE", "runtime/simulation.sqlite3")),
        )

