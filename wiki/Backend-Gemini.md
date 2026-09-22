# Backend: Gemini

Google's Gemini via **aider** as the file-editing layer. Free tier is generous (~1500 requests/day on Gemini 2.0 Flash), no card required.

**Don't use the standalone `gemini` CLI entry (`agent.py -a gemini`) for autonomous runs** — it's a general chat tool, not built for commit-and-push loops. Use aider as the driver instead.

## Install

```bash
pip install aider-chat
```

## Auth

Get a free API key from [aistudio.google.com](https://aistudio.google.com) → **Get API key**.

```bash
export GEMINI_API_KEY=<your-key>
export AIDER_MODEL=gemini/gemini-2.0-flash-exp
```

On Windows PowerShell:
```powershell
$env:GEMINI_API_KEY = "<your-key>"
$env:AIDER_MODEL = "gemini/gemini-2.0-flash-exp"
```

For persistence, use `setx` (Windows) or add to your shell rc (Linux/macOS).

## Run

```bash
python agent.py -a aider
```

## Env vars

| Var | Value | Required |
|---|---|---|
| `GEMINI_API_KEY` | Your aistudio key | Yes |
| `AIDER_MODEL` | `gemini/gemini-2.0-flash-exp` (or `gemini/gemini-2.5-pro` if you have paid access) | Yes |

## Model options

- `gemini/gemini-2.0-flash-exp` — free, fast, decent for most edits
- `gemini/gemini-2.5-pro` — paid, better quality, ~$2/M tokens
- `gemini/gemini-1.5-pro` — paid, older, cheaper

## Notes

- Aider doesn't emit the `===MEMORY_START===` markers, so **memory saving won't work**. Every run is effectively a "first run" that re-scans the repo. Costs more tokens but daemonctl still functions.
- `===NO_WORK===` escape hatch is not honored — aider will try to make edits regardless.
- Free tier rate limits: 15 requests/minute, 1500/day. One repo run typically uses 20-50 requests, so 2 repos/day fits comfortably.

## Common issues

| Symptom | Cause |
|---|---|
| `AI_APIError: rate limit exceeded` | Hit the 15 req/min limit — space runs apart or reduce `REPOS_PER_RUN` |
| Aider commits with weird author `aider <aider@aider.chat>` | Not an issue — daemonctl's `GIT_AUTHOR/COMMITTER` env vars override this at commit time |
| Empty commits or no changes | Model didn't produce valid edits — check aider's output, try a bigger model |
