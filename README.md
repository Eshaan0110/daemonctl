# daemonctl

Autonomous agent that keeps your repos alive. Picks 2 random repos daily, reads the codebase, and pushes meaningful improvements — no input required.

## What it does

Every day at a scheduled time, daemonctl:
- Randomly selects 2 repos from your local collection
- Reads the codebase to understand what the project is
- Identifies meaningful improvements — missing features, incomplete modules, untested code, missing demos
- Implements each change and commits with a descriptive message
- Pushes to GitHub under your account

## Persistent memory

daemonctl maintains a memory file per repo in a local `memory/` folder (never committed to your repos).

**First run** — reads the entire codebase, builds out features, and saves a memory summary covering the project architecture, current state, and next priorities.

**Subsequent runs** — reads only the memory summary instead of re-scanning the entire repo. Picks up where it left off using the prioritized task list from the previous run.

This cuts token usage by ~80-90% on repeat visits and prevents the agent from redoing work or losing context between runs.

## Stack

- **Claude Code** — the agent that reads, reasons, and writes
- **Python** — orchestrates repo selection and agent invocation
- **Task Scheduler / Cron** — triggers the run on a schedule
- **Git** — commits and pushes under your identity

## Setup

### 1. Install Claude Code
```bash
curl -fsSL https://claude.ai/install.sh | bash
claude login
```

### 2. Clone this repo and add your repos
```bash
git clone https://github.com/YOUR_USERNAME/daemonctl.git
cd daemonctl
```

Clone your repos into the `repos/` folder:
```bash
git clone https://github.com/YOUR_USERNAME/your-repo.git repos/your-repo
```

Or use the helper script — edit `add-repos.sh` with your GitHub username and repo names, then:
```bash
chmod +x add-repos.sh
./add-repos.sh
```

### 3. Schedule it

**Linux / macOS (cron):**
```bash
crontab -e
# Add this line (runs daily at 9am):
0 9 * * * cd /path/to/daemonctl && python3 agent.py >> /tmp/daemonctl.log 2>&1
```

**Windows (Task Scheduler):**

Open Task Scheduler → Create Basic Task:
- **Program:** `"C:\Program Files\Git\usr\bin\bash.exe"`
- **Arguments:** `-c "cd /d/daemonctl && python agent.py"`
- **Trigger:** Daily at 9:00 AM

## Configuration

Edit the top of `agent.py`:
```python
REPOS_DIR = "path/to/your/repos"   # folder containing your repos
REPOS_PER_RUN = 2                   # how many repos to work on per day
```

The two prompt variables (`CLAUDE_PROMPT_FIRST_RUN` and `CLAUDE_PROMPT_WITH_MEMORY`) control what kinds of improvements the agent focuses on. Edit these to match your priorities.

## How memory works

Memory files are stored locally in `daemonctl/memory/` — one per repo. They never touch your actual repos.

```
daemonctl/
  memory/
    meshmerize.md       ← memory for meshmerize repo
    rl-navigation-agent.md
  repos/
    meshmerize/         ← the actual repo (clean, no traces)
    rl-navigation-agent/
```

The agent outputs a memory block after each run which gets parsed and saved automatically. On the next run, memory is injected into the prompt so the agent skips the full codebase scan.

## Timeout

Each repo has a 20-minute timeout. If Claude Code takes longer, daemonctl skips that repo and moves to the next one.

## Requirements

- Python 3.x
- Claude Code (requires a Claude subscription)
- Git with push access to your repos