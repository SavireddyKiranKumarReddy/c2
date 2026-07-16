import os
import unittest
from pathlib import Path
from unittest.mock import patch

from windows_manager_sim.config import Settings


class ConfigTests(unittest.TestCase):
    def test_settings_from_environment(self) -> None:
        environment = {
            "WM_SIM_TOKEN": "a-secure-test-token",
            "WM_SIM_PORT": "9000",
            "WM_SIM_DATABASE": "tmp/test.sqlite3",
        }
        with patch.dict(os.environ, environment, clear=True):
            settings = Settings.from_env()
        self.assertEqual(settings.port, 9000)
        self.assertEqual(settings.database, Path("tmp/test.sqlite3"))

    def test_short_token_is_rejected(self) -> None:
        with patch.dict(os.environ, {"WM_SIM_TOKEN": "short"}, clear=True):
            with self.assertRaisesRegex(ValueError, "at least 16"):
                Settings.from_env()


if __name__ == "__main__":
    unittest.main()

