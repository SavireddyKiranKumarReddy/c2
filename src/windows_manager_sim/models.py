"""Validated protocol models without third-party runtime dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def required_text(data: dict[str, Any], name: str, maximum: int) -> str:
    value = data.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{name} exceeds {maximum} characters")
    return value


@dataclass(frozen=True, slots=True)
class CheckIn:
    agent_id: str
    hostname: str
    platform: str
    username: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CheckIn":
        return cls(
            agent_id=required_text(data, "agent_id", 128),
            hostname=required_text(data, "hostname", 255),
            platform=required_text(data, "platform", 255),
            username=required_text(data, "username", 255),
            timestamp=required_text(data, "timestamp", 64),
        )


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    agent_id: str
    category: str
    content: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TelemetryEvent":
        category = required_text(data, "category", 64)
        if category not in {"simulation", "status", "command_result"}:
            raise ValueError("unsupported telemetry category")
        return cls(
            agent_id=required_text(data, "agent_id", 128),
            category=category,
            content=required_text(data, "content", 4096),
            timestamp=required_text(data, "timestamp", 64),
        )

