import os
import random
import subprocess
import logging
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────
REPOS_DIR = os.path.join(os.path.dirname(__file__), "repos")
REPOS_PER_RUN = 2
# ────────────────────────────────────────────────────────────────────────

CLAUDE_PROMPT = """You are an autonomous repo improvement agent.

Your job:
1. Read the entire codebase — README, source files, tests, open TODOs, comments
2. Understand what this project is trying to do and what is incomplete or broken
3. Choose 2-3 meaningful improvements you can make. Good options:
   - Fix a bug or broken functionality
   - Add missing tests for existing code
   - Add the next logical feature that is currently missing
   - Complete a TODO or half-finished function
   - Improve or add missing documentation / README sections
   - Add error handling where it's missing
   - Fix broken imports or outdated dependencies
   - Refactor a messy function (without changing behaviour)
   - most importantly go ahead and build the project bit by bit until it's working and complete
4. Implement each improvement one at a time
5. Make a separate git commit for each change with a clear descriptive message
6. Push all commits to origin

Rules:
- Do not break existing functionality
- Do not change the overall architecture or direction of the project
- Keep each change small and focused
- If you are unsure what the project does, read more files before acting
- Commit message format: short summary line, blank line, 1-2 sentences explaining why
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
