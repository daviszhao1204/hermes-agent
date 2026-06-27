from plugins.agently_mail.parser import format_mail_me, parse_cli_envelope


def test_parse_cli_envelope_returns_payload_dict():
    payload = parse_cli_envelope('{"ok": true, "data": {"aliases": []}}')

    assert payload["ok"] is True
    assert payload["data"] == {"aliases": []}


def test_format_mail_me_renders_primary_alias():
    rendered = format_mail_me(
        {
            "aliases": [
                {
                    "email": "zhaolei0138@agent.qq.com",
                    "is_primary": True,
                    "name": "zhaolei0138",
                }
            ],
            "rate_limits": {"daily_send_quota": 50},
        }
    )

    assert "zhaolei0138@agent.qq.com" in rendered
    assert "daily send quota: 50" in rendered.lower()
