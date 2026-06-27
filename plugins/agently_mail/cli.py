from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Sequence

from .parser import (
    format_mail_me,
    format_message_detail,
    format_message_list,
    format_search_results,
    parse_cli_envelope,
)


@dataclass
class CliInvocationResult:
    exit_code: int
    stdout: str
    stderr: str


def run_agently_cli(argv: Sequence[str]) -> CliInvocationResult:
    completed = subprocess.run(
        ["agently-cli", *argv],
        capture_output=True,
        text=True,
        check=False,
    )
    return CliInvocationResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def handle_mail_me(raw_args: str) -> str | None:
    if raw_args.strip():
        return "Usage: /mail-me"
    result = run_agently_cli(["+me"])
    payload = parse_cli_envelope(result.stdout)
    return format_mail_me(payload["data"])


def handle_mail_list(raw_args: str) -> str | None:
    if raw_args.strip():
        return "Usage: /mail-list"
    result = run_agently_cli(["message", "+list", "--dir", "inbox", "--limit", "10"])
    payload = parse_cli_envelope(result.stdout)
    return format_message_list(payload["data"])


def handle_mail_read(raw_args: str) -> str | None:
    message_id = raw_args.strip()
    if not message_id:
        return "Usage: /mail-read <msg_id>"
    result = run_agently_cli(["message", "+read", "--id", message_id])
    payload = parse_cli_envelope(result.stdout)
    return format_message_detail(payload["data"])


def handle_mail_search(raw_args: str) -> str | None:
    query = raw_args.strip()
    if not query:
        return "Usage: /mail-search <query>"
    result = run_agently_cli(["message", "+search", "--q", query])
    payload = parse_cli_envelope(result.stdout)
    return format_search_results(payload["data"])
