---
id: "doc-84b7fce40acb"
title: "BKL UAT 运维手册"
date: "2026-10-23T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Shell", "Nginx", "监控告警", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8823%E6%97%A5-bkl%E8%BF%90%E7%BB%B4%E6%89%8B%E5%86%8C/2026%E5%B9%B410%E6%9C%8823%E6%97%A5-bkl%E8%BF%90%E7%BB%B4%E6%89%8B%E5%86%8C.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月23日-bkl运维手册/2026年10月23日-bkl运维手册.md"
sourceSha256: "798fb06b3e982c47e9378c39564c257258aea063de529ee27d543a6292d3a7aa"
sourceSystem: "project-doc"
---

# BKL UAT 运维手册

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610230000-%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E4%B8%8E%E8%87%AA%E5%8A%A8%E5%8C%96%2BBKL%20UAT%2BShell-BKL%20UAT%20%E8%BF%90%E7%BB%B4%E6%89%8B%E5%86%8C.md)

> 整理日期：2026-10-23 00:00｜日期依据：文件名日期

日期：2026-10-23
执行人：Ben（运维）
版本：v1

## 需求

详细学习 `UAT部署/` 全部资料三遍，结合真实 UAT 环境，参考 `运维发布页.html` 风格，生成运维可逐步操作的 `bkl-运维手册.html`。

## 三遍学习

### 第一遍：资料盘点

- `视讯项目UAT部署规划.xmind`：整体方案、逻辑/物理架构、节点配置、Swarm 资源规划
- `视讯项目UAT部署操作.xmind`：环境初始化、Harbor/Jenkins/ELK/中间件、Swarm、Portainer、Prometheus
- `视讯项目UAT部署.drawio`：前端、后端 Stack、中间件、运维支撑关系
- `UAT服务器.docx`：机器规格、IP、旧 SRS 规划
- 全部 compose、nginx、SQL、ELK 模板、发布脚本

### 第二遍：对照真实环境

- 5 台 UAT + 2 台 SRS，Beszel 全部 status up
- middleware 磁盘 77.2%，其余 12.3%~47%
- Swarm：manager .12 + worker .13/.14
- GitLab 独立部署在堡垒机
- SRS 实际为专线内网 .1 + 韩国/新加坡 2 台
- 旧 `/home/stack` game compose 的 `start_period=30s` 与仓库 UAT部署新版 200s 不一致

### 第三遍：运维流程抽取

整理成：

1. 环境边界与责任
2. 真实架构/域名/端口
3. 每日巡检
4. 发布前检查
5. 单服务发布
6. 全量 Stack 部署/回滚
7. 中间件/Harbor/Jenkins/ELK/Nginx
8. Beszel 与专线监控
9. CPU/重启/磁盘/FD/SRS/证书故障 Runbook
10. 备份、回滚、安全纪律、已知差异

## 交付物

[bkl-运维手册.html](../../bkl-运维手册.html)

特性：

- 参考运维发布页的 hero、卡片、折叠分组、代码块、复制按钮、勾选进度、打印/PDF
- 自包含 HTML，无外部依赖
- 不包含密码、Token、私钥
- 检查项进度存 localStorage
- 适配手机和打印

## 资料去敏

原始 `UAT部署/` 包含明文密码、Harbor 凭据、Prometheus bot token 和 Jenkins Maven 密码，已加入 `.gitignore`，不提交 Git。

去敏摘要：

`doc/2026年10月23日-UAT部署资料摘要/2026年10月23日-UAT部署资料摘要.md`

## 验证

- HTML：39,922 bytes，13 个折叠分组，26 个检查项，14 个复制按钮。
- 导航锚点：12 个，缺失 0。
- Chrome headless 桌面 1280×1800、手机 430×1100 均成功渲染。
- `node --check`：JS 语法通过。
- 已知秘密扫描：无命中。
- `make check`：通过。

## 提交

- 主提交：`e1938f9`
- 文档收尾提交：见 `git log -1`
- 远端：`root/devops` main
