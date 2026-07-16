import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from windows_manager_sim.server import SimulationServer
from windows_manager_sim.storage import Storage


class ServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = Storage(Path(self.temp_dir.name) / "test.sqlite3")
        self.server = SimulationServer("127.0.0.1", 0, "integration-test-token", self.storage)
        handler = self.server._handler_class()
        from http.server import ThreadingHTTPServer

        self.server.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = self.server.httpd.server_address[1]
        self.thread = threading.Thread(target=self.server.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.stop()
        self.thread.join(timeout=2)
        self.storage.close()
        self.temp_dir.cleanup()

    def request(self, path: str, token: str | None = None, payload: dict | None = None):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        data = None
        method = "GET"
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode()
            method = "POST"
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=data, headers=headers, method=method
        )
        return urllib.request.urlopen(request, timeout=2)

    def test_health_is_public_but_data_requires_authentication(self) -> None:
        with self.request("/healthz") as response:
            self.assertEqual(response.status, 200)
        with self.assertRaises(urllib.error.HTTPError) as context:
            self.request("/api/agents")
        self.assertEqual(context.exception.code, 401)

    def test_checkin_and_safe_command_validation(self) -> None:
        token = "integration-test-token"
        checkin = {
            "agent_id": "agent-1",
            "hostname": "host",
            "platform": "test-platform",
            "username": "student",
            "timestamp": "2026-01-01T00:00:00Z",
        }
        with self.request("/api/checkin", token, checkin) as response:
            self.assertEqual(response.status, 200)
        with self.assertRaises(urllib.error.HTTPError) as context:
            self.request(
                "/api/commands",
                token,
                {"agent_id": "agent-1", "name": "whoami", "argument": ""},
            )
        self.assertEqual(context.exception.code, 400)


if __name__ == "__main__":
    unittest.main()

