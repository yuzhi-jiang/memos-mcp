---
name: memos-mcp
description: Interact with your Memos note-taking instance via the Memos MCP server. Use this skill to search, create, update, delete, and manage memos and tags. Activate when the user wants to work with their personal notes, save information to Memos, find past notes, or organize memo content with tags.
---

# Memos MCP Skill

This skill provides integration with [Memos](https://usememos.com/) — a privacy-first, lightweight note-taking service — through the Memos MCP server. It enables you to interact with your memos directly from Claude.

## Setup

Before using this skill, ensure the Memos MCP server is configured with your credentials:

```json
{
  "mcpServers": {
    "memos-mcp": {
      "command": "uvx",
      "args": ["memos-mcp"],
      "env": {
        "MEMOS_URL": "https://your-memos-instance-url",
        "MEMOS_API_KEY": "your-memos-api-key"
      }
    }
  }
}
```

## Available Tools

### Search and Filter

- **`search_memos(query, filter_expr)`** — Search memos by keyword or CEL expression
- **`filter_memos(filter_expr)`** — Filter memos using CEL expressions for advanced queries

### Create and Manage

- **`create_memo(content, visibility, tags)`** — Create a new memo with optional tags and visibility
- **`update_memo(memo_id, content, visibility)`** — Update an existing memo's content or visibility
- **`delete_memo(memo_id)`** — Delete a memo by ID
- **`delete_memo_tag(memo_id, tag)`** — Remove a tag from a memo

### Resources

- `memos://recent` — The 10 most recent memos
- `memos://all` — All memos
- `memos://memos/{memo_id}` — A specific memo by ID

## Instructions

When a user asks to interact with their notes or memos:

1. **Search**: Use `search_memos` with a relevant keyword or `filter_memos` with a CEL expression for precise queries.
2. **Create**: Use `create_memo` to save new information. By default, a `mcp` tag is added automatically.
3. **Update**: Use `update_memo` with the memo's ID (short form, e.g. `G3o72r9oijTWFxy9ueWzW7`, not `memos/G3o72r9oijTWFxy9ueWzW7`).
4. **Delete**: Use `delete_memo` to remove a memo, or `delete_memo_tag` to remove just a tag.
5. **Browse**: Access `memos://recent` or `memos://all` to list memos without a specific search term.

### Memo ID Format

Always use the short ID format: `G3o72r9oijTWFxy9ueWzW7`
Not the full path format: `memos/G3o72r9oijTWFxy9ueWzW7`

### Visibility Options

- `PRIVATE` — Only visible to you (default)
- `PROTECTED` — Visible to authenticated users
- `PUBLIC` — Visible to everyone

## CEL Expression Examples

| Goal | Expression |
|------|-----------|
| Find memos containing a keyword | `content.contains('keyword')` |
| Find memos after a date | `createTime > timestamp('2024-01-01T00:00:00Z')` |
| Find private memos | `visibility == 'PRIVATE'` |
| Combine conditions | `content.contains('project') && visibility == 'PRIVATE'` |

## Examples

### Save a note
> "Save a note that I finished the project proposal and it needs review by Friday"

Use `create_memo` with the content and optionally add a `work` tag.

### Find past notes
> "Find all my notes about machine learning"

Use `search_memos(query="machine learning")`.

### Weekly review
> "Summarize my notes from this week"

Use `filter_memos(filter_expr="createTime > timestamp('2024-01-01T00:00:00Z')")` (adjust the date) then summarize the results.

### Organize by tags
> "Remove the 'draft' tag from memo G3o72r9oijTWFxy9ueWzW7"

Use `delete_memo_tag(memo_id="G3o72r9oijTWFxy9ueWzW7", tag="draft")`.
