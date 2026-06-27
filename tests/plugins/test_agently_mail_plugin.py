from plugins.agently_mail import register


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
