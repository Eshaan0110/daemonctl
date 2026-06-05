import os
import random
import subprocess
import logging
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────
REPOS_DIR = os.path.join(os.path.dirname(__file__), "repos")
REPOS_PER_RUN = 2
MEMORY_FILE = ".daemonctl_memory.md"
# ────────────────────────────────────────────────────────────────────────

CLAUDE_PROMPT_FIRST_RUN = """You are an autonomous developer working on this project.

This is your FIRST TIME seeing this repo. No memory file exists yet.

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

AFTER you finish your work, create a file called `.daemonctl_memory.md` in the repo root with this structure:

```markdown
# daemonctl memory — {project name}
Last updated: {today's date}

## Project summary
{2-3 sentences: what this project is, what stack it uses}

## Architecture
{folder structure overview, key files and what they do}

## Current state
{what's been built, what's working}

## Changelog
- {today's date}: {what you did in this run}

## Next priorities
- {what should be done next, ordered by impact}
- {be specific — name files, functions, features}

## Gotchas
- {any patterns, quirks, or things to watch out for}
```

Commit this memory file with message: "chore: init daemonctl memory"

Rules:
- DO NOT make trivial changes like fixing typos or adding comments
- Every commit should add real working functionality
- If the project is half-built, your job is to build the other half
- Think big — add features, build modules, create demos
- Do not break existing functionality
- Commit message format: short summary, blank line, 1-2 sentences explaining why
"""

CLAUDE_PROMPT_WITH_MEMORY = """You are an autonomous developer working on this project.

A memory file (`.daemonctl_memory.md`) exists from your previous runs.

Your job:
1. Read `.daemonctl_memory.md` FIRST — this is your memory. You already understand this project.
2. Check what changed since your last run: `git log --oneline -10`
3. Look at the "Next priorities" section — that's your task list.
4. Scan ONLY the files relevant to your chosen task (not the full repo).
5. Build out the highest-priority item. Think like a developer who owns this repo:
   - Add a major missing feature that the project clearly needs
   - Build out an incomplete module end to end
   - Create a working example or demo script
   - Add a meaningful integration (API endpoint, CLI command, new pipeline stage)
   - Write a full test suite for an untested module
6. Each commit should be a meaningful chunk of work, not a one-line fix
7. Make a separate git commit for each change with a clear descriptive message
8. Push all commits to origin

AFTER you finish your work, UPDATE `.daemonctl_memory.md`:
- Update "Last updated" date
- Update "Current state" to reflect new additions
- Add entries to "Changelog" with today's date
- Update "Next priorities" — remove what you did, add new items you discovered
- Add any new "Gotchas" you found

Commit the updated memory file with message: "chore: update daemonctl memory"

Rules:
- DO NOT make trivial changes like fixing typos or adding comments
- DO NOT redo work listed in the Changelog — it's already done
- Every commit should add real working functionality
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
    """Discover all git repos in the repos/ directory."""
    if not os.path.isdir(REPOS_DIR):
        raise FileNotFoundError(f"repos/ folder not found at {REPOS_DIR}")
    repos = []
    for name in os.listdir(REPOS_DIR):
        path = os.path.join(REPOS_DIR, name)
        if os.path.isdir(path) and os.path.isdir(os.path.join(path, ".git")):
            repos.append((name, path))
    return repos


def has_memory(repo_path):
    """Check if a repo has a daemonctl memory file."""
    return os.path.isfile(os.path.join(repo_path, MEMORY_FILE))


def run_agent_on_repo(name, path):
    """Run Claude Code on a single repo with the appropriate prompt."""
    log.info(f"Starting: {name}")
    memory_exists = has_memory(path)

    if memory_exists:
        prompt = CLAUDE_PROMPT_WITH_MEMORY
        log.info(f"  Memory found — running incremental mode")
    else:
        prompt = CLAUDE_PROMPT_FIRST_RUN
        log.info(f"  No memory — running full scan mode")

    print(f"\n{'='*50}")
    print(f"  Working on: {name}")
    print(f"  Mode: {'incremental (memory exists)' if memory_exists else 'first run (full scan)'}")
    print(f"{'='*50}\n")

    result = subprocess.run(
        ["claude", "--dangerously-skip-permissions", "-p", prompt],
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