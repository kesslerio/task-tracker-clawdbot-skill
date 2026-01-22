#!/usr/bin/env python3
"""
Shared utilities for task tracker scripts.
Supports both Obsidian (preferred) and legacy TASKS.md formats.
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Try Obsidian first, fall back to legacy
OBSIDIAN_WORK = Path.home() / "Obsidian" / "03-Areas" / "ShapeScale" / "Work Tasks.md"
OBSIDIAN_PERSONAL = Path.home() / "Obsidian" / "03-Areas" / "Personal" / "Personal Tasks.md"
LEGACY_WORK = Path.home() / "clawd" / "memory" / "work" / "TASKS.md"
ARCHIVE_DIR = Path.home() / "clawd" / "memory" / "work"


def get_current_quarter() -> str:
    """Return current quarter string like '2026-Q1'."""
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"{now.year}-Q{quarter}"


def get_tasks_file(personal: bool = False, force_legacy: bool = False) -> tuple[Path, str]:
    """Get the appropriate tasks file and its format.
    
    Returns:
        tuple: (file_path, format) where format is 'obsidian' or 'legacy'
    """
    if force_legacy:
        return LEGACY_WORK, 'legacy'
    
    # Try Obsidian first
    obsidian_file = OBSIDIAN_PERSONAL if personal else OBSIDIAN_WORK
    if obsidian_file.exists():
        return obsidian_file, 'obsidian'
    
    # Fall back to legacy for work tasks only
    if not personal and LEGACY_WORK.exists():
        return LEGACY_WORK, 'legacy'
    
    # Return Obsidian path anyway (will show error if missing)
    return obsidian_file, 'obsidian'


def parse_tasks(content: str, personal: bool = False, format: str = 'obsidian') -> dict:
    """Parse tasks content into categorized task lists.
    
    Args:
        content: File content to parse
        personal: If True, use personal task categories
        format: 'obsidian' or 'legacy'
    
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
    
    # Personal task sections differ
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
        # Detect section headers
        if line.startswith('## '):
            if format == 'obsidian':
                section_match = re.match(r'## ([🔴🟡🟠👥⚪✅]) (?:.*?: )?(.+)', line)
            else:
                # Legacy format: ## 🔴 High Priority
                section_match = re.match(r'## ([🔴🟡🟢📅✅]) (.+)', line)
            
            if section_match:
                emoji = section_match.group(1)
                current_section = mapping.get(emoji)
            continue
        
        # Detect task line
        if format == 'obsidian':
            # Obsidian: - [ ] **Task name** 🗓️2026-01-22 area:: Sales
            task_match = re.match(r'^- \[([ x])\] \*\*(.+?)\*\*(.*)$', line)
        else:
            # Legacy: - [ ] **Task name** — Description
            task_match = re.match(r'^- \[([ x])\] \*\*(.+?)\*\*(.*)$', line)
        
        if task_match:
            done = task_match.group(1) == 'x'
            title = task_match.group(2).strip()
            rest = task_match.group(3).strip()
            
            due_str = None
            area = None
            
            if format == 'obsidian':
                # Parse emoji date and inline fields
                date_match = re.search(r'🗓️(\d{4}-\d{2}-\d{2})', rest)
                if date_match:
                    due_str = date_match.group(1)
                
                for field in ['area::', 'goal::', 'owner::']:
                    field_match = re.search(rf'{field}([^\s]+)', rest)
                    if field_match:
                        value = field_match.group(1).strip()
                        if field == 'area::':
                            area = value
            else:
                # Legacy: Parse "Due: X" and extract from description
                due_match = re.search(r'Due:\s*([^\s—]+)', rest)
                if due_match:
                    due_str = due_match.group(1)
                
                # Extract area from category headers if we tracked them
                # Legacy format doesn't have area field
            
            current_task = {
                'title': title,
                'done': done,
                'section': current_section,
                'due': due_str,
                'area': area,
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
        
        # Handle task continuation (indented lines)
        if current_task and line.startswith('  - '):
            meta_line = line.strip()[2:].strip()
            
            if format == 'legacy':
                if meta_line.lower().startswith('due:'):
                    due_str = meta_line.split(':', 1)[1].strip()
                    if not current_task['due']:
                        current_task['due'] = due_str
                elif meta_line.lower().startswith('blocks:'):
                    current_task['blocks'] = meta_line.split(':', 1)[1].strip()
    
    return result


def load_tasks(personal: bool = False, force_legacy: bool = False) -> tuple[str, dict]:
    """Load and parse tasks from file."""
    tasks_file, format = get_tasks_file(personal, force_legacy)
    
    if not tasks_file.exists():
        task_type = "Personal" if personal else "Work"
        source = "Obsidian" if format == 'obsidian' else "legacy"
        
        print(f"\n❌ {task_type} tasks file not found: {tasks_file}\n", file=sys.stderr)
        
        if format == 'obsidian':
            print(f"Hint: This skill reads from Obsidian by default.")
            print(f"Make sure: ~/Obsidian/03-Areas/{'Personal' if personal else 'ShapeScale'}/{'Personal Tasks.md' if personal else 'Work Tasks.md'}")
        else:
            print(f"Hint: Legacy format at: {LEGACY_WORK}")
        
        sys.exit(1)
    
    content = tasks_file.read_text()
    tasks = parse_tasks(content, personal, format)
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
    
    return section_names.get(section, section or 'Uncategorized')
