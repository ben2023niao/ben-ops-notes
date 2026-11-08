#!/usr/bin/env python3
"""Validate generated SEO pages, metadata, structured data and sitemap."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup


SITE_BASE = "https://ben2023niao.github.io/ben-ops-notes/"


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    assets = root / "assets"
    data = json.loads((assets / "data.json").read_text(encoding="utf-8"))
    manifest = json.loads((assets / "seo-manifest.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    canonicals: set[str] = set()

    if len(data["documents"]) != len(manifest):
        errors.append(
            f"manifest count mismatch: {len(manifest)} != {len(data['documents'])}"
        )

    for index, row in enumerate(manifest, 1):
        page = root / str(row["html"])
        if not page.is_file():
            errors.append(f"missing page: {page}")
            continue
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        title = soup.find("title")
        description = soup.find("meta", attrs={"name": "description"})
        keywords = soup.find("meta", attrs={"name": "keywords"})
        robots = soup.find("meta", attrs={"name": "robots"})
        canonical = soup.find("link", attrs={"rel": "canonical"})
        article = soup.find("article")
        h1s = soup.find_all("h1")
        json_ld = soup.find("script", attrs={"type": "application/ld+json"})

        label = str(row["html"])
        if not title or len(title.get_text(strip=True)) < 8:
            errors.append(f"{label}: missing/short title")
        if not description or len(str(description.get("content", "")).strip()) < 20:
            errors.append(f"{label}: missing/short description")
        if not keywords or len(str(keywords.get("content", "")).strip()) < 4:
            errors.append(f"{label}: missing keywords")
        if not robots or "index" not in str(robots.get("content", "")):
            errors.append(f"{label}: not indexable")
        expected = str(row["canonical"])
        actual = str(canonical.get("href", "")) if canonical else ""
        if actual != expected:
            errors.append(f"{label}: canonical mismatch")
        if expected in canonicals:
            errors.append(f"{label}: duplicate canonical")
        canonicals.add(expected)
        has_structured_content = bool(
            article
            and (
                article.find(["img", "pre", "table", "ul", "ol", "blockquote"])
                or len(article.get_text(" ", strip=True)) >= 1
            )
        )
        if not article or not has_structured_content:
            errors.append(f"{label}: missing embedded article body")
        for image in article.find_all("img") if article else []:
            src = str(image.get("src", ""))
            if src.startswith(SITE_BASE):
                local = root / unquote(urlsplit(src).path.removeprefix("/ben-ops-notes/"))
                if not local.is_file():
                    errors.append(f"{label}: missing image {src}")
            elif src.startswith(("http://", "https://")):
                continue
            else:
                errors.append(f"{label}: non-canonical image URL {src}")
        if len(h1s) != 1:
            errors.append(f"{label}: expected one H1, found {len(h1s)}")
        if not json_ld:
            errors.append(f"{label}: missing JSON-LD")
        else:
            try:
                parsed = json.loads(json_ld.string or "{}")
                if parsed.get("@context") != "https://schema.org":
                    errors.append(f"{label}: invalid JSON-LD context")
            except json.JSONDecodeError as exc:
                errors.append(f"{label}: invalid JSON-LD ({exc})")
        scripts = soup.find_all("script")
        if len(scripts) != 1:
            errors.append(f"{label}: unexpected executable scripts")
        if index % 500 == 0:
            print(f"VALIDATE SEO {index}/{len(manifest)}", flush=True)

    index_page = assets / "seo" / "index.html"
    if not index_page.is_file():
        errors.append("missing assets/seo/index.html")
    else:
        soup = BeautifulSoup(index_page.read_text(encoding="utf-8"), "html.parser")
        links = {
            unquote(urlsplit(str(link.get("href", ""))).path)
            for link in soup.find_all("a", href=True)
            if str(link.get("href", "")).startswith(SITE_BASE + "assets/seo/doc-")
        }
        if len(links) != len(manifest):
            errors.append(
                f"SEO index links: {len(links)} != manifest {len(manifest)}"
            )
        if not soup.find("link", attrs={"rel": "canonical"}):
            errors.append("SEO index missing canonical")

    robots = root / "robots.txt"
    if not robots.is_file() or f"Sitemap: {SITE_BASE}assets/sitemap.xml" not in robots.read_text(
        encoding="utf-8"
    ):
        errors.append("robots.txt missing sitemap declaration")

    sitemap = assets / "sitemap.xml"
    if not sitemap.is_file():
        errors.append("missing assets/sitemap.xml")
    else:
        try:
            tree = ET.parse(sitemap)
            namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemap_urls = {
                str(node.text) for node in tree.findall(".//sm:loc", namespace)
            }
            missing = canonicals - sitemap_urls
            if missing:
                errors.append(f"sitemap missing {len(missing)} article URLs")
            if f"{SITE_BASE}assets/seo/index.html" not in sitemap_urls:
                errors.append("sitemap missing SEO index")
        except ET.ParseError as exc:
            errors.append(f"invalid sitemap XML: {exc}")

    if errors:
        print(f"FAIL: {len(errors)} SEO issue(s)")
        for error in errors[:100]:
            print(error)
        return 1
    print(
        f"OK: {len(manifest)} SEO pages, "
        f"{len(canonicals)} unique canonicals"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
