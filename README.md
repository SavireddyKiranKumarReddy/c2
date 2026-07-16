# Windows Manager Simulation

A consent-based endpoint telemetry lab for learning agent/server architecture. The project sends
synthetic events to an authenticated local API and supports three safe, in-process commands. It
does **not** capture keyboard input, install persistence, disguise processes, or execute a shell.

## Architecture

```text
SimulationAgent -> authenticated localhost HTTP API -> SQLite -> browser dashboard
                       |                              |
                       +-- allowlisted commands -----+
```

## Repository layout

```text
.
|-- src/windows_manager_sim/
|   |-- client.py       # Synthetic agent
|   |-- server.py       # Authenticated HTTP API
|   |-- storage.py      # Thread-safe SQLite repository
|   |-- commands.py     # Safe command allowlist
|   |-- models.py       # Input validation
|   `-- dashboard.py    # Local dashboard
|-- tests/              # Unit and integration tests
|-- docs/               # Design and security documentation
|-- agent.py            # Compatibility agent launcher
|-- server.py           # Compatibility server launcher
|-- pyproject.toml      # Packaging and tool configuration
`-- .env.example        # Configuration reference
```

## Quick start

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
$env:WM_SIM_TOKEN = "replace-with-a-long-random-development-token"
wm-sim-server
```

In another terminal:

```powershell
$env:WM_SIM_TOKEN = "replace-with-a-long-random-development-token"
wm-sim-agent --once --agent-id demo-workstation
```

Open `http://127.0.0.1:8443`, enter the same token, and select **Refresh**.

The compatibility commands also work from a source checkout:

```powershell
python server.py
python agent.py --once --agent-id demo-workstation
```

## Safe commands

| Command | Behavior |
|---|---|
| `ping` | Returns `pong` |
| `system_info` | Returns non-sensitive runtime metadata |
| `echo` | Returns at most 1,000 characters supplied by the operator |

Commands run as Python functions in the agent process. No command interpreter or subprocess is
used.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `WM_SIM_TOKEN` | none | Required shared token, minimum 16 characters |
| `WM_SIM_HOST` | `127.0.0.1` | API bind address |
| `WM_SIM_PORT` | `8443` | API port |
| `WM_SIM_DATABASE` | `runtime/simulation.sqlite3` | Local SQLite path |

The server intentionally defaults to loopback. If you expose it to another interface, place it
behind TLS and a production identity-aware reverse proxy.

## Quality checks

```powershell
python -m unittest discover -s tests
python -m ruff check .
```

See [docs/SECURITY.md](docs/SECURITY.md) for the threat model and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for design details.
