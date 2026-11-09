---
id: "doc-75c25e05ff64"
title: "前端域名维护 SSL 续签分类与点击签发"
date: "2026-08-12T18:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Nginx", "CDN", "DNS", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1830-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E5%89%8D%E7%AB%AF%E5%9F%9F%E5%90%8D%E7%BB%B4%E6%8A%A4SSL%E7%BB%AD%E7%AD%BE%E5%88%86%E7%B1%BB%E4%B8%8E%E7%82%B9%E5%87%BB%E7%AD%BE%E5%8F%91.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1830-【优化+运维记录】前端域名维护SSL续签分类与点击签发.md"
sourceSha256: "e8077bfbdfaedc7deb0fcf33eb9fb6affe2346f73a10c09056df56422bc3dac2"
sourceSystem: "project-doc"
---

# 前端域名维护 SSL 续签分类与点击签发

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608121830-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-%E5%89%8D%E7%AB%AF%E5%9F%9F%E5%90%8D%E7%BB%B4%E6%8A%A4%20SSL%20%E7%BB%AD%E7%AD%BE%E5%88%86%E7%B1%BB%E4%B8%8E%E7%82%B9%E5%87%BB%E7%AD%BE%E5%8F%91.md)

> 整理日期：2026-08-12 18:30｜日期依据：文件名日期

环境标签：通用 / ben-bot / 前端域名维护 / SSL / 16.208.38.88

时间：2026-08-12 18:30（Asia/Manila）

## 任务来源

用户要求优化 `🧭 前端域名维护`：

- 菜单只保留 3 个按钮：🔄 快速检查（DNS/模式/证书到期）、🛡 SSL 续签、➕ 增加域名；其余按钮移除。
- 🛡 SSL 续签 内部分类显示：没证书域名 / 快到期证书域名 / 正常证书域名。
- 在分类里点击具体域名即可制作/更新该域名的 SSL 证书。

## 实现内容

### 菜单精简

`benbot_plugin.py` 的 `_buttons` 现在只保留：

- `🔄 快速检查（DNS/模式/证书到期）`
- `🛡 SSL 续签`
- `➕ 增加域名`
- `返回主页`

已移除：`📜 SSL 状态`、`📋 未切CDN回源域名`、`✅ 标记已切换CDN回源` 三个按钮。

### SSL 续签分类

点击 `🛡 SSL 续签` 后实时读取服务器 `check --quick --json`，按证书状态分类并显示数量：

- `🚫 没证书域名`：ssl=placeholder/none（占位证书未签发或无证书），显示 可签/未切回源 数量。
- `⏳ 快到期证书域名（30天内）`：有证书且 30 天内到期（含已过期）。
- `✅ 正常证书域名`：有证书且剩余有效期大于 30 天。

### 点击域名签发

- 点分类进入域名列表（每页 15 条），每个可签域名有 `🔐 制作/更新证书 <域名>` 按钮；支持 `🔐 本页全部签发（N）` 与翻页。
- 点击单个域名：客户端执行 `cert -d <域名>`（服务器 certbot webroot 签发/续签），结果 HTML 转义后回显。
- 未切 CDN 回源的域名只显示“未切回源”标注、不提供签发按钮；点击已过期数据会提示先切换回源。
- 签发成功后客户端自动把该域名状态从 pending 更新为 switched（不再需要单独的“标记回源”按钮）。

### 顺带修复

1. 客户端缺少 `cert` 动作（上一版“签发本页”按钮实际调用不到）：新增 `cert -d <域名>` 分支，透传服务器签发结果并在成功后 auto-mark。
2. 服务器脚本 `remove_placeholder` 会误删指向有效证书的 `live/<域名>` 软链：改为仅当软链目标无 fullchain.pem 或证书 SAN 不覆盖该域名时才删除；dry-run 模式完全不动软链（演练不落盘）。

## 验证

### 本地

