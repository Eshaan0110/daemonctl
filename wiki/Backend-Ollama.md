# Backend: Ollama

Fully local, fully free. No signup, no API key, no data leaving your machine. Runs a model on your own hardware via [Ollama](https://ollama.com).

Uses **aider** under the hood — Ollama provides the model, aider drives the file edits.

## Requirements

- **8GB+ RAM** for a usable model (7B params, quantized)
- **16GB+ RAM** recommended for anything larger
- GPU optional but speeds things up considerably
- ~5GB disk per model

## Install

```bash
# 1. Install Ollama from ollama.com
# 2. Pull a coding model
ollama pull qwen2.5-coder:7b

# 3. Install aider
pip install aider-chat
```

Verify Ollama is running:
```bash
ollama list
```

## Auth

None. Ollama runs locally, no keys involved.

## Run

```bash
python agent.py -a ollama
```

Under the hood:
```
aider --yes-always --model ollama/qwen2.5-coder:7b --message "<prompt>"
```

## Env vars

| Var | Value | Default |
|---|---|---|
| `OLLAMA_MODEL` | Ollama model name | `qwen2.5-coder:7b` |

Override to try a different model:
```bash
export OLLAMA_MODEL=deepseek-coder-v2:16b
python agent.py -a ollama
```

## Model recommendations

| Model | RAM | Quality | Notes |
|---|---|---|---|
| `qwen2.5-coder:7b` | 8GB | Good | Default. Best 7B coder available. |
| `deepseek-coder-v2:16b` | 16GB | Very good | Slower, higher quality |
| `codellama:13b` | 12GB | Decent | Older but stable |
| `qwen2.5-coder:32b` | 32GB | Excellent | Approaches GPT-4 quality on code |

Larger = slower but better output. Match to your hardware.

## Notes

- **Speed**: 7B models on CPU produce a few tokens/second. One repo run can take 30-90 minutes. GPU is highly recommended.
- Aider doesn't emit `===MEMORY_START===` markers → **memory won't be saved**. Every run re-scans.
- `===NO_WORK===` not honored — will attempt edits regardless.
- Local model quality is a step below Claude/GPT-4/Gemini. Expect simpler features and occasional wonky edits. Best for keeping small projects alive, not for architectural refactors.

## Common issues

| Symptom | Cause |
|---|---|
| `Error: could not connect to ollama` | Ollama daemon isn't running — start it (`ollama serve` or the desktop app) |
| Extremely slow | Running on CPU — install CUDA/ROCm drivers to enable GPU |
| `model not found` | Run `ollama pull <model>` first |
| Nonsense commits or broken code | Model too small — try `qwen2.5-coder:32b` if you have the RAM |
| High CPU/RAM usage during runs | Normal — local inference is compute-heavy. Schedule runs when the machine is otherwise idle. |
