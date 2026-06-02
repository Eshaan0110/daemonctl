import os
import random
import subprocess
import logging
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────
REPOS_DIR = os.path.join(os.path.dirname(__file__), "repos")
REPOS_PER_RUN = 2
# ────────────────────────────────────────────────────────────────────────

CLAUDE_PROMPT = """You are an autonomous developer working on this project.

Your job:
1. Read the entire codebase — README, source files, tests, TODOs, comments
2. Understand what this project is trying to do and what is MISSING
3. Build out the project substantially. Think like a developer who owns this repo:
   - Add a major missing feature that the project clearly needs
   - Build out an incomplete module end to end
   - Create a working example or demo script
   - Add a meaningful integration (API endpoint, CLI command, new pipeline stage)
   - Write a full test suite for an untested module
4. Each commit should be a meaningful chunk of work, not a one-line fix
5. Make a separate git commit for each change with a clear descriptive message
6. Push all commits to origin

Rules:
- DO NOT make trivial changes like adding requirements.txt or fixing typos
- DO NOT just add comments or docstrings — that is not a real contribution
- Every commit should add real working functionality
- If the project is half-built, your job is to build the other half
- Think big — add features, build modules, create demos
- Do not break existing functionality
- Commit message format: short summary, blank line, 1-2 sentences explaining why
"""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger()


def get_repos():
    if not os.path.isdir(REPOS_DIR):
        raise FileNotFoundError(f"repos/ folder not found at {REPOS_DIR}")
    repos = []
    for name in os.listdir(REPOS_DIR):
        path = os.path.join(REPOS_DIR, name)
        if os.path.isdir(path) and os.path.isdir(os.path.join(path, ".git")):
            repos.append((name, path))
    return repos


def run_agent_on_repo(name, path):
    log.info(f"Starting: {name}")
    print(f"\n{'='*50}\n  Working on: {name}\n{'='*50}\n")

    result = subprocess.run(
        ["claude", "--dangerously-skip-permissions", "-p", CLAUDE_PROMPT],
        cwd=path,
        text=True,
    )

    if result.returncode == 0:
        log.info(f"SUCCESS: {name}")
        print(f"\n✓ Done with {name}")
    else:
        log.error(f"FAILED: {name} (exit code {result.returncode})")
        print(f"\n✗ Failed on {name}")


def main():
    log.info("=== daemonctl run started ===")
    repos = get_repos()

    if len(repos) < REPOS_PER_RUN:
        log.error(f"Not enough repos — found {len(repos)}, need {REPOS_PER_RUN}")
        return

    chosen = random.sample(repos, REPOS_PER_RUN)
    log.info(f"Chose: {[n for n, _ in chosen]}")
    print(f"Today's repos: {', '.join(n for n, _ in chosen)}\n")

    for name, path in chosen:
        run_agent_on_repo(name, path)

    log.info("=== daemonctl run complete ===")


if __name__ == "__main__":
    main()
