"""Thread-safe SQLite persistence for the local simulation lab."""

from __future__ import annotations

import sqlite3
import threading
import uuid
from pathlib import Path
from typing import Any

from .models import CheckIn, TelemetryEvent, utc_now


class Storage:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        with self._lock, self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    hostname TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    username TEXT NOT NULL,
                    last_seen TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS commands (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    argument TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    result TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                );
                """
            )

    def upsert_agent(self, checkin: CheckIn) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO agents (id, hostname, platform, username, last_seen)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET hostname=excluded.hostname,
                    platform=excluded.platform, username=excluded.username,
                    last_seen=excluded.last_seen
                """,
                (
                    checkin.agent_id,
                    checkin.hostname,
                    checkin.platform,
                    checkin.username,
                    checkin.timestamp,
                ),
            )

    def list_agents(self) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM agents ORDER BY last_seen DESC")

    def save_event(self, event: TelemetryEvent) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                "INSERT INTO telemetry (agent_id, category, content, timestamp) VALUES (?, ?, ?, ?)",
                (event.agent_id, event.category, event.content, event.timestamp),
            )

    def list_events(self, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 500))
        return self._rows(
            "SELECT * FROM telemetry ORDER BY id DESC LIMIT ?",
            (limit,),
        )

    def queue_command(self, agent_id: str, name: str, argument: str = "") -> str:
        command_id = uuid.uuid4().hex[:12]
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO commands (id, agent_id, name, argument, status, created_at)
                VALUES (?, ?, ?, ?, 'pending', ?)
                """,
                (command_id, agent_id, name, argument, utc_now()),
            )
        return command_id

    def claim_command(self, agent_id: str) -> dict[str, Any] | None:
        with self._lock, self._connection:
            row = self._connection.execute(
                """
                SELECT * FROM commands
                WHERE agent_id = ? AND status = 'pending'
                ORDER BY created_at LIMIT 1
                """,
                (agent_id,),
            ).fetchone()
            if row is None:
                return None
            self._connection.execute(
                "UPDATE commands SET status = 'claimed' WHERE id = ? AND status = 'pending'",
                (row["id"],),
            )
            self._connection.commit()
            return dict(row)

    def complete_command(self, command_id: str, result: str) -> bool:
        with self._lock, self._connection:
            cursor = self._connection.execute(
                """
                UPDATE commands SET status = 'completed', result = ?, completed_at = ?
                WHERE id = ? AND status = 'claimed'
                """,
                (result[:4096], utc_now(), command_id),
            )
            return cursor.rowcount == 1

    def list_commands(self, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 500))
        return self._rows("SELECT * FROM commands ORDER BY created_at DESC LIMIT ?", (limit,))

    def _rows(self, query: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(row) for row in self._connection.execute(query, parameters).fetchall()]

    def close(self) -> None:
        with self._lock:
            self._connection.close()

