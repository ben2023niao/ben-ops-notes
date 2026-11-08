(() => {
  "use strict";

  const DATA = window.NOTES_DATA;
  const byId = new Map((DATA?.documents || []).map((doc) => [doc.id, doc]));
  const mdByPath = new Map();
  (DATA?.documents || []).forEach((doc) => {
    mdByPath.set(doc.mdHref, doc);
    try {
      mdByPath.set(decodeURI(doc.mdHref), doc);
    } catch (_) {}
  });
  const state = { query: "", category: "", tag: "", sort: "newest", limit: 80, docId: "", view: "" };
  const themes = ["terminal", "matrix", "blueprint", "amber", "light"];
  const view = document.getElementById("view");
  const search = document.getElementById("global-search");
  const categoryTree = document.getElementById("category-tree");
  const tocPanel = document.getElementById("toc-panel");
  const rightPanelBody = document.getElementById("right-panel-body");
  const breadcrumb = document.getElementById("breadcrumb");
  const palette = document.getElementById("search-palette");
  const progress = document.getElementById("reading-progress");
  const favoritesKey = "ben-notes-favorites";
  const historyKey = "ben-notes-history";
  const motionKey = "ben-notes-motion";
  const eyeKey = "ben-notes-eye-care";
  const quotes = [
    ["工欲善其事，必先利其器。", "《论语》"],
    ["合抱之木，生于毫末；九层之台，起于累土。", "《道德经》"],
    ["路漫漫其修远兮，吾将上下而求索。", "屈原"],
    ["纸上得来终觉浅，绝知此事要躬行。", "陆游"],
    ["不积跬步，无以至千里；不积小流，无以成江海。", "《荀子》"],
    ["博学之，审问之，慎思之，明辨之，笃行之。", "《礼记》"],
    ["苟日新，日日新，又日新。", "《礼记》"],
    ["天下大事，必作于细。", "《道德经》"],
    ["知不足，然后能自反也；知困，然后能自强也。", "《礼记》"],
    ["Stay hungry. Stay foolish.", "Steve Jobs"],
    ["Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"]
  ];
  let quoteTimer = null;

  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[ch]));
  const fmt = (n) => new Intl.NumberFormat("zh-CN").format(Number(n || 0));
  const highlightText = (value, query) => {
    const safe = esc(value);
    if (!query) return safe;
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return safe.replace(new RegExp(`(${escaped})`, "ig"), "<mark>$1</mark>");
  };
  const dateFmt = (value) => {
    if (!value) return "日期未知";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("zh-CN", {
      year: "numeric", month: "2-digit", day: "2-digit"
    }).format(date);
  };
  const icon = (name, size = 14) => `<i data-lucide="${name}" width="${size}" height="${size}"></i>`;
  const refreshIcons = () => window.lucide?.createIcons();
  const favorites = () => new Set(JSON.parse(localStorage.getItem(favoritesKey) || "[]"));
  const history = () => JSON.parse(localStorage.getItem(historyKey) || "[]");
  const remember = (id) => {
    const list = history().filter((item) => item !== id);
    list.unshift(id);
    localStorage.setItem(historyKey, JSON.stringify(list.slice(0, 50)));
  };

  function resolveTheme(preference) {
    if (preference !== "auto") return themes.includes(preference) ? preference : "terminal";
    const hour = new Date().getHours();
    return hour >= 6 && hour < 18 ? "light" : "terminal";
  }

  function setTheme(preference, persist = true) {
    const selected = preference === "auto" || themes.includes(preference) ? preference : "auto";
    document.documentElement.dataset.theme = resolveTheme(selected);
    document.documentElement.dataset.preference = selected;
    document.getElementById("theme-select").value = selected;
    if (persist) localStorage.setItem("ben-notes-theme", selected);
  }

  function initTheme() {
    setTheme(localStorage.getItem("ben-notes-theme") || "auto", false);
    document.getElementById("theme-select").addEventListener("change", (event) => setTheme(event.target.value));
    document.getElementById("theme-cycle").addEventListener("click", () => {
      const current = document.documentElement.dataset.theme || "terminal";
      setTheme(themes[(themes.indexOf(current) + 1) % themes.length]);
    });
    window.setInterval(() => {
      if ((localStorage.getItem("ben-notes-theme") || "auto") === "auto") setTheme("auto", false);
    }, 60_000);
  }

  function motionEnabled() {
    return localStorage.getItem(motionKey) !== "off" && !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function initComfort() {
    document.body.classList.toggle("eye-care", localStorage.getItem(eyeKey) !== "off");
    const motion = document.getElementById("motion-toggle");
    const eye = document.getElementById("eye-toggle");
    const sync = () => {
      document.body.classList.toggle("reduce-motion", !motionEnabled());
      motion.textContent = `命令动效：${motionEnabled() ? "开" : "关"}`;
      eye.textContent = `护眼模式：${document.body.classList.contains("eye-care") ? "开" : "关"}`;
    };
    motion.addEventListener("click", () => {
      localStorage.setItem(motionKey, motionEnabled() ? "off" : "on");
      sync();
      render();
    });
    eye.addEventListener("click", () => {
      document.body.classList.toggle("eye-care", localStorage.getItem(eyeKey) === "off");
      localStorage.setItem(eyeKey, document.body.classList.contains("eye-care") ? "on" : "off");
      sync();
    });
    sync();
  }

  function typeCommand(node) {
    const text = node.dataset.type || "";
    if (!text) return;
    if (!motionEnabled()) {
      node.textContent = text;
      return;
    }
    let index = 0;
    node.textContent = "";
    const timer = setInterval(() => {
      node.textContent = text.slice(0, ++index);
      if (index >= text.length) clearInterval(timer);
    }, 70);
  }

  function startQuoteRotation(root) {
    window.clearInterval(quoteTimer);
    const text = root.querySelector(".quote-text");
    const source = root.querySelector(".quote-source");
    if (!text || !source) return;
    let index = 0;
    const paint = () => {
      text.textContent = `“${quotes[index][0]}”`;
      source.textContent = `— ${quotes[index][1]}`;
    };
    paint();
    quoteTimer = window.setInterval(() => {
      index = (index + 1) % quotes.length;
      if (!motionEnabled()) {
        paint();
        return;
      }
      text.classList.add("switching");
      source.classList.add("switching");
      window.setTimeout(() => {
        paint();
        text.classList.remove("switching");
        source.classList.remove("switching");
      }, 220);
    }, 7000);
  }

  function stopQuoteRotation() {
    window.clearInterval(quoteTimer);
    quoteTimer = null;
  }

  function openDrawer(open) {
    document.body.classList.toggle("drawer-open", open);
  }

  function route() {
    const hash = decodeURIComponent(location.hash.slice(1));
    const params = new URLSearchParams(hash);
    state.docId = params.get("doc") || "";
    state.view = params.get("view") || "";
    state.category = params.get("category") || "";
    state.tag = params.get("tag") || "";
    state.query = params.get("q") || "";
    search.value = state.query;
    state.limit = 80;
    render();
    openDrawer(false);
  }

  function go(params) {
    const clean = {};
    Object.entries(params).forEach(([key, value]) => {
      if (value !== "" && value != null) clean[key] = value;
    });
    location.hash = new URLSearchParams(clean).toString();
  }

  function renderPrimaryNav() {
    const favs = favorites();
    const reads = history();
    const items = [
      ["home", "terminal", "知识首页", DATA.stats.documents],
      ["recent", "history", "最近更新", DATA.stats.documents],
      ["all", "files", "全部文档", DATA.stats.documents],
      ["favorites", "star", "收藏夹", favs.size],
      ["history", "clock-3", "阅读历史", reads.length],
    ];
    document.getElementById("primary-nav").innerHTML = items.map(([id, iconName, label, count]) => `
      <button class="nav-item" data-nav="${id}">
        <span class="nav-icon">${icon(iconName, 14)}</span><span>${esc(label)}</span><span class="nav-badge">${fmt(count)}</span>
      </button>`).join("");
    document.querySelectorAll("[data-nav]").forEach((button) => {
      button.addEventListener("click", () => {
        if (button.dataset.nav === "home") go({});
        else if (button.dataset.nav === "recent") go({ sort: "recent" });
        else if (button.dataset.nav === "favorites") go({ view: "favorites" });
        else if (button.dataset.nav === "history") go({ view: "history" });
        else go({ sort: "all" });
      });
    });
  }

  function renderCategoryTree() {
    const roots = DATA.categoryTree || [];
    const categoryIcon = (name) => {
      if (/Linux|Shell|主机|系统/.test(name)) return "terminal-square";
      if (/Docker|Kubernetes|容器/.test(name)) return "boxes";
      if (/Network|网络|Nginx|DNS/.test(name)) return "network";
      if (/Security|安全|CVE|漏洞|应急/.test(name)) return "shield-check";
      if (/Database|SQL|Redis|Mongo/.test(name)) return "database";
      if (/Cloud|DevOps|AWS|CI|工具/.test(name)) return "cloud-cog";
      if (/Web|XSS|注入|客户端|文件/.test(name)) return "globe-2";
      return "folder-tree";
    };
    const nodeHtml = (node, depth = 0) => {
      const children = node.children || [];
      return `<div class="tree-node ${depth < 1 ? "open" : ""}" data-category-node="${esc(node.id)}">
        <button class="tree-button" data-category="${esc(node.id)}">
          <span class="tree-caret">${children.length ? "▸" : ""}</span>
          <span class="tree-icon">${icon(categoryIcon(node.name), 12)}</span>
          <span class="tree-label">${esc(node.name)}</span>
          <span class="tree-count">${fmt(node.count)}</span>
        </button>
        ${children.length ? `<div class="tree-children">${children.map((child) => nodeHtml(child, depth + 1)).join("")}</div>` : ""}
      </div>`;
    };
    categoryTree.innerHTML = roots.map((node) => nodeHtml(node)).join("");
    categoryTree.querySelectorAll("[data-category]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        const node = button.closest(".tree-node");
        if (node && node.querySelector(".tree-children")) node.classList.toggle("open");
        go({ category: button.dataset.category });
      });
    });
  }

  function renderSidebarTags() {
    document.getElementById("sidebar-tags").innerHTML = DATA.tags.slice(0, 30).map((tag) =>
      `<button class="tag-chip" data-tag="${esc(tag.name)}">${esc(tag.name)}</button>`
    ).join("");
    document.querySelectorAll("#sidebar-tags [data-tag]").forEach((button) => {
      button.addEventListener("click", () => go({ tag: button.dataset.tag }));
    });
  }

  function docsForCategory(categoryId) {
    const node = DATA.categoryIndex?.[categoryId];
    if (!node) return [];
    const ids = new Set(node.documentIds || []);
    return DATA.documents.filter((doc) => ids.has(doc.id) || (node.path || []).every((part, index) => doc.categoryPath[index] === part));
  }

  function filteredDocs() {
    let docs = DATA.documents.slice();
    if (state.view === "favorites") docs = docs.filter((doc) => favorites().has(doc.id));
    if (state.view === "history") docs = history().map((id) => byId.get(id)).filter(Boolean);
    if (state.category) docs = docsForCategory(state.category);
    if (state.tag) docs = docs.filter((doc) => doc.tags.includes(state.tag));
    if (state.query) {
      const q = state.query.toLowerCase();
      docs = docs
        .map((doc) => ({ doc, score: fuzzyScore(q, doc.searchText.toLowerCase()) }))
        .filter((item) => item.score > 0)
        .sort((a, b) => b.score - a.score)
        .map((item) => item.doc);
    }
    if (!state.query && state.sort === "oldest") docs.sort((a, b) => a.dateTime.localeCompare(b.dateTime));
    else if (!state.query) docs.sort((a, b) => b.dateTime.localeCompare(a.dateTime));
    return docs;
  }

  function fuzzyScore(query, haystack) {
    if (!query) return 1;
    if (haystack.includes(query)) return 1000 - Math.min(900, haystack.indexOf(query) / 10);
    let cursor = 0;
    let score = 0;
    for (const char of query) {
      const found = haystack.indexOf(char, cursor);
      if (found < 0) return 0;
      score += found === cursor ? 8 : 2;
      cursor = found + 1;
    }
    return score;
  }

  function snippetFor(doc, query) {
    const source = doc.description || doc.searchText || "";
    const index = source.toLowerCase().indexOf(query.toLowerCase());
    const text = index >= 0 ? source.slice(Math.max(0, index - 40), index + 130) : source.slice(0, 150);
    if (!query) return esc(text);
    const safe = esc(text);
    return safe.replace(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "ig"), "<mark>$1</mark>");
  }

  function renderSearchPalette() {
    const query = search.value.trim();
    if (!query) {
      palette.hidden = true;
      palette.innerHTML = "";
      return;
    }
    let pool = state.category ? docsForCategory(state.category) : DATA.documents.slice();
    if (state.tag) pool = pool.filter((doc) => doc.tags.includes(state.tag));
    const matches = pool
      .map((doc) => ({ doc, score: fuzzyScore(query.toLowerCase(), doc.searchText.toLowerCase()) }))
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 14)
      .map((item) => item.doc);
    palette.innerHTML = `<div class="palette-head"><span>全局搜索</span><kbd>ESC</kbd></div>
      ${matches.map((doc) => `<button class="palette-item" data-doc="${esc(doc.id)}">
        <span class="palette-icon">${icon("file-text", 14)}</span>
        <span class="palette-main"><strong>${esc(doc.title)}</strong><small>${snippetFor(doc, query)}</small></span>
        <span class="palette-meta">${esc(doc.categoryLabel)}<br>${esc(doc.dateOnly)}</span>
      </button>`).join("") || `<div class="palette-empty">没有匹配的文档</div>`}`;
    palette.hidden = false;
    palette.querySelectorAll("[data-doc]").forEach((button) => button.addEventListener("click", () => {
      palette.hidden = true;
      go({ doc: button.dataset.doc });
    }));
    refreshIcons();
  }

  function updateReadingProgress() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${max > 0 ? Math.min(100, (window.scrollY / max) * 100) : 0}%`;
  }

  let headingObserver = null;
  function watchHeadings(root) {
    headingObserver?.disconnect();
    const links = [...rightPanelBody.querySelectorAll(".article-toc a")];
    if (!links.length || !("IntersectionObserver" in window)) return;
    headingObserver = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!visible) return;
      links.forEach((link) => link.classList.toggle("active", link.getAttribute("href") === `#${visible.target.id}`));
    }, { rootMargin: "-80px 0px -72% 0px", threshold: [0, 1] });
    root.querySelectorAll("h1,h2,h3,h4").forEach((heading) => heading.id && headingObserver.observe(heading));
  }

  function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(() => toast.classList.remove("show"), 1600);
  }

  function openLightbox(src, alt = "") {
    const overlay = document.createElement("div");
    overlay.className = "lightbox";
    overlay.innerHTML = `<button aria-label="关闭">×</button><img src="${esc(src)}" alt="${esc(alt)}">`;
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay || event.target.closest("button")) overlay.remove();
    });
    document.body.appendChild(overlay);
  }

  function markdownToHtml(markdown, title) {
    if (!window.marked?.parse) return `<blockquote><p>Markdown 渲染器未加载。</p></blockquote>`;
    const template = document.createElement("template");
    template.innerHTML = window.marked.parse(markdown || "", { gfm: true, breaks: false });
    const firstHeading = template.content.querySelector("h1");
    if (firstHeading && firstHeading.textContent.trim() === title.trim()) firstHeading.remove();
    template.content.querySelectorAll("script,style,iframe,object,embed,form,input,button,textarea,select,meta,link").forEach((node) => node.remove());
    template.content.querySelectorAll("*").forEach((node) => {
      [...node.attributes].forEach((attribute) => {
        const name = attribute.name.toLowerCase();
        const value = attribute.value.trim();
        if (name.startsWith("on") || name === "style") node.removeAttribute(attribute.name);
        if ((name === "href" || name === "src" || name === "xlink:href") && /^(?:javascript|vbscript|data:text\/html)/i.test(value)) {
          node.removeAttribute(attribute.name);
        }
      });
      if (node.tagName === "A") {
        node.rel = "noopener noreferrer";
      }
    });
    return template.innerHTML;
  }

  function prepareHeadings(root) {
    const seen = new Map();
    return [...root.querySelectorAll("h1,h2,h3,h4,h5,h6")].map((heading, index) => {
      const text = heading.textContent.trim();
      const base = text
        .toLowerCase()
        .replace(/[^\p{L}\p{N}\s-]/gu, "")
        .trim()
        .replace(/\s+/g, "-") || `section-${index + 1}`;
      const count = (seen.get(base) || 0) + 1;
      seen.set(base, count);
      heading.id = count === 1 ? base : `${base}-${count}`;
      return { level: Number(heading.tagName.slice(1)), text, id: heading.id };
    });
  }

  function renderRightHome() {
    const docs = DATA.documents.slice().sort((a, b) => b.dateTime.localeCompare(a.dateTime));
    const recentIds = history().map((id) => byId.get(id)).filter(Boolean).slice(0, 5);
    const favs = [...favorites()].map((id) => byId.get(id)).filter(Boolean).slice(0, 5);
    rightPanelBody.innerHTML = `
      <section class="side-panel"><div class="toc-head">本地状态</div><div class="status-list">
        <div><span>本地数据</span><b class="ok">已加载</b></div>
        <div><span>静态构建</span><b class="ok">就绪</b></div>
        <div><span>最近更新</span><b>${esc(DATA.generatedAt.slice(0, 10))}</b></div>
        <div><span>数据版本</span><b>${esc(DATA.schemaVersion)}.0</b></div>
        <div><span>作者</span><b><a class="author-link" href="https://t.me/Ben_Bird" target="_blank" rel="noopener">@Ben_Bird</a></b></div>
      </div></section>
      <section class="side-panel"><div class="toc-head">快速入口</div>
        ${DATA.tags.slice(0, 6).map((tag) => `<button class="side-link" data-side-tag="${esc(tag.name)}">${icon("command", 12)} ${esc(tag.name)}</button>`).join("")}
        <a class="side-link" href="assets/rss.xml">${icon("rss", 12)} RSS 订阅</a>
        <a class="side-link" href="assets/sitemap.xml">${icon("map", 12)} 站点地图</a>
        <a class="side-link" href="assets/README.html">${icon("book-open", 12)} 维护说明</a>
      </section>
      <section class="side-panel"><div class="toc-head">最近活动</div>
        ${(recentIds.length ? recentIds : docs.slice(0, 5)).map((doc) => `<button class="side-link truncate" data-side-doc="${esc(doc.id)}">${icon("clock", 12)} ${esc(doc.title)}</button>`).join("")}
      </section>
      ${favs.length ? `<section class="side-panel"><div class="toc-head">收藏夹</div>${favs.map((doc) => `<button class="side-link truncate" data-side-doc="${esc(doc.id)}">${icon("star", 12)} ${esc(doc.title)}</button>`).join("")}</section>` : ""}`;
    tocPanel.hidden = false;
    rightPanelBody.querySelectorAll("[data-side-tag]").forEach((button) => button.addEventListener("click", () => go({ tag: button.dataset.sideTag })));
    rightPanelBody.querySelectorAll("[data-side-doc]").forEach((button) => button.addEventListener("click", () => go({ doc: button.dataset.sideDoc })));
    refreshIcons();
  }

  function docCard(doc) {
    return `<article class="doc-card" data-doc="${esc(doc.id)}">
      <div class="doc-card-top"><span class="doc-type">${esc(doc.kind)}</span><span>${esc(doc.categoryLabel)}</span><span>·</span><time>${dateFmt(doc.date)}</time></div>
      <h3>${esc(doc.title)}</h3>
      <p>${esc(doc.description || "暂无摘要")}</p>
      <div class="card-meta">${doc.tags.slice(0, 4).map((tag) => `<span>#${esc(tag)}</span>`).join("")}</div>
    </article>`;
  }

  function bindCards(root = view) {
    root.querySelectorAll("[data-doc]").forEach((node) => {
      node.addEventListener("click", (event) => {
        if (event.target.closest("[data-inline-action]")) return;
        go({ doc: node.dataset.doc });
      });
    });
  }

  let lastTerminalResults = [];
  const terminalHistory = [];
  let terminalHistoryIndex = 0;

  function appendTerminalLine(text, className = "") {
    const output = document.getElementById("terminal-output");
    if (!output) return;
    const line = document.createElement("div");
    line.className = `terminal-output-line ${className}`.trim();
    line.textContent = text;
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
  }

  function printTerminalLines(lines, state = "") {
    lines.forEach((line, index) => {
      window.setTimeout(() => appendTerminalLine(line, state), motionEnabled() ? index * 70 : 0);
    });
  }

  function runTerminalCommand(raw) {
    const command = raw.trim();
    if (!command) return;
    appendTerminalLine(`root@ben-ops:~$ ${command}`, "command");
    terminalHistory.push(command);
    terminalHistoryIndex = terminalHistory.length;
    const [verb, ...rest] = command.split(/\s+/);
    const argument = rest.join(" ");
    const lower = verb.toLowerCase();
    if (lower === "help") {
      printTerminalLines([
        "可用命令：",
        "  whoami                 显示当前身份",
        "  ls categories          列出技术分类",
        "  stats                  显示知识库统计",
        "  search <关键词>         全文检索",
        "  open <序号|文档ID>      打开检索结果",
        "  cat <序号>              只查看文档元信息",
        "  theme [auto|terminal|matrix|blueprint|amber|light]",
        "  motion [on|off]        开关命令动效",
        "  eye [on|off]           开关护眼色调",
        "  date | pwd | clear | history"
      ]);
      return;
    }
    if (lower === "whoami") {
      printTerminalLines(["基础设施工程师", "Linux · DevOps · SRE · Cloud · Security", "Telegram: @Ben_Bird"], "ok");
      return;
    }
    if (lower === "pwd") {
      printTerminalLines(["/Users/ben/ben随笔文档"], "ok");
      return;
    }
    if (lower === "date") {
      printTerminalLines([new Date().toString()], "ok");
      return;
    }
    if (lower === "stats") {
      printTerminalLines([
        `文档：${fmt(DATA.stats.documents)}`,
        `分类：${fmt(DATA.stats.categories)}`,
        `标签：${fmt(DATA.stats.tags)}`,
        `媒体：${fmt(DATA.stats.media)}`,
        `关系：${fmt(DATA.stats.relationships)}`,
        `最近构建：${DATA.generatedAt}`
      ], "ok");
      return;
    }
    if (lower === "history") {
      printTerminalLines(terminalHistory.slice(-20).map((item, index) => `${index + 1}  ${item}`), "ok");
      return;
    }
    if (lower === "clear") {
      document.getElementById("terminal-output").innerHTML = "";
      return;
    }
    if (lower === "ls" && (argument === "categories" || argument === "./categories")) {
      printTerminalLines(DATA.categoryTree.map((item, index) => `${String(index + 1).padStart(2, "0")}  ${item.name.padEnd(18, " ")} ${fmt(item.count)} 篇`), "ok");
      return;
    }
    if (lower === "search") {
      if (!argument) {
        printTerminalLines(["用法：search <关键词>"], "error");
        return;
      }
      const query = argument.toLowerCase();
      lastTerminalResults = DATA.documents
        .map((doc) => ({ doc, score: fuzzyScore(query, doc.searchText.toLowerCase()) }))
        .filter((item) => item.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 12)
        .map((item) => item.doc);
      if (!lastTerminalResults.length) {
        printTerminalLines([`未找到：${argument}`], "error");
        return;
      }
      printTerminalLines(lastTerminalResults.map((doc, index) => `${String(index + 1).padStart(2, "0")}  ${doc.dateOnly}  ${doc.title}`).concat("使用 open <序号> 打开文档。"), "ok");
      return;
    }
    if (lower === "cat" || lower === "open") {
      const numeric = Number(argument);
      const doc = Number.isInteger(numeric) && numeric > 0
        ? lastTerminalResults[numeric - 1]
        : (byId.get(argument) || lastTerminalResults.find((item) => item.title.toLowerCase().includes(argument.toLowerCase())));
      if (!doc) {
        printTerminalLines(["文档不存在。先执行 search <关键词>，再使用 open <序号>。"], "error");
        return;
      }
      if (lower === "open") {
        printTerminalLines([`打开：${doc.title}`], "ok");
        window.setTimeout(() => go({ doc: doc.id }), motionEnabled() ? 180 : 0);
      } else {
        printTerminalLines([
          `文档：${doc.title}`,
          `分类：${doc.categoryLabel}`,
          `日期：${doc.dateDisplay}`,
          `阅读：${doc.readingTime} 分钟`,
          `路径：${doc.mdHref}`
        ], "ok");
      }
      return;
    }
    if (lower === "theme") {
      const value = argument.toLowerCase() || "auto";
      if (value !== "auto" && !themes.includes(value)) {
        printTerminalLines([`未知主题：${value}`], "error");
        return;
      }
      setTheme(value);
      printTerminalLines([`主题已切换：${value}，当前显示：${resolveTheme(value)}`], "ok");
      return;
    }
    if (lower === "motion") {
      localStorage.setItem(motionKey, argument === "off" ? "off" : "on");
      document.body.classList.toggle("reduce-motion", !motionEnabled());
      printTerminalLines([`命令动效：${motionEnabled() ? "on" : "off"}`], "ok");
      return;
    }
    if (lower === "eye") {
      const enabled = argument !== "off";
      document.body.classList.toggle("eye-care", enabled);
      localStorage.setItem(eyeKey, enabled ? "on" : "off");
      printTerminalLines([`护眼模式：${enabled ? "on" : "off"}`], "ok");
      return;
    }
    if (lower === "echo") {
      printTerminalLines([argument], "ok");
      return;
    }
    printTerminalLines([`command not found: ${verb}`, "输入 help 查看可用命令。"], "error");
  }

  function initInteractiveTerminal() {
    const form = document.getElementById("terminal-form");
    const input = document.getElementById("terminal-command");
    if (!form || !input) return;
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const command = input.value;
      input.value = "";
      runTerminalCommand(command);
    });
    input.addEventListener("keydown", (event) => {
      if (event.key === "ArrowUp" && terminalHistory.length) {
        event.preventDefault();
        terminalHistoryIndex = Math.max(0, terminalHistoryIndex - 1);
        input.value = terminalHistory[terminalHistoryIndex] || "";
      }
      if (event.key === "ArrowDown" && terminalHistory.length) {
        event.preventDefault();
        terminalHistoryIndex = Math.min(terminalHistory.length, terminalHistoryIndex + 1);
        input.value = terminalHistory[terminalHistoryIndex] || "";
      }
      if (event.key === "Tab") {
        event.preventDefault();
        const suggestions = ["help", "whoami", "ls categories", "stats", "search ", "open ", "cat ", "theme ", "motion ", "eye ", "date", "pwd", "history", "clear"];
        const match = suggestions.find((item) => item.startsWith(input.value) && item !== input.value);
        if (match) input.value = match;
      }
    });
    rootTerminalSuggestions().forEach((button) => button.addEventListener("click", () => {
      input.value = button.dataset.terminalFill;
      input.focus();
    }));
  }

  function rootTerminalSuggestions() {
    return [...view.querySelectorAll("[data-terminal-fill]")];
  }

  function renderHome() {
    const docs = DATA.documents.slice().sort((a, b) => b.dateTime.localeCompare(a.dateTime));
    const featuredCategories = DATA.categoryTree.map((item, index) => {
      const info = DATA.categoryIndex[item.id] || item;
      return `<button class="category-line" data-category="${esc(info.id)}">
        <span class="category-number">${String(index + 1).padStart(2, "0")}</span>
        <span class="category-name">${esc(info.name)}</span>
        <span class="category-path">${(item.children || []).slice(0, 5).map((child) => esc(child.name)).join(" / ") || "notes"}</span>
        <span class="category-count">${fmt(info.count)} 篇</span>
      </button>`;
    }).join("");
    const recent = docs.slice(0, 14).map((doc) => `<button class="terminal-note-row" data-doc="${esc(doc.id)}">
      <time>${esc(doc.dateOnly)}</time><span class="path-mark">./</span><strong>${esc(doc.title)}</strong><small>${esc(doc.categoryLabel)}</small>
    </button>`).join("");
    const tools = DATA.tags.slice(0, 18).map((tag) => `<button class="command-chip" data-tag="${esc(tag.name)}">--tag=${esc(tag.name)}<sup>${fmt(tag.count)}</sup></button>`).join("");
    const commands = ["docker ps -a", "systemctl status nginx", "journalctl -xe", "ss -tulpn", "df -h", "free -h", "top", "htop"];
    const wanted = ["渗透测试综合笔记", "work 归档原样", "项目安全资料索引", "DBQP 全服务器 CVE"];
    const featured = [];
    wanted.forEach((needle) => {
      const doc = DATA.documents.find((item) => item.title.includes(needle));
      if (doc && !featured.some((item) => item.id === doc.id)) featured.push(doc);
    });
    view.innerHTML = `
      <section class="terminal-panel intro-panel">
        <div class="terminal-line"><span class="prompt-user">root@ben-ops</span>:<span class="prompt-path">~</span># <strong class="type-command" data-type="whoami"></strong><span class="cursor">▌</span></div>
        <div class="identity-sub">基础设施工程师 · Linux · DevOps · SRE · Cloud · Security · <a class="author-link" href="https://t.me/Ben_Bird" target="_blank" rel="noopener">@Ben_Bird</a></div>
        <div class="quote-carousel" aria-live="polite"><div class="identity quote-text"></div><div class="quote-source"></div></div>
        <div class="status-grid">
          <div><span>文档</span><b>${fmt(DATA.stats.documents)}</b></div>
          <div><span>分类</span><b>${fmt(DATA.stats.categories)}</b></div>
          <div><span>标签</span><b>${fmt(DATA.stats.tags)}</b></div>
          <div><span>附件</span><b>${fmt(DATA.stats.media)}</b></div>
          <div><span>关联</span><b>${fmt(DATA.stats.relationships)}</b></div>
        </div>
      </section>
      <section class="terminal-panel interactive-terminal">
        <div class="terminal-line"><span class="prompt-user">root@ben-ops</span>:<span class="prompt-path">~</span># <strong>interactive-shell --local</strong><span class="hint-inline">输入 help 查看命令</span></div>
        <div class="terminal-output" id="terminal-output" aria-live="polite">
          <div class="terminal-output-line ok">本地知识库已就绪。输入 <code>help</code> 查看可用命令。</div>
        </div>
        <form class="terminal-input-line" id="terminal-form" autocomplete="off">
          <label for="terminal-command"><span class="prompt-user">root@ben-ops</span>:<span class="prompt-path">~</span>$</label>
          <input id="terminal-command" name="command" autocomplete="off" spellcheck="false" placeholder="输入命令，例如：search nginx">
          <span class="terminal-caret">▌</span>
          <button type="submit">执行</button>
        </form>
        <div class="terminal-suggestions"><button data-terminal-fill="help">help</button><button data-terminal-fill="ls categories">ls categories</button><button data-terminal-fill="stats">stats</button><button data-terminal-fill="search nginx">search nginx</button><button data-terminal-fill="theme light">theme light</button></div>
      </section>
      <section class="terminal-panel">
        <div class="terminal-line"><span class="prompt-user">root@ben-ops</span>:<span class="prompt-path">~</span># <strong>ls -1 ./categories</strong></div>
        <div class="category-lines">${featuredCategories}</div>
      </section>
      <section class="terminal-panel">
        <div class="terminal-line"><span class="prompt-user">root@ben-ops</span>:<span class="prompt-path">~</span># <strong>tail -n 14 ./latest-notes</strong></div>
        <div class="terminal-note-list">${recent}</div>
        <button class="terminal-more" data-view-all>more ./notes ↓</button>
      </section>
      <div class="terminal-split">
        <section class="terminal-panel">
          <div class="terminal-line"><span class="prompt-user">root@ben-ops</span>:<span class="prompt-path">~</span># <strong>tags --top</strong></div>
          <div class="command-cloud">${tools}</div>
        </section>
        <section class="terminal-panel">
          <div class="terminal-line"><span class="prompt-user">root@ben-ops</span>:<span class="prompt-path">~</span># <strong>open ./featured</strong></div>
          <div class="featured-list">${featured.map((doc) => `<button data-doc="${esc(doc.id)}"><span>→</span>${esc(doc.title)}<small>${esc(doc.kind)}</small></button>`).join("")}</div>
        </section>
      </div>
      <section class="terminal-panel">
        <div class="terminal-line"><span class="prompt-user">root@ben-ops</span>:<span class="prompt-path">~</span># <strong>commands --quick-copy</strong></div>
        <div class="command-shelf">${commands.map((command) => `<button data-command="${esc(command)}"><code>$ ${esc(command)}</code><span>复制</span></button>`).join("")}</div>
      </section>`;
    view.querySelectorAll("[data-category]").forEach((node) => node.addEventListener("click", () => go({ category: node.dataset.category })));
    view.querySelectorAll("[data-tag]").forEach((node) => node.addEventListener("click", () => go({ tag: node.dataset.tag })));
    view.querySelectorAll("[data-view-all]").forEach((node) => node.addEventListener("click", () => go({ sort: "all" })));
    view.querySelectorAll("[data-command]").forEach((node) => node.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(node.dataset.command);
        const label = node.querySelector("span");
        label.textContent = "已复制";
        setTimeout(() => { label.textContent = "复制"; }, 1000);
      } catch {
        showToast("复制失败");
      }
    }));
    initInteractiveTerminal();
    bindCards();
    breadcrumb.innerHTML = "<button>~/</button>";
    renderRightHome();
    refreshIcons();
    typeCommand(view.querySelector(".type-command"));
    startQuoteRotation(view);
  }

  function renderList(mode = "all") {
    const docs = filteredDocs();
    const category = state.category ? DATA.categoryIndex[state.category] : null;
    const title = state.query
      ? `搜索：${state.query}`
      : (state.view === "favorites"
        ? "收藏夹"
        : (state.view === "history"
          ? "阅读历史"
          : (state.tag ? `标签：${state.tag}` : (category?.name || (mode === "recent" ? "最近文档" : "全部文档")))));
    const visible = docs.slice(0, state.limit);
    view.innerHTML = `
      <div class="section-head"><div><h1>${esc(title)}</h1><p>${state.query ? "匹配标题、标签、分类和正文" : "按日期、分类与标签组织"}</p></div></div>
      <div class="list-toolbar"><span class="result-count">共 ${fmt(docs.length)} 篇</span>
        <select class="sort-select" id="sort-select"><option value="newest" ${state.sort !== "oldest" ? "selected" : ""}>日期从新到旧</option><option value="oldest" ${state.sort === "oldest" ? "selected" : ""}>日期从旧到新</option></select>
      </div>
      <div class="doc-list">${visible.map((doc) => `<article class="doc-row" data-doc="${esc(doc.id)}">
        <span class="date-badge">${esc(doc.dateOnly)}</span>
        <span class="doc-row-main"><strong>${highlightText(doc.title, state.query)}</strong><small>${esc(doc.categoryLabel)} · ${highlightText(doc.description, state.query)}</small></span>
        <span class="row-tags">${doc.tags.slice(0, 3).map((tag) => `<button class="tag-chip" data-filter-tag="${esc(tag)}">${esc(tag)}</button>`).join("")}</span>
      </article>`).join("") || `<div class="empty-state">没有找到匹配的文档</div>`}</div>
      ${visible.length < docs.length ? `<button class="load-more" id="load-more">继续加载 ${fmt(Math.min(80, docs.length - visible.length))} 篇</button>` : ""}`;
    view.querySelectorAll("[data-doc]").forEach((node) => node.addEventListener("click", () => go({ doc: node.dataset.doc })));
    view.querySelectorAll("[data-filter-tag]").forEach((node) => node.addEventListener("click", (event) => {
      event.stopPropagation();
      go({ tag: node.dataset.filterTag });
    }));
    const sort = document.getElementById("sort-select");
    if (sort) sort.addEventListener("change", () => { state.sort = sort.value; state.limit = 80; renderList(mode); });
    const more = document.getElementById("load-more");
    if (more) more.addEventListener("click", () => { state.limit += 80; renderList(mode); });
    breadcrumb.innerHTML = `<button data-home>首页</button><span>/</span><span>${esc(title)}</span>`;
    breadcrumb.querySelector("[data-home]").addEventListener("click", () => go({}));
    renderRightHome();
    refreshIcons();
  }

  function decorateContent(root) {
    const detectLanguage = (text) => {
      if (/^#!.*(?:bash|sh)/m.test(text) || /^\s*(?:sudo|systemctl|journalctl|docker|kubectl|ssh|grep|awk|sed)\s/m.test(text)) return "BASH";
      if (/^\s*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER)\s/im.test(text)) return "SQL";
      if (/^\s*(?:apiVersion|kind):/m.test(text)) return "YAML";
      if (/^\s*[{[][\s\S]*[}\]]\s*$/.test(text)) return "JSON";
      if (/^\s*(?:def|import|from|class)\s/m.test(text)) return "PYTHON";
      if (/server\s*\{|location\s+|proxy_pass\s+/m.test(text)) return "NGINX";
      if (/^\s*<\w+/m.test(text)) return "HTML";
      return "CODE";
    };
    root.querySelectorAll("pre").forEach((block) => {
      if (block.closest(".code-shell")) return;
      const pre = block;
      const code = pre.querySelector("code");
      if (code && window.hljs) window.hljs.highlightElement(code);
      const parent = block.parentElement;
      const shell = document.createElement("div");
      shell.className = "code-shell";
      const toolbar = document.createElement("div");
      toolbar.className = "code-toolbar";
      const codeLanguage = [...(code?.classList || [])].find((name) => name.startsWith("language-"))?.slice(9);
      toolbar.innerHTML = `<span>${esc((codeLanguage || pre.dataset.language || detectLanguage(pre.innerText)).toUpperCase())}</span>`;
      const button = document.createElement("button");
      button.className = "copy-code";
      button.textContent = "复制";
      button.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(pre.innerText);
          button.textContent = "已复制";
          setTimeout(() => { button.textContent = "复制"; }, 1200);
        } catch {
          button.textContent = "FAILED";
        }
      });
      toolbar.appendChild(button);
      parent.insertBefore(shell, block);
      shell.appendChild(toolbar);
      shell.appendChild(block);
      if (block.getBoundingClientRect().height > 520) {
        shell.classList.add("collapsed");
        const toggle = document.createElement("button");
        toggle.className = "code-expand";
        toggle.textContent = "展开";
        toggle.addEventListener("click", () => {
          shell.classList.toggle("collapsed");
          toggle.textContent = shell.classList.contains("collapsed") ? "展开" : "收起";
        });
        toolbar.appendChild(toggle);
      }
    });
    root.querySelectorAll("a[href]").forEach((a) => {
      const rawHref = a.getAttribute("href");
      let resolvedHref = rawHref;
      try {
        resolvedHref = decodeURI(rawHref);
      } catch (_) {}
      const targetDoc = mdByPath.get(rawHref) || mdByPath.get(resolvedHref);
      if (targetDoc) a.dataset.docId = targetDoc.id;
    });
    root.querySelectorAll("a[data-doc-id]").forEach((a) => {
      a.addEventListener("click", (event) => {
        event.preventDefault();
        go({ doc: a.dataset.docId });
      });
    });
    root.querySelectorAll('a[href^="http"]').forEach((a) => {
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    });
    root.querySelectorAll('img[src^="http"]').forEach((image) => {
      image.referrerPolicy = "no-referrer";
    });
    root.querySelectorAll("img").forEach((image) => {
      image.loading = "lazy";
      image.addEventListener("click", () => openLightbox(image.currentSrc || image.src, image.alt));
    });
  }

  function renderDocument(doc) {
    const related = (doc.relatedIds || []).map((id) => byId.get(id)).filter(Boolean);
    const backlinks = (doc.backlinks || []).map((id) => byId.get(id)).filter(Boolean);
    const originals = (doc.originals || []).map((file) => `<a href="${esc(file.href)}">${esc(file.label)}</a>`).join(" · ");
    const canEmbedSource = /^https:\/\/(?:ji-shu-jian-li|xn--6o0a585a)\.gitbook\.io\/.*\.html(?:[?#].*)?$/.test(doc.sourceUrl || "");
    const categoryDocs = DATA.documents.filter((item) => item.categoryId === doc.categoryId).sort((a, b) => a.dateTime.localeCompare(b.dateTime));
    const index = categoryDocs.findIndex((item) => item.id === doc.id);
    const previous = index > 0 ? categoryDocs[index - 1] : null;
    const next = index >= 0 && index < categoryDocs.length - 1 ? categoryDocs[index + 1] : null;
    const isFavorite = favorites().has(doc.id);
    view.innerHTML = `<article class="document-page">
      <header class="doc-header">
        <div class="doc-kicker">分类：${esc(doc.categoryLabel)} / ${esc(doc.kind)}</div>
        <h1>${esc(doc.title)}</h1>
        <div class="meta-bar"><span>发布：${esc(doc.dateDisplay || doc.dateOnly)}</span><span>·</span><span>${fmt(doc.wordCount)} 字</span><span>·</span><span>阅读：${esc(doc.readingTime || 1)} 分钟</span><span>·</span><span>难度：${esc(doc.difficulty || "ENGINEERING")}</span><span>·</span><span>作者：<a class="author-link" href="https://t.me/Ben_Bird" target="_blank" rel="noopener">@Ben_Bird</a></span>
          <span class="doc-actions"><button class="small-button" id="favorite-doc">${isFavorite ? "★ 已收藏" : "☆ 收藏"}</button><button class="small-button" id="share-doc">分享</button>${canEmbedSource ? '<button class="small-button" id="source-embed-toggle" aria-expanded="false">内嵌原网页</button>' : ""}<a class="small-button" href="${esc(doc.mdHref)}">打开 Markdown</a><span class="small-button">Markdown 渲染</span></span>
        </div>
        <div class="tag-cloud">${doc.tags.map((tag) => `<button class="tag-chip" data-inline-tag="${esc(tag)}">#${esc(tag)}</button>`).join("")}</div>
      </header>
      <div class="doc-content" id="doc-content">${markdownToHtml(doc.markdownBody, doc.title)}</div>
      ${canEmbedSource ? `<section class="source-embed-shell" id="source-embed-shell" hidden>
        <div class="source-embed-head"><span>原始 HTML 页面</span><a href="${esc(doc.sourceUrl)}" target="_blank" rel="noopener noreferrer">新窗口打开</a></div>
        <iframe id="source-embed-frame" title="${esc(doc.title)} 原始网页" loading="lazy" referrerpolicy="no-referrer" sandbox="allow-scripts allow-same-origin allow-popups allow-forms"></iframe>
      </section>` : ""}
      <nav class="article-pager">${previous ? `<button data-pager="${esc(previous.id)}"><span>← 上一篇</span><strong>${esc(previous.title)}</strong></button>` : "<span></span>"}${next ? `<button data-pager="${esc(next.id)}"><span>下一篇 →</span><strong>${esc(next.title)}</strong></button>` : ""}</nav>
      ${(related.length || backlinks.length) ? `<section class="relation-grid">
        <div class="relation-box"><h3>相关文档</h3><ul>${related.map((item) => `<li><button data-rel="${esc(item.id)}">${esc(item.title)}</button></li>`).join("") || "<li>暂无</li>"}</ul></div>
        <div class="relation-box"><h3>反向链接</h3><ul>${backlinks.map((item) => `<li><button data-rel="${esc(item.id)}">${esc(item.title)}</button></li>`).join("") || "<li>暂无</li>"}</ul></div>
      </section>` : ""}
      <p class="source-note">原始位置：<a href="${esc(doc.sourceUrl || doc.sourcePath)}" target="_blank" rel="noopener noreferrer">${esc(doc.sourceUrl || doc.sourcePath)}</a> · ${esc(doc.dateSource)}${originals ? `<br>原始附件：${originals}` : ""}</p>
    </article>`;
    const content = document.getElementById("doc-content");
    decorateContent(content);
    const headings = prepareHeadings(content);
    content.querySelectorAll("[data-inline-tag]").forEach((button) => button.addEventListener("click", () => go({ tag: button.dataset.inlineTag })));
    view.querySelectorAll("[data-rel]").forEach((button) => button.addEventListener("click", () => go({ doc: button.dataset.rel })));
    view.querySelectorAll("[data-pager]").forEach((button) => button.addEventListener("click", () => go({ doc: button.dataset.pager })));
    document.getElementById("favorite-doc").addEventListener("click", (event) => {
      const set = favorites();
      if (set.has(doc.id)) set.delete(doc.id); else set.add(doc.id);
      localStorage.setItem(favoritesKey, JSON.stringify([...set]));
      event.currentTarget.textContent = set.has(doc.id) ? "★ 已收藏" : "☆ 收藏";
      renderPrimaryNav();
      refreshIcons();
    });
    document.getElementById("share-doc").addEventListener("click", async () => {
      const shareUrl = location.href;
      try {
        if (navigator.share) await navigator.share({ title: doc.title, url: shareUrl });
        else {
          await navigator.clipboard.writeText(shareUrl);
          showToast("链接已复制");
        }
      } catch (_) {}
    });
    const sourceEmbedToggle = document.getElementById("source-embed-toggle");
    if (sourceEmbedToggle) {
      sourceEmbedToggle.addEventListener("click", () => {
        const shell = document.getElementById("source-embed-shell");
        const frame = document.getElementById("source-embed-frame");
        const open = shell.hidden;
        if (open && !frame.src) frame.src = doc.sourceUrl;
        shell.hidden = !open;
        sourceEmbedToggle.setAttribute("aria-expanded", String(open));
        sourceEmbedToggle.textContent = open ? "收起原网页" : "内嵌原网页";
        if (open) shell.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
    rightPanelBody.innerHTML = `
      <section class="side-panel"><div class="toc-head">本文目录</div><nav class="article-toc">${headings.map((heading) => `<a class="level-${heading.level}" href="#${esc(heading.id)}">${esc(heading.text)}</a>`).join("") || '<span class="source-note">本文没有分级标题</span>'}</nav></section>
      <section class="side-panel"><div class="toc-head">文章信息</div><div class="status-list"><div><span>作者</span><b><a class="author-link" href="https://t.me/Ben_Bird" target="_blank" rel="noopener">@Ben_Bird</a></b></div><div><span>阅读时长</span><b>${esc(doc.readingTime || 1)} 分钟</b></div><div><span>难度</span><b>${esc(doc.difficulty || "N/A")}</b></div><div><span>更新</span><b>${esc(doc.dateOnly)}</b></div></div></section>
      ${related.length ? `<section class="side-panel"><div class="toc-head">相关文档</div>${related.slice(0, 5).map((item) => `<button class="side-link truncate" data-side-doc="${esc(item.id)}">${icon("link", 12)} ${esc(item.title)}</button>`).join("")}</section>` : ""}`;
    tocPanel.hidden = false;
    rightPanelBody.querySelectorAll(".article-toc a").forEach((a) => a.addEventListener("click", (event) => {
      event.preventDefault();
      content.querySelector(`#${CSS.escape(a.getAttribute("href").slice(1))}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }));
    rightPanelBody.querySelectorAll("[data-side-doc]").forEach((button) => button.addEventListener("click", () => go({ doc: button.dataset.sideDoc })));
    watchHeadings(content);
    breadcrumb.innerHTML = `<button data-home>首页</button><span>/</span><button data-category-link>${esc(doc.categoryLabel)}</button><span>/</span><span>${esc(doc.title)}</span>`;
    breadcrumb.querySelector("[data-home]").addEventListener("click", () => go({}));
    breadcrumb.querySelector("[data-category-link]").addEventListener("click", () => go({ category: doc.categoryId }));
    document.title = `${doc.title} · ${DATA.title}`;
    remember(doc.id);
    progress.style.width = "0%";
    updateReadingProgress();
    window.scrollTo({ top: 0, behavior: "instant" });
    refreshIcons();
  }

  function renderNotFound() {
    view.innerHTML = `<section class="terminal-panel not-found">
      <div class="terminal-line"><span class="prompt-user">root@ben-ops</span>:<span class="prompt-path">~</span># <strong>cat ./requested-note</strong></div>
      <div class="not-found-code">404</div>
      <div class="identity">未找到文档。</div>
      <p>请求的文档不存在，可能已被移动、重命名或未包含在当前构建中。</p>
      <button class="small-button" data-home>cd ~</button>
    </section>`;
    view.querySelector("[data-home]").addEventListener("click", () => go({}));
    rightPanelBody.innerHTML = "";
    tocPanel.hidden = true;
    breadcrumb.innerHTML = "<button>~/</button><span>/</span><span>404</span>";
    document.title = `404 · ${DATA.title}`;
  }

  function render() {
    stopQuoteRotation();
    if (state.docId) {
      const doc = byId.get(state.docId);
      if (doc) return renderDocument(doc);
      return renderNotFound();
    }
    document.title = DATA.title;
    if (state.view) return renderList(state.view);
    if (state.query) return renderList("search");
    if (state.category || state.tag) return renderList("filter");
    const hash = new URLSearchParams(decodeURIComponent(location.hash.slice(1)));
    if (hash.get("sort") === "all") return renderList("all");
    if (hash.get("sort") === "recent") return renderList("recent");
    renderHome();
  }

  function initEvents() {
    search.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        palette.hidden = true;
        go({ q: search.value.trim() });
      }
      if (event.key === "Escape") {
        search.value = "";
        palette.hidden = true;
        go({});
      }
    });
    let timer;
    search.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(renderSearchPalette, 160);
    });
    search.addEventListener("focus", renderSearchPalette);
    document.getElementById("open-search").addEventListener("click", () => { search.focus(); search.select(); });
    document.getElementById("menu-toggle").addEventListener("click", () => openDrawer(true));
    document.getElementById("sidebar-close").addEventListener("click", () => openDrawer(false));
    document.getElementById("drawer-backdrop").addEventListener("click", () => openDrawer(false));
    document.addEventListener("keydown", (event) => {
      if (event.key === "/" && document.activeElement !== search) {
        event.preventDefault(); search.focus();
      }
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault(); search.focus(); search.select();
      }
    });
    document.addEventListener("click", (event) => {
      if (!event.target.closest(".global-search") && !event.target.closest("#search-palette")) palette.hidden = true;
    });
    window.addEventListener("scroll", updateReadingProgress, { passive: true });
    window.addEventListener("hashchange", route);
  }

  function boot() {
    if (!DATA) {
      view.innerHTML = `<div class="empty-state">数据未加载。请确认 <code>assets/data.js</code> 存在。</div>`;
      return;
    }
    document.getElementById("build-date").textContent = `数据生成：${DATA.generatedAt}`;
    initTheme();
    initComfort();
    renderPrimaryNav();
    renderCategoryTree();
    renderSidebarTags();
    initEvents();
    route();
  }

  boot();
})();
