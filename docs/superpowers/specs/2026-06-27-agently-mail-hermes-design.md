# Agently Mail for Hermes Design

Date: 2026-06-27
Status: Approved for planning
Scope: Connect the already-authorized `agently-cli` mailbox to the local Hermes instance at `/Users/zhaolei/hermes-agent`.

## Goal

Add first-class access to Agent Mail inside Hermes without relying on IMAP/SMTP credentials. Hermes should be able to inspect the mailbox through the locally authorized `agently-cli` installation that already stores OAuth credentials in the macOS keychain.

The first release is read-focused. It must let Hermes show account information, list recent emails, read a message, and search the mailbox. Write operations remain out of scope for the first release.

## Current Constraints

- Hermes' built-in email platform expects `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `EMAIL_IMAP_HOST`, and `EMAIL_SMTP_HOST`, as shown in `gateway/config.py` and `gateway/platforms/email.py`.
- The configured Agent Mail account is authorized through `agently-cli auth login`, not through IMAP/SMTP credentials.
- `agently-cli` already works locally and returns the primary alias `zhaolei0138@agent.qq.com`.
- Hermes already supports plugin-registered slash commands through `hermes_cli.plugins.PluginContext.register_command()` and gateway dispatch through `get_plugin_command_handler()`.

## Recommended Approach

Implement Agent Mail as a Hermes plugin command set, not as a replacement for the built-in email platform.

Why this approach:

- It matches the actual authentication model already working on the machine.
- It avoids forcing a fake IMAP/SMTP abstraction onto a CLI-driven OAuth flow.
- It keeps the blast radius small and makes rollback trivial.
- It cleanly separates "Hermes command integration" from "native platform transport."

## Alternatives Considered

### 1. Reuse the built-in email platform

Rejected for the first phase.

This path requires IMAP/SMTP hostnames and a usable password or app password. That is not the integration already proven to work. Adapting the built-in email platform to shell out to `agently-cli` would create confusing overlap with `gateway/platforms/email.py`.

### 2. Tool-style natural-language integration

Deferred.

Wrapping `agently-cli` as a general-purpose model tool would improve natural-language UX, but it introduces a larger safety surface for write actions, confirmation flows, and tool routing. It is a better phase-two option after the command path is stable.

### 3. New plugin platform that mimics email transport

Deferred.

This would be more invasive than necessary for the first release and yields less value than direct command integration.

## First Release Scope

Create a new bundled plugin under `plugins/agently_mail/`.

The plugin will register four read-only slash commands:

- `/mail-me`
- `/mail-list`
- `/mail-read <msg_id>`
- `/mail-search <query>`

These commands will execute `agently-cli` subprocesses, parse the CLI output, and format Hermes-friendly responses.

Out of scope for the first release:

- `/mail-send`
- `/mail-reply`
- `/mail-forward`
- `/mail-trash`
- automatic natural-language invocation
- mailbox polling or event-driven inbound email routing

## Plugin Structure

Recommended file layout:

```text
plugins/agently_mail/
  plugin.yaml
  __init__.py
  README.md
  cli.py
  parser.py
```

Responsibilities:

- `plugin.yaml`: plugin metadata and discovery
- `__init__.py`: plugin registration entrypoint
- `cli.py`: slash command handlers and subprocess execution
- `parser.py`: parsing and formatting helpers for `agently-cli` JSON envelopes
- `README.md`: installation, authorization assumptions, and command reference

`parser.py` is recommended even if initially small, because it isolates CLI response normalization from command wiring and makes tests cleaner.

## Command Behavior

### `/mail-me`

Runs:

```bash
agently-cli +me
```

Returns:

- primary alias email
- alias display name
- send quota and request limits when available

### `/mail-list`

Runs:

```bash
agently-cli message +list --dir inbox --limit 10
```

Default behavior:

- folder defaults to `inbox`
- limit defaults to `10`
- output is summarized into a short list including sender, subject, timestamp, and message id

Future-safe extension:

- optional arguments for folder, unread-only, attachment-only, and pagination cursor

