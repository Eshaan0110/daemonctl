# Backend: Claude Code

The default and most reliable backend. Full agentic loop — reads files, edits, runs tests, iterates.

## Install

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version
```

Windows: use Git Bash or WSL for the install line, or follow the Windows installer from claude.com/docs.

## Auth

```bash
claude login
```

Opens a browser, sign in with your Claude account. Session persists across runs. Requires a Claude subscription (Pro or Team).

If OAuth breaks (`401 OAuth access token has been revoked`), just run `claude login` again. This happens every few months.

## Run

```bash
python agent.py -a claude
# or just:
python agent.py
```

Under the hood, daemonctl invokes:
```
claude --dangerously-skip-permissions -p "<prompt>"
```
`--dangerously-skip-permissions` is required because the run is fully headless — there's no human to approve file writes and shell commands.

## Env vars

None required. Auth is handled by `claude login`.

## Notes

- Only backend that reliably emits the `===MEMORY_START===`/`===MEMORY_END===` and `===COMMITS_START===`/`===COMMITS_END===` markers, so memory saving works as designed.
- Only backend that fully honors the `===NO_WORK===` escape hatch — others will attempt to make edits regardless of the prompt's "don't commit if nothing meaningful" rule.
- Typical run time: 5–15 minutes per repo.

## Common issues

| Symptom | Cause |
|---|---|
| `Failed to authenticate. API Error: 401` | Token revoked — run `claude login` again |
| Runs forever, hits Task Scheduler timeout | Very large repo; consider raising `-ExecutionTimeLimit` on the task |
| Weird "confirm this action" prompts in the log | You forgot `--dangerously-skip-permissions` (shouldn't happen with default `AGENTS` entry) |
