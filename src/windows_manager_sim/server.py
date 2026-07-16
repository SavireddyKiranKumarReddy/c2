"""Authenticated localhost HTTP API for the simulation lab."""

from __future__ import annotations

import hmac
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from .commands import COMMANDS
from .dashboard import DASHBOARD_HTML
from .models import CheckIn, TelemetryEvent, required_text
from .storage import Storage


class SimulationServer:
    def __init__(self, host: str, port: int, token: str, storage: Storage) -> None:
        self.host = host
        self.port = port
        self.token = token
        self.storage = storage
        self.httpd: ThreadingHTTPServer | None = None

    def _handler_class(self) -> type[BaseHTTPRequestHandler]:
        application = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "WindowsManagerSimulation/1.0"

            def _authorized(self) -> bool:
                supplied = self.headers.get("Authorization", "")
                expected = f"Bearer {application.token}"
                return hmac.compare_digest(supplied, expected)

            def _json(self, status: int, payload: Any) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def _body(self) -> dict[str, Any]:
                length = int(self.headers.get("Content-Length", "0"))
                if length > 16_384:
                    raise ValueError("request body exceeds 16 KiB")
                raw = self.rfile.read(length)
                data = json.loads(raw or b"{}")
                if not isinstance(data, dict):
                    raise ValueError("JSON body must be an object")
                return data

            def _require_auth(self) -> bool:
                if self._authorized():
                    return True
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "authentication required"})
                return False

            def do_GET(self) -> None:  # noqa: N802
                route = urlparse(self.path)
                if route.path == "/":
                    body = DASHBOARD_HTML.encode("utf-8")
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'")
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.end_headers()
                    self.wfile.write(body)
                    return
                if route.path == "/healthz":
                    self._json(HTTPStatus.OK, {"status": "ok", "mode": "simulation"})
                    return
                if not self._require_auth():
                    return
                params = parse_qs(route.query)
                limit = _parse_limit(params)
                routes = {
                    "/api/agents": lambda: application.storage.list_agents(),
                    "/api/telemetry": lambda: application.storage.list_events(limit),
                    "/api/commands": lambda: application.storage.list_commands(limit),
                }
                action = routes.get(route.path)
                if action is None:
                    self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                else:
                    self._json(HTTPStatus.OK, action())

            def do_POST(self) -> None:  # noqa: N802
                if not self._require_auth():
                    return
                route = urlparse(self.path).path
                try:
                    data = self._body()
                    if route == "/api/checkin":
                        checkin = CheckIn.from_dict(data)
                        application.storage.upsert_agent(checkin)
                        command = application.storage.claim_command(checkin.agent_id)
                        response = {"status": "ok"}
                        if command:
                            response["command"] = {
                                "id": command["id"],
                                "name": command["name"],
                                "argument": command["argument"],
                            }
                        self._json(HTTPStatus.OK, response)
                    elif route == "/api/telemetry":
                        application.storage.save_event(TelemetryEvent.from_dict(data))
                        self._json(HTTPStatus.CREATED, {"status": "stored"})
                    elif route == "/api/commands":
                        agent_id = required_text(data, "agent_id", 128)
                        name = required_text(data, "name", 64)
                        argument = str(data.get("argument", ""))[:1000]
                        if name not in COMMANDS:
                            raise ValueError("command is not allowlisted")
                        command_id = application.storage.queue_command(agent_id, name, argument)
                        self._json(HTTPStatus.CREATED, {"id": command_id, "status": "queued"})
                    elif route == "/api/result":
                        command_id = required_text(data, "id", 64)
                        result = required_text(data, "result", 4096)
                        if not application.storage.complete_command(command_id, result):
                            self._json(HTTPStatus.CONFLICT, {"error": "command is not claimable"})
                        else:
                            self._json(HTTPStatus.OK, {"status": "completed"})
                    else:
                        self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                except (ValueError, json.JSONDecodeError) as exc:
                    self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

            def log_message(self, message: str, *args: Any) -> None:
                print(f"[http] {self.address_string()} {message % args}")

        return Handler

    def start(self) -> None:
        self.httpd = ThreadingHTTPServer((self.host, self.port), self._handler_class())
        print(f"Simulation dashboard: http://{self.host}:{self.port}")
        print("Synthetic telemetry only; no keyboard capture or shell execution.")
        self.httpd.serve_forever()

    def stop(self) -> None:
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()


def _parse_limit(parameters: dict[str, list[str]]) -> int:
    try:
        return max(1, min(int(parameters.get("limit", ["100"])[0]), 500))
    except ValueError:
        return 100

