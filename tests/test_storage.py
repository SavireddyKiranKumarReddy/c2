import tempfile
import unittest
from pathlib import Path

from windows_manager_sim.models import CheckIn, TelemetryEvent
from windows_manager_sim.storage import Storage


class StorageTests(unittest.TestCase):
    def test_agent_event_and_command_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = Storage(Path(directory) / "simulation.sqlite3")
            checkin = CheckIn(
                "agent-1", "host", "Windows-test", "student", "2026-01-01T00:00:00Z"
            )
            storage.upsert_agent(checkin)
            self.assertEqual(storage.list_agents()[0]["id"], "agent-1")

            storage.save_event(
                TelemetryEvent(
                    "agent-1", "simulation", "synthetic input", "2026-01-01T00:00:01Z"
                )
            )
            self.assertEqual(storage.list_events()[0]["content"], "synthetic input")

            command_id = storage.queue_command("agent-1", "ping")
            command = storage.claim_command("agent-1")
            self.assertIsNotNone(command)
            self.assertEqual(command["id"], command_id)
            self.assertIsNone(storage.claim_command("agent-1"))
            self.assertTrue(storage.complete_command(command_id, "pong"))
            self.assertEqual(storage.list_commands()[0]["status"], "completed")
            storage.close()


if __name__ == "__main__":
    unittest.main()