- 本机安装 Python 3.11（Homebrew `python@3.11`，3.11.15）用于本地验证（原 3.9 无法运行 `str | None` 注解）。
- `py_compile`、`git diff --check` 通过；插件纯函数断言通过：分类正确（没证书 2 / 快到期 1 / 正常 1）、菜单仅 3 按钮、未切回源无签发按钮、分页第 2 页按钮正确。

### 容器（52.79.252.255 ben-bot）

- 容器文件与本地 md5 一致（插件 90e0db2c、客户端 816a1cec）。
- 容器重建后启动通知成功 10 失败 0。
- 容器内断言：分类/菜单/回调 `plugin:n1:sign:no_cert:b.com`、`plugin:n1:renew` 正确。

### 服务器（16.208.38.88）

- 修复前发现 `cert -d shouyek.com --dry-run` 会误删 `live/shouyek.com` 软链；已恢复软链（指向 `live/shouyek.com-0001`，到期 2026-11-10，ssl=ok）。
- 部署修复后脚本（md5 0d7a5876，备份 `/root/.codex-backup/youdianse-domain-maint.py.pre-placeholder-fix.bak`），dry-run 不再删软链，PC/手机 UA 直连均 200。

## 群通知

已同步发送 `18GAME_ 上线群（正式環境）` 与 `18game运维`：步骤 1 方案、步骤 2 上线与验证、最终汇总与文档。

## 结论

- 前端域名维护菜单已精简为 3 个按钮，SSL 续签按 没证书/快到期/正常 分类，点击域名即可制作或更新证书。
- 未切 CDN 回源的域名仍受保护不签发；切换回源后点击制作成功会自动标记状态。
- 顺手修复了服务器脚本误删有效证书软链的隐患，避免演练或签发失败导致 HTTPS 证书丢失。

## 追加：重复点击报 Message is not modified 修复（2026-08-12）

- 现象：快速检查 / SSL 续签等按钮重复点击时，机器人对同一消息执行内容完全相同的编辑，Telegram 返回 `Message is not modified`，被误当成“读取失败”提示刷到群里。
- 修复：`benbot_plugin.py` 新增 `_safe_edit`，编辑时捕获 `BadRequest` 且命中 `Message is not modified` 时静默跳过；其他错误仍正常抛出。前端域名维护所有 `edit_text` 调用全部切换为 `_safe_edit`；快速检查/SSL 续签读取失败改为 `answer_callback` 弹窗提示，不再用报错文本覆盖消息内容。
- 验证：本地 python3.11 与容器内断言通过（not-modified 跳过、其他 BadRequest 照常抛出、正常编辑通过）；启动通知 10/10。

## 追加：全部操作异步化（2026-08-12）

- 现象：快速检查、SSL 续签菜单、展示域名列表以及单个/批量签发都是同步等待（快速检查要 SSH 检查 93 个域名，签发要跑 certbot），点击后长时间无响应。
- 改造：`benbot_plugin.py` 全部改为异步返回：
  - `🔄 快速检查` / `🛡 SSL 续签` 菜单：点击立即显示“正在读取…完成后自动更新”，后台线程执行检查，完成后按消息 id 自动更新同一消息。
  - 分类列表 / 翻页 / 分类筛选 / 排序：统一走 `_async_edit_view`，点击立即显示加载态，后台渲染完成后更新。
  - 单个域名签发：点击立即回复“已开始为 xxx 制作/更新 SSL（约 1-3 分钟）”，后台完成后自动发送结果消息。
  - 本页全部签发：点击立即回复“已开始为 N 个域名制作/更新 SSL”，后台逐个签发并每完成一个发送进度（`SSL制作进度 i/N`），最后发送汇总（成功/失败明细）。
- 实现：新增 `_spawn`（守护线程）、`_edit_by_ids`（后台按消息 id 幂等编辑）、`_async_edit_view`（通用异步渲染）。
- 验证：本地 python3.11 与容器内断言通过（单个签发立即返回+后台结果、批量签发进度+汇总、异步展示加载态+最终更新）；启动通知 10/10。

