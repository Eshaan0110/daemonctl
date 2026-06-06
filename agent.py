import os
import random
import subprocess
import logging
import argparse

REPOS_DIR = os.path.join(os.path.dirname(__file__), "repos")
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
REPOS_PER_RUN = 2
DEFAULT_AGENT = "claude"

AGENTS = {
    "claude": {
        "name": "Claude Code",
        "build_cmd": lambda prompt: [
            "claude", "--dangerously-skip-permissions", "-p", prompt
        ],
    },
    "gemini": {
        "name": "Gemini CLI",
        "build_cmd": lambda prompt: [
            "gemini", "-p", prompt
        ],
    },
    "codex": {
        "name": "OpenAI Codex CLI",
        "build_cmd": lambda prompt: [
            "codex", "--approval-mode", "full-auto", "-q", prompt
        ],
    },
    "aider": {
        "name": "Aider",
        "build_cmd": lambda prompt: [
            "aider", "--yes-always", "--message", prompt
        ],
    },
}

PROMPT_FIRST = """Read this repo. Find what's missing or incomplete. Build it out — add real features, working code, tests, or demos. Make separate commits for each change. Push to origin. Never mention AI or automation in commits or code. Do NOT add any Co-authored-by or Signed-off-by trailers to commits.

When done, print your summary between ===MEMORY_START=== and ===MEMORY_END=== markers with: what the project is, what you did, what's left to do."""

PROMPT_MEMORY = """Here's what you know about this project from last time:

{memory}

Pick the most important item from what's left to do. Build it. Commit and push. Never mention AI or automation in commits or code. Do NOT add any Co-authored-by or Signed-off-by trailers to commits.

When done, print an updated summary between ===MEMORY_START=== and ===MEMORY_END=== markers with: what the project is, what you did today added to the previous changelog, and what's left to do next."""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger()


def get_repos():
    repos = []
    for name in os.listdir(REPOS_DIR):
        path = os.path.join(REPOS_DIR, name)
        if os.path.isdir(path) and os.path.isdir(os.path.join(path, ".git")):
            repos.append((name, path))
    return repos


def load_memory(repo_name):
    path = os.path.join(MEMORY_DIR, f"{repo_name}.md")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def save_memory(repo_name, output):
    s = output.find("===MEMORY_START===")
    e = output.find("===MEMORY_END===")
    if s != -1 and e != -1:
        os.makedirs(MEMORY_DIR, exist_ok=True)
        with open(os.path.join(MEMORY_DIR, f"{repo_name}.md"), "w", encoding="utf-8") as f:
            f.write(output[s + 18:e].strip())
        log.info(f"  Memory saved")


def strip_coauthor(path):
    """Remove any Co-authored-by or AI trailers from recent unpushed commits."""
    try:
        subprocess.run(
            ["git", "filter-branch", "--force", "--msg-filter",
             "sed '/^Co-authored-by:/d; /^Signed-off-by:.*claude/Id; /^Signed-off-by:.*anthropic/Id'",
             "HEAD~10..HEAD"],
            cwd=path, capture_output=True, text=True, timeout=30
        )
        subprocess.run(["git", "push", "--force-with-lease"], cwd=path, capture_output=True, timeout=30)
    except Exception:
        pass


def run_agent(name, path, agent_key):
    agent = AGENTS[agent_key]
    memory = load_memory(name)
    prompt = PROMPT_MEMORY.replace("{memory}", memory) if memory else PROMPT_FIRST
    mode = "incremental" if memory else "first run"

    print(f"\n{'='*50}")
    print(f"  {name} ({agent['name']}, {mode})")
    print(f"{'='*50}\n")

    result = subprocess.run(
        agent["build_cmd"](prompt),
        cwd=path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=None,
    )

    if result.returncode == 0:
        print(f"\n✓ {name}")
        save_memory(name, result.stdout)
        strip_coauthor(path)
    else:
        print(f"\n✗ {name} (exit {result.returncode})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", "-a", choices=list(AGENTS.keys()), default=DEFAULT_AGENT)
    parser.add_argument("--repos", "-n", type=int, default=REPOS_PER_RUN)
    parser.add_argument("--list-agents", action="store_true")
    args = parser.parse_args()

    if args.list_agents:
        for k, v in AGENTS.items():
            print(f"  {k:10s} — {v['name']}")
        return

    repos = get_repos()
    chosen = random.sample(repos, min(args.repos, len(repos)))
    print(f"Today's repos: {', '.join(n for n, _ in chosen)}\n")

    for name, path in chosen:
        run_agent(name, path, args.agent)


if __name__ == "__main__":
    main()