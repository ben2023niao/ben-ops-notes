---
id: "doc-52b17498e7cc"
title: "Agent 工作日志 · web-live-sentry-release"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-web-live-sentry-release.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-web-live-sentry-release.md"
sourceSha256: "b3cdf383fd5ed5d6b7e220f4a50810896bf6b6a2d2c59e7745fb87bef1fdc1ef"
sourceSystem: "project-doc"
---

# Agent 工作日志 · web-live-sentry-release

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606100000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20web-live-sentry-release.md)

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：Web 直播卡片状态与 Sentry 构建内联 release 分支

## 输入资料

- PRD：`docs/prd/product-prd.md`、`docs/prd/modules/kickoff-home.md`
- 需求 ID：OPS
- 接口/契约：不涉及后端接口或 OpenAPI 契约变更
- 团队可读文档：`AGENTS.md`、`infra/deploy/main-business-code-update.md`
- 其他：`origin/main`、`origin/dev` 当前发布分支差异

## 本次目标

1. 从 `origin/main` 创建干净 release 分支。
2. 只合入本次 Web 直播卡片状态与 Sentry 构建内联变更。
3. 先提交到 `dev` 测试环境验收，验收通过后同一 release 分支再进入 `main`。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/web/app/components/home/LiveRooms.vue` | 直播卡片 live 状态透传展示 |
| `apps/web/app/components/match/MatchCard.vue` | 直播卡片 live 状态展示控制 |
| `apps/web/app/utils/adapters.ts` | 补充匹配视图字段适配 |
| `apps/web/shared/types/match-view.ts` | 补充前端视图模型字段 |
| `apps/web/nuxt.config.ts` | Sentry 服务端配置构建期内联 |
| `apps/web/sentry.server.config.ts` | SSR Sentry 配置使用构建期内联值 |
| `docs/agents/logs/2026-06-10-web-live-sentry-release.md` | 本次 Agent 工作日志 |

## 核心决策

1. release 分支从 `origin/main` 创建，不从 `dev` 直接上线。
2. 跳过包含真实 `SENTRY_AUTH_TOKEN` 的 `7f3721b7`，避免密钥进入 `main`。
3. 本分支先合并到 `dev` 触发测试环境验收，验收通过后再合并到 `main`。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | OPS |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-home.md` |
| OpenAPI / Event / DTO | 不涉及 |
| 不涉及契约的原因 | 仅调整 C 端 Web 展示与构建配置，不改后端返回字段、接口路径或 OpenAPI |
| 是否影响前端字段变更 | 仅 Web 内部 view model 增加/消费 live 状态，不涉及后端公开契约改名或删除 |
| 项目级验收 | `docs/qa/project-acceptance.md` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 Web 生产构建产物；不改变服务入口、端口或 health check |
| 回滚 | 回滚该 release 分支对应 merge commit 后重新发布 |
| 密钥 | `SENTRY_AUTH_TOKEN` 不进 Git，应放 GitLab CI/CD Variables；已发现 dev 历史曾含真实 token，建议立即在 Sentry 轮换 |
| 备份恢复 | 不涉及数据库、对象存储、账本或审计日志 |
| 观测 | Sentry SSR 初始化配置改为构建期内联 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 分支从 `main` 创建，仅包含本次 release 必要变更；本地门禁和构建通过 |
| 红队质疑 | `7f3721b7` 含真实 Sentry token，不能进入 `main`；已跳过并在 MR 描述中提示轮换 |
| 合入判断 | 允许先合入 `dev` 验收；正式发布前需确认 dev pipeline 和测试环境验收通过 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已创建 release 分支并提交 MR 到 `dev`，等待 CI 和测试环境验收 |
| 完成裁决 | 由 Reviewer / Owner / QA / CI / Release Manager 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `npm run check:ops` | 通过 |
| `npm run check:mr-gates` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `go vet ./...` | 通过 |
| `go test -count=1 ./...` | 通过 |
| `pnpm --filter @kickoff/web typecheck` | 通过 |
| `pnpm --filter @kickoff/web build:prod` | 通过；存在 Tailwind sourcemap 与大 chunk 构建警告 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 不涉及新设计图 |
| 页面截图 | 待 dev 环境部署后补充 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json`，本次未新增 |
| 真实手机视口 | 待 dev 环境验收 |
| 桌面/平板视口 | 待 dev 环境验收 |
| 响应式验收 | 待 dev 环境验收 |
| API 接口路径 | 不涉及新增或变更 |
| SEO异常验证/分享/下载渠道 | 不涉及 |
| mock/fallback 状态与原因 | 不涉及 |
| 后台权限与审计 | 不涉及 |
| 根节点是否挂载 | 待 dev 环境验收 |
| 静态资源是否 200 | 待 dev 环境验收 |
| console 是否无 error | 待 dev 环境验收 |
| 合入判断 | 先合入 dev 验收 |

## 风险与待办

1. 需要轮换曾进入 `dev` 历史的 Sentry token。
2. dev pipeline 通过后，需要在测试环境验收 Web 首页直播卡片和 Sentry SSR 初始化。
3. dev 验收通过后，同一 release 分支再开 MR 到 `main`。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 当前 MR 方向应为 `release/2026-06-10-web-live-sentry -> dev`。
2. 不要把 `7f3721b7` 中真实 `SENTRY_AUTH_TOKEN` 带入 `main`。
3. 正式发布前确认 GitLab CI/CD Variables 中配置了新的 `SENTRY_AUTH_TOKEN`。
