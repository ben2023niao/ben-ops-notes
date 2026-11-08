#!/usr/bin/env python3
"""Commit generated SEO article pages using each document's real date."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path


def git(
    root: Path,
    args: list[str],
    *,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=check,
        env=env,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("/Users/ben/ben随笔文档"))
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    rows = json.loads(
        (root / "assets" / "seo-manifest.json").read_text(encoding="utf-8")
    )
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[str(row["date"])[:10]].append(row)

    commits = 0
    for date in sorted(groups):
        items = sorted(groups[date], key=lambda item: str(item["html"]))
        paths = sorted(
            {
                str(item[key])
                for item in items
                for key in ("html", "markdown")
            }
        )
        if not args.execute:
            print(date, len(paths), paths[0])
            commits += 1
            continue
        git(root, ["add", "--", *paths])
        if git(root, ["diff", "--cached", "--quiet"], check=False).returncode == 0:
            continue
        group_time = min(str(item["date"]) for item in items)
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Ben"
        env["GIT_AUTHOR_EMAIL"] = "ben2023niao@users.noreply.github.com"
        env["GIT_COMMITTER_NAME"] = "Ben"
        env["GIT_COMMITTER_EMAIL"] = "ben2023niao@users.noreply.github.com"
        env["GIT_AUTHOR_DATE"] = group_time
        env["GIT_COMMITTER_DATE"] = group_time
        git(
            root,
            [
                "commit",
                "-m",
                f"docs+seo: publish {len(paths)} article files for {date}",
            ],
            env=env,
        )
        commits += 1
        print(f"{commits:03d} {date} {len(paths)} files")

    print(
        json.dumps(
            {
                "root": str(root),
                "documents": len(rows),
                "dateGroups": len(groups),
                "commits": commits,
                "execute": args.execute,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
