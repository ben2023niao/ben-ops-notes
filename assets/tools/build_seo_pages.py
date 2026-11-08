#!/usr/bin/env python3
"""Build crawlable, per-document SEO pages from the canonical Markdown index."""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlsplit

import markdown
from bs4 import BeautifulSoup


SITE_BASE = "https://ben2023niao.github.io/ben-ops-notes/"
SITE_NAME = "BEN.OPS 工程笔记"
AUTHOR_NAME = "Ben"
AUTHOR_URL = "https://t.me/Ben_Bird"
GITHUB_URL = "https://github.com/ben2023niao/ben-ops-notes"
DEFAULT_DESCRIPTION = (
    "BEN.OPS 中文基础设施工程笔记，覆盖 Linux、DevOps、SRE、Kubernetes、"
    "数据库、监控告警、CDN、安全运维与故障排查。"
)
DEFAULT_KEYWORDS = [
    "Linux",
    "DevOps",
    "SRE",
    "Kubernetes",
    "Docker",
    "Nginx",
    "MySQL",
    "Redis",
    "CDN",
    "安全运维",
    "故障排查",
]
REMOVE_TAGS = {
    "script",
    "style",
    "iframe",
    "object",
    "embed",
    "form",
    "input",
    "button",
    "noscript",
}
PAGE_STYLE = r"""
:root{color-scheme:light dark;--bg:#f4f0e8;--panel:#fffdf8;--bg2:#e8e1d6;--fg:#202621;--muted:#66736b;
--line:#d4cbbd;--accent:#176b55;--accent2:#0b6094;--code:#17211d;--codefg:#d8f0e4;--warn:#9b5c12;
--max:1120px}@media(prefers-color-scheme:dark){:root{--bg:#111713;--panel:#18201b;--bg2:#202b24;
--fg:#dce9df;--muted:#9aad9f;--line:#314238;--accent:#67d4ad;--accent2:#76b9df;--code:#0a100d;
--codefg:#cceadd;--warn:#f0b35c}}*{box-sizing:border-box}html{scroll-behavior:smooth;background:var(--bg)}
body{margin:0;background:radial-gradient(circle at 15% 0,color-mix(in srgb,var(--accent) 8%,transparent),transparent 32rem),var(--bg);
color:var(--fg);font:16px/1.82 ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
a{color:var(--accent);text-underline-offset:.22em}a:hover{color:var(--accent2)}.shell{width:min(var(--max),calc(100% - 32px));margin:auto}
.topbar{position:sticky;top:0;z-index:5;border-bottom:1px solid var(--line);background:color-mix(in srgb,var(--bg) 88%,transparent);
backdrop-filter:blur(14px)}.topbar .shell{min-height:62px;display:flex;align-items:center;gap:18px}.brand{font:700 1rem/1 ui-monospace,SFMono-Regular,Menlo,monospace;
color:var(--fg);text-decoration:none;letter-spacing:.04em}.brand b{color:var(--accent)}.topbar nav{margin-left:auto;display:flex;gap:16px;flex-wrap:wrap;font-size:.9rem}
main{padding:34px 0 64px}.crumbs{font-size:.84rem;color:var(--muted);margin-bottom:18px}.hero{border:1px solid var(--line);background:var(--panel);
border-radius:16px;padding:clamp(20px,4vw,42px);box-shadow:0 16px 50px #0000000a}.eyebrow{font:700 .74rem/1.2 ui-monospace,SFMono-Regular,Menlo,monospace;
color:var(--accent);letter-spacing:.12em;text-transform:uppercase}.hero h1{font-size:clamp(1.8rem,4.4vw,3.2rem);line-height:1.2;margin:.55rem 0 1rem;
letter-spacing:-.025em;overflow-wrap:anywhere}.lede{font-size:1.04rem;color:var(--muted);max-width:75ch;margin:0 0 18px}.meta{display:flex;flex-wrap:wrap;gap:8px}
.badge{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:999px;padding:.22rem .68rem;background:var(--bg2);
font-size:.78rem;color:var(--fg);text-decoration:none}.layout{margin-top:24px;display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:24px;align-items:start}
.article,.aside-box,.seo-summary{border:1px solid var(--line);background:var(--panel);border-radius:14px}.article{padding:clamp(20px,4vw,48px);min-width:0}
.article h1,.article h2,.article h3,.article h4{line-height:1.35;letter-spacing:-.012em;scroll-margin-top:80px}.article h2{margin-top:2.2em;padding-top:.6em;
border-top:1px solid var(--line)}.article h1{display:none}.article img{display:block;max-width:100%;height:auto;margin:1.4rem auto;border-radius:8px}
.article pre{overflow:auto;background:var(--code);color:var(--codefg);padding:16px;border-radius:9px;line-height:1.6}
.article code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.9em}.article :not(pre)>code{background:var(--bg2);padding:.12em .34em;border-radius:4px}
.article table{display:block;max-width:100%;overflow:auto;border-collapse:collapse}.article th,.article td{border:1px solid var(--line);padding:.45rem .65rem}
.article blockquote{margin:1.4rem 0;padding:.4rem 1rem;border-left:4px solid var(--accent);background:var(--bg2);color:var(--muted)}
.article hr{border:0;border-top:1px solid var(--line);margin:2rem 0}.aside{position:sticky;top:82px;display:grid;gap:14px}
.aside-box{padding:16px}.aside-box h2{font-size:.83rem;margin:0 0 12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.aside-box ol,.aside-box ul{margin:0;padding-left:1.15rem}.aside-box li{margin:.5rem 0;font-size:.9rem}.aside-box a{text-decoration:none}
.seo-summary{margin-top:24px;padding:20px 24px}.seo-summary h2{font-size:1rem;margin:0 0 .65rem}.seo-summary p{margin:0;color:var(--muted)}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:24px}.pager a{border:1px solid var(--line);border-radius:12px;
padding:14px 16px;background:var(--panel);text-decoration:none}.pager a:last-child{text-align:right}.pager small{display:block;color:var(--muted)}
footer{padding:28px 0 48px;border-top:1px solid var(--line);color:var(--muted);font-size:.88rem}footer .shell{display:flex;gap:16px;flex-wrap:wrap}
.index-hero h1{font-size:clamp(2.1rem,6vw,4.4rem)}.stat-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:20px}
.stat{border:1px solid var(--line);background:var(--bg2);border-radius:10px;padding:12px}.stat strong{display:block;font:700 1.35rem/1.2 ui-monospace,monospace}
.stat span{font-size:.78rem;color:var(--muted)}.year{margin-top:34px}.year>h2{position:sticky;top:62px;z-index:2;margin:0;padding:12px 0;
background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(8px);font:700 1.25rem/1.2 ui-monospace,monospace}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.card{border:1px solid var(--line);background:var(--panel);border-radius:12px;padding:18px}
.card h3{font-size:1.02rem;line-height:1.45;margin:.35rem 0 .55rem}.card h3 a{text-decoration:none}.card p{margin:.45rem 0;color:var(--muted);font-size:.87rem}
.card .date{font:600 .77rem/1 ui-monospace,monospace;color:var(--accent)}.tags{display:flex;flex-wrap:wrap;gap:5px}.tag{font-size:.72rem;color:var(--muted);border:1px solid var(--line);
border-radius:99px;padding:.12rem .48rem}@media(max-width:860px){.layout{grid-template-columns:1fr}.aside{position:static;grid-row:1}.cards{grid-template-columns:1fr}}
@media(max-width:620px){body{font-size:15px}.shell{width:min(100% - 22px,var(--max))}.topbar nav{gap:10px;font-size:.8rem}.hero,.article{padding:18px}
.meta{gap:6px}.stat-grid{grid-template-columns:repeat(2,1fr)}.pager{grid-template-columns:1fr}.pager a:last-child{text-align:left}}
@media print{.topbar,.aside,.pager,footer{display:none}.shell{width:100%}.article,.hero{border:0;box-shadow:none;padding:0}}
""".strip()


