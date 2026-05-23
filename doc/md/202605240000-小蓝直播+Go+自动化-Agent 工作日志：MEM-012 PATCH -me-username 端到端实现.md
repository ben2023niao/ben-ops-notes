---
id: "doc-d7b53b340cc6"
title: "Agent 工作日志：MEM-012 PATCH /me/username 端到端实现"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-mem-012-username-patch.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-mem-012-username-patch.md"
sourceSha256: "1a24be73cb93685504eb1edbd2a4a581aeda024efbd288d9e38d6d736a9b3b02"
sourceSystem: "project-doc"
---

# Agent 工作日志：MEM-012 PATCH /me/username 端到端实现

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-mem-012-username-patch.md`

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期：2026-05-24
Agent：claude-code
任务：补齐 v0.3 PRD MEM-012 中 `PATCH /api/v1/me/username` 后端实现（service + repository + handler + router + OpenAPI），打通端到端契约。

## 输入资料

- PRD：`docs/prd/modules/kickoff-member.md`
- 需求 ID：MEM-012（编辑个人信息 modal — 用户名 + 头像）
- 接口契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- v0.3 字段对齐：users.nickname → username（迁移 000010；ADR-0011）

## 本次目标

1. service 层增加 UpdateUsername，含 PRD §5 校验规则（2-20 字 / 中英文+数字+`_-.`）
2. repository 层增加 UpdateUsername 方法
3. handler 层增加 UpdateUsername，绑定 dto.MeUpdateUsernameRequest
4. router 挂载 `PATCH /api/v1/me/username`（在 me group 下，requireUserAuth 中间件）
5. OpenAPI 增加 PATCH 操作，包含 x-prd-id / x-apifox-folder / 校验规则文档
6. 单测覆盖 username 校验正则的 14 种边界场景

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/repository/user/user.go` | 接口新增 UpdateUsername；repo 实现 |
| `services/go-app/internal/service/member/service.go` | 新增 UpdateUsername + usernameAllowed regex + audit |
| `services/go-app/internal/http/public/member.go` | 新增 UpdateUsername handler |
| `services/go-app/internal/http/router/public.go` | 挂载 PATCH /me/username |
| `docs/api/openapi.yaml` | 新增 PATCH /api/v1/me/username 操作 |
| `packages/contracts/openapi/v1.yaml` | 同步 contracts 镜像 |
| `services/go-app/internal/service/member/username_test.go` | 14 cases 覆盖中英文/长度/符号/空/emoji |

## 核心决策

1. **不做唯一性校验**：PRD 定义 username 为 display name（非登录凭证），允许重名；与 admins.username 不同义
2. **正则放 service 层**：而非 binding tag — 中英文 + 长度 + 字符集组合用 `^[\p{Han}A-Za-z0-9_\-.]{2,20}$` 比 binding 表达更准确
3. **HTTP method = PATCH**：单字段局部更新，符合 REST 语义；与已有 POST /me/avatar 并存（avatar 的 method 不在本次变更范围）
4. **审计字段记录新值**：`member.username.update` 与已有 `member.avatar.update` 命名风格统一
5. **dto 已存在**：`MeUpdateUsernameRequest` 在前次 v0.3 PRD 对齐时已定义，本次只补 service/handler/router/openapi

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | MEM-012 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-member.md` §5（边界与异常）/ §8（API 契约） |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml` PATCH /api/v1/me/username；`dto.MeUpdateUsernameRequest` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` 待补 MEM-012 行（pending E2E 后） |
| 不涉及契约的原因 | 涉及，已同步 OpenAPI |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | gofmt / goimports / go vet 全过 |
| 数据表设计 | 不影响（沿用 000010 已迁移的 `users.username` 字段） |
| 是否使用表设计模板 | 不涉及（无新表） |
| 是否影响账本、事务、幂等或审计 | 涉及审计：`member.username.update`；无资金/账本 |
| 规范例外与原因 | 无 |

## 验证结果

- `go build ./...`：通过
- `go vet ./...`：通过
- `go test -race ./internal/service/member/...`：通过（14 cases）
- `make framework-check`：17/17 全绿

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 校验规则同 PRD §5；新值落库 + audit 记录；OpenAPI 已同步双 contracts；route 在 requireUserAuth 中间件下，未鉴权请求返回 401 |
| 红队质疑 | (1) username 允许重名是否被滥用做钓鱼？→ 蓝队答：display name 业务定义如此，反钓鱼走 admin 后台举报通道；(2) regex 是否被 ReDoS？→ 字符集均为单字符匹配，长度上限 20，无嵌套量词，安全；(3) 高频改名是否被刷？→ 当前无速率限制，下个迭代加 RateLimiter 中间件按 user_id 5 次/小时 |
| 合入判断 | 允许合入；速率限制项进入 backlog 跟踪 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified（单测）；待 E2E 后续补 |
| Project Decision | pending-review |

## 后续动作

1. apps/web / apps/h5 接入：调用 PATCH /me/username 后刷新 me-header username 显示
2. E2E：手工或自动化测一次 modal 编辑 → 接口调用 → 头部同步
3. 补 `docs/qa/acceptance-evidence.md` MEM-012 行（待 E2E 证据齐后改为"已完成"）
4. 补 `docs/qa/project-acceptance.md` kickoff-member 行（当前"未开始"，待端到端打通后升级为"进行中"）
5. 速率限制：下迭代为 PATCH /me/username 接入限流中间件（5 次/小时/用户）
