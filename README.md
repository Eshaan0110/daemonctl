# daemonctl

Autonomous agent that keeps your repos alive. Picks 2 random repos daily, reads the codebase, and pushes meaningful improvements — no input required.

## What it does

Every day at 9am, daemonctl:
- Randomly selects 2 repos from your local collection
- Reads the entire codebase to understand what the project is
- Identifies meaningful improvements — bug fixes, missing tests, incomplete functions, poor documentation, error handling gaps
- Implements each change and commits with a descriptive message
- Pushes to GitHub under your account

All commits appear as yours. No traces of automation.

## Stack

- **Claude Code** — the agent that reads, reasons, and writes
- **Python** — orchestrates repo selection and agent invocation
- **Windows Task Scheduler** — triggers the run daily
- **Git** — commits and pushes under your identity

## Setup

### 1. Install Claude Code
```bash
curl -fsSL https://claude.ai/install.sh | bash
claude login
```

### 2. Clone your repos
```bash
mkdir repos
# clone your repos into the repos/ folder
git clone https://github.com/YOU/your-repo.git repos/your-repo
```

### 3. Schedule it
Open Windows Task Scheduler → Create Basic Task:
- **Program:** `"C:\Program Files\Git\usr\bin\bash.exe"`
- **Arguments:** `-c "cd /d/daemonctl && python agent.py"`
- **Trigger:** Daily at 9:00 AM

### 4. Enable wake on task (optional)
Task properties → Conditions → tick *Wake the computer to run this task*

## Requirements

- Python 3.x
- Claude Code (claude.ai Pro or higher)
- Git for Windows

## Configuration

Edit the top of `agent.py` to change:
```python
REPOS_DIR = "path/to/your/repos"   # folder containing your repos
REPOS_PER_RUN = 2                   # how many repos to work on per day
```

Adjust the `CLAUDE_PROMPT` to change what kinds of improvements the agent focuses on.
