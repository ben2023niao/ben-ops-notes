#!/usr/bin/env python3
"""Validate the portable BEN.OPS delivery without third-party dependencies."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote


def markdown_prose(markdown: str) -> str:
    """Return Markdown outside fenced code blocks."""
    prose = []
    fence_char = ""
    fence_len = 0
    for line in markdown.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if not fence_char:
                fence_char = marker[0]
                fence_len = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len:
                fence_char = ""
                fence_len = 0
            continue
        if not fence_char:
            prose.append(line)
    return "\n".join(prose)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    assets = root / "assets"
    data = json.loads((assets / "data.json").read_text(encoding="utf-8"))
    missing = []
    for doc in data["documents"]:
        md_href = doc.get("mdHref", "")
        md_file = root / md_href
        if not md_file.is_file():
            missing.append(md_href)
        for item in doc.get("originals", []):
            if not (root / item["href"]).is_file():
                missing.append(item["href"])
        md_path = Path(md_href)
        if (
            md_path.parent.as_posix() != "doc/md"
            or not re.match(
                r"^\d{12}-[^-]+-[^-]+(?:-.+)?$", md_path.stem
            )
            or not re.search(r"[\u3400-\u9fff]", md_path.stem)
        ):
            missing.append(f"invalid Markdown path: {md_href}")
        if not str(doc.get("markdownBody", "")).lstrip().startswith("# "):
            missing.append(f"missing canonical Markdown body: {md_href}")
        markdown = md_file.read_text(encoding="utf-8") if md_file.is_file() else ""
        prose = markdown_prose(markdown)
        if len(re.findall(r"^#\s+", prose, re.M)) != 1:
            missing.append(f"invalid H1 count: {md_href}")
        if "\n\n\n" in markdown or re.search(r"\]\(<?https%3A", prose, re.I):
            missing.append(f"non-canonical Markdown spacing/link: {md_href}")
        for target in re.findall(r"!?\[[^\]]*\]\(<?([^)>\s]+)", prose):
            clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if re.match(r"^(?:[a-z][a-z0-9+.-]*:|#|//)", clean, re.I):
                continue
            if not clean.startswith(("../media/", "../md/", "../../assets/")):
                continue
            if not (md_file.parent / clean).resolve().exists():
                missing.append(f"missing Markdown resource: {md_href} -> {target}")
        for item in doc.get("originals", []):
            if Path(item["href"]).parent.as_posix() != "assets/originals/documents":
                missing.append(f"invalid original location: {item['href']}")
    roots = sorted(path.name for path in root.iterdir())
    if roots != ["assets", "doc", "index.html", "robots.txt"]:
        missing.append(f"invalid root entries: {roots}")
    doc_roots = sorted(path.name for path in (root / "doc").iterdir())
    if doc_roots != ["md", "media"]:
        missing.append(f"invalid doc entries: {doc_roots}")
    html_files = list((root / "doc").rglob("*.html"))
    if html_files:
        missing.append(f"unexpected document HTML copies: {len(html_files)}")
    if missing:
        print(f"FAIL: {len(missing)} issue(s)")
        for item in missing[:100]:
            print(item)
        return 1
    print(
        f"OK: {len(data['documents'])} documents, "
        f"{data['stats']['media']} media files, "
        f"{len(data['brokenLinks'])} source-only broken link(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
