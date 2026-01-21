#!/usr/bin/env python3
"""
Task Extractor - Extract action items from meeting notes.

This script is meant to be invoked by the LLM, which will parse
the meeting notes and call tasks.py add for each extracted task.
"""

import argparse
import sys
from pathlib import Path


def extract_prompt(text: str) -> str:
    """Generate a prompt for LLM to extract tasks."""
    return f"""Extract action items from these meeting notes and format each as a task.

For each task, determine:
- title: Brief, actionable title (verb + noun)
- priority: high (blocking/deadline/revenue), medium (important), low (nice-to-have)
- due: Date if mentioned, ASAP if urgent, or leave blank
- owner: Person responsible (default: martin)
- blocks: Who/what is blocked if this isn't done

Meeting Notes:
---
{text}
---

Output each task as a command:
```
tasks.py add "Task title" --priority high --due YYYY-MM-DD --blocks "person (reason)"
```

Only output the commands, one per line. No explanations."""


def main():
    parser = argparse.ArgumentParser(description='Extract tasks from meeting notes')
    parser.add_argument('--from-text', help='Meeting notes text')
    parser.add_argument('--from-file', type=Path, help='File containing meeting notes')
    
    args = parser.parse_args()
    
    if args.from_file:
        if not args.from_file.exists():
            print(f"File not found: {args.from_file}", file=sys.stderr)
            sys.exit(1)
        text = args.from_file.read_text()
    elif args.from_text:
        text = args.from_text
    else:
        print("Provide --from-text or --from-file", file=sys.stderr)
        sys.exit(1)
    
    # Output prompt for LLM processing
    print(extract_prompt(text))
    print("\n---")
    print("NOTE: This output is meant for LLM processing.")
    print("The LLM should parse meeting notes and call tasks.py add for each task.")


if __name__ == '__main__':
    main()
