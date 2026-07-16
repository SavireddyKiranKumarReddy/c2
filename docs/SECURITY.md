# Security policy and threat model

## Safety guarantees

The maintained source code must not:

- Capture global keyboard input or credentials.
- Create registry, scheduled-task, service, or Startup-folder persistence.
- Copy itself under a misleading system filename.
- Execute arbitrary command strings, shells, PowerShell, or subprocesses.
- Send data to a hard-coded external service.

## Controls

- Every API route except `/` and `/healthz` requires a bearer token.
- Tokens are compared with `hmac.compare_digest`.
- JSON request bodies are limited to 16 KiB and fields have explicit size limits.
- Commands are selected from a three-item allowlist.
- The service binds to `127.0.0.1` by default.
- Dashboard values are HTML-escaped before rendering.
- Secrets and runtime artifacts are excluded by `.gitignore`.

The shared-token design is intended for a local lab, not an internet-facing production system.

## Historical artifacts

Old executables, databases, captured logs, certificates, and environment files may still exist in
an existing working directory. They are ignored by the new repository configuration but should be
removed from published history and rotated or destroyed according to the owner's retention policy.

