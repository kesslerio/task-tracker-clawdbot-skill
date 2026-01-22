#!/usr/bin/env python3
"""
Shared utilities for task tracker scripts.
Supports both Work Tasks and Personal Tasks.
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Single source of truth: Obsidian
WORK_TASKS_FILE = Path.home() / "Obsidian" / "03-Areas" / "ShapeScale" / "Work Tasks.md"
PERSONAL_TASKS_FILE = Path.home() / "Obsidian" / "03-Areas" / "Personal" / "Personal Tasks.md"
ARCHIVE_DIR = Path.home() / "clawd" / "memory" / "work"


def get_current_quarter() -> str:
    """Return current quarter string like '2026-Q1'."""
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"{now.year}-Q{quarter}"


def get_tasks_file(personal: bool = False) -> Path:
    """Get the appropriate tasks file."""
    return PERSONAL_TASKS_FILE if personal else WORK_TASKS_FILE


def parse_tasks(content: str, personal: bool = False) -> dict:
    """Parse Obsidian Tasks.md content into categorized task lists.
    
    Supports emoji date format: 🗓️YYYY-MM-DD
    Inline fields: area::, goal::, owner::
    Eisenhower sections: Q1, Q2, Q3, Team, Backlog
    
    Args:
        content: File content to parse
        personal: If True, use personal task categories
    
    Returns dict with keys:
    - q1: list of Q1 (Urgent & Important) tasks
    - q2: list of Q2 (Important, Not Urgent) tasks
    - q3: list of Q3 (Waiting/Blocked) tasks
    - team: list of Team Tasks (monitored) - work only
    - backlog: list of Backlog (someday/maybe) tasks
    - done: list of completed tasks
    - due_today: list of tasks due today
    - all: list of all tasks
    """
    result = {
        'q1': [],
        'q2': [],
        'q3': [],
        'team': [],
        'backlog': [],
        'done': [],
        'due_today': [],
        'all': [],
    }
    
    section_mapping = {
        '🔴': 'q1',
        '🟡': 'q2',
        '🟠': 'q3',
        '👥': 'team',
        '⚪': 'backlog',
        '✅': 'done',
    }
    
    # Personal task sections differ slightly
    personal_section_mapping = {
        '🔴': 'q1',
        '🟡': 'q2',
        '🟠': 'q3',
        '⚪': 'backlog',
        '✅': 'done',
    }
    
    mapping = personal_section_mapping if personal else section_mapping
    
    current_section = None
    current_task = None
    today = datetime.now().date()
    
    for line in content.split('\n'):
        # Detect section headers (Eisenhower quadrants)
        if line.startswith('## '):
            section_match = re.match(r'## ([🔴🟡🟠👥⚪✅]) (?:.*?: )?(.+)', line)
            if section_match:
                current_section = mapping.get(section_match.group(1))
            continue
        
        # Detect task line with emoji date
        task_match = re.match(r'^- \[([ x])\] \*\*(.+?)\*\*(.*)$', line)
        if task_match:
            done = task_match.group(1) == 'x'
            title = task_match.group(2).strip()
            rest = task_match.group(3).strip()
            
            # Parse emoji date and inline fields
            due_str = None
            area = None
            goal = None
            owner = None
            
            date_match = re.search(r'🗓️(\d{4}-\d{2}-\d{2})', rest)
            if date_match:
                due_str = date_match.group(1)
            
            for field in ['area::', 'goal::', 'owner::']:
                field_match = re.search(rf'{field}([^\s]+)', rest)
                if field_match:
                    value = field_match.group(1).strip()
                    if field == 'area::':
                        area = value
                    elif field == 'goal::':
                        goal = value
                    elif field == 'owner::':
                        owner = value
            
            current_task = {
                'title': title,
                'done': done,
                'section': current_section,
                'due': due_str,
                'area': area,
                'goal': goal,
                'owner': owner,
                'raw_line': line,
            }
            
            result['all'].append(current_task)
            
            if done:
                result['done'].append(current_task)
            elif current_section:
                result[current_section].append(current_task)
            
            # Check if due today
            if due_str and not done:
                try:
                    due_date = datetime.strptime(due_str, '%Y-%m-%d').date()
                    if due_date == today:
                        result['due_today'].append(current_task)
                except ValueError:
                    pass
            
            continue
        
        # Handle task continuation
        if current_task and line.startswith('  - '):
            meta_line = line.strip()[2:].strip()
            
            if meta_line.lower().startswith('due:'):
                due_str = meta_line.split(':', 1)[1].strip()
                if not current_task['due']:
                    current_task['due'] = due_str
            elif meta_line.lower().startswith('blocks:'):
                current_task['blocks'] = meta_line.split(':', 1)[1].strip()
            elif meta_line.lower().startswith('owner:') and not current_task.get('owner'):
                current_task['owner'] = meta_line.split(':', 1)[1].strip()
    
    return result


def load_tasks(personal: bool = False) -> tuple[str, dict]:
    """Load and parse tasks from Obsidian file."""
    tasks_file = get_tasks_file(personal)
    
    if not tasks_file.exists():
        print(f"\n❌ Tasks file not found: {tasks_file}\n", file=sys.stderr)
        print("Make sure the Obsidian vault is accessible.\n")
        sys.exit(1)
    
    content = tasks_file.read_text()
    tasks = parse_tasks(content, personal)
    return content, tasks


def check_due_date(due: str, check_type: str = 'today') -> bool:
    """Check if a due date matches the given type."""
    if not due:
        return check_type == 'today'
    
    today = datetime.now().date()
    week_end = today + timedelta(days=(6 - today.weekday()))
    
    try:
        due_date = datetime.strptime(due, '%Y-%m-%d').date()
        
        if check_type == 'today':
            return due_date <= today
        elif check_type == 'this-week':
            return due_date <= week_end
        elif check_type == 'overdue':
            return due_date < today
    except ValueError:
        pass
    
    return False


def get_section_display_name(section: str, personal: bool = False) -> str:
    """Get human-readable section name."""
    section_names = {
        'q1': '🔴 Q1: Urgent & Important',
        'q2': '🟡 Q2: Important, Not Urgent',
        'q3': '🟠 Q3: Waiting / Blocked',
        'team': '👥 Team Tasks',
        'backlog': '⚪ Backlog',
        'done': '✅ Done',
    }
    
    if personal:
        section_names['q1'] = '🔴 Must Do Today'
        section_names['q2'] = '🟡 Should Do This Week'
        section_names['q3'] = '🟠 Waiting On'
    
    return section_names.get(section, section or 'Uncategorized')
