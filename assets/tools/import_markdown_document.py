#!/usr/bin/env python3
"""Import a canonical Markdown note into the BEN.OPS data index."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
TIMEZONE = ZoneInfo("Asia/Manila")


def split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise ValueError("Markdown must start with YAML frontmatter")
    try:
        _, raw_frontmatter, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError("Markdown frontmatter is not closed") from exc

    metadata: dict[str, object] = {}
    for line in raw_frontmatter.splitlines():
        if not line.strip():
            continue
        key, separator, raw_value = line.partition(":")
        if not separator:
            raise ValueError(f"Invalid frontmatter line: {line}")
        value = raw_value.strip()
        if value.startswith("[") and value.endswith("]"):
            metadata[key.strip()] = [
                item.strip().strip("\"'")
                for item in value[1:-1].split(",")
                if item.strip()
            ]
        else:
            metadata[key.strip()] = value.strip("\"'")
    return metadata, body


def strip_fenced_code(text: str) -> str:
    output: list[str] = []
    fence_char = ""
    fence_len = 0
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            value = marker.group(1)
            if not fence_char:
                fence_char = value[0]
                fence_len = len(value)
            elif value[0] == fence_char and len(value) >= fence_len:
                fence_char = ""
                fence_len = 0
            output.append("")
            continue
        output.append("" if fence_char else line)
    return "\n".join(output)


def word_count(text: str) -> int:
    prose = strip_fenced_code(text)
    cjk = len(re.findall(r"[\u3400-\u9fff]", prose))
    words = len(re.findall(r"[A-Za-z0-9_.:+/-]+", prose))
    return cjk + words


def headings(text: str) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    fence_char = ""
    fence_len = 0
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            value = marker.group(1)
            if not fence_char:
                fence_char = value[0]
                fence_len = len(value)
            elif value[0] == fence_char and len(value) >= fence_len:
                fence_char = ""
                fence_len = 0
            continue
        if fence_char:
            continue
        match = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
        if match:
            label = re.sub(r"`", "", match.group(2)).strip()
            result.append({"level": len(match.group(1)), "text": label})
    return result


def category_catalog(documents: list[dict[str, object]]) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, dict[str, object]],
]:
    existing: dict[tuple[str, ...], dict[str, object]] = {}
    for category in json.loads((ASSETS / "data.json").read_text(encoding="utf-8"))[
        "categories"
    ]:
        existing[tuple(category.get("path", []))] = category

    grouped_paths: dict[tuple[str, ...], set[str]] = {}
    for document in documents:
        category_path = tuple(str(item) for item in document.get("categoryPath", []))
        for length in range(1, len(category_path) + 1):
            prefix = category_path[:length]
            grouped_paths.setdefault(prefix, set()).add(str(document["id"]))

    categories: list[dict[str, object]] = []
    for path in sorted(grouped_paths, key=lambda item: (len(item), item)):
        prior = existing.get(path, {})
        category_id = str(
            prior.get(
                "id",
                "category-" + hashlib.sha256("/".join(path).encode()).hexdigest()[:10],
            )
        )
        document_ids = sorted(grouped_paths[path])
        categories.append(
            {
                "id": category_id,
                "name": path[-1],
                "path": list(path),
                "parentId": (
                    str(existing[path[:-1]]["id"])
                    if path[:-1] in existing
                    else ""
                ),
                "count": len(document_ids),
                "documentIds": document_ids,
            }
        )

    by_path = {tuple(item["path"]): item for item in categories}
    roots: list[dict[str, object]] = []
    for category in categories:
        path = tuple(category["path"])
        node = {
            "id": category["id"],
            "name": category["name"],
            "path": category["path"],
            "count": category["count"],
            "children": [],
        }
        if len(path) == 1:
            roots.append(node)
        else:
            parent = next(
                (
                    item
                    for item in roots
                    if tuple(item["path"]) == path[:-1]
                ),
                None,
            )
            if parent is None:
                parent = next(
                    (
                        item
                        for item in categories
                        if tuple(item["path"]) == path[:-1]
                    ),
                    None,
                )
            if parent is not None:
                for root in roots:
                    if tuple(root["path"]) == path[:-1]:
                        root["children"].append(node)
                        break
                    for child in root.get("children", []):
                        if tuple(child["path"]) == path[:-1]:
                            child["children"].append(node)
                            break
    return categories, roots, by_path


def build_description(metadata: dict[str, object], body: str) -> str:
    explicit = str(metadata.get("description", "")).strip()
    if explicit:
        return explicit
    prose = strip_fenced_code(body)
    paragraphs = [
        re.sub(r"\s+", " ", item).strip()
        for item in re.split(r"\n\s*\n", prose)
        if item.strip() and not item.lstrip().startswith(("#", ">", "|", "-", "*"))
    ]
    return (paragraphs[0] if paragraphs else str(metadata.get("title", "")))[:260]


def import_document(
    markdown_path: Path, *, allow_new_category: bool = False
) -> dict[str, object]:
    metadata, body = split_frontmatter(markdown_path.read_text(encoding="utf-8"))
    relative = markdown_path.resolve().relative_to(ROOT).as_posix()
    title = str(metadata["title"])
    date_time = str(metadata["date"])
    parsed_date = datetime.fromisoformat(date_time)
    if parsed_date.tzinfo is None:
        parsed_date = parsed_date.replace(tzinfo=TIMEZONE)
    date_only = parsed_date.date().isoformat()
    category_path = [str(item) for item in metadata.get("categories", [])]
    tags = [str(item) for item in metadata.get("tags", [])]
    source_sha = str(metadata.get("sourceSha256", ""))
    document_id = str(
        metadata.get(
            "id",
            "doc-"
            + hashlib.sha256(
                f"{relative}\0{source_sha}".encode("utf-8")
            ).hexdigest()[:12],
        )
    )
    description = build_description(metadata, body)
    article_word_count = int(metadata.get("wordCount", 0) or word_count(body))
    source_path = str(metadata.get("sourcePath", ""))
    source_url = str(metadata.get("sourceUrl", ""))

    category_catalog_docs = json.loads(
        (ASSETS / "data.json").read_text(encoding="utf-8")
    )["documents"]
    categories, _, by_path = category_catalog(category_catalog_docs)
    category_href = tuple(category_path)
    category = by_path.get(category_href)
    if category is None:
        if not allow_new_category:
            raise ValueError(f"Unknown category path: {category_path}")
        category = {
            "id": "category-"
            + hashlib.sha256("/".join(category_path).encode()).hexdigest()[:10]
        }

    candidates: list[tuple[int, str]] = []
    for item in category_catalog_docs:
        if str(item.get("id")) == document_id:
            continue
        overlap = len(set(tags) & set(item.get("tags", [])))
        same_category = int(tuple(item.get("categoryPath", [])) == category_href)
        candidates.append((overlap * 2 + same_category, str(item["id"])))
    related_ids = [
        item_id
        for score, item_id in sorted(candidates, key=lambda row: (-row[0], row[1]))
        if score > 0
    ][:8]

    return {
        "id": document_id,
        "title": title,
        "description": description,
        "date": date_only,
        "dateTime": parsed_date.isoformat(),
        "dateOnly": date_only,
        "dateDisplay": parsed_date.strftime("%Y-%m-%d %H:%M"),
        "dateSource": str(metadata.get("dateSource", "附件文件名")),
        "published": parsed_date.strftime("%Y-%m-%d %H:%M"),
        "updated": parsed_date.strftime("%Y-%m-%d %H:%M"),
        "author": str(metadata.get("author", "BEN")),
        "readingTime": max(1, math.ceil(article_word_count / 350)),
        "difficulty": str(metadata.get("difficulty", "高级")),
        "kind": "Markdown",
        "categoryPath": category_path,
        "categoryLabel": " / ".join(category_path),
        "categoryId": str(category["id"]),
        "tags": list(dict.fromkeys(tags)),
        "mdHref": relative,
        "markdownBody": body,
        "originals": [],
        "sourcePath": source_path,
        "sourceUrl": source_url,
        "sourceSha256": source_sha,
        "archiveSha256": str(metadata.get("archiveSha256", "")),
        "archiveBytes": int(metadata.get("archiveBytes", 0) or 0),
        "wordCount": article_word_count,
        "headings": headings(body),
        "links": [],
        "backlinks": [],
        "relatedIds": related_ids,
        "previousId": "",
        "nextId": "",
        "searchText": re.sub(
            r"\s+", " ", f"{title} {' '.join(tags)} {body}"
        ).lower(),
    }


def rebuild_index(document: dict[str, object]) -> None:
    data_path = ASSETS / "data.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    current_documents = {
        str(item["id"]): item for item in data["documents"]
    }
    prior_relationships: dict[str, tuple[str, str]] = {}
    prior_document_ids: list[str] = []
    prior_category_order: list[tuple[str, ...]] = []
    prior_tag_order: list[str] = []
    try:
        prior = json.loads(
            subprocess.check_output(
                ["git", "show", "HEAD:assets/data.json"],
                cwd=ROOT,
                text=True,
            )
        )
        prior_document_ids = [
            str(item["id"]) for item in prior.get("documents", [])
        ]
        prior_relationships = {
            str(item["id"]): (
                str(item.get("previousId", "")),
                str(item.get("nextId", "")),
            )
            for item in prior.get("documents", [])
        }
        prior_category_order = [
            tuple(str(part) for part in item.get("path", []))
            for item in prior.get("categories", [])
        ]
        prior_tag_order = [
            str(item.get("name")) for item in prior.get("tags", [])
        ]
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
        pass

    prior_ids = set(prior_document_ids)
    documents = [
        current_documents[item_id]
        for item_id in prior_document_ids
        if item_id in current_documents and item_id != str(document["id"])
    ]
    documents.extend(
        item
        for item in data["documents"]
        if str(item["id"]) not in prior_ids and str(item["id"]) != str(document["id"])
    )

    for item in documents:
        if str(item["id"]) in prior_relationships:
            item["previousId"], item["nextId"] = prior_relationships[str(item["id"])]

    document["previousId"] = str(documents[-1]["id"]) if documents else ""
    document["nextId"] = ""
    if documents:
        documents[-1]["nextId"] = str(document["id"])
    documents.append(document)

    tag_docs: dict[str, set[str]] = {}
    for item in documents:
        for tag in item.get("tags", []):
            tag_docs.setdefault(str(tag), set()).add(str(item["id"]))
    tags = [
        {
            "name": name,
            "count": len(document_ids),
            "documentIds": sorted(document_ids),
        }
        for name, document_ids in tag_docs.items()
    ]
    if prior_tag_order:
        by_name = {str(item["name"]): item for item in tags}
        ordered_tags = [
            by_name[name] for name in prior_tag_order if name in by_name
        ]
        ordered_names = {str(item["name"]) for item in ordered_tags}
        ordered_tags.extend(
            item for item in tags if str(item["name"]) not in ordered_names
        )
        tags = ordered_tags
    else:
        tags.sort(
            key=lambda item: (
                -int(item["count"]),
                str(item["name"]).casefold(),
            )
        )

    categories, category_tree, _ = category_catalog(documents)
    if prior_category_order:
        by_path = {tuple(item["path"]): item for item in categories}
        ordered_categories = [
            by_path[path] for path in prior_category_order if path in by_path
        ]
        ordered_ids = {str(item["id"]) for item in ordered_categories}
        ordered_categories.extend(
            item for item in categories if str(item["id"]) not in ordered_ids
        )
        categories = ordered_categories
    category_nodes: dict[str, dict[str, object]] = {}
    roots: list[dict[str, object]] = []
    for category in categories:
        node = {
            "id": category["id"],
            "name": category["name"],
            "path": category["path"],
            "count": category["count"],
            "children": [],
        }
        category_nodes[str(category["id"])] = node
        parent = category_nodes.get(str(category.get("parentId", "")))
        if parent is None:
            roots.append(node)
        else:
            parent["children"].append(node)
    category_tree = roots
    category_index = {
        str(category["id"]): category for category in categories
    }
    month_counts = Counter(str(item["dateOnly"])[:7] for item in documents)
    timeline = [
        {"month": month, "count": count}
        for month, count in sorted(month_counts.items(), reverse=True)
    ]

    data["documents"] = documents
    data["categories"] = categories
    data["categoryTree"] = category_tree
    data["categoryIndex"] = category_index
    data["tags"] = tags
    data["timeline"] = timeline
    data["generatedAt"] = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M %z")
    data["stats"]["documents"] = len(documents)
    data["stats"]["categories"] = len(categories)
    data["stats"]["tags"] = len(tags)
    data["stats"]["markdown"] = len(documents)
    current_relationships = int(data["stats"].get("relationships", 0))
    data["stats"]["relationships"] = current_relationships + (
        0
        if str(document["id"]) in current_documents
        else len(document.get("relatedIds", []))
    )
    data_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown", type=Path)
    args = parser.parse_args()
    document = import_document(args.markdown)
    rebuild_index(document)
    print(
        json.dumps(
            {
                "id": document["id"],
                "title": document["title"],
                "markdown": document["mdHref"],
                "documents": json.loads(
                    (ASSETS / "data.json").read_text(encoding="utf-8")
                )["stats"]["documents"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
