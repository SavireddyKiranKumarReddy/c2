# Architecture

The code follows a small ports-and-adapters style without adding runtime dependencies:

- `SimulationAgent` owns protocol communication and produces explicit synthetic events.
- Protocol dataclasses validate untrusted JSON at the boundary.
- `SimulationServer` handles authentication, routing, size limits, and HTTP responses.
- `Storage` owns all SQL and serializes access to one SQLite connection.
- `commands.py` is the only command execution boundary. Its dictionary is an explicit allowlist.
- The dashboard escapes all values before inserting them into generated HTML.

Root-level Python files are compatibility launchers. New code should import the package from
`src/windows_manager_sim` or use the installed console scripts.

## Request flow

1. The agent submits an authenticated check-in.
2. The server updates the agent record and atomically claims one pending safe command.
3. The agent dispatches the command through the in-process allowlist.
4. The result is authenticated and stored.
5. Synthetic telemetry is stored separately and displayed by the dashboard.

