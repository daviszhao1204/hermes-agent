from .cli import (
    handle_mail_list,
    handle_mail_me,
    handle_mail_read,
    handle_mail_search,
)


def register(ctx) -> None:
    ctx.register_command(
        "mail-me",
        handler=handle_mail_me,
        description="Show the current Agent Mail account.",
    )
    ctx.register_command(
        "mail-list",
        handler=handle_mail_list,
        description="List recent inbox messages.",
    )
    ctx.register_command(
        "mail-read",
        handler=handle_mail_read,
        description="Read a message by Agent Mail message id.",
        args_hint="<msg_id>",
    )
    ctx.register_command(
        "mail-search",
        handler=handle_mail_search,
        description="Search Agent Mail messages.",
        args_hint="<query>",
    )
