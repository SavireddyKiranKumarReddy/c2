"""Command-line entry points."""

from __future__ import annotations

import argparse

from .client import SimulationAgent
from .config import Settings
from .server import SimulationServer
from .storage import Storage


def server_main() -> None:
    parser = argparse.ArgumentParser(description="Run the local endpoint simulation server")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    settings = Settings.from_env()
    storage = Storage(settings.database)
    server = SimulationServer(args.host or settings.host, args.port or settings.port, settings.token, storage)
    try:
        server.start()
    except KeyboardInterrupt:
        print("Stopping simulation server")
    finally:
        server.stop()
        storage.close()


def agent_main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic endpoint telemetry agent")
    parser.add_argument("--server", default=None)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--agent-id", default="")
    args = parser.parse_args()
    settings = Settings.from_env()
    server_url = args.server or f"http://{settings.host}:{settings.port}"
    SimulationAgent(
        server_url=server_url,
        token=settings.token,
        interval=args.interval,
        agent_id=args.agent_id,
    ).run(once=args.once)

