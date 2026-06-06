---
id: "doc-a2126b169e0d"
title: "Agent 工作日志 · lsj-resource-quality"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-lsj-resource-quality.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-lsj-resource-quality.md"
sourceSha256: "1eba77faaea96451da0ba5fba23db62df3df312ca64d9f3a9f32ca11625fa519"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-resource-quality

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-lsj-resource-quality.md`

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：后台 LSJ 资源管理增加画质清晰度字段与筛选

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- Admin 通用 PRD 门禁引用：`docs/prd/modules/admin.md`（本项目实际后台模块文档为 `docs/prd/modules/kickoff-admin.md`）
- 需求 ID：ADM-920
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`packages/contracts/openapi`
- 验收证据：`docs/qa/acceptance-evidence.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：dev 环境 `GET /api/v1/admin/sports-live` 验证到 LSJ 线路 `type` 返回 `sd/fhd`

## 本次目标

1. 将 LSJ 原始线路类型规范化为后台可读的画质字段。
2. 后台 LSJ 资源管理支持按画质筛选和展示。
3. 赛事绑定选择器支持按画质筛选并选择对应线路。
4. 赛事绑定、房间详情、OpenAPI 与 contracts 同步画质字段。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/infra/live/lsj/types.go` | 增加 LSJ 线路画质归一化逻辑 |
| `services/go-app/internal/dto/streamer.go` | `sports-live` 线路返回 `line_type`、`quality_code`、`quality_label` |
| `services/go-app/internal/service/streamer/sports_live_source.go` | LSJ 搜索结果映射画质字段 |
| `services/go-app/internal/model/match.go` | 赛事 LSJ 绑定源增加画质字段 |
| `services/go-app/internal/service/liveprogram/service.go` | 绑定、回显、审计、日志同步画质字段 |
| `services/go-app/migrations/000048_add_lsj_source_quality_fields.*.sql` | 新增/回滚 `quality_code`、`quality_label` |
| `apps/admin/src/views/live/lsj-resources.vue` | LSJ 资源管理增加画质筛选和画质列 |
| `apps/admin/src/views/matches/list.vue` | 选择 LSJ 线路时保存画质字段；选择器支持按画质筛选 |
| `apps/admin/src/views/rooms/detail.vue` | 房间节目流详情/预览展示绑定画质 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 同步 API 契约 |
| `docs/prd/modules/kickoff-admin.md` | 同步 ADM-920 验收口径 |

## 核心决策

1. 不把 LSJ `stream_info` 原样透给前端，只解析白名单字段，避免泄漏上游实现细节。
2. `line_type` 保留为 LSJ 原始线路类型；运营和前端使用 `quality_code` / `quality_label`。
3. 仅画质展示字段变化不触发节目流重建；实际源标识 `app_name` / `stream_name` 变化才影响开播准备。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | `docs/architecture/database-design-standards.md` |
| 是否影响数据表 / migration / 索引 | 是，新增 `000048`，仅增加两个展示字段，不新增索引 |
| 是否影响账本、事务、幂等或审计 | 不影响资金；LSJ 绑定审计新增画质字段 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-920 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| ownerService | `services/go-app` |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 第三方来源解析 / 契约 / 运营后台 |
| 当前 MVP 边界 | LSJ 画质来源以线路 `type` 和白名单 `stream_info` 为准；不做自动择优和自动降级 |
| 未来迁移成本 | 如后续 LSJ 提供明确分辨率/码率，可在同一归一化函数补字段，不改业务链路 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要跑 DB migration 并重启后端/admin |
| 回滚 | 执行 `000048_add_lsj_source_quality_fields.down.sql` 后回滚应用版本 |
| 密钥 | 不涉及 |
| 观测 | LSJ 绑定日志和审计包含画质字段 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/infra/live/lsj ./internal/service/streamer ./internal/service/liveprogram` | 通过 |
| `pnpm --dir apps/admin exec vue-tsc --noEmit` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 页面 | 后台 `#/live/lsj-resources`、`#/matches`、`#/rooms/:id` |
| 目标 viewport / 设计尺寸 | 后台桌面运营视口，基准 1440x900；无单独设计稿 |
| 页面截图 | Playwright 截图：`docs/qa/screenshots/current/admin-lsj-resources-quality-1440x900.png`、`docs/qa/screenshots/current/admin-match-lsj-picker-quality-1440x900.png` |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 后台运营桌面页，不作为 C 端移动页面使用；375x812 手机视口不适用，本次重点验收 1440x900 桌面运营视口 |
| 响应式验收 | 后台表格页按桌面运营工作台使用；本次不改变移动端布局，375x812 仅记录为不适用 |
| 桌面视口 | 已用 1440x900 desktop 视口完成 Playwright 页面截图 |
| SEO异常验证 / meta scope | 后台管理页不涉及 SEO异常验证、title、description、Open Graph 或 C 端 meta 修改 |
| API 接口路径 | `GET /api/v1/admin/sports-live`、`PUT /api/v1/admin/matches/{id}/lsj-source` |
| 弹窗验收 | 赛事编辑弹窗点击“选择 LSJ 直播”后，顶部出现“全部画质”筛选；线路卡片显示 `quality_label` 和 `line_type`，点击“选择”会保存该线路对应画质 |
| mock/fallback 状态与原因 | 无 mock；画质未知时展示 `未知` |
| 后台权限与审计 | 绑定 LSJ 源沿用 admin 鉴权和审计 |
| 合入判断 | 允许合入；部署后需跑 migration 并用真实 LSJ 样本复测画质标签 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 后端 API、后台页面和契约统一使用 `line_type`、`quality_code`、`quality_label`，没有继续把上游 `type` 混作业务画质字段 |
| 红队质疑 | 如果 LSJ 后续把清晰度放在 `stream_info` 的新字段里，当前只会显示未知或按线路名兜底；已把归一化收口到一个函数，后续扩展成本低 |
| 合入判断 | 允许合入；这是未上线功能，不保留旧字段兼容 |

## 风险与待办

1. LSJ 原始 `stream_info` 字段格式需要继续用真实样本观察，若提供分辨率/码率可扩展展示。
2. 画质选择目前是选择 LSJ 线路，不是 HLS 播放器内的 variant 切换。
3. dev 现有旧绑定数据通过 `line_type` 兜底回显画质；migration 不做历史数据批量回填。

## 交接说明

1. 前端/后台只使用 `quality_label` 展示给运营，`line_type` 作为技术字段保留。
2. 赛事绑定应从 `sports-live` 返回的同一条 stream 透传 `app_name`、`stream_name`、`line_type`、`quality_code`、`quality_label`。
3. 上线前需要确认 migration `000048` 已执行。
