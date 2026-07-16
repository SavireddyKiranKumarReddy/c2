"""Consent-based agent that emits synthetic telemetry only."""

from __future__ import annotations

import getpass
import json
import platform
import socket
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Any

from .commands import execute
from .models import utc_now


@dataclass(slots=True)
class SimulationAgent:
    server_url: str
    token: str
    interval: float = 5.0
    agent_id: str = ""

    def __post_init__(self) -> None:
        self.server_url = self.server_url.rstrip("/")
        if not self.agent_id:
            self.agent_id = f"sim-{socket.gethostname()}-{uuid.uuid4().hex[:6]}"
        if self.interval < 0.1:
            raise ValueError("interval must be at least 0.1 seconds")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            self.server_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def check_in(self) -> dict[str, Any]:
        response = self._post(
            "/api/checkin",
            {
                "agent_id": self.agent_id,
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "username": getpass.getuser(),
                "timestamp": utc_now(),
            },
        )
        command = response.get("command")
        if isinstance(command, dict):
            result = execute(str(command.get("name", "")), str(command.get("argument", "")))
            self._post(
                "/api/result",
                {
                    "id": command.get("id"),
                    "agent_id": self.agent_id,
                    "result": result,
                },
            )
        return response

    def send_simulation_event(self, content: str) -> dict[str, Any]:
        """Send explicit synthetic text; this never reads keyboard input."""
        return self._post(
            "/api/telemetry",
            {
                "agent_id": self.agent_id,
                "category": "simulation",
                "content": content,
                "timestamp": utc_now(),
            },
        )

    def run(self, once: bool = False) -> None:
        sequence = 0
        while True:
            try:
                self.check_in()
                self.send_simulation_event(f"synthetic event #{sequence}")
                sequence += 1
            except (OSError, urllib.error.URLError, ValueError) as exc:
                print(f"simulation agent connection error: {exc}")
            if once:
                return
            time.sleep(self.interval)

