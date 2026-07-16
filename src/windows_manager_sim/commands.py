"""Safe, deterministic commands supported by simulation agents."""

from __future__ import annotations

import json
import platform
import socket
from collections.abc import Callable


def _ping(_: str) -> str:
    return "pong"


def _system_info(_: str) -> str:
    return json.dumps(
        {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        sort_keys=True,
    )


def _echo(argument: str) -> str:
    return argument[:1000]


COMMANDS: dict[str, Callable[[str], str]] = {
    "ping": _ping,
    "system_info": _system_info,
    "echo": _echo,
}


def execute(name: str, argument: str = "") -> str:
    """Execute an allowlisted in-process simulation command."""
    command = COMMANDS.get(name)
    if command is None:
        return f"unsupported command: {name}"
    return command(argument)

