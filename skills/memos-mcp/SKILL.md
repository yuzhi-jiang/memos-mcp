---
name: memos-mcp
description: Interact with a Memos note-taking instance directly using a bundled Python script — no MCP server installation required. Use this skill to list, search, create, update, delete, and tag memos. Activate when the user wants to work with their personal notes, save new information, find past memos, or organize content with tags.
---

# Memos Skill

This skill communicates with [Memos](https://usememos.com/) directly through its REST API using the bundled script `scripts/memos.py`. **No MCP server installation is required** — only Python 3 (standard library only, no extra packages needed).

## First-time Setup

The script needs two pieces of information: your Memos instance URL and your API key.

**Option A — Environment variables (recommended):**
```bash
export MEMOS_URL=https://your-memos-instance-url
export MEMOS_API_KEY=your-memos-api-key
```

**Option B — Config file `~/.memos-config`:**
```
MEMOS_URL=https://your-memos-instance-url
MEMOS_API_KEY=your-memos-api-key
```

**Option C — CLI flags on every command:**
```bash
python scripts/memos.py --url https://... --token your-key <command>
```

Ask the user which option they prefer if credentials have not been set yet.

## Script Location

The script is at `scripts/memos.py` relative to the skill folder. When running it, use the path to where the skill was installed, for example:

```bash
python ~/.claude/skills/memos-mcp/scripts/memos.py <command>
```

Or if installed in the project:
```bash
python .claude/skills/memos-mcp/scripts/memos.py <command>
```

## Available Commands

### List memos
```bash
python scripts/memos.py list [--limit N]
```
Returns the N most recent memos (default: 20).

### Get a memo by ID
```bash
python scripts/memos.py get <memo_id>
```

### Search memos by keyword
```bash
python scripts/memos.py search <query>
```
Example: `python scripts/memos.py search "machine learning"`

### Filter memos with a CEL expression
```bash
python scripts/memos.py filter "<cel_expression>"
```
Example: `python scripts/memos.py filter "createTime > timestamp('2024-01-01T00:00:00Z')"`

### Create a new memo
```bash
python scripts/memos.py create "<content>" [--visibility PRIVATE|PROTECTED|PUBLIC] [--tags tag1,tag2]
```
Example: `python scripts/memos.py create "Finished the project proposal" --tags work,review`

### Update an existing memo
```bash
python scripts/memos.py update <memo_id> [--content "<new content>"] [--visibility PRIVATE|PROTECTED|PUBLIC]
```

### Delete a memo
```bash
python scripts/memos.py delete <memo_id>
```

### Remove a tag from a memo
```bash
python scripts/memos.py delete-tag <memo_id> <tag>
```
Example: `python scripts/memos.py delete-tag G3o72r9oijTWFxy9ueWzW7 draft`

## Instructions

When a user wants to interact with their Memos:

1. **Check credentials** — If `MEMOS_URL` or `MEMOS_API_KEY` are not set, ask the user and help them configure one of the three options above.
2. **Run the script** using the Bash tool with the appropriate command. All output is JSON.
3. **Present results** in a readable format — summarize memo content rather than dumping raw JSON.
4. **Memo ID format** — Always use the short ID `G3o72r9oijTWFxy9ueWzW7`, not the prefixed form `memos/G3o72r9oijTWFxy9ueWzW7`. The script handles both automatically.

### Visibility Options

| Value | Meaning |
|-------|---------|
| `PRIVATE` | Only visible to you (default) |
| `PROTECTED` | Visible to authenticated users |
| `PUBLIC` | Visible to everyone |

### CEL Expression Reference

| Goal | Expression |
|------|-----------|
| Keyword in content | `content.contains('keyword')` |
| Created after date | `createTime > timestamp('2024-01-01T00:00:00Z')` |
| Private memos only | `visibility == 'PRIVATE'` |
| Combined filter | `content.contains('project') && visibility == 'PRIVATE'` |

## Usage Examples

### Save a note
> "Save a note that I finished the project proposal"

```bash
python scripts/memos.py create "Finished the project proposal" --tags work
```

### Find past notes
> "Find all my notes about machine learning"

```bash
python scripts/memos.py search "machine learning"
```

### Weekly review
> "List memos from this week"

```bash
python scripts/memos.py filter "createTime > timestamp('2024-01-06T00:00:00Z')"
```
Adjust the date to the start of the current week, then summarize the returned memos.

### Organize by tags
> "Remove the 'draft' tag from memo G3o72r9oijTWFxy9ueWzW7"

```bash
python scripts/memos.py delete-tag G3o72r9oijTWFxy9ueWzW7 draft
```
