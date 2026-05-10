#!/usr/bin/env python3
"""
Stamp an attribution footer on every .md file in one or more repos.

Usage:
    python stamp_attribution.py                  # runs against both default repos
    python stamp_attribution.py path/to/repo     # specific repo
    python stamp_attribution.py --dry-run        # preview without writing

Re-running is safe — files already stamped are skipped.
"""

import sys
import pathlib

# ── Identity ──────────────────────────────────────────────────────────────────
AUTHOR  = "Tiffany Moore"
COMPANY = "Ameritech Consulting Group"
EMAIL   = "tiffany@a-techconsulting.com"
WEBSITE = "www.a-techconsulting.com"
GITHUB_BASE = "https://github.com/ameritechconsulting"

# Hidden marker so we never double-stamp
MARKER = "<!-- ameritech-attribution -->"

# Directories to skip entirely
SKIP_DIRS = {".git", "archive", "__pycache__", ".venv", ".ipynb_checkpoints"}


def footer(repo_slug: str) -> str:
    repo_url = f"{GITHUB_BASE}/{repo_slug}"
    line = (
        f"{AUTHOR}  •  {COMPANY}  •  "
        f"[{EMAIL}](mailto:{EMAIL})  •  "
        f"[{WEBSITE}](https://{WEBSITE})  •  "
        f"[GitHub]({repo_url})"
    )
    return f"\n---\n\n{MARKER}\n*{line}*\n"


def stamp(md_file: pathlib.Path, repo_slug: str, dry_run: bool) -> str:
    text = md_file.read_text(encoding="utf-8")
    if MARKER in text:
        return "skip"
    new_text = text.rstrip() + "\n" + footer(repo_slug)
    if not dry_run:
        md_file.write_text(new_text, encoding="utf-8")
    return "stamped"


def process_repo(repo: pathlib.Path, dry_run: bool) -> None:
    slug = repo.name
    prefix = "[dry-run] " if dry_run else ""
    print(f"\n{prefix}{repo.name}  →  {GITHUB_BASE}/{slug}")

    stamped, skipped = [], []
    for md in sorted(repo.rglob("*.md")):
        # Skip unwanted directories
        rel = md.relative_to(repo)
        if set(rel.parts[:-1]) & SKIP_DIRS:
            continue
        result = stamp(md, slug, dry_run)
        if result == "stamped":
            stamped.append(rel)
            print(f"  +  {rel}")
        else:
            skipped.append(rel)
            print(f"  ~  {rel}  (already stamped)")

    print(f"\n  stamped {len(stamped)}, skipped {len(skipped)}")


def main() -> None:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    paths = [a for a in args if not a.startswith("--")]

    if paths:
        repos = [pathlib.Path(p).expanduser().resolve() for p in paths]
    else:
        base = pathlib.Path(__file__).parent
        repos = [
            base / "cmta-analysis",
            base / "austin-ada-accessibility-analysis",
        ]

    for repo in repos:
        if not repo.is_dir():
            print(f"ERROR: {repo} not found — skipping")
            continue
        process_repo(repo, dry_run)


if __name__ == "__main__":
    main()