def compact(value: object, limit: int | None = None) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    if limit and len(text) > limit:
        return text[: max(1, limit - 1)].rstrip("，,；;、 ") + "…"
    return text


def json_for_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )


def doc_url(document: dict[str, object]) -> str:
    return f"{SITE_BASE}assets/seo/{quote(str(document['id']), safe='')}.html"


def markdown_url(document: dict[str, object]) -> str:
    return f"{SITE_BASE}{quote(str(document['mdHref']), safe='/')}"


def keyword_list(document: dict[str, object]) -> list[str]:
    candidates: list[str] = []
    candidates.extend(str(tag) for tag in (document.get("tags") or []))
    candidates.extend(str(part) for part in (document.get("categoryPath") or []))
    candidates.append(str(document.get("categoryLabel", "")))
    candidates.append(str(document.get("title", "")))
    for heading in (document.get("headings") or [])[:12]:
        if isinstance(heading, dict):
            candidates.append(str(heading.get("text", "")))
    technical_terms = re.findall(
        r"\b(?:Linux|DevOps|SRE|Kubernetes|K8s|Docker|Nginx|MySQL|Redis|"
        r"Python|Shell|Go|CDN|DNS|CVE|WAF|SSH|Bash|PHP|Java|Git|CI/CD)\b",
        compact(
            " ".join(
                [
                    str(document.get("title", "")),
                    str(document.get("description", "")),
                    str(document.get("categoryLabel", "")),
                ]
            )
        ),
        re.I,
    )
    candidates.extend(term.upper() if term.lower() == "cve" else term for term in technical_terms)
    result: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        value = re.sub(r"\s+", " ", item).strip(" /，,、")
        key = value.casefold()
        if not value or len(value) > 48 or key in seen:
            continue
        seen.add(key)
        result.append(value)
        if len(result) >= 14:
            break
    return result or list(DEFAULT_KEYWORDS)