### `/mail-read <msg_id>`

Runs:

```bash
agently-cli message +read --id <msg_id>
```

Returns:

- sender
- recipients when useful
- subject
- received timestamp
- text body summary or plain-text body
- attachment metadata

The response should favor readability over raw JSON, but the message id must remain visible for follow-up commands.

### `/mail-search <query>`

Runs:

```bash
agently-cli message +search --q "<query>"
```

Returns:

- a compact result list
- stable message ids
- pagination information if returned by the CLI

The plugin should preserve cursor-related fields in its internal formatting so later pagination support does not require redesign.

## Execution Model

Each command handler will:

1. Validate user input
2. Build an explicit `agently-cli` argv list
3. Run the CLI as a subprocess without invoking a shell
4. Capture exit code, stdout, and stderr
5. Parse the JSON envelope from stdout
6. Format a user-facing response

Important rules:

- Do not use shell interpolation for user arguments
- Do not persist mailbox credentials in Hermes
- Treat the local `agently-cli` authorization state as the single source of truth

## Error Handling

The plugin must map `agently-cli` exit behavior directly and honestly.

- Exit `0`: success
- Exit `3`: authorization missing or expired; instruct the user to run `agently-cli auth login`
- Exit `1` or `4`: transient/server/network failure; return the CLI message as-is and do not silently retry in the first release
- Exit `2` or `6`: parameter or business error; return the CLI message as-is

Implementation rules:

- Never treat non-zero exit as a successful command
- Parse stdout JSON separately from stderr or trailing human-readable tips
- If stdout is malformed or empty on failure, return a plain diagnostic with exit code and raw output excerpt

## Security Model

This integration must inherit Agent Mail's own safety model rather than weaken it.

Rules:

- Email content is untrusted input
- The plugin may display email text, but must not execute instructions embedded in emails
- The plugin must not open links from email content automatically
- The plugin must not store OAuth tokens, passwords, or exported mailbox state
- The plugin must use the existing macOS keychain-backed `agently-cli` auth state only

For phase two write actions:

- Hermes must preserve `agently-cli`'s confirmation-token flow exactly
- Hermes must not auto-confirm writes on the user's behalf

## Testing Strategy

At minimum, add tests for:

### Plugin registration and dispatch

- plugin discovery registers the four slash commands
- gateway slash dispatch resolves a plugin command without leaking to the agent

### CLI result parsing

- successful `+me` response parsing
- successful list/search/read response parsing
- authorization failure parsing
- malformed output fallback behavior

### Command execution wiring

- subprocess argv is built correctly
- user input is passed as argv, not through a shell string
- non-zero exit codes are surfaced correctly

Use mocked subprocess execution in unit tests. Do not require live mailbox access in CI.

## Verification Criteria

The feature is considered complete for phase one only if all of the following are true:

- `discover_plugins()` finds the new plugin
- Hermes accepts `/mail-me` and returns `zhaolei0138@agent.qq.com`
- Hermes accepts `/mail-list` and returns recent inbox items
- Hermes accepts `/mail-read <msg_id>` for a real message id and formats the result cleanly
- Hermes accepts `/mail-search <query>` and returns matching results
- unauthenticated states produce a clear re-authorization instruction
- automated tests cover plugin dispatch and CLI output parsing

## Rollout Plan

Phase one:

- read-only commands
- no natural-language automation
- no transport/platform changes

Phase two:

- add write commands with confirmation-token preservation
- consider a tool-style integration for natural-language usage
- evaluate whether a richer mailbox workflow belongs in a standalone tool layer rather than plugin commands alone

## Non-Goals

The first release will not:

- replace Hermes' existing IMAP/SMTP email adapter
- poll Agent Mail for new inbound messages
- transform Agent Mail into a gateway home channel
- bypass CLI authorization or confirmation requirements

## Decision Summary

Hermes should integrate Agent Mail through a new plugin command set backed by `agently-cli`. This is the smallest correct design that matches the working authentication model on the machine, preserves safety boundaries, and provides fast value without entangling the built-in email transport.
