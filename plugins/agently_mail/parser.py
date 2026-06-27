from __future__ import annotations

import json
from typing import Any


def parse_cli_envelope(stdout: str) -> dict[str, Any]:
    return json.loads(stdout.strip())


def format_mail_me(payload: dict[str, Any]) -> str:
    aliases = payload.get("aliases") or []
    primary = next(
        (alias for alias in aliases if alias.get("is_primary")),
        aliases[0] if aliases else {},
    )
    email = primary.get("email", "(unknown)")
    name = primary.get("name", "(unknown)")
    limits = payload.get("rate_limits") or {}
    quota = limits.get("daily_send_quota", "unknown")
    return (
        f"Agent Mail account: {email}\n"
        f"Display name: {name}\n"
        f"Daily send quota: {quota}"
    )
