#!/usr/bin/env python3
"""
Task Tracker CLI - Supports both Work and Personal tasks.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from utils import (
    get_tasks_file,
    get_section_display_name,
    parse_tasks,
    load_tasks,
    check_due_date,
    get_current_quarter,
)


def list_tasks(args):
    """List tasks with optional filters."""
    _, tasks_data = load_tasks(args.personal)
    tasks = tasks_data['all']
    
    # Apply filters
    filtered = tasks
    
    if args.priority:
        priority_map = {
            'high': 'q1',
            'medium': 'q2',
            'low': 'backlog',
        }
        target_key = priority_map.get(args.priority.lower())
        if target_key:
            filtered = tasks_data.get(target_key, [])
    
    if args.status:
        normalized_status = args.status.lower().replace('-', ' ')
        filtered = [t for t in filtered if t.get('status', '').lower().replace('-', ' ') == normalized_status]
    
    if args.due:
        filtered = [t for t in filtered if check_due_date(t.get('due', ''), args.due)]
    
    if not filtered:
        task_type = "Personal" if args.personal else "Work"
        print(f"No {task_type} tasks found matching criteria.")
        return
    
    print(f"\n📋 {('Personal' if args.personal else 'Work')} Tasks ({len(filtered)} items)\n")
    
    current_section = None
    for task in filtered:
        section = task.get('section')
        if section != current_section:
            current_section = section
            print(f"### {get_section_display_name(section, args.personal)}\n")
        
        checkbox = '✅' if task['done'] else '⬜'
        due_str = f" (🗓️{task['due']})" if task.get('due') else ''
        area_str = f" [{task.get('area')}]" if task.get('area') else ''
        
        print(f"{checkbox} **{task['title']}**{due_str}{area_str}")
        if task.get('description'):
            print(f"   {task['description']}")


def add_task(args):
    """Add a new task."""
    tasks_file = get_tasks_file(args.personal)
    content = tasks_file.read_text()
    
    # Build task entry
    priority_section = {
        'high': '🔴 Q1',
        'medium': '🟡 Q2',
        'low': '⚪ Backlog',
    }.get(args.priority, '🟡 Q2')
    
    task_lines = [f'- [ ] **{args.title}**']
    if args.due:
        task_lines.append(f'  🗓️{args.due}')
    if args.owner and args.owner != 'martin' and args.owner != 'me':
        task_lines.append(f'  owner:: {args.owner}')
    if args.area:
        task_lines.append(f'  area:: {args.area}')
    
    task_entry = '\n'.join(task_lines)
    
    # Find section and insert
    import re
    section_pattern = rf'(## {re.escape(priority_section)}.*?\n)(.*?)(\n## |\n---|\Z)'
    match = re.search(section_pattern, content, re.DOTALL)
    
    if match:
        insert_content = match.group(2).rstrip() + '\n\n' + task_entry + '\n'
        new_content = content[:match.start(2)] + insert_content + content[match.end(2):]
        tasks_file.write_text(new_content)
        task_type = "Personal" if args.personal else "Work"
        print(f"✅ Added {task_type} task: {args.title}")
    else:
        print(f"⚠️ Section '{priority_section}' not found. Add manually.")


def done_task(args):
    """Mark a task as done using fuzzy matching."""
    tasks_file = get_tasks_file(args.personal)
    content = tasks_file.read_text()
    tasks_data = parse_tasks(content, args.personal)
    tasks = tasks_data['all']
    
    query = args.query.lower()
    matches = [t for t in tasks if query in t['title'].lower() and not t['done']]
    
    if not matches:
        print(f"No matching task found for: {args.query}")
        return
    
    if len(matches) > 1:
        print(f"Multiple matches found:")
        for i, t in enumerate(matches, 1):
            print(f"  {i}. {t['title']}")
        print("\nBe more specific.")
        return
    
    task = matches[0]
    
    # Update in content
    old_line = task['raw_lines'][0]
    new_line = old_line.replace('- [ ]', '- [x]')
    
    new_content = content.replace(old_line, new_line)
    tasks_file.write_text(new_content)
    task_type = "Personal" if args.personal else "Work"
    print(f"✅ Completed {task_type} task: {task['title']}")


def show_blockers(args):
    """Show tasks that are blocking others."""
    _, tasks_data = load_tasks(args.personal)
    blockers = [t for t in tasks_data['all'] if t.get('blocks') and not t['done']]
    
    if args.person:
        blockers = [t for t in blockers if args.person.lower() in t['blocks'].lower()]
    
    if not blockers:
        print("No blocking tasks found.")
        return
    
    print(f"\n🚧 Blocking Tasks ({len(blockers)} items)\n")
    
    for task in blockers:
        print(f"⬜ **{task['title']}**")
        print(f"   Blocks: {task['blocks']}")
        if task.get('due'):
            print(f"   Due: {task['due']}")
        print()


def archive_done(args):
    """Archive completed tasks to quarterly file."""
    from utils import ARCHIVE_DIR
    
    tasks_file = get_tasks_file(args.personal)
    content = tasks_file.read_text()
    tasks_data = parse_tasks(content, args.personal)
    done_tasks = tasks_data['done']
    
    if not done_tasks:
        print("No completed tasks to archive.")
        return
    
    # Create archive entry
    quarter = get_current_quarter()
    archive_file = ARCHIVE_DIR / f"ARCHIVE-{quarter}.md"
    
    task_type = "Personal" if args.personal else "Work"
    archive_entry = f"\n## Archived {datetime.now().strftime('%Y-%m-%d')} ({task_type})\n\n"
    for task in done_tasks:
        archive_entry += f"- ✅ **{task['title']}**\n"
    
    # Append to archive
    if archive_file.exists():
        archive_content = archive_file.read_text()
    else:
        archive_content = f"# Task Archive - {quarter}\n"
    
    archive_content += archive_entry
    archive_file.write_text(archive_content)
    
    # Remove from done section
    import re
    done_section_pattern = r'(## ✅ Done.*?\n\n).*?(\n## |\n---|\Z)'
    new_content = re.sub(
        done_section_pattern,
        r'\1_Move completed items here during daily standup_\n\n\2',
        content,
        flags=re.DOTALL
    )
    
    tasks_file.write_text(new_content)
    print(f"✅ Archived {len(done_tasks)} {task_type} tasks to {archive_file.name}")


def main():
    parser = argparse.ArgumentParser(description='Task Tracker CLI (Work & Personal)')
    parser.add_argument('--personal', action='store_true', help='Use Personal Tasks instead of Work Tasks')
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--priority', choices=['high', 'medium', 'low'])
    list_parser.add_argument('--status', choices=['todo', 'in-progress', 'blocked', 'waiting', 'done'])
    list_parser.add_argument('--due', choices=['today', 'this-week', 'overdue'])
    list_parser.set_defaults(func=list_tasks)
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('--priority', default='medium', choices=['high', 'medium', 'low'])
    add_parser.add_argument('--due', help='Due date (YYYY-MM-DD)')
    add_parser.add_argument('--owner', default='me')
    add_parser.add_argument('--area', help='Area/category')
    add_parser.set_defaults(func=add_task)
    
    # Done command
    done_parser = subparsers.add_parser('done', help='Mark task as done')
    done_parser.add_argument('query', help='Task title (fuzzy match)')
    done_parser.set_defaults(func=done_task)
    
    # Blockers command
    blockers_parser = subparsers.add_parser('blockers', help='Show blocking tasks')
    blockers_parser.add_argument('--person', help='Filter by person being blocked')
    blockers_parser.set_defaults(func=show_blockers)
    
    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Archive completed tasks')
    archive_parser.set_defaults(func=archive_done)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
