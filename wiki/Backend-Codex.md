# Backend: Codex

OpenAI's Codex CLI — a full agentic loop similar to Claude Code. Requires a ChatGPT Plus/Team subscription or an OpenAI API key.

## Install

```bash
npm install -g @openai/codex
codex --version
```

Node.js 20+ required.

## Auth

Two options:

**ChatGPT subscription (recommended):**
```bash
codex login
```
Opens a browser. Uses your ChatGPT Plus/Team plan quotas.

**API key:**
```bash
export OPENAI_API_KEY=sk-...
```
Bills per-token. Get a key from platform.openai.com.

## Run

```bash
python agent.py -a codex
```

Under the hood:
```
codex --approval-mode full-auto -q "<prompt>"
```
`--approval-mode full-auto` skips all confirmation prompts (equivalent to Claude Code's `--dangerously-skip-permissions`). `-q` is quiet mode.

## Env vars

| Var | Value | Required |
|---|---|---|
| `OPENAI_API_KEY` | Your OpenAI key | Only if using API-key auth |

## Notes

- Codex is a strong agentic loop, comparable to Claude Code for most tasks.
- Memory marker emission is inconsistent — sometimes the memory block gets echoed, sometimes not. Expect occasional "first run" behavior on repos that should have memory.
- Typical run time: 5–20 minutes per repo.

## Common issues

| Symptom | Cause |
|---|---|
| `Not authenticated` | Run `codex login` or export `OPENAI_API_KEY` |
| Task hangs on approval prompt | `--approval-mode full-auto` wasn't applied — check that `AGENTS["codex"]` in `agent.py` still includes it |
| Rate limit errors on API-key auth | You're on a low-tier OpenAI plan; upgrade at platform.openai.com/settings/organization/limits |