def article_description(document: dict[str, object], body_html: str = "") -> str:
    title = compact(document.get("title"))
    category = compact(document.get("categoryLabel")) or "工程笔记"
    body = ""
    if body_html:
        soup = BeautifulSoup(body_html, "html.parser")
        snippets: list[str] = []
        noise = re.compile(
            r"^(?:来源|原文|来源文件|整理日期|归档性质|页面时间|日期依据|"
            r"本文|发布时间|更新时间|作者[:：])",
            re.I,
        )
        for node in soup.find_all(["p", "li"]):
            text = compact(node.get_text(" ", strip=True))
            if (
                len(text) < 24
                or len(text) > 320
                or noise.search(text)
                or text.casefold() == title.casefold()
                or re.match(r"^(?:\d{1,6}\s+){8,}", text)
                or len(re.findall(r"\d", text)) / max(1, len(text)) > 0.35
            ):
                continue
            snippets.append(text)
            if len(" ".join(snippets)) >= 115:
                break
        body = compact(" ".join(snippets))
    body = body or compact(document.get("description")) or compact(document.get("searchText"))
    if not body:
        body = DEFAULT_DESCRIPTION
    if title and title.casefold() not in body.casefold():
        body = f"{title}。本文属于{category}，{body}"
    if len(body) < 55:
        body = f"{body}。{DEFAULT_DESCRIPTION}"
    return compact(body, 158)


def safe_slug(value: str, fallback: str) -> str:
    slug = re.sub(r"[^\w\u3400-\u9fff-]+", "-", value, flags=re.UNICODE).strip("-")
    return slug[:80] or fallback


def unique_seo_titles(
    documents: list[dict[str, object]],
) -> dict[str, str]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for document in documents:
        groups[compact(document.get("title")).casefold()].append(document)
    result: dict[str, str] = {}
    for items in groups.values():
        if len(items) == 1:
            result[str(items[0]["id"])] = compact(items[0].get("title"))
            continue
        by_date = Counter(str(item["dateOnly"]) for item in items)
        for document in items:
            title = compact(document.get("title"))
            date_only = str(document.get("dateOnly"))
            suffix = (
                date_only
                if by_date[date_only] == 1
                else f"{date_only} · {str(document['id'])[-4:]}"
            )
            result[str(document["id"])] = f"{title}（{suffix}）"
    return result


