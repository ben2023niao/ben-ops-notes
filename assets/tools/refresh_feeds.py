#!/usr/bin/env python3
"""Rebuild RSS and sitemap feeds from the canonical data.json index."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape


SITE_BASE = "https://ben2023niao.github.io/ben-ops-notes/"


def main() -> int:
    assets = Path(__file__).resolve().parents[1]
    data = json.loads((assets / "data.json").read_text(encoding="utf-8"))
    documents = data["documents"]
    seo_manifest_path = assets / "seo-manifest.json"
    if not seo_manifest_path.is_file():
        raise SystemExit("assets/seo-manifest.json is missing; build SEO pages first")
    seo_rows = json.loads(seo_manifest_path.read_text(encoding="utf-8"))
    seo_by_id = {str(item["id"]): item for item in seo_rows}

    latest = sorted(
        documents,
        key=lambda item: item["dateTime"],
        reverse=True,
    )[:100]
    rss_items = []
    for document in latest:
        link = str(seo_by_id[str(document["id"])]["canonical"])
        rss_items.append(
            "<item>"
            f"<title>{escape(document['title'])}</title>"
            f"<link>{escape(link)}</link>"
            f'<guid isPermaLink="true">{escape(link)}</guid>'
            f"<pubDate>{escape(document['dateTime'])}</pubDate>"
            f"<description>{escape(document['description'])}</description>"
            "</item>"
        )
    (assets / "rss.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>'
        "<title>BEN.OPS Engineering Notes</title>"
        f"<link>{SITE_BASE}</link>"
        "<description>Linux, DevOps, SRE, Cloud and Security notes</description>"
        f"<lastBuildDate>{escape(data['generatedAt'])}</lastBuildDate>"
        + "".join(rss_items)
        + "</channel></rss>\n",
        encoding="utf-8",
    )

    sitemap_items = [
        f"<url><loc>{escape(str(seo_by_id[str(document['id'])]['canonical']))}</loc>"
        f"<lastmod>{document['dateOnly']}</lastmod>"
        "<changefreq>monthly</changefreq><priority>0.8</priority></url>"
        for document in seo_rows
    ]
    (assets / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>{SITE_BASE}</loc><lastmod>{data['generatedAt'][:10]}</lastmod>"
        "<changefreq>daily</changefreq><priority>1.0</priority></url>"
        f"<url><loc>{SITE_BASE}assets/seo/index.html</loc>"
        f"<lastmod>{data['generatedAt'][:10]}</lastmod>"
        "<changefreq>daily</changefreq><priority>0.9</priority></url>"
        + "".join(sitemap_items)
        + "</urlset>\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "documents": len(documents),
                "articleUrls": len(seo_rows),
                "rssItems": len(latest),
                "rss": str(assets / "rss.xml"),
                "sitemap": str(assets / "sitemap.xml"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
