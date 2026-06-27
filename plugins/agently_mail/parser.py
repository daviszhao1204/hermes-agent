from __future__ import annotations

import html
import json
import re
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
    messages = payload.get("messages")
    if messages is None:
        messages = payload.get("data")
    messages = messages or []
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


def _strip_agent_mail_footer(text: str) -> str:
    footer_start = text.find("此邮件由")
    if footer_start == -1:
        return text.strip()

    footer = text[footer_start:]
    if "Agent Mail" in footer and ("举报" in footer or "退订" in footer):
        text = text[:footer_start]
    return text.strip()


def _html_to_text(value: str) -> str:
    text = re.sub(r"(?i)<br\s*/?>", "\n", value)
    text = re.sub(r"(?i)</p\s*>", "\n\n", text)
    text = re.sub(r"(?i)</div\s*>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    return text.strip()


def render_message_body(payload: dict[str, Any]) -> str:
    text_body = payload.get("text_body")
    if text_body:
        return _strip_agent_mail_footer(text_body)

    body = payload.get("body") or ""
    if payload.get("body_format") == "HTML":
        return _strip_agent_mail_footer(_html_to_text(body))

    return _strip_agent_mail_footer(body) if body else "(empty email)"


def format_message_detail(payload: dict[str, Any]) -> str:
    subject = payload.get("subject", "(no subject)")
    sender = (payload.get("from") or {}).get("email", "(unknown sender)")
    body = render_message_body(payload)
    message_id = payload.get("message_id", "(missing id)")
    attachments = payload.get("attachments") or []
    attachment_lines = [
        f"- {item.get('attachment_id', '(no id)')} | "
        f"{item.get('filename', '(unnamed attachment)')}"
        for item in attachments
    ]
    attachment_block = "\n".join(attachment_lines) if attachment_lines else "(none)"
    return (
        f"Message: {message_id}\nFrom: {sender}\nSubject: {subject}\n\n{body}"
        f"\n\nAttachments:\n{attachment_block}"
    )


def format_search_results(payload: dict[str, Any]) -> str:
    return format_message_list(payload)