def render_markdown(
    document: dict[str, object],
    doc_by_md: dict[str, dict[str, object]],
) -> tuple[str, list[tuple[int, str, str]], str]:
    converter = markdown.Markdown(
        extensions=["extra", "sane_lists", "fenced_code", "tables", "toc"],
        extension_configs={"toc": {"permalink": False}},
        output_format="html5",
    )
    raw_html = converter.convert(str(document.get("markdownBody", "")))
    soup = BeautifulSoup(raw_html, "html.parser")

    for node in soup.find_all(REMOVE_TAGS):
        node.decompose()
    for node in soup.find_all(True):
        for attribute in list(node.attrs):
            if attribute.lower().startswith("on") or attribute.lower() in {
                "srcdoc",
                "formaction",
            }:
                del node.attrs[attribute]

    current_md_path = str(document["mdHref"])
    current_md_url = f"{SITE_BASE}{quote(current_md_path, safe='/')}"

    def rewrite_url(raw: str, *, image: bool = False) -> str:
        value = raw.strip()
        if not value or value.startswith(("#", "mailto:", "tel:", "data:")):
            return value
        parsed = urlsplit(value)
        if parsed.scheme in {"http", "https"} or value.startswith("//"):
            return value
        if value.startswith(("doc/md/", "doc/media/", "assets/")):
            absolute = SITE_BASE + value.lstrip("/")
            path = unquote(urlsplit(absolute).path).lstrip("/")
        else:
            absolute = urljoin(current_md_url, value)
            path = unquote(urlsplit(absolute).path).lstrip("/")
        if path in doc_by_md:
            return doc_url(doc_by_md[path])
        if path.startswith(("doc/md/", "doc/media/", "assets/")):
            return SITE_BASE + quote(path, safe="/")
        if image:
            return absolute
        return absolute

    for node in soup.find_all("img"):
        src = str(node.get("src", "")).strip()
        if src:
            node["src"] = rewrite_url(src, image=True)
        node["loading"] = "lazy"
        node["decoding"] = "async"
        if not node.get("alt"):
            node["alt"] = compact(document.get("title"))
    for node in soup.find_all("source"):
        srcset = str(node.get("srcset", "")).strip()
        if srcset:
            node["srcset"] = ", ".join(
                f"{rewrite_url(item.strip().split()[0], image=True)}"
                + (f" {item.strip().split(maxsplit=1)[1]}" if len(item.strip().split(maxsplit=1)) > 1 else "")
                for item in srcset.split(",")
                if item.strip()
            )
    for node in soup.find_all("a"):
        href = str(node.get("href", "")).strip()
        if href:
            node["href"] = rewrite_url(href)
        target = str(node.get("href", ""))
        if target.startswith(("http://", "https://", "//")):
            node["rel"] = "noopener noreferrer"

    for heading in soup.find_all("h1"):
        heading.decompose()

    toc: list[tuple[int, str, str]] = []
    used_ids: Counter[str] = Counter()
    for heading in soup.find_all(["h2", "h3"]):
        text = compact(heading.get_text(" ", strip=True))
        base = safe_slug(text, "section")
        used_ids[base] += 1
        heading_id = base if used_ids[base] == 1 else f"{base}-{used_ids[base]}"
        heading["id"] = heading_id
        toc.append((int(heading.name[1]), text, heading_id))

    first_image = ""
    image = soup.find("img")
    if image and str(image.get("src", "")).startswith(("http://", "https://")):
        first_image = str(image["src"])

    return str(soup), toc, first_image


