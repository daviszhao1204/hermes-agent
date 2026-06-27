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


def test_handle_mail_search_supports_nested_data_payload(monkeypatch):
    monkeypatch.setattr(
        "plugins.agently_mail.cli.run_agently_cli",
        lambda argv: CliInvocationResult(
            exit_code=0,
            stdout='{"ok": true, "data": {"data": [{"message_id": "msg_nested", "subject": "Hermes Agent Mail 联通测试", "from": {"email": "zhaolei0138@agent.qq.com"}}], "pagination": {"has_more": false, "next_cursor": ""}}}',
            stderr="",
        ),
    )

    rendered = handle_mail_search("Hermes Agent Mail 联通测试")

    assert "msg_nested" in rendered


def test_handle_mail_me_surfaces_reauth_instruction(monkeypatch):
    monkeypatch.setattr(
        "plugins.agently_mail.cli.run_agently_cli",
        lambda argv: CliInvocationResult(
            exit_code=3,
            stdout='{"ok": false, "error": {"message": "authorization required"}}',
            stderr="tip: Authorization required; follow the agently mail skill OAuth login flow.",
        ),
    )

    rendered = handle_mail_me("")

    assert "agently-cli auth login" in rendered
    assert "authorization required" in rendered


def test_handle_mail_read_formats_body_and_attachments(monkeypatch):
    monkeypatch.setattr(
        "plugins.agently_mail.cli.run_agently_cli",
        lambda argv: CliInvocationResult(
            exit_code=0,
            stdout='{"ok": true, "data": {"message_id": "msg_100", "subject": "Invoice", "from": {"email": "finance@example.com"}, "body": "See attached.", "attachments": [{"attachment_id": "att_001", "filename": "invoice.pdf"}]}}',
            stderr="",
        ),
    )

    rendered = handle_mail_read("msg_100")

    assert "msg_100" in rendered
    assert "invoice.pdf" in rendered


def test_handle_mail_read_strips_html_and_agent_mail_footer(monkeypatch):
    monkeypatch.setattr(
        "plugins.agently_mail.cli.run_agently_cli",
        lambda argv: CliInvocationResult(
            exit_code=0,
            stdout='{"ok": true, "data": {"message_id": "msg_html", "subject": "HTML body", "body_format": "HTML", "from": {"email": "sender@example.com"}, "body": "<div>第一段</div><div>第二段<br>第三行</div><div>此邮件由<a href=\\"https://agent.qq.com\\">Agent Mail</a>自动发送。<a href=\\"https://agent.qq.com/report\\">举报</a><a href=\\"https://agent.qq.com/unsub\\">退订</a></div>", "attachments": []}}',
            stderr="",
        ),
    )

    rendered = handle_mail_read("msg_html")

    assert "<div" not in rendered
    assert "第一段" in rendered
    assert "第二段" in rendered
    assert "第三行" in rendered
    assert "此邮件由" not in rendered
    assert "举报" not in rendered
    assert "退订" not in rendered


def test_handle_mail_read_preserves_meaningful_line_breaks(monkeypatch):
    monkeypatch.setattr(
        "plugins.agently_mail.cli.run_agently_cli",
        lambda argv: CliInvocationResult(
            exit_code=0,
            stdout='{"ok": true, "data": {"message_id": "msg_breaks", "subject": "Line breaks", "body_format": "HTML", "from": {"email": "sender@example.com"}, "body": "<p>甲</p><p>乙</p><div>丙<br>丁</div>", "attachments": []}}',
            stderr="",
        ),
    )

    rendered = handle_mail_read("msg_breaks")

    assert "甲\n\n乙" in rendered or "甲\n乙" in rendered
    assert "丙\n丁" in rendered
