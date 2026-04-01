# cli-journal-notes

A lightweight CLI for logging daily dev notes and journal entries from the terminal.

## Features

- Quick entry creation with titles, tags, and content
- Full-text search across all entries
- Tag-based organization and filtering
- Markdown export for sharing or archiving
- Configuration for default tags and storage paths
- No external dependencies — pure Python standard library

## Installation

No installation required. Just clone or copy `journal.py` and run it directly:

```bash
python3 journal.py --help
```

For convenience, add an alias to your shell config (`~/.bashrc` or `~/.zshrc`):

```bash
alias journal='python3 /path/to/journal.py'
```

Or make it executable and place it in your PATH:

```bash
chmod +x journal.py
sudo mv journal.py /usr/local/bin/journal
```

## Usage

### Add an entry

```bash
journal add --title "Fixed auth bug" --tag "backend" --content "Root cause was expired token middleware."
```

Pipe content via stdin:

```bash
cat notes.txt | journal add --title "Meeting notes" --tag "work"
```

### List entries

```bash
journal list
journal list --tag "frontend"
journal list --search "docker"
journal list --limit 5
```

### View a single entry

```bash
journal show 20260413102345
```

### Edit an entry

```bash
journal edit 20260413102345 --content "Updated content here."
```

### Delete an entry

```bash
journal delete 20260413102345
```

### List tags

```bash
journal tags
```

### Export to markdown

```bash
journal export
journal export --output ~/journal-backup.md
```

### Configuration

```bash
journal config show
journal config set default_tag "dev"
journal config path
```

## Data Storage

All data is stored in `~/.cli-journal-notes/`:

| File               | Purpose                    |
|--------------------|----------------------------|
| `entries.json`     | All journal entries        |
| `config.json`      | User configuration         |

Each entry stores: `id`, `title`, `tag`, `content`, `created_at`, and `updated_at`.

## Command Reference

| Command                        | Description                  |
|--------------------------------|------------------------------|
| `journal add`                  | Add a new entry              |
| `journal list` / `journal ls`  | List entries with filters    |
| `journal show <id>`            | Display a single entry       |
| `journal edit <id>`            | Edit an existing entry       |
| `journal delete` / `journal rm`| Delete an entry              |
| `journal tags`                 | Show all tags with counts    |
| `journal export`               | Export to markdown file      |
| `journal config`               | Manage configuration         |

## Examples

Log a quick note:

```bash
journal add -t "Sprint planning" -c "Decided to prioritize API v2 over dashboard redesign."
```

Search for all entries mentioning a specific topic:

```bash
journal list -s "kubernetes"
```

Export weekly notes for review:

```bash
journal export -o ~/weekly-notes.md
```

## Requirements

- Python 3.6 or later
- No external packages required

## License

MIT
