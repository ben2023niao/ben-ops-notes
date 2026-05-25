---
id: "doc-65866d2a9438"
title: "Agent 工作日志：H5 直播间接口契约与前端文档对齐"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "CDN", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-h5-live-room-contract-docs.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-h5-live-room-contract-docs.md"
sourceSha256: "67dbd4cfcd0120fd6e2ad100f5761e29c3d0ca7da28c502b13c5b82461ccabdc"
sourceSystem: "project-doc"
---

# Agent 工作日志：H5 直播间接口契约与前端文档对齐

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-h5-live-room-contract-docs.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：核对 H5 产品原型里的直播间页面返回 API、后台管理能力和给前端看的联调文档，并修正文档/契约/实现口径不一致处。

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-001、LIVE-002、LIVE-005、LIVE-007、LIVE-008、LIVE-013、LIVE-016、ADM-901~ADM-918
- 设计图：用户本地 H5 原型
- 设计图文件名：`/Users/qx/Downloads/2026.05.23迭代版.html#h5`
- 视觉要点：H5 直播间剧场式/横屏、弹幕、打赏、竞猜卡、线路选择、分享
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/frontend-integration.md`
- AI/工具控制文件：`AGENTS.md`
- 项目 Overlay：`project.config.json`
- 其他：`docs/qa/project-acceptance.md`

## 本次目标

1. 明确 H5 直播间应调用的真实 `/api/v1/*` 接口，替换原型简写路径。
2. 修正 OpenAPI 与 contracts 中弹幕字数、线路 query、`auto` 线路说明。
3. 给前端联调文档补直播间专项接口表，同时保留原有启动/账号/CORS 信息。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `docs/prd/modules/kickoff-live.md` | 把已实现 live 接口从“待设计/待实现”更新为真实状态，新增 H5/Web 联调口径。 |
| `docs/api/openapi.yaml` | 弹幕 `content.maxLength=100`；`GET /live/lines` 补 `room_id` 预留 query；`line_id` 说明支持 `auto`。 |
| `packages/contracts/openapi/v1.yaml` | 与 canonical OpenAPI 同步。 |
| `services/go-app/internal/dto/live.go` | 弹幕请求绑定从 `max=200` 收紧为 `max=100`，与 PRD/OpenAPI 一致。 |
| `docs/frontend-integration.md` | 追加 H5 直播间接口对接口径和后台管理入口说明。 |

## 核心决策

1. H5 原型里的 `/rooms/{id}`、`/tip`、`/bets` 只作为产品简写，不作为联调路径。
2. 当前 v0.3.1 线路选择只做上报统计；`play-url` 尚不按 `line_id` 返回不同 CDN 地址，文档明确提示前端不要假设切线会改变 URL。
3. `apps/web/**` 按 AGENTS §14 不主动修改；本次只修后端 DTO、OpenAPI、PRD 和团队联调文档。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-001、LIVE-002、LIVE-005、LIVE-007、LIVE-008、LIVE-013、LIVE-016、ADM-901~ADM-918 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`services/go-app/internal/dto/live.go` |
| 验收证据行 | `docs/qa/project-acceptance.md` |
| 不涉及契约的原因 | 不适用，本次直接修契约与 DTO 一致性。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否使用表设计模板 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不改变资金逻辑；文档明确打赏仍需 `Idempotency-Key`。 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 结构化证据 | `docs/qa/architecture-capability-evidence.json` |
| 是否只是 CRUD | 否，是 H5 直播间契约/文档/DTO 对齐。 |
| 涉及能力 | 权限安全、数据一致性、可观测性 |
| 不适用项及原因 | 无新增存储/队列/缓存能力。 |
| 当前 MVP 边界 | 线路选择只做上报；按线路返回播放 URL 留后续实现。 |
| 未来迁移成本 | 后续给 `play-url` 增 `line_id` 路由时需同步 OpenAPI 和前端。 |
| 升级触发指标 | 线路切换需要真实 CDN 分流或某线路故障率可观测时。 |
| 高风险触发项 | 资金、权限 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 go-app 二进制中的弹幕长度校验；不影响服务入口。 |
| 回滚 | 回滚本次文档和 DTO 修改即可。 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | PRD、OpenAPI、contracts、DTO 已统一 H5 直播间关键字段和路径。 |
| 红队质疑 | 线路 UI 是否真切流？当前不真切，已在 PRD 和前端联调文档明确，避免前端误判。 |
| 合入判断 | 可合入；H5 前端仍需按文档修 `data.items` 等读取逻辑。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现文档、契约和 DTO 口径对齐，并跑过验证命令。 |
| 完成裁决 | 只能由 Reviewer / Owner / QA / CI / Release Manager 给出。 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `npm run check:openapi` | 通过 |
| `cd services/go-app && go test ./...` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | `/Users/qx/Downloads/2026.05.23迭代版.html#h5` |
| 页面截图 | 未生成；本次不改前端页面实现。 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` 未更新；不涉及 UI 改动。 |
| 真实手机视口 | 未验证；不改前端实现。 |
| 桌面/平板视口 | 未验证；不改前端实现。 |
| 响应式验收 | 不涉及 |
| 公共组件拆分 | 不涉及 |
| API 接口路径 | `/api/v1/live/room/{room_id}`、`/play-url`、`/danmaku`、`/tip`、`/activities`、`/live/lines`、`/live/lines/select` |
| SEO异常验证/分享/下载渠道 | 只核对分享日志为 P1 待对齐；未改实现。 |
| mock/fallback 状态与原因 | H5 前端仍需按联调文档读取 `data.items`；本次不改 `apps/web/**`。 |
| 后台权限与审计 | 后台直播间管理和直播线路管理接口/页面存在；部分操作 UI 尚需补齐。 |
| 根节点是否挂载 | 不涉及 |
| 静态资源是否 200 | 不涉及 |
| console 是否无 error | 不涉及 |
| 与设计图主要偏差 | 线路选择当前不改变播放 URL，只做选择上报。 |
| 合入判断 | 文档/契约/DTO 可合入；前端实现需另起任务。 |

## 风险与待办

1. `apps/web` 当前弹幕历史读取仍可能按 `data[]` 处理，需前端团队按 `data.items[]` 修。
2. 线路选择目前不会改变 `play-url`，如要真实切 CDN，需要补后端路由和契约。
3. 后台房间详情 UI 未完整覆盖切主播、切比赛、分配管理员、会话历史、删弹幕/禁言。

## 交接说明

下一位 Agent 或工程师需要知道：

1. H5 房间页联调先看 `docs/frontend-integration.md` 第 8 节。
2. API 事实源头是 `docs/api/openapi.yaml` 与 `packages/contracts/openapi/v1.yaml`，不要按原型简写路径开发。
3. 本次没有修改 `apps/web/**`，符合 AGENTS §14 的职责边界。
