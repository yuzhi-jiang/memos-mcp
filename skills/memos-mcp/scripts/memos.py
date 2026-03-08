#!/usr/bin/env python3
"""
memos.py — Standalone Memos API client script for the Memos skill.

Uses only Python standard library (no pip install required).

Configuration (in priority order):
  1. Command-line flags: --url, --token
  2. Environment variables: MEMOS_URL, MEMOS_API_KEY
  3. Config file: ~/.memos-config  (lines: MEMOS_URL=... and MEMOS_API_KEY=...)

Usage:
  python memos.py list [--limit N]
  python memos.py get <memo_id>
  python memos.py search <query>
  python memos.py filter <cel_expression>
  python memos.py create <content> [--visibility PRIVATE|PROTECTED|PUBLIC] [--tags tag1,tag2]
  python memos.py update <memo_id> [--content "..."] [--visibility PRIVATE|PROTECTED|PUBLIC]
  python memos.py delete <memo_id>
  python memos.py delete-tag <memo_id> <tag>
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _load_config_file() -> dict:
    """Read key=value pairs from ~/.memos-config if it exists."""
    config_path = Path.home() / ".memos-config"
    cfg = {}
    if config_path.exists():
        for line in config_path.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, _, value = line.partition("=")
                cfg[key.strip()] = value.strip()
    return cfg


def _get_config(args: argparse.Namespace) -> tuple[str, str]:
    """Return (memos_url, api_key) resolved from CLI flags > env vars > config file."""
    file_cfg = _load_config_file()

    url = (
        getattr(args, "url", None)
        or os.environ.get("MEMOS_URL")
        or file_cfg.get("MEMOS_URL")
    )
    token = (
        getattr(args, "token", None)
        or os.environ.get("MEMOS_API_KEY")
        or file_cfg.get("MEMOS_API_KEY")
    )

    if not url:
        _die(
            "Memos URL not set.\n"
            "Set MEMOS_URL environment variable, add it to ~/.memos-config, "
            "or pass --url <url>."
        )
    if not token:
        _die(
            "Memos API key not set.\n"
            "Set MEMOS_API_KEY environment variable, add it to ~/.memos-config, "
            "or pass --token <key>."
        )

    return url.rstrip("/"), token


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _request(method: str, url: str, token: str, params: dict = None, body: dict = None) -> object:
    """Perform an HTTP request and return the parsed JSON response (or None for 204)."""
    if params:
        url = url + "?" + urllib.parse.urlencode(params)

    data = json.dumps(body).encode() if body is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            if not raw:
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode(errors="replace")
        _die(f"HTTP {exc.code} {exc.reason}: {body_text}")


# ---------------------------------------------------------------------------
# Memos API calls
# ---------------------------------------------------------------------------

def _format_id(memo_id: str) -> str:
    """Strip the 'memos/' prefix if present."""
    return memo_id[len("memos/"):] if memo_id.startswith("memos/") else memo_id


def cmd_list(base: str, token: str, limit: int):
    params = {"pageSize": limit} if limit else {}
    result = _request("GET", f"{base}/api/v1/memos", token, params=params)
    _print(result)


def cmd_get(base: str, token: str, memo_id: str):
    memo_id = _format_id(memo_id)
    result = _request("GET", f"{base}/api/v1/memos/{memo_id}", token)
    _print(result)


def cmd_search(base: str, token: str, query: str):
    params = {"filter": f"content.contains('{query}')"}
    result = _request("GET", f"{base}/api/v1/memos", token, params=params)
    _print(result)


def cmd_filter(base: str, token: str, expr: str):
    params = {"filter": expr}
    result = _request("GET", f"{base}/api/v1/memos", token, params=params)
    _print(result)


def cmd_create(base: str, token: str, content: str, visibility: str, tags: list[str]):
    # Append tags to content (only add newline separator when there are tags)
    body_content = content
    tags_to_add = []
    for tag in tags:
        tag_str = tag if tag.startswith("#") else f"#{tag}"
        if tag_str not in body_content:
            tags_to_add.append(tag_str)
    if tags_to_add:
        body_content = body_content + "\n" + " ".join(tags_to_add)

    body = {"content": body_content, "visibility": visibility}
    result = _request("POST", f"{base}/api/v1/memos", token, body=body)
    _print(result)


def cmd_update(base: str, token: str, memo_id: str, content: str, visibility: str):
    memo_id = _format_id(memo_id)
    body = {}
    if content is not None:
        body["content"] = content
    if visibility is not None:
        body["visibility"] = visibility
    if not body:
        _die("Provide at least --content or --visibility to update.")
    result = _request("PATCH", f"{base}/api/v1/memos/{memo_id}", token, body=body)
    _print(result)


def cmd_delete(base: str, token: str, memo_id: str):
    memo_id = _format_id(memo_id)
    _request("DELETE", f"{base}/api/v1/memos/{memo_id}", token)
    print(json.dumps({"status": "deleted", "id": memo_id}))


def cmd_delete_tag(base: str, token: str, memo_id: str, tag: str):
    memo_id = _format_id(memo_id)
    memo = _request("GET", f"{base}/api/v1/memos/{memo_id}", token)
    old_content = (memo or {}).get("content", "")
    tag_str = tag if tag.startswith("#") else f"#{tag}"
    # Match the tag only as a whole word (not as part of another tag like #homework when removing #home)
    new_content = re.sub(r"(?<!\S)" + re.escape(tag_str) + r"(?!\S)", "", old_content).strip()
    result = _request(
        "PATCH",
        f"{base}/api/v1/memos/{memo_id}",
        token,
        body={"content": new_content},
    )
    _print(result)


# ---------------------------------------------------------------------------
# Output / error helpers
# ---------------------------------------------------------------------------

def _print(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _die(msg: str):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="memos.py",
        description="Standalone Memos API client — no MCP server required.",
    )
    parser.add_argument("--url", metavar="URL", help="Memos instance URL (overrides MEMOS_URL env var)")
    parser.add_argument("--token", metavar="KEY", help="Memos API key (overrides MEMOS_API_KEY env var)")

    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List recent memos")
    p_list.add_argument("--limit", type=int, default=20, metavar="N", help="Max number of memos (default: 20)")

    # get
    p_get = sub.add_parser("get", help="Get a memo by ID")
    p_get.add_argument("memo_id", help="Memo ID (e.g. G3o72r9oijTWFxy9ueWzW7)")

    # search
    p_search = sub.add_parser("search", help="Search memos by keyword")
    p_search.add_argument("query", help="Search keyword")

    # filter
    p_filter = sub.add_parser("filter", help="Filter memos with a CEL expression")
    p_filter.add_argument("expr", help="CEL expression, e.g. \"content.contains('keyword')\"")

    # create
    p_create = sub.add_parser("create", help="Create a new memo")
    p_create.add_argument("content", help="Memo content")
    p_create.add_argument(
        "--visibility",
        choices=["PRIVATE", "PROTECTED", "PUBLIC"],
        default="PRIVATE",
        help="Visibility (default: PRIVATE)",
    )
    p_create.add_argument(
        "--tags",
        default="",
        metavar="tag1,tag2",
        help="Comma-separated tags to append (without #)",
    )

    # update
    p_update = sub.add_parser("update", help="Update an existing memo")
    p_update.add_argument("memo_id", help="Memo ID")
    p_update.add_argument("--content", help="New content")
    p_update.add_argument(
        "--visibility",
        choices=["PRIVATE", "PROTECTED", "PUBLIC"],
        help="New visibility",
    )

    # delete
    p_delete = sub.add_parser("delete", help="Delete a memo")
    p_delete.add_argument("memo_id", help="Memo ID")

    # delete-tag
    p_dtag = sub.add_parser("delete-tag", help="Remove a tag from a memo")
    p_dtag.add_argument("memo_id", help="Memo ID")
    p_dtag.add_argument("tag", help="Tag name to remove (without #)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    base, token = _get_config(args)

    if args.command == "list":
        cmd_list(base, token, args.limit)
    elif args.command == "get":
        cmd_get(base, token, args.memo_id)
    elif args.command == "search":
        cmd_search(base, token, args.query)
    elif args.command == "filter":
        cmd_filter(base, token, args.expr)
    elif args.command == "create":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        cmd_create(base, token, args.content, args.visibility, tags)
    elif args.command == "update":
        cmd_update(base, token, args.memo_id, args.content, args.visibility)
    elif args.command == "delete":
        cmd_delete(base, token, args.memo_id)
    elif args.command == "delete-tag":
        cmd_delete_tag(base, token, args.memo_id, args.tag)


if __name__ == "__main__":
    main()
