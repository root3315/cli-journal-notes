#!/usr/bin/env python3
"""
cli-journal-notes — A lightweight CLI for logging daily dev notes and journal entries.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

JOURNAL_DIR = Path.home() / ".cli-journal-notes"
ENTRIES_FILE = JOURNAL_DIR / "entries.json"
CONFIG_FILE = JOURNAL_DIR / "config.json"

DEFAULT_EDITOR = os.environ.get("EDITOR", "nano")


def ensure_dirs():
    """Create the journal directory if it doesn't exist."""
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    if not ENTRIES_FILE.exists():
        ENTRIES_FILE.write_text(json.dumps([], indent=2))
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps({"default_tag": "general"}, indent=2))


def load_entries():
    """Load all journal entries from the JSON file."""
    ensure_dirs()
    try:
        data = json.loads(ENTRIES_FILE.read_text())
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def save_entries(entries):
    """Persist journal entries back to disk."""
    ensure_dirs()
    ENTRIES_FILE.write_text(json.dumps(entries, indent=2))


def load_config():
    """Load user configuration."""
    ensure_dirs()
    try:
        return json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"default_tag": "general"}


def save_config(config):
    """Save user configuration."""
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def generate_id():
    """Create a short unique ID based on timestamp."""
    return datetime.now().strftime("%Y%m%d%H%M%S")


def cmd_add(args):
    """Add a new journal entry."""
    entries = load_entries()
    title = args.title if hasattr(args, "title") and args.title else "Untitled"
    tag = args.tag if hasattr(args, "tag") and args.tag else load_config()["default_tag"]
    content = args.content if hasattr(args, "content") and args.content else ""

    if not content and not sys.stdin.isatty():
        content = sys.stdin.read().strip()

    if not content:
        print("Error: no content provided. Use --content or pipe text via stdin.")
        sys.exit(1)

    entry = {
        "id": generate_id(),
        "title": title,
        "tag": tag,
        "content": content,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }

    entries.insert(0, entry)
    save_entries(entries)
    print(f"Entry added: [{entry['id']}] {entry['title']} (#{entry['tag']})")


def cmd_list(args):
    """List journal entries with optional filtering."""
    entries = load_entries()

    if not entries:
        print("No journal entries found.")
        return

    if hasattr(args, "tag") and args.tag:
        entries = [e for e in entries if e.get("tag") == args.tag]
        if not entries:
            print(f"No entries found with tag '{args.tag}'.")
            return

    if hasattr(args, "search") and args.search:
        keyword = args.search.lower()
        entries = [
            e for e in entries
            if keyword in e.get("title", "").lower()
            or keyword in e.get("content", "").lower()
            or keyword in e.get("tag", "").lower()
        ]
        if not entries:
            print(f"No entries matching '{args.search}'.")
            return

    limit = args.limit if hasattr(args, "limit") and args.limit else 10
    entries = entries[:limit]

    for entry in entries:
        date_str = entry.get("created_at", "unknown")[:10]
        tag = entry.get("tag", "untagged")
        title = entry.get("title", "Untitled")
        eid = entry.get("id", "????")
        preview = entry.get("content", "")[:80].replace("\n", " ")
        print(f"[{eid}] {date_str} | #{tag:<12} | {title}")
        print(f"        {preview}")
        print()

    print(f"Showing {len(entries)} of {len(load_entries())} entries.")


def cmd_show(args):
    """Display a single journal entry."""
    entries = load_entries()
    target = args.id

    for entry in entries:
        if entry["id"] == target:
            date_str = entry.get("created_at", "unknown")
            tag = entry.get("tag", "untagged")
            title = entry.get("title", "Untitled")
            content = entry.get("content", "")

            print("=" * 60)
            print(f"  {title}")
            print("=" * 60)
            print(f"  ID:        {entry['id']}")
            print(f"  Date:      {date_str}")
            print(f"  Tag:       {tag}")
            print("-" * 60)
            print(content)
            print()
            print("=" * 60)
            return

    print(f"Entry '{target}' not found.")
    sys.exit(1)


def cmd_edit(args):
    """Edit an existing journal entry."""
    entries = load_entries()
    target = args.id

    for i, entry in enumerate(entries):
        if entry["id"] == target:
            new_content = args.content if hasattr(args, "content") and args.content else ""
            if not new_content and not sys.stdin.isatty():
                new_content = sys.stdin.read().strip()

            if not new_content:
                print(f"Current content of [{target}]:")
                print(entry["content"])
                print("\nProvide new content via --content or stdin.")
                sys.exit(1)

            entries[i]["content"] = new_content
            entries[i]["updated_at"] = datetime.now().isoformat(timespec="seconds")
            save_entries(entries)
            print(f"Entry [{target}] updated.")
            return

    print(f"Entry '{target}' not found.")
    sys.exit(1)


