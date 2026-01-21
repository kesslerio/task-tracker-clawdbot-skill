#!/usr/bin/env bash
# Telegram slash command wrapper for task-tracker skill
# Usage: telegram-commands.sh {daily|weekly|done24h|done7d}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
  daily)
    python3 "$SCRIPT_DIR/standup.py"
    ;;
  weekly)
    python3 "$SCRIPT_DIR/tasks.py" list --priority high,medium
    ;;
  done24h)
    # Show completed tasks from last 24 hours
    python3 "$SCRIPT_DIR/tasks.py" list --status done | grep -A 10 "$(date -d '1 day ago' '+%Y-%m-%d')" || echo "No tasks completed in last 24 hours"
    ;;
  done7d)
    # Show completed tasks from last 7 days
    python3 "$SCRIPT_DIR/tasks.py" list --status done | grep -A 50 "$(date -d '7 days ago' '+%Y-%m-%d')" || echo "No tasks completed in last 7 days"
    ;;
  *)
    echo "Usage: $0 {daily|weekly|done24h|done7d}"
    exit 1
    ;;
esac