def page_html(
    document: dict[str, object],
    body_html: str,
    toc: list[tuple[int, str, str]],
    og_image: str,
    doc_by_id: dict[str, dict[str, object]],
    display_title: str,
) -> str:
    title = compact(document.get("title")) or str(document["id"])
    description = article_description(document, body_html)
    keywords = keyword_list(document)
    canonical = doc_url(document)
    markdown_href = markdown_url(document)
    category = compact(document.get("categoryLabel")) or "工程笔记"
    category_path = [compact(item) for item in document.get("categoryPath", []) if compact(item)]
    tags = [compact(item) for item in document.get("tags", []) if compact(item)]
    date_only = str(document.get("dateOnly"))
    date_time = str(document.get("dateTime"))
    author = compact(document.get("author")) or AUTHOR_NAME
    if not BeautifulSoup(body_html, "html.parser").get_text(" ", strip=True):
        source_link = compact(document.get("sourceUrl"))
        source_note = (
            f'<p><a href="{html.escape(source_link)}" rel="noopener noreferrer">'
            "查看原始 GitBook 页面</a></p>"
            if source_link.startswith(("http://", "https://"))
            else ""
        )
        body_html = (
            '<section class="seo-summary">'
            "<h2>文档说明</h2>"
            "<p>该原始文档是工程目录、章节或占位记录，源文件中仅保留了标题，"
            "没有可公开展示的正文。本页保留真实标题、分类、标签、日期、"
            "来源链接与 Markdown 原文入口，便于后续补充和检索。</p>"
            f"{source_note}</section>"
        )

    previous = doc_by_id.get(str(document.get("previousId", "")))
    next_doc = doc_by_id.get(str(document.get("nextId", "")))

    toc_html = ""
    if len(toc) >= 2:
        items = "".join(
            f'<li style="margin-left:{(level - 2) * 0.8:.1f}rem"><a href="#{html.escape(anchor)}">'
            f"{html.escape(text)}</a></li>"
            for level, text, anchor in toc[:28]
        )
        toc_html = f'<aside class="aside-box"><h2>本页目录</h2><ol>{items}</ol></aside>'

    tag_html = "".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in tags)
    category_html = " / ".join(html.escape(item) for item in category_path) or html.escape(category)
    source = compact(document.get("sourceUrl"))
    source_html = ""
    if source.startswith(("https://", "http://")):
        source_html = (
            f'<li><a href="{html.escape(source)}" rel="noopener noreferrer">查看原始来源</a></li>'
        )
    else:
        source_path = compact(document.get("sourcePath"), 90)
        if source_path:
            source_html = f"<li><span>来源：{html.escape(source_path)}</span></li>"
    source_html += (
        f'<li><a href="{html.escape(markdown_href)}" type="text/markdown">查看 Markdown 原文</a></li>'
    )

    pager_html = ""
    pager_items = []
    if previous:
        pager_items.append(
            f'<a href="{html.escape(doc_url(previous))}"><small>上一篇</small>'
            f"{html.escape(compact(previous.get('title'), 70))}</a>"
        )
    if next_doc:
        pager_items.append(
            f'<a href="{html.escape(doc_url(next_doc))}"><small>下一篇</small>'
            f"{html.escape(compact(next_doc.get('title'), 70))}</a>"
        )
    if pager_items:
        pager_html = f'<nav class="pager" aria-label="文章翻页">{"".join(pager_items)}</nav>'

    structured = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "TechArticle",
                "@id": canonical + "#article",
                "headline": display_title,
                "description": description,
                "datePublished": date_time,
                "dateModified": str(document.get("updated") or date_time),
                "inLanguage": "zh-CN",
                "articleSection": category_path or [category],
                "keywords": keywords,
                "wordCount": int(document.get("wordCount") or 0),
                "mainEntityOfPage": canonical,
                "url": canonical,
                "author": {
                    "@type": "Person",
                    "name": author,
                    "url": AUTHOR_URL,
                },
                "publisher": {
                    "@type": "Organization",
                    "name": SITE_NAME,
                    "url": SITE_BASE,
                },
                **({"image": [og_image]} if og_image else {}),
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": SITE_NAME,
                        "item": SITE_BASE,
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": category,
                        "item": f"{SITE_BASE}assets/seo/index.html",
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": title,
                        "item": canonical,
                    },
                ],
            },
        ],
    }

    og_image_html = (
        f'<meta property="og:image" content="{html.escape(og_image)}">'
        if og_image
        else ""
    )
    twitter_image_html = (
        f'<meta name="twitter:image" content="{html.escape(og_image)}">'
        if og_image
        else ""
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{html.escape(display_title)}｜{html.escape(category)}｜BEN.OPS</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="keywords" content="{html.escape('，'.join(keywords))}">
  <meta name="author" content="{html.escape(author)}">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
  <meta name="googlebot" content="index,follow,max-snippet:-1,max-image-preview:large">
  <meta name="baiduspider" content="index,follow">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="canonical" href="{html.escape(canonical)}">
  <link rel="alternate" hreflang="zh-CN" href="{html.escape(canonical)}">
  <link rel="alternate" type="text/markdown" href="{html.escape(markdown_href)}">
  <link rel="alternate" type="application/rss+xml" title="BEN.OPS RSS" href="{SITE_BASE}assets/rss.xml">
  <link rel="alternate" type="application/xml" title="BEN.OPS Sitemap" href="{SITE_BASE}assets/sitemap.xml">
  <link rel="author" href="{html.escape(AUTHOR_URL)}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="zh_CN">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{html.escape(display_title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{html.escape(canonical)}">
  <meta property="article:published_time" content="{html.escape(date_time)}">
  <meta property="article:modified_time" content="{html.escape(str(document.get('updated') or date_time))}">
  <meta property="article:section" content="{html.escape(category)}">
  <meta property="article:author" content="{html.escape(AUTHOR_URL)}">
  {og_image_html}
  <meta name="twitter:card" content="{'summary_large_image' if og_image else 'summary'}">
  <meta name="twitter:title" content="{html.escape(display_title)}">
  <meta name="twitter:description" content="{html.escape(description)}">
  {twitter_image_html}
  <style>{PAGE_STYLE}</style>
  <script type="application/ld+json">{json_for_script(structured)}</script>
</head>
<body>
  <header class="topbar"><div class="shell">
    <a class="brand" href="{SITE_BASE}"><b>$_</b> BEN.OPS</a>
    <nav aria-label="站点导航">
      <a href="{SITE_BASE}">交互知识库</a>
      <a href="{SITE_BASE}assets/seo/index.html">静态文章索引</a>
      <a href="{html.escape(AUTHOR_URL)}">@Ben_Bird</a>
    </nav>
  </div></header>
  <main class="shell">
    <nav class="crumbs" aria-label="面包屑">
      <a href="{SITE_BASE}">首页</a> › <a href="{SITE_BASE}assets/seo/index.html">工程笔记</a>
      › <span>{category_html}</span> › <span>{html.escape(display_title)}</span>
    </nav>
    <header class="hero">
      <div class="eyebrow">{html.escape(category)}</div>
      <h1>{html.escape(display_title)}</h1>
      <p class="lede">{html.escape(description)}</p>
      <div class="meta">
        <time class="badge" datetime="{html.escape(date_time)}">发布于 {html.escape(date_only)}</time>
        <span class="badge">作者 {html.escape(author)}</span>
        <span class="badge">{int(document.get('wordCount') or 0):,} 字</span>
        <span class="badge">{int(document.get('readingTime') or 0)} 分钟阅读</span>
      </div>
    </header>
    <div class="layout">
      <article class="article" itemscope itemtype="https://schema.org/TechArticle">
        {body_html}
      </article>
      <aside class="aside">
        {toc_html}
        <div class="aside-box"><h2>文章信息</h2><ul>
          <li>分类：{category_html}</li>
          <li>日期：{html.escape(date_only)}</li>
          <li>标签：{tag_html}</li>
          {source_html}
        </ul></div>
        <div class="aside-box"><h2>作者</h2>
          <p><a href="{html.escape(AUTHOR_URL)}">@Ben_Bird</a></p>
          <p>Linux / DevOps / SRE / 云平台 / 安全运维</p>
        </div>
      </aside>
    </div>
    <section class="seo-summary" aria-labelledby="seo-summary-title">
      <h2 id="seo-summary-title">文章摘要</h2>
      <p>{html.escape(description)}</p>
      <p>关键词：{html.escape('、'.join(keywords))}</p>
    </section>
    {pager_html}
  </main>
  <footer><div class="shell">
    <span>© {datetime.now().year} BEN.OPS</span>
    <a href="{html.escape(GITHUB_URL)}">GitHub</a>
    <a href="{html.escape(AUTHOR_URL)}">Telegram @Ben_Bird</a>
    <a href="{html.escape(canonical)}">本页永久链接</a>
  </div></footer>
</body>
</html>
"""


def build_index(
    documents: list[dict[str, object]],
    categories: list[dict[str, object]],
    descriptions: dict[str, str],
) -> str:
    ordered = sorted(
        documents,
        key=lambda item: (str(item.get("dateTime")), str(item.get("title"))),
        reverse=True,
    )
    by_year: dict[str, list[dict[str, object]]] = defaultdict(list)
    for document in ordered:
        by_year[str(document["dateOnly"])[:4]].append(document)

    category_counts = Counter(str(item.get("categoryLabel")) for item in documents)
    category_nav = "".join(
        f'<span class="tag">{html.escape(name)} {count:,}</span>'
        for name, count in category_counts.most_common(20)
    )
    year_html: list[str] = []
    for year in sorted(by_year, reverse=True):
        cards = []
        for document in by_year[year]:
            tags = "".join(
                f'<span class="tag">{html.escape(compact(tag))}</span>'
                for tag in document.get("tags", [])[:5]
            )
            cards.append(
                '<article class="card">'
                f'<time class="date" datetime="{html.escape(str(document["dateOnly"]))}">'
                f'{html.escape(str(document["dateOnly"]))}</time>'
                f'<h3><a href="{html.escape(doc_url(document))}">'
                f'{html.escape(compact(document.get("title")))}</a></h3>'
                f'<p>{html.escape(descriptions[str(document["id"])])}</p>'
                f'<div class="meta">{tags}</div>'
                "</article>"
            )
        year_html.append(
            f'<section class="year" aria-labelledby="year-{year}">'
            f'<h2 id="year-{year}">{year} 年 · {len(by_year[year]):,} 篇</h2>'
            f'<div class="cards">{"".join(cards)}</div></section>'
        )

    description = (
        f"BEN.OPS 工程笔记静态索引，共 {len(documents):,} 篇中文技术文章，"
        "覆盖 Linux、DevOps、SRE、Kubernetes、数据库、监控、CDN、安全运维与故障排查。"
    )
    structured = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "BEN.OPS 工程笔记静态文章索引",
        "description": description,
        "url": f"{SITE_BASE}assets/seo/index.html",
        "inLanguage": "zh-CN",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_BASE},
        "author": {"@type": "Person", "name": AUTHOR_NAME, "url": AUTHOR_URL},
        "numberOfItems": len(documents),
    }
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>BEN.OPS 工程笔记静态索引｜{len(documents):,} 篇 Linux、DevOps、SRE 与安全运维文章</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="keywords" content="{html.escape('，'.join(DEFAULT_KEYWORDS))}">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
  <meta name="googlebot" content="index,follow,max-snippet:-1,max-image-preview:large">
  <meta name="baiduspider" content="index,follow">
  <link rel="canonical" href="{SITE_BASE}assets/seo/index.html">
  <link rel="alternate" hreflang="zh-CN" href="{SITE_BASE}assets/seo/index.html">
  <link rel="alternate" type="application/rss+xml" title="BEN.OPS RSS" href="{SITE_BASE}assets/rss.xml">
  <link rel="alternate" type="application/xml" title="BEN.OPS Sitemap" href="{SITE_BASE}assets/sitemap.xml">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="zh_CN">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="BEN.OPS 工程笔记静态索引">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{SITE_BASE}assets/seo/index.html">
  <meta name="twitter:card" content="summary">
  <style>{PAGE_STYLE}</style>
  <script type="application/ld+json">{json_for_script(structured)}</script>
</head>
<body>
  <header class="topbar"><div class="shell">
    <a class="brand" href="{SITE_BASE}"><b>$_</b> BEN.OPS</a>
    <nav aria-label="站点导航"><a href="{SITE_BASE}">交互知识库</a>
      <a href="{SITE_BASE}assets/rss.xml">RSS</a><a href="{html.escape(AUTHOR_URL)}">@Ben_Bird</a></nav>
  </div></header>
  <main class="shell">
    <header class="hero index-hero">
      <div class="eyebrow">Crawlable Engineering Notes</div>
      <h1>BEN.OPS 工程笔记静态索引</h1>
      <p class="lede">{html.escape(description)}</p>
      <div class="stat-grid">
        <div class="stat"><strong>{len(documents):,}</strong><span>技术文章</span></div>
        <div class="stat"><strong>{len(category_counts):,}</strong><span>内容分类</span></div>
        <div class="stat"><strong>{len(by_year):,}</strong><span>记录年份</span></div>
        <div class="stat"><strong>{sum(int(item.get('wordCount') or 0) for item in documents):,}</strong><span>累计字词</span></div>
      </div>
      <p class="meta"><span class="badge">作者 @Ben_Bird</span><span class="badge">静态 HTML</span><span class="badge">完整正文</span><span class="badge">结构化数据</span></p>
    </header>
    <section class="seo-summary"><h2>热门分类</h2><div class="meta">{category_nav}</div></section>
    {''.join(year_html)}
  </main>
  <footer><div class="shell"><span>© {datetime.now().year} BEN.OPS</span>
    <a href="{html.escape(GITHUB_URL)}">GitHub</a><a href="{html.escape(AUTHOR_URL)}">Telegram @Ben_Bird</a>
  </div></footer>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("/Users/ben/ben随笔文档"))
    args = parser.parse_args()
    root = args.root.resolve()
    assets = root / "assets"
    seo_dir = assets / "seo"
    seo_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads((assets / "data.json").read_text(encoding="utf-8"))
    documents: list[dict[str, object]] = data["documents"]
    doc_by_id = {str(item["id"]): item for item in documents}
    doc_by_md = {str(item["mdHref"]): item for item in documents}
    seo_titles = unique_seo_titles(documents)

    manifest: list[dict[str, object]] = []
    descriptions: dict[str, str] = {}
    errors: list[str] = []
    image_count = 0
    for index, document in enumerate(documents, 1):
        try:
            body_html, toc, og_image = render_markdown(document, doc_by_md)
            if "<main" in body_html or "<html" in body_html.lower():
                raise ValueError("unexpected document wrapper")
            page_path = seo_dir / f"{document['id']}.html"
            display_title = seo_titles[str(document["id"])]
            page_path.write_text(
                page_html(
                    document,
                    body_html,
                    toc,
                    og_image,
                    doc_by_id,
                    display_title,
                ),
                encoding="utf-8",
            )
            description = article_description(document, body_html)
            descriptions[str(document["id"])] = description
            manifest.append(
                {
                    "id": document["id"],
                    "title": display_title,
                    "sourceTitle": document["title"],
                    "date": document["dateTime"],
                    "dateOnly": document["dateOnly"],
                    "category": document["categoryLabel"],
                    "tags": document["tags"],
                    "description": description,
                    "keywords": keyword_list(document),
                    "markdown": document["mdHref"],
                    "html": page_path.relative_to(root).as_posix(),
                    "canonical": doc_url(document),
                }
            )
            image_count += body_html.count("<img")
        except Exception as exc:  # Continue and report all document failures.
            errors.append(f"{document.get('id')}: {exc}")
        if index % 250 == 0:
            print(f"SEO PAGES {index}/{len(documents)}", flush=True)

    index_path = seo_dir / "index.html"
    index_path.write_text(
        build_index(documents, data["categories"], descriptions),
        encoding="utf-8",
    )
    manifest_path = assets / "seo-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    robots_path = root / "robots.txt"
    robots_path.write_text(
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_BASE}assets/sitemap.xml\n",
        encoding="utf-8",
    )
    result = {
        "documents": len(documents),
        "pages": len(manifest),
        "dateGroups": len({str(item["dateOnly"]) for item in manifest}),
        "imagesEmbedded": image_count,
        "seoIndex": str(index_path),
        "manifest": str(manifest_path),
        "robots": str(robots_path),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
