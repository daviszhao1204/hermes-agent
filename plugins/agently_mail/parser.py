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


def format_message_list(payload: dict[str, Any]) -> str:
    messages = payload.get("messages") or []
    if not messages:
        return "No messages found."

    lines = []
    for item in messages:
        sender = (item.get("from") or {}).get("email")
        if not sender:
            sender = (item.get("from") or {}).get("name", "(unknown sender)")
        lines.append(
            f"- {item.get('message_id', '(missing id)')} | "
            f"{item.get('subject', '(no subject)')} | {sender}"
        )
    return "\n".join(lines)


def format_message_detail(payload: dict[str, Any]) -> str:
    subject = payload.get("subject", "(no subject)")
    sender = (payload.get("from") or {}).get("email", "(unknown sender)")
    body = payload.get("body") or payload.get("text_body") or "(empty email)"
    message_id = payload.get("message_id", "(missing id)")
    return f"Message: {message_id}\nFrom: {sender}\nSubject: {subject}\n\n{body}"


def format_search_results(payload: dict[str, Any]) -> str:
    return format_message_list(payload)