## 追加：SSL 续签列表全量域名 + 点域名续签 + 失败日志文件（2026-08-12）

- 按用户要求重构 SSL 续签列表：
  - 放入全部域名（一行一个），每个域名是一行按钮（`域名 · 状态`，状态含 快到期日期/正常日期/无证书·可签发/无证书·未切回源）。
  - 列表顶部/按钮行带分类标签：全部 / 🚫 没证书 / ⏳ 快到期 / ✅ 正常，点击即筛选；支持 ◀ 上一页 / 下一页 ▶ 翻页与 🔄 刷新。
  - 点击具体域名即续签该域名证书（异步：立即回复“已开始”，后台执行约 1-3 分钟）。
- 续签失败：自动把完整续签日志作为 `域名.txt` 附件发到群里，方便运维直接查看失败原因（如 DNS/校验失败）。
- 续签成功：服务器脚本签发完成后自动 `nginx -t && reload`；客户端同步更新机器人域名状态文件（cdn→switched、ssl=ok、last_renew 时间）。
- 未切 CDN 回源域名也可点击续签（不再拦截），失败日志会给出具体原因，切换回源后即可成功。
- 代码：插件 `_render_renew_list`/`_show_renew_list`/`_send_log_file`/`_sign_domain` 重写；客户端 cert 增加 `RESULT=SUCCESS/FAILED` 标记与状态更新；服务器脚本 issue_cert 成功后自动 reload nginx。
- 验证：本地与容器内断言通过（全量列表/分类/翻页/每行域名按钮、失败发 域名.txt、成功发结果）；真实走通 shouyek.com 续签（certbot 未到期跳过 + nginx reload + RESULT=SUCCESS + 状态文件 last_renew 已更新）；启动通知 10/10。

## 追加：SSL 续签域名搜索（2026-08-12）

- 按用户要求给 SSL 续签列表新增 `🔍 搜索域名` 按钮，避免一页页翻找。
- 点击按钮后提示直接回复域名关键词（支持模糊匹配，如 `shouyek.com` 或 `shouyek`）。
- 文本钩子 `app/benbot/handlers/domain_maint.py` 新增 search 分支：读取已加载的续签域名列表，按关键词大小写不敏感模糊匹配，渲染匹配结果（每行一个域名按钮，可直接点击续签，支持翻页）。
- 搜索结果可翻页（`renew_search_page`），提供 `↩ SSL 续签列表` 返回；搜索数据过期会提示重新搜索。
- 代码：插件新增 `render_search`/`_show_search_page` 与 `renew_search`/`renew_search_page` 回调；`_sign_domain` 兼容 `renew_search` 数据。
- 验证：本地与容器内断言通过（列表含搜索按钮、搜索 shouyek.com/syyhslzp.com 精确匹配、翻页、搜索结果点击续签）；启动通知 10/10。

## 追加：搜索交互与数据持久化优化（2026-08-12）

- 问题：搜索会把当前分页数据文件覆盖为搜索结果，导致连续第二次搜索报“请先打开 🛡 SSL 续签 列表再搜索”；搜索提示和结果各发一条消息较刷屏；续签成功消息过长。
- 优化：
  - 域名基础数据单独持久化到 `data/upload/domain_maint_renew.json`（`load_renew_rows`），搜索直接读缓存，数据缺失时自动后台从服务器拉取（不再要求先打开列表），连续搜索可用。
  - 点 `🔍 搜索域名` 后把当前消息编辑为输入提示（带 ↩ 返回），回复关键词后同一消息编辑为搜索结果/无匹配提示，不再额外刷消息。
  - 续签成功消息精简为“成功 ✅ + 已 reload nginx 并更新域名信息 + 简短日志尾部”；完整日志仅在失败时以 `域名.txt` 发送。
- 验证：本地与容器内断言通过（自动加载 93 域名并缓存、连续搜索 shouyek.com/syyhslzp.com、搜索提示同消息编辑为结果、成功消息精简）；启动通知 10/10。