def cmd_delete(args):
    """Delete a journal entry."""
    entries = load_entries()
    target = args.id
    original_count = len(entries)
    entries = [e for e in entries if e["id"] != target]

    if len(entries) == original_count:
        print(f"Entry '{target}' not found.")
        sys.exit(1)

    save_entries(entries)
    print(f"Entry [{target}] deleted.")


def cmd_tags(args):
    """List all tags and their entry counts."""
    entries = load_entries()
    tag_counts = {}

    for entry in entries:
        tag = entry.get("tag", "untagged")
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if not tag_counts:
        print("No tags found.")
        return

    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    print(f"{'Tag':<20} {'Count':>5}")
    print("-" * 26)
    for tag, count in sorted_tags:
        print(f"#{tag:<19} {count:>5}")
    print(f"\nTotal: {sum(tag_counts.values())} entries across {len(tag_counts)} tags.")


def cmd_export(args):
    """Export entries to a markdown file."""
    entries = load_entries()

    if not entries:
        print("No entries to export.")
        return

    output_path = Path(args.output) if hasattr(args, "output") and args.output else JOURNAL_DIR / "export.md"

    with open(output_path, "w") as f:
        f.write("# Journal Export\n\n")
        f.write(f"Exported at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total entries: {len(entries)}\n\n")
        f.write("---\n\n")

        for entry in entries:
            date_str = entry.get("created_at", "unknown")
            tag = entry.get("tag", "untagged")
            title = entry.get("title", "Untitled")
            content = entry.get("content", "")

            f.write(f"## {title}\n\n")
            f.write(f"**Date:** {date_str}  \n")
            f.write(f"**Tag:** {tag}  \n")
            f.write(f"**ID:** {entry['id']}\n\n")
            f.write(f"{content}\n\n")
            f.write("---\n\n")

    print(f"Exported {len(entries)} entries to {output_path}")


def cmd_config(args):
    """Manage configuration settings."""
    config = load_config()

    if args.action == "show":
        print("Current configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    elif args.action == "set":
        if not hasattr(args, "key") or not hasattr(args, "value"):
            print("Usage: journal config set <key> <value>")
            sys.exit(1)
        config[args.key] = args.value
        save_config(config)
        print(f"Config updated: {args.key} = {args.value}")
    elif args.action == "path":
        print(f"Journal directory: {JOURNAL_DIR}")
        print(f"Entries file:      {ENTRIES_FILE}")
        print(f"Config file:       {CONFIG_FILE}")


def main():
    parser = argparse.ArgumentParser(
        prog="journal",
        description="A lightweight CLI for logging daily dev notes and journal entries.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new journal entry")
    add_parser.add_argument("--title", "-t", default=None, help="Entry title")
    add_parser.add_argument("--tag", default=None, help="Entry tag/category")
    add_parser.add_argument("--content", "-c", default=None, help="Entry content")

    # list
    list_parser = subparsers.add_parser("list", aliases=["ls"], help="List journal entries")
    list_parser.add_argument("--tag", default=None, help="Filter by tag")
    list_parser.add_argument("--search", "-s", default=None, help="Search entries")
    list_parser.add_argument("--limit", "-n", type=int, default=10, help="Max entries to show")

    # show
    show_parser = subparsers.add_parser("show", help="Show a single entry")
    show_parser.add_argument("id", help="Entry ID")

    # edit
    edit_parser = subparsers.add_parser("edit", help="Edit an existing entry")
    edit_parser.add_argument("id", help="Entry ID to edit")
    edit_parser.add_argument("--content", "-c", default=None, help="New content")

    # delete
    del_parser = subparsers.add_parser("delete", aliases=["rm"], help="Delete an entry")
    del_parser.add_argument("id", help="Entry ID to delete")

    # tags
    subparsers.add_parser("tags", help="List all tags")

    # export
    export_parser = subparsers.add_parser("export", help="Export entries to markdown")
    export_parser.add_argument("--output", "-o", default=None, help="Output file path")

    # config
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("action", choices=["show", "set", "path"], help="Config action")
    config_parser.add_argument("key", nargs="?", default=None, help="Config key")
    config_parser.add_argument("value", nargs="?", default=None, help="Config value")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "ls": cmd_list,
        "show": cmd_show,
        "edit": cmd_edit,
        "delete": cmd_delete,
        "rm": cmd_delete,
        "tags": cmd_tags,
        "export": cmd_export,
        "config": cmd_config,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
