"""hermes-agent-stt: Speech-to-text transcription plugin for Hermes Agent."""

from hermes_agent_stt.transcription_tools import (  # noqa: F401
    transcribe_audio,
    MAX_FILE_SIZE,
    _get_provider,
    _load_stt_config,
    is_stt_enabled,
)


def register(ctx):
    """Entry point for the hermes_agent.plugins entry point group.

    Registers STT tool functions, constants, and config helpers in the
    plugin capability registry so core code (gateway, CLI) can look
    them up without importing from ``hermes_agent_stt`` directly.
    """
    from hermes_agent_stt.transcription_tools import (
        transcribe_audio,
        MAX_FILE_SIZE,
        _get_provider,
        _load_stt_config,
        is_stt_enabled,
    )
    ctx.register_tool_provider_entry(
        name="stt",
        tool_functions={
            "transcribe_audio": transcribe_audio,
        },
        constants={
            "MAX_FILE_SIZE": MAX_FILE_SIZE,
        },
        config_functions={
            "_get_provider": _get_provider,
            "_load_stt_config": _load_stt_config,
            "is_stt_enabled": is_stt_enabled,
        },
    )
