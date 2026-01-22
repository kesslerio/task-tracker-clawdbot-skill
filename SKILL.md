---
name: task-tracker
description: "Personal task management with daily standups and weekly reviews. Supports both Work and Personal tasks from Obsidian. Use when: (1) User says 'daily standup' or asks what's on my plate, (2) User says 'weekly review' or asks about last week's progress, (3) User wants to add/update/complete tasks, (4) User asks about blockers or deadlines, (5) User shares meeting notes and wants tasks extracted, (6) User asks 'what's due this week' or similar."
homepage: https://github.com/kesslerio/task-tracker-clawdbot-skill
metadata: {"clawdbot":{"emoji":"📋","requires":{"files":["~/Obsidian/03-Areas/ShapeScale/Work Tasks.md","~/Obsidian/03-Areas/Personal/Personal Tasks.md"]},"install":[{"id":"verify-obsidian","kind":"check","label":"Verify Obsidian vault access"}]}}
---

<div align="center">

![Task Tracker](https://img.shields.io/badge/Task_Tracker-Clawdbot_skill-blue?style=for-the-badge&logo=checklist)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=flat-square&logo=python)
![Status](https://img.shields.io/badge/Status-Production-green?style=flat-square)
![Issues](https://img.shields.io/badge/Issues-0-black?style=flat-square)
![Last Updated](https://img.shields.io/badge/Last_Updated-Jan_2026-orange?style=flat-square)

**Personal task management with daily standups and weekly reviews**

[Homepage](https://github.com/kesslerio/task-tracker-clawdbot-skill) • [Trigger Patterns](#what-this-skill-does) • [Commands](#commands-reference)

</div>

---

# Task Tracker

A personal task management skill for daily standups and weekly reviews. Tracks work and personal tasks from your Obsidian vault, surfaces priorities, and manages blockers.

---

## What This Skill Does

1. **Lists tasks** - Shows what's on your plate, filtered by priority, status, or deadline
2. **Daily standup** - Shows today's #1 priority, blockers, and what was completed (Work & Personal)
3. **Weekly review** - Summarizes last week, archives done items, plans this week
4. **Add tasks** - Create new tasks with priority and due date
5. **Complete tasks** - Mark tasks as done
6. **Extract from notes** - Pull action items from meeting notes
7. **Dual support** - Separate Work and Personal task workflows

---

## Obsidian Setup

This skill reads tasks directly from your Obsidian vault. No separate task files needed.

### Required Files

| Task Type | Obsidian Path |
|-----------|---------------|
| Work | `~/Obsidian/03-Areas/ShapeScale/Work Tasks.md` |
| Personal | `~/Obsidian/03-Areas/Personal/Personal Tasks.md` |

### Task Format

Tasks use the **emoji date format** for Dataview compatibility:

```markdown
- [ ] **Task name** 🗓️2026-01-22 area:: Sales
  - Additional notes here
```

#### Inline Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `🗓️YYYY-MM-DD` | Due date | `🗓️2026-01-22` |
| `area::` | Category/area | `area:: Sales` |
| `goal::` | Weekly goal link | `goal:: [[2026-W04]]` |
| `owner::` | Task owner | `owner:: Lilla` |

#### Section Structure (Eisenhower Matrix)

```markdown
## 🔴 Q1: Do Now (Urgent & Important)
## 🟡 Q2: Schedule (Important, Not Urgent)
## 🟠 Q3: Waiting (Blocked on External)
## 👥 Team Tasks (Monitor/Check-in)
## ⚪ Q4: Backlog (Someday/Maybe)
## ✅ Done
```

### Personal Tasks Section Structure

```markdown
## 🔴 Must Do Today
## 🟡 Should Do This Week
## 🟠 Waiting On
## ⚪ Backlog
## ✅ Done
```

---

## File Structure

```
~/Obsidian/
├── 03-Areas/
│   ├── ShapeScale/
│   │   └── Work Tasks.md      # Work tasks (Eisenhower format)
│   └── Personal/
│       └── Personal Tasks.md   # Personal tasks
```

**Legacy format (deprecated):**
```
~/clawd/memory/work/
├── TASKS.md              # No longer used
└── ARCHIVE-YYYY-QX.md    # Archived completed tasks
```

---

## Quick Start

### List Work Tasks
```bash
python3 scripts/tasks.py list

# Due today
python3 scripts/tasks.py list --due today

# By priority
python3 scripts/tasks.py list --priority high
```

### List Personal Tasks
```bash
python3 scripts/tasks.py --personal list

# Due today
python3 scripts/tasks.py --personal list --due today
```

### Daily Standup
```bash
# Work standup
python3 scripts/standup.py

# Personal standup
python3 scripts/personal_standup.py
```

### Weekly Review
```bash
python3 scripts/weekly_review.py
```

---

## Commands Reference

### List Tasks
```bash
# All tasks
tasks.py list
tasks.py --personal list

# Only high priority
tasks.py list --priority high
tasks.py --personal list --priority high

# Due today or this week
tasks.py list --due today
tasks.py list --due this-week

# Only blocked
tasks.py blockers
```

### Add Task
```bash
# Work task
tasks.py add "Draft project proposal" --priority high --due 2026-01-23

# Personal task
tasks.py --personal add "Call mom" --priority high --due 2026-01-22
```

### Complete Task
```bash
tasks.py done "proposal"  # Fuzzy match - finds "Draft project proposal"
tasks.py --personal done "call mom"
```

### Show Blockers
```bash
tasks.py blockers              # All blocking tasks
tasks.py blockers --person sarah  # Only blocking Sarah
```

### Extract from Meeting Notes
```bash
extract_tasks.py --from-text "Meeting: discuss Q1 planning, Sarah to own budget review"
# Outputs: tasks.py add "Discuss Q1 planning" --priority medium
#          tasks.py add "Sarah to own budget review" --owner sarah
```

---

## Priority Levels (Work)

| Icon | Meaning | When to Use |
|------|---------|-------------|
| 🔴 **Q1** | Critical, blocking, deadline-driven | Revenue impact, blocking others |
| 🟡 **Q2** | Important but not urgent | Reviews, feedback, planning |
| 🟠 **Q3** | Waiting on external | Blocked by others |
| 👥 **Team** | Monitor team tasks | Delegated, check-in only |
| ⚪ **Backlog** | Someday/maybe | Low priority |

## Priority Levels (Personal)

| Icon | Meaning |
|------|---------|
| 🔴 **Must Do Today** | Non-negotiable today |
| 🟡 **Should Do This Week** | Important, flexible timing |
| 🟠 **Waiting On** | Blocked by others/external |
| ⚪ **Backlog** | Someday/maybe |

---

## Status Workflow

```
Todo → In Progress → Done
      ↳ Blocked (waiting on external)
      ↳ Waiting (delegated, monitoring)
```

---

## Automation (Cron)

| Job | When | What |
|-----|------|------|
| Daily Work Standup | Weekdays 8:30 AM | Posts to Telegram Journaling group |
| Daily Personal Standup | Daily 8:00 AM | Posts to Telegram Journaling group |
| Weekly Review | Mondays 9:00 AM | Posts summary, archives done items |

---

## Natural Language Triggers

| You Say | Skill Does |
|---------|-----------|
| "daily standup" | Runs work standup, posts to Journaling |
| "personal standup" | Runs personal standup, posts to Journaling |
| "weekly review" | Runs weekly review, posts summary |
| "what's on my plate?" | Lists all work tasks |
| "personal tasks" | Lists all personal tasks |
| "what's blocking Lilla?" | Shows tasks blocking Lilla |
| "mark IMCAS done" | Completes matching work task |
| "what's due this week?" | Lists work tasks due this week |
| "add task: X" | Adds work task X to Obsidian |
| "add personal task: X" | Adds personal task X to Obsidian |
| "extract tasks from: [notes]" | Parses notes, outputs add commands |

---

## Examples

**Morning work check-in:**
```
$ python3 scripts/standup.py

📋 Daily Standup — Tuesday, January 21

🎯 #1 Priority: Complete project proposal draft
   ↳ Blocking: Sarah (client review)

⏰ Due Today:
  • Complete project proposal draft
  • Schedule team sync

🔴 High Priority:
  • Review Q1 budget (due: 2026-01-23)
```

**Personal task check-in:**
```
$ python3 scripts/personal_standup.py

🏠 Personal Daily Standup — Thursday, January 22

🎯 #1 Priority: Quality time with parents

🟡 Should Do This Week:
  • Call mom (🗓️2026-01-23)
  • Gym session (🗓️2026-01-25)
```

**Adding a task:**
```
$ python3 scripts/tasks.py add "Draft blog post" --priority high --due 2026-01-25

✅ Added task: Draft blog post
```

**Extracting from meeting notes:**
```
$ python3 scripts/extract_tasks.py --from-text "Meeting: Sarah needs budget review, create project timeline"

# Extracted 2 task(s) from meeting notes
# Run these commands to add them:

tasks.py add "Budget review for Sarah" --priority high
tasks.py add "Create project timeline" --priority medium
```

---

## Integration Points

- **Telegram Journaling group:** Standup/review summaries posted automatically
- **Obsidian:** Daily standups logged to `01-Daily/YYYY-MM-DD.md`
- **MEMORY.md:** Patterns and recurring blockers promoted during weekly reviews
- **Cron:** Automated standups and reviews (Work + Personal)

---

## Troubleshooting

**"Tasks file not found"**
```bash
# Verify Obsidian vault is accessible
ls ~/Obsidian/03-Areas/ShapeScale/Work Tasks.md
ls ~/Obsidian/03-Areas/Personal/Personal Tasks.md

# Create task files from templates if needed
# See: https://github.com/kesslerio/task-tracker-clawdbot-skill/tree/main/assets/templates
```

**Tasks not showing up**
- Check Obsidian files exist at the paths above
- Verify task format uses emoji dates (`🗓️YYYY-MM-DD`)
- Run `tasks.py list --json` to debug parsing

**Date parsing issues**
- Due dates must use: `🗓️YYYY-MM-DD` format
- Examples: `🗓️2026-01-22`, `🗓️2026-12-31`
- The emoji date is required for Dataview compatibility

---

## Files

| File | Purpose |
|------|---------|
| `scripts/tasks.py` | Main CLI - list, add, done, blockers (supports --personal) |
| `scripts/standup.py` | Work daily standup generator |
| `scripts/personal_standup.py` | Personal daily standup generator |
| `scripts/weekly_review.py` | Weekly review generator |
| `scripts/extract_tasks.py` | Extract tasks from meeting notes |
| `scripts/utils.py` | Shared utilities (DRY) |
| `assets/templates/` | Templates for Obsidian task files |

---

## Dataview Integration

This skill is designed to work seamlessly with Dataview in Obsidian.

### Daily Note Query (Work Tasks)

```dataview
TASK
FROM "03-Areas/ShapeScale/Work Tasks.md"
WHERE due = date("today")
SORT due ASC
LIMIT 10
```

### Daily Note Query (Personal Tasks)

```dataview
TASK
FROM "03-Areas/Personal/Personal Tasks.md"
WHERE due = date("today")
SORT due ASC
LIMIT 10
```

### Completed Today (Work)

```dataview
TASK
FROM "03-Areas/ShapeScale/Work Tasks.md"
WHERE completed AND due = date("today")
SORT file.mtime DESC
```

---

## Migrating from Legacy Format

If you were using the old `~/clawd/memory/work/TASKS.md`:

1. **Move your tasks** to `~/Obsidian/03-Areas/ShapeScale/Work Tasks.md`
2. **Convert dates** from `Due: ASAP` to `🗓️2026-01-22`
3. **Convert sections** from `## High Priority` to `## 🔴 Q1: Do Now`
4. **Remove inline metadata** - convert `  - Due: 2026-01-22` to `🗓️2026-01-22`

The skill now reads directly from Obsidian, eliminating file synchronization issues.
