from plugins.agently_mail import register
from plugins.agently_mail.cli import CliInvocationResult, handle_mail_me


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
