from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Sequence

from .parser import format_mail_me, parse_cli_envelope


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
    return "Not implemented yet."


def handle_mail_read(raw_args: str) -> str | None:
    return "Not implemented yet."


def handle_mail_search(raw_args: str) -> str | None:
    return "Not implemented yet."
