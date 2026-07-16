import json
import unittest

from windows_manager_sim.commands import execute


class CommandTests(unittest.TestCase):
    def test_allowlisted_commands(self) -> None:
        self.assertEqual(execute("ping"), "pong")
        self.assertEqual(execute("echo", "hello"), "hello")
        self.assertIn("python", json.loads(execute("system_info")))

    def test_unknown_command_is_not_executed(self) -> None:
        self.assertEqual(execute("whoami"), "unsupported command: whoami")


if __name__ == "__main__":
    unittest.main()

