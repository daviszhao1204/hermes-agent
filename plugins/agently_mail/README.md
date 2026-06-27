# Agently Mail Plugin

Prerequisites:
- `agently-cli` must be installed on the host
- `agently-cli auth login` must have completed successfully on the host machine

Commands:
- `/mail-me`
- `/mail-list`
- `/mail-read <msg_id>`
- `/mail-search <query>`

Re-authentication:
- If a command reports authorization failure, run `agently-cli auth login`
