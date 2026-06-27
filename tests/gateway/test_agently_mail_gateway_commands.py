from unittest.mock import AsyncMock

import pytest

from tests.gateway.test_unknown_command import _make_event, _make_runner


@pytest.mark.asyncio
async def test_gateway_dispatches_mail_me_plugin_command(monkeypatch):
    import gateway.run as gateway_run
    from hermes_cli import plugins as plugins_mod

    runner = _make_runner()
    runner._run_agent = AsyncMock(
        side_effect=AssertionError("plugin command leaked to the agent")
    )

    monkeypatch.setattr(
        gateway_run, "_resolve_runtime_agent_kwargs", lambda: {"api_key": "***"}
    )
    monkeypatch.setattr(
        plugins_mod,
        "get_plugin_commands",
        lambda: {"mail-me": {"description": "Agent Mail account", "args_hint": ""}},
    )
    monkeypatch.setattr(
        plugins_mod,
        "get_plugin_command_handler",
        lambda name: (
            lambda raw_args: "Agent Mail account: zhaolei0138@agent.qq.com"
        ) if name == "mail-me" else None,
    )

    result = await runner._handle_message(_make_event("/mail-me"))

    assert result == "Agent Mail account: zhaolei0138@agent.qq.com"
