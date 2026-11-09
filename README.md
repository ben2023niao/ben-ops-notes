# BEN.OPS 工程笔记

> 安全、运维、Linux、DevOps、云平台、故障排查与事件响应。

作者：[@Ben_Bird](https://t.me/Ben_Bird)

## 内容

- `2581` 篇 Markdown 技术笔记，按文档真实记录时间生成 Git 提交历史。
- `index.html` 为离线知识库入口，直接渲染 `doc/md/`。
- `doc/media/` 保存正文引用的图片与附件。
- 两个 GitBook 共 `232` 篇已恢复完整原文，正文直接内嵌渲染；`412` 个图片引用均对应本地媒体资源。
- `assets/seo/` 为每篇 Markdown 生成独立、可抓取的静态 HTML，共 `2581` 页，正文不依赖 JavaScript。
- 本机项目与内网老 Mac 的 `doc/`、`docs/` 共收集 `2439` 个源文件，内容去重后新增 `1213` 篇；原始快照保存在独立私有归档。
- 公开版已对已知密码、Token、私钥、邮箱和手机号做脱敏；历史技术记录中的公网地址会按原文保留。
- 超过 GitHub 单文件限制或属于原始归档的 ZIP/RAR/7Z 未提交，完整原文件保留在作者本地。
- `assets/originals/` 不在公开仓库中，相关链接已从索引移除。

## 本地浏览

直接用浏览器打开 `index.html`。页面支持全文搜索、分类、标签、主题切换、代码高亮和复制。

## 数据说明

`assets/data.json` 是文档索引和分类关系的结构化数据，`assets/data.js` 是供 `file://` 离线打开加载的同内容包装。Markdown 是唯一正文源。

`assets/seo-manifest.json` 保存每篇 SEO 页面的标题、描述、关键词、日期、Markdown 路径和 Canonical URL；`assets/gitbook-content-manifest.json` 保存 GitBook 原文还原来源、HTML SHA-256 与本地图片清单。

## 搜索引擎优化

- [静态文章索引](assets/seo/index.html)：每篇文章具有独立 URL、完整正文和内链。
- 每页包含 `title`、`description`、`keywords`、Canonical、Open Graph、Twitter Card、Google/Baidu robots 和 Schema.org `TechArticle` 结构化数据。
- [Sitemap](assets/sitemap.xml)：提交全部静态文章 URL，不在 URL 中使用 SPA 的 `#` 片段。
- [RSS](assets/rss.xml)：最近 100 篇文章直接链接到静态 HTML。
- [robots.txt](robots.txt)：声明 Sitemap 地址。

## 统计

- Markdown：2581
- 正文媒体：2192
- GitBook 完整还原：232
- SEO 静态 HTML：2581
<!-- MONTHLY_ENGINEERING_LOG -->
## 月度真实工程摘要

按实际 Git 提交日期和文档来源日期生成，不做随机回溯或补造提交。

- [查看完整月度工程索引](docs/monthly/README.md)
