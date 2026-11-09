---
id: "doc-8e3cc4e36de3"
title: "Agent 工作日志 · admin-system-config-empty-value"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-admin-system-config-empty-value.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-admin-system-config-empty-value.md"
sourceSha256: "2f514e359c6276664216f191a10c415afd50acab3342766083d2e176b8d7814f"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-system-config-empty-value

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606090000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-system-config-empty-value.md)

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：后台 `#/system/config` 配置值允许保存为空字符串

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-006
- 接口/契约：`PUT /api/v1/admin/system/config/{key}`（operationId: `adminSystemConfigUpdate`）
- AI/工具控制文件：`AGENTS.md` / `CLAUDE.md`
- 其他：`apps/admin/src/views/system/config.vue`、`services/go-app/internal/dto/admin_modules.go`、`services/go-app/internal/service/admin/system.go`

## 本次目标

1. 确认配置值为空时是前端拦截还是接口也拦截。
2. 允许后台显式提交 `value: ""` 清空配置值。
3. 保持漏传 `value` 时仍返回参数错误。

## 数据链路

入口页面：`apps/admin` `#/system/config` 编辑弹窗
API：`systemApi.updateConfig(key, body)` -> `PUT /api/v1/admin/system/config/{key}`
DTO / handler：`AdminSystemConfigUpdateRequest` -> `SystemHandler.UpdateConfig`
service：`SystemService.UpdateConfig`
数据表：`system_configs.config_value`（TEXT NOT NULL，允许空字符串）
返回字段：保存成功返回空 OK，列表刷新读取 `SystemConfigItem.value`
前端消费字段：`value` 字段名未变化，仅允许空字符串语义变化

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/system/config.vue` | 去掉配置值必填校验，提交时保证 `value` 字段存在 |
| `services/go-app/internal/dto/admin_modules.go` | `value` 改为 `*string binding:"required"`，允许空字符串但拒绝漏传 |
| `services/go-app/internal/service/admin/system.go` | 保存和审计使用解引用后的配置值 |
| `services/go-app/internal/dto/admin_modules_test.go` | 覆盖空字符串通过、漏传失败 |
| `docs/api/openapi.yaml` | 契约标明 `value` 为 string 且允许空字符串 |
| `packages/contracts/openapi/v1.yaml` | 同步 contracts OpenAPI |
| `services/go-app/internal/service/admin/system_public_test.go` | 覆盖公开配置中 site 展示字段空字符串原样返回 |

## 核心决策

1. 不是单纯前端拦截：前端 `rules: 'required'` 与后端 `binding:"required"` 都会拒绝空字符串。
2. 后端不直接删除 required，避免漏传字段被误认为清空配置。
3. OpenAPI 保持 `required: [value]`，仅明确 string 类型且不设置 `minLength`。
4. `GET /api/v1/config/system` 对钱包 / 礼物数值配置仍保留空值兜底；`site` 下客服邮箱、商务合作邮箱、主域名清空后原样返回空字符串，表示前端不展示。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-006 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 已更新 OpenAPI、contracts 与 DTO |
| 前端字段变更 | 不涉及字段改名；`value` 字段语义改为允许空字符串；`site.*` 允许返回空字符串 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及，`config_value` 已为 TEXT NOT NULL，可保存空字符串 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金账本；系统配置写操作继续写审计 |
| 规范例外与原因 | 本地缺 Go 工具链，无法执行 gofmt/go test |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 是，系统配置更新语义修正 |
| 涉及能力 | 权限安全 / 审计 |
| 高风险触发项 | 权限 |
| 能力门禁结论 | 允许进入 Review；需 CI 或有 Go 工具链环境补跑 Go 测试 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 不影响服务入口、health check 或部署脚本 |
| 回滚 | 回滚本次代码与契约变更即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 审计日志字段保持 before/after |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `git fetch origin` | 通过；Git 提示历史 gc/loose objects 维护警告 |
| `git status --short` | 开工时干净 |
| `git rev-list --left-right --count HEAD...@{upstream}` | `0 0` |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 阻塞：缺少 `PIL`，且本机无 `pip` |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `pnpm exec prettier --write ...` | 通过 |
| `pnpm typecheck` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `curl -L https://api-dev.54-151-131-132.sslip.io/api/v1/config/system` | 当前 dev 仍返回 `site.primary_domain="kickoff.example"`，确认线上命中空字符串 fallback 逻辑；需部署本次修复后生效 |
| `gofmt -w ...` | 未执行：环境无 `gofmt` |
| `go test ./internal/dto` | 未执行：环境无 `go` |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 不涉及视觉变更 |
| 页面截图 | 未截图，行为/校验变更 |
| API 接口路径 | `PUT /api/v1/admin/system/config/{key}` |
| 后台权限与审计 | 复用原后台鉴权；服务端继续写 `admin.system.config_update` 审计 |
| 与设计图主要偏差 | 不涉及 |
| 合入判断 | 允许进入 Review；需补 Go 工具链验证 |

## 风险与待办

1. 需在有 Go 工具链环境补跑 `gofmt` 与 `go test ./internal/dto`。
2. 线上接口文档发布后，Stoplight 深链为 `https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminSystemConfigUpdate`。
3. 运营清空 `site` 展示字段后，公开读取接口会返回空字符串；C 端需要按空字符串不展示对应 footer 项。
