#!/usr/bin/env python3
"""Restore the complete archived GitBook body and local media into public Markdown."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import markdown
from bs4 import BeautifulSoup


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from import_gitbook_competition_notes import (  # noqa: E402
    frontmatter,
    merge_public_index,
    render_text,
    sanitize_public_text,
)


def strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S).strip()


def excerpt(
    body: str,
    title: str,
    tags: list[str],
    categories: list[str],
) -> str:
    rendered_html = markdown.markdown(
        body,
        extensions=["extra", "sane_lists", "fenced_code", "tables"],
        output_format="html5",
    )
    rendered = BeautifulSoup(rendered_html, "html.parser")
    candidates: list[str] = []
    noise = re.compile(
        r"^(?:来源|原文|来源文件|整理日期|归档性质|页面时间|日期依据|作者[:：])",
        re.I,
    )
    for node in rendered.find_all(["p", "li"]):
        text = " ".join(node.get_text(" ", strip=True).split())
        if (
            len(text) >= 24
            and not noise.search(text)
            and not re.match(r"^(?:\d{1,6}\s+){8,}", text)
        ):
            candidates.append(text)
        if len(" ".join(candidates)) >= 125:
            break
    value = " ".join(candidates)
    if not value:
        tag_text = "、".join(tags)
        value = (
            f"{title}。GitBook 原始正文完整归档，属于"
            f"{' / '.join(categories)}，"
            f"包含图片与本地资源，涉及 {tag_text or '工程实践'}。"
        )
    if title.casefold() not in value.casefold():
        value = f"{title}：{value}"
    return value[:158].rstrip("，,；;、 ") + ("…" if len(value) > 158 else "")


def category_id(path: list[str]) -> str:
    return "category-" + hashlib.sha1("/".join(path).encode()).hexdigest()[:10]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--public-root",
        type=Path,
        default=Path("/Users/ben/ben随笔文档"),
    )
    parser.add_argument(
        "--private-root",
        type=Path,
        default=Path("/Users/ben/ben随笔文档-竞赛复盘私有归档-20261109"),
    )
    args = parser.parse_args()
    public_root = args.public_root.resolve()
    private_root = args.private_root.resolve()

    gitbook_manifest = json.loads(
        (private_root / "assets" / "gitbook-html-import.json").read_text(
            encoding="utf-8"
        )
    )["documents"]
    public_data_path = public_root / "assets" / "data.json"
    public_data = json.loads(public_data_path.read_text(encoding="utf-8"))
    public_by_id = {str(item["id"]): item for item in public_data["documents"]}

    restored_docs: list[dict[str, object]] = []
    evidence: list[dict[str, object]] = []
    errors: list[str] = []
    image_files: set[str] = set()

    for row in gitbook_manifest:
        doc_id = str(row["id"])
        public_doc = public_by_id.get(doc_id)
        if not public_doc:
            errors.append(f"{doc_id}: missing public index entry")
            continue
        private_md = private_root / "doc" / "md" / str(row["file"])
        public_md = public_root / str(public_doc["mdHref"])
        if not private_md.is_file():
            errors.append(f"{doc_id}: missing private Markdown {private_md}")
            continue
        raw = private_md.read_text(encoding="utf-8", errors="replace")
        body = sanitize_public_text(strip_frontmatter(raw))
        body = re.sub(
            r"\n{3,}",
            "\n\n",
            "\n".join(line.rstrip() for line in body.splitlines()).strip(),
        )
        if not body.startswith("# "):
            title = str(row["title"]).strip()
            body = f"# {title}\n\n{body}"

        title = str(row["title"]).strip()
        categories = [str(item) for item in row["category"]]
        tags = [str(item) for item in row["tags"] if str(item) != "原始归档"]
        source = str(row["source"])
        date_value = str(row["date"])
        date_time = datetime.fromisoformat(date_value)
        date_only = date_time.strftime("%Y-%m-%d")
        date_display = date_time.strftime("%Y-%m-%d %H:%M")
        meta = {
            "id": doc_id,
            "title": title,
            "date": date_value,
            "dateSource": str(row["dateSource"]),
            "categories": categories,
            "tags": tags,
            "source": source,
            "sourceFormat": "GitBook rendered HTML",
            "sourceHtmlSha256": str(row["sourceHtmlSha256"]),
        }
        public_md.parent.mkdir(parents=True, exist_ok=True)
        public_md.write_text(frontmatter(meta, body), encoding="utf-8")

        refs = re.findall(r"!\[[^\]]*\]\(([^) >]+)", body)
        local_refs: list[str] = []
        for ref in refs:
            if ref.startswith(("http://", "https://", "data:")):
                continue
            name = Path(ref.split("#", 1)[0].split("?", 1)[0]).name
            local_refs.append(name)
            image_files.add(name)
            if not (public_root / "doc" / "media" / name).is_file():
                errors.append(f"{doc_id}: missing public media {name}")

        headings, plain, word_count = render_text(body)
        description = excerpt(body, title, tags, categories)
        document = {
            "id": doc_id,
            "title": title,
            "description": description,
            "date": date_only,
            "dateTime": date_time.isoformat(),
            "dateOnly": date_only,
            "dateDisplay": date_display,
            "dateSource": str(row["dateSource"]),
            "published": date_display,
            "updated": date_display,
            "author": "Ben",
            "readingTime": max(1, (word_count + 349) // 350),
            "difficulty": "进阶" if "安全竞赛复盘" in categories else "工程",
            "kind": "Markdown",
            "categoryPath": categories,
            "categoryLabel": " / ".join(categories),
            "categoryId": category_id(categories),
            "tags": tags,
            "mdHref": str(public_doc["mdHref"]),
            "markdownBody": body.replace("../media/", "doc/media/"),
            "originals": [],
            "sourcePath": source,
            "sourceUrl": source,
            "wordCount": word_count,
            "headings": headings,
            "links": [],
            "backlinks": [],
            "relatedIds": [],
            "previousId": "",
            "nextId": "",
            "searchText": (
                title + " " + " ".join(tags) + " " + description + " " + plain
            ).lower()[:50000],
        }
        restored_docs.append(document)
        evidence.append(
            {
                "id": doc_id,
                "title": title,
                "date": date_time.isoformat(),
                "source": source,
                "sourceHtmlSha256": str(row["sourceHtmlSha256"]),
                "markdown": str(public_doc["mdHref"]),
                "bodyCharacters": len(body),
                "localImages": local_refs,
            }
        )

    if errors:
        print(f"FAIL: {len(errors)} restoration issue(s)")
        for error in errors[:100]:
            print(error)
        return 1

    merge_public_index(restored_docs)
    report_path = public_root / "assets" / "gitbook-content-manifest.json"
    report_path.write_text(
        json.dumps(
            {
                "documents": len(evidence),
                "localImages": len(image_files),
                "records": sorted(evidence, key=lambda item: (item["date"], item["id"])),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "documents": len(evidence),
                "localImages": len(image_files),
                "publicData": str(public_data_path),
                "manifest": str(report_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
