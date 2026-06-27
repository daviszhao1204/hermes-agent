from plugins.agently_mail import register
from plugins.agently_mail.cli import (
    CliInvocationResult,
    handle_mail_list,
    handle_mail_me,
    handle_mail_read,
    handle_mail_search,
)


class _Ctx:
    def __init__(self) -> None:
        self.calls = []

    def register_command(self, name, handler, description="", args_hint=""):
        self.calls.append((name, handler.__name__, description, args_hint))


def test_registers_agently_mail_commands():
    ctx = _Ctx()

    register(ctx)

    assert [call[0] for call in ctx.calls] == [
        "mail-me",
        "mail-list",
        "mail-read",
        "mail-search",
    ]
    assert ctx.calls[2][3] == "<msg_id>"
    assert ctx.calls[3][3] == "<query>"


def test_handle_mail_me_calls_agently_cli(monkeypatch):
    monkeypatch.setattr(
        "plugins.agently_mail.cli.run_agently_cli",
        lambda argv: CliInvocationResult(
            exit_code=0,
            stdout='{"ok": true, "data": {"aliases": [{"email": "zhaolei0138@agent.qq.com", "is_primary": true, "name": "zhaolei0138"}]}}',
            stderr="",
        ),
    )

    rendered = handle_mail_me("")

    assert "zhaolei0138@agent.qq.com" in rendered


def test_handle_mail_list_uses_default_inbox_limit(monkeypatch):
    seen = {}

    def _fake(argv):
        seen["argv"] = argv
        return CliInvocationResult(
            exit_code=0,
            stdout='{"ok": true, "data": {"messages": [{"message_id": "msg_001", "subject": "Weekly update", "from": {"name": "Alice", "email": "alice@example.com"}, "received_at": "2026-06-27T01:00:00Z"}]}}',
            stderr="",
        )

    monkeypatch.setattr("plugins.agently_mail.cli.run_agently_cli", _fake)

    rendered = handle_mail_list("")

    assert seen["argv"] == ["message", "+list", "--dir", "inbox", "--limit", "10"]
    assert "msg_001" in rendered
    assert "Weekly update" in rendered


def test_handle_mail_read_requires_message_id():
    assert handle_mail_read("") == "Usage: /mail-read <msg_id>"


def test_handle_mail_search_uses_query_string(monkeypatch):
    seen = {}

    def _fake(argv):
        seen["argv"] = argv
        return CliInvocationResult(
            exit_code=0,
            stdout='{"ok": true, "data": {"messages": [{"message_id": "msg_002", "subject": "Project progress", "from": {"name": "Bob", "email": "bob@example.com"}}]}}',
            stderr="",
        )

    monkeypatch.setattr("plugins.agently_mail.cli.run_agently_cli", _fake)

    rendered = handle_mail_search("project progress")

    assert seen["argv"] == ["message", "+search", "--q", "project progress"]
    assert "msg_002" in rendered
