# daemonctl Wiki

daemonctl is a scheduler-driven agent that picks random repos from your local collection and pushes meaningful commits under your identity every day.

The core loop is in `agent.py`. You choose which coding-assistant CLI drives the runs with the `-a` flag.

## Pick a backend

| Backend | Command | Cost | Quality | Setup effort |
|---|---|---|---|---|
| [Claude Code](Backend-Claude-Code) | `agent.py -a claude` | Subscription | Best | Low |
| [Gemini](Backend-Gemini) | `agent.py -a aider` + env vars | Free tier | Good | Medium |
| [Codex](Backend-Codex) | `agent.py -a codex` | Subscription/key | Good | Low |
| [Aider](Backend-Aider) | `agent.py -a aider` | Any endpoint | Depends on model | Medium |
| [Ollama](Backend-Ollama) | `agent.py -a ollama` | Free, local | Fair (model-dependent) | Higher (needs 8GB+ RAM) |

Default is Claude Code (subscription required). If you don't have one, the two zero-cost paths are **Gemini free tier via aider** or **Ollama locally**.

## Common setup (any backend)

```bash
git clone https://github.com/Eshaan0110/daemonctl.git
cd daemonctl
# put your repos into repos/ (see add-repos.sh)
python agent.py --list-agents
```

Schedule it with cron (Linux/macOS) or Task Scheduler (Windows). See the [README](https://github.com/Eshaan0110/daemonctl#setup) for scheduling.

## What every backend needs

- Git configured with push access to each repo in `repos/`
- Python 3.x
- `agent.py` uses env vars `GIT_AUTHOR_NAME/EMAIL` and `GIT_COMMITTER_NAME/EMAIL` internally to force every commit under your identity — no configuration needed on your side, just make sure your git remote can push

## Troubleshooting

- **`✗ <repo> (exit 1)` with no output** — usually the CLI's auth is broken (revoked token, expired session). Run the CLI standalone with a test prompt to see the real error.
- **No commits despite `✓`** — check the `Commits landed:` block in the log. If it's missing, the CLI ran but didn't produce any diffs. See the per-backend page for common causes.
- **Memory not saving** — the CLI didn't emit `===MEMORY_START===`/`===MEMORY_END===` markers in its output. Only Claude Code does this reliably; others may skip memory (see per-backend pages).
