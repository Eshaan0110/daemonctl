import os
import random
import subprocess
import logging
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────
REPOS_DIR = os.path.join(os.path.dirname(__file__), "repos")
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
REPOS_PER_RUN = 2
# ────────────────────────────────────────────────────────────────────────

CLAUDE_PROMPT_FIRST_RUN = """You are an autonomous developer working on this project.

This is your first time seeing this repo.

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
- DO NOT make trivial changes like fixing typos or adding comments
- Every commit should add real working functionality
- If the project is half-built, your job is to build the other half
- Think big — add features, build modules, create demos
- Do not break existing functionality
- NEVER mention Claude, AI, LLM, automation, agents, or daemonctl in commit messages, comments, or code
- Commit messages should sound like a normal developer wrote them
- Commit message format: short summary, blank line, 1-2 sentences explaining why

After all commits are pushed, output a summary in this exact format between the markers:

===MEMORY_START===
# {project name}
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
===MEMORY_END===
"""

CLAUDE_PROMPT_WITH_MEMORY = """You are an autonomous developer working on this project.

Here is your memory from previous sessions:

{memory}

Your job:
1. You already understand this project from the memory above.
2. Check what changed since your last run: `git log --oneline -10`
3. Look at the "Next priorities" section — that's your task list.
4. Scan ONLY the files relevant to your chosen task (not the full repo).
5. Build out the highest-priority item substantially.
6. Each commit should be a meaningful chunk of work, not a one-line fix
7. Make a separate git commit for each change with a clear descriptive message
8. Push all commits to origin

Rules:
- DO NOT make trivial changes like fixing typos or adding comments
- DO NOT redo work listed in the Changelog — it's already done
- Every commit should add real working functionality
- Think big — add features, build modules, create demos
- Do not break existing functionality
- NEVER mention Claude, AI, LLM, automation, agents, or daemonctl in commit messages, comments, or code
- Commit messages should sound like a normal developer wrote them
- Commit message format: short summary, blank line, 1-2 sentences explaining why

After all commits are pushed, output an updated summary in this exact format between the markers:

===MEMORY_START===
# {project name}
Last updated: {today's date}

## Project summary
{keep from previous memory, update if needed}

## Architecture
{keep from previous memory, update with new files}

## Current state
{update to reflect new additions}

## Changelog
{keep all previous entries, add new ones}
- {today's date}: {what you did in this run}

## Next priorities
- {remove completed items, add new ones discovered}

## Gotchas
- {keep previous, add new if any}
===MEMORY_END===
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


def get_memory_path(repo_name):
    """Get the memory file path for a repo (stored centrally, not in the repo)."""
    return os.path.join(MEMORY_DIR, f"{repo_name}.md")


def load_memory(repo_name):
    """Load memory for a repo. Returns content string or None."""
    path = get_memory_path(repo_name)
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def save_memory(repo_name, output):
    """Extract memory block from agent output and save it."""
    start_marker = "===MEMORY_START==="
    end_marker = "===MEMORY_END==="
    start = output.find(start_marker)
    end = output.find(end_marker)
    if start != -1 and end != -1:
        memory = output[start + len(start_marker):end].strip()
        os.makedirs(MEMORY_DIR, exist_ok=True)
        with open(get_memory_path(repo_name), "w", encoding="utf-8") as f:
            f.write(memory)
        log.info(f"  Memory saved for {repo_name}")
    else:
        log.warning(f"  No memory block found in output for {repo_name}")


def run_agent_on_repo(name, path):
    """Run Claude Code on a single repo with the appropriate prompt."""
    log.info(f"Starting: {name}")
    memory = load_memory(name)

    if memory:
        prompt = CLAUDE_PROMPT_WITH_MEMORY.replace("{memory}", memory)
        log.info(f"  Memory found — running incremental mode")
    else:
        prompt = CLAUDE_PROMPT_FIRST_RUN
        log.info(f"  No memory — running full scan mode")

    print(f"\n{'='*50}")
    print(f"  Working on: {name}")
    print(f"  Mode: {'incremental' if memory else 'first run'}")
    print(f"{'='*50}\n")

    try:
        result = subprocess.run(
            ["claude", "--dangerously-skip-permissions", "-p", prompt],
            cwd=path,
            text=True,
            capture_output=True,
            timeout=1200,
        )

        if result.returncode == 0:
            log.info(f"SUCCESS: {name}")
            print(f"\n✓ Done with {name}")
            save_memory(name, result.stdout)
        else:
            log.error(f"FAILED: {name} (exit code {result.returncode})")
            print(f"\n✗ Failed on {name}")
            if result.stderr:
                log.error(f"  stderr: {result.stderr[:500]}")

    except subprocess.TimeoutExpired:
        log.warning(f"TIMEOUT: {name} — exceeded 20 min, skipping")
        print(f"\n⏰ Timeout on {name}, moving on")


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