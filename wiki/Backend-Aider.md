# Backend: Aider

Aider is a file-editing tool that can point at any OpenAI-compatible endpoint. Use this backend for any model provider that isn't listed elsewhere — Groq, DeepSeek, Together, OpenRouter, self-hosted vLLM, etc.

For provider-specific setups, see the [Gemini](Backend-Gemini) or [Ollama](Backend-Ollama) pages.

## Install

```bash
pip install aider-chat
aider --version
```

## Auth

Depends on the provider. Aider reads model-specific env vars:

- OpenAI-compatible endpoint: `OPENAI_API_KEY` + `OPENAI_API_BASE`
- Anthropic: `ANTHROPIC_API_KEY`
- Google: `GEMINI_API_KEY` (see [Gemini](Backend-Gemini) page)
- Groq (free tier): `OPENAI_API_KEY=gsk_...` + `OPENAI_API_BASE=https://api.groq.com/openai/v1`
- DeepSeek: `DEEPSEEK_API_KEY`
- OpenRouter: `OPENROUTER_API_KEY`

Full list: [aider.chat/docs/llms.html](https://aider.chat/docs/llms.html)

## Run

```bash
export AIDER_MODEL=<provider>/<model-name>
python agent.py -a aider
```

Examples:
- Groq (free): `AIDER_MODEL=openai/llama-3.3-70b-versatile` + Groq env vars above
- DeepSeek Chat: `AIDER_MODEL=deepseek/deepseek-chat`
- Claude via API: `AIDER_MODEL=anthropic/claude-sonnet-4-5` + `ANTHROPIC_API_KEY`

If `AIDER_MODEL` is unset, aider defaults to Claude Sonnet (needs `ANTHROPIC_API_KEY`).

## Env vars

| Var | Purpose |
|---|---|
| `AIDER_MODEL` | Which model aider uses. Overrides its default. |
| Provider-specific keys | As above |
| `OPENAI_API_BASE` | Override endpoint for OpenAI-compatible providers |

## Notes

- Aider does NOT emit `===MEMORY_START===` markers. Memory won't be saved. Every run re-scans the repo.
- Aider auto-commits after each edit. daemonctl's post-run push handles the push side.
- Aider's default author (`aider <aider@aider.chat>`) is overridden by daemonctl's `GIT_AUTHOR/COMMITTER` env vars, so commits land under your identity regardless.
- No `===NO_WORK===` support — aider will try to edit something on every run.

## Common issues

| Symptom | Cause |
|---|---|
| `AI_APIError: model not found` | `AIDER_MODEL` typo — check provider prefix (`openai/`, `gemini/`, etc.) |
| Aider makes trivial edits or no edits | Model too small/weak — try a bigger model |
| Repeated same commit | Aider's edit loop failed to converge — bump `--max-chat-history-tokens` or switch models |
