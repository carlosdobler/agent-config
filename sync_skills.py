#!/usr/bin/env python3
"""
sync_skills.py — Pull AI skills from GitHub into a local directory.

Usage:
    python3 sync_skills.py [--manifest skills-manifest.json] [--dest ./skills] [--dry-run]
"""

import argparse
import sys
import urllib.request
import urllib.error
import json
from pathlib import Path


GITHUB_API = "https://api.github.com"


def github_get(url: str) -> dict | list:
    """Fetch a GitHub API URL and return parsed JSON."""
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ✗ GitHub API error {e.code} for {url}")
        print(f"    {body[:200]}")
        sys.exit(1)


def fetch_raw(download_url: str) -> str:
    """Download raw file content."""
    with urllib.request.urlopen(download_url) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_path(repo: str, gh_path: str, dest: Path, dry_run: bool):
    """
    Recursively fetch a file or directory from GitHub into dest.
    gh_path: path inside the repo (e.g. "skills/summarizer")
    dest:    local target directory
    """
    url = f"{GITHUB_API}/repos/{repo}/contents/{gh_path}"
    item = github_get(url)

    # Single file
    if isinstance(item, dict):
        _write_file(item, dest, dry_run)
        return

    # Directory listing
    for entry in item:
        if entry["type"] == "file":
            _write_file(entry, dest, dry_run)
        elif entry["type"] == "dir":
            sub_dest = dest / entry["name"]
            if not dry_run:
                sub_dest.mkdir(parents=True, exist_ok=True)
            fetch_path(repo, entry["path"], sub_dest, dry_run)


def _write_file(entry: dict, dest: Path, dry_run: bool):
    target = dest / entry["name"]
    print(f"  {'[dry]' if dry_run else '✓'} {entry['path']} → {target}")
    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)
        content = fetch_raw(entry["download_url"])
        target.write_text(content, encoding="utf-8")


def resolve_dest(skill: dict, base_dest: Path) -> Path:
    """Determine local destination folder for a skill entry."""
    if "dest" in skill:
        return base_dest / skill["dest"]
    # Default: use the repo name (after the slash)
    repo_name = skill["repo"].split("/")[-1]
    return base_dest / repo_name


def main():
    parser = argparse.ArgumentParser(description="Sync AI skills from GitHub.")
    parser.add_argument(
        "--manifest", default="skills-manifest.json", help="Path to manifest file"
    )
    parser.add_argument(
        "--dest", default="./skills", help="Local destination directory"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions without writing files"
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Error: manifest not found at {manifest_path}")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    base_dest = Path(args.dest)
    if not args.dry_run:
        base_dest.mkdir(parents=True, exist_ok=True)

    skills = manifest.get("skills", [])
    if not skills:
        print("No skills defined in manifest.")
        sys.exit(0)

    print(f"Syncing {len(skills)} skill(s) → {base_dest.resolve()}\n")

    for skill in skills:
        repo = skill["repo"]
        paths = skill.get("paths", [])
        dest = resolve_dest(skill, base_dest)

        print(f"[{repo}]")
        if not paths:
            print("  ⚠ No paths specified, skipping.")
            continue

        for gh_path in paths:
            fetch_path(repo, gh_path, dest, dry_run=args.dry_run)

        print()

    print("Done." if not args.dry_run else "Dry run complete — no files written.")


if __name__ == "__main__":
    main()
