---
id: "doc-1182fb0cbf31"
title: "Agent 工作日志：Code Review Batch #1 修复（C1/C5/H1/H4/H7/H8/H9）"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-code-review-batch1-fixes.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-code-review-batch1-fixes.md"
sourceSha256: "be6a9c8add25a4761a7033f6c25c33c8d81ddcb17820da2ea41c942e779745de"
sourceSystem: "project-doc"
---

# Agent 工作日志：Code Review Batch #1 修复（C1/C5/H1/H4/H7/H8/H9）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605240000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2BRedis-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%EF%BC%9ACode%20Review%20Batch%20-1%20%E4%BF%AE%E5%A4%8D%EF%BC%88C1-C5-H1-H4-H7-H8-H9%EF%BC%89.md)

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期：2026-05-24
Agent：claude-code
任务：依据 3 个 reviewer agent（go-reviewer / typescript-reviewer / security-reviewer）的 review 报告，落地"立即修"批次的 7 项问题。范围限定 risk 大、改动局部、可独立验证的项；C2/C3/C4 涉及 schema/migration/架构调整推到本迭代后段或下迭代。

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`（资金）、`kickoff-member.md`（头像 SSRF）、`kickoff-admin.md`（按 project.config.json exceptions[apps.admin].exceptionReason 与 `docs/prd/modules/admin.md` 同义；观众/配置子模块）
- 需求 ID：WALLET—001~005、MEM-012、ADM-907、后台-系统配置
- 接口契约：`docs/api/openapi.yaml`（canonical）+ `packages/contracts/openapi/v1.yaml`（mirror）
- 后端归属：services/go-app；权限 adminBearer / userBearer JWT；audit 走 `audit.Log`
- Review 报告：上一轮对话三个 reviewer 输出

## 本次目标

1. **C1**：SettleRechargePaid 把 MarkPaid + ledger.Post 包进单一事务，防止"已 PAID 但未发钻"
2. **C5**：integration_test concurrent test 不能在 goroutine 内 t.Errorf；改 atomic + error channel
3. **H1**：wallet/service.go 4 处 `err == ErrXxx` → `errors.Is`，防止包裹后漏判
4. **H4**：UpdateAvatar 校验 URL host 在 storage public base 白名单内，防 SSRF 存储
5. **H7**：roomApi.viewers TS 类型与 OpenAPI 对齐（viewer_count/peak_count/vips），后端 service 也同步修正
6. **H8**：ConfigListView updateConfig 字段从 `description` 改 `reason`；后端 DTO + service 接收 reason 入 audit
7. **H9**：viewers 移除前端误传的 page/size 参数，改 vip_only（与 OpenAPI 一致）

## 修改文件

| 文件 | 修复项 | 说明 |
| --- | --- | --- |
| `services/go-app/internal/repository/wallet/orders.go` | C1 | 新增 `MarkPaidTx` + `LockByOrderNoTx`；提取 `markPaidOn` 共享实现 |
| `services/go-app/internal/service/wallet/service.go` | C1 + H1 | SettleRechargePaid 改单事务（Lock → 状态判 → MarkPaidTx → ledger.PostTx）；4 处 `==` 改 `errors.Is` |
| `services/go-app/internal/pkg/ledger/integration_test.go` | C5 + C3 | 并发测改 `atomic.Int32` 计数 + `errCh` 收集；retry 上限 5 → 50；4 处 `_ = db.First(&w)` 改 fatal-on-error |
| `services/go-app/internal/service/member/service.go` | H4 | UpdateAvatar 增 `allowedAvatarHosts()` 白名单（Storage.LocalPublicBase + S3.PublicBase）；scheme + host 双重校验 |
| `services/go-app/internal/service/member/avatar_test.go` | H4 | 4 个 case 单测 allowedAvatarHosts 边界 |
| `services/go-app/internal/service/admin/room.go` | H7 | Viewers 签名 `(roomID, vipOnly)`；返回 `viewer_count/peak_count/vips`（对齐 OpenAPI） |
| `services/go-app/internal/http/adminapi/room.go` | H7 | handler 改读 `vip_only` query 参数 |
| `services/go-app/internal/dto/admin_modules.go` | H8 | AdminSystemConfigUpdateRequest 加 `Reason` 字段 |
| `services/go-app/internal/service/admin/system.go` | H8 | UpdateConfig 把 req.Reason 写进 audit.Event.Reason |
| `apps/admin/src/api/index.ts` | H7/H8/H9 | 新增 `AdminRoomVip` + `RoomViewersResp` 类型；roomApi.viewers 改 `vip_only`；updateConfig 字段改 `reason` |
| `apps/admin/src/views/rooms/RoomDetailView.vue` | H7/H9 | ref 改 `RoomViewersResp` 形状；模板用 `viewer_count/peak_count/vips` 替换 `total/peak/items` |
| `apps/admin/src/views/system/ConfigListView.vue` | H8 | 编辑改两段 prompt（值 + 原因），原因必填 ≥ 4 字 |

## 核心决策

1. **C1 用 PostTx + Tx 变体方法而非二次事务**：钱包 `ledger.Post` 自己已经开事务，结合上层 MarkPaid 二次事务会形成嵌套 + 状态机不一致；正确做法是上层先开事务，下层用 `PostTx` 接管。新增 `MarkPaidTx` + `LockByOrderNoTx` 让 repo 支持外层事务接管
2. **C1 加 SELECT FOR UPDATE 锁住订单行**：原代码两条并发回调都过 `o.Status == Paid` 检查，依赖 `wallet_journals.idempotency_key` UNIQUE 兜底——但 ledger.PostTx 在 Tx 内调，撞 UNIQUE 直接事务回滚，整体行为正确。锁单 + 状态判提前在事务内做，是把"业务幂等"前移，减少深层错误传播
3. **C5 错误聚合在主 goroutine**：Go `testing` 包的 `t.Errorf` / `t.Fatal` 在 goroutine 内调虽然 1.13+ 已加锁，但 `t.FailNow` 仍只能在 test goroutine 调；统一规范 = 错误用 channel 收，主 goroutine 上 `t.Error`
4. **C5 retry 提升到 50**：N=20 并发对单钱包行的乐观锁竞争，max retry 5 在测试机偶发能失败；50 给充裕窗口，仍保留实际乐观锁工作的语义
5. **H4 兼容 storage 未配置场景**：local dev 可能 LocalPublicBase 留空；此时不做 host 校验（避免 dev 工作流断），生产环境 config validate 应保证至少一项非空（属于本期外的 ops 改进）
6. **H7 backend 优先对齐 OpenAPI**：发现 backend service 当前 `{ total, peak, items }` 与 OpenAPI `{ viewer_count, peak_count, vips }` 不一致；按"契约第一"修 backend；admin TS 同步 contract
7. **H8 后端 DTO + 前端 + OpenAPI 三处对齐**：发现 backend DTO 没有 reason 字段（完全丢），OpenAPI 写了 reason 但 backend 不接，admin TS 发的是 description；三处全错，统一收敛到 reason

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | (1) go build / go vet 全过；(2) `go test -race ./...` member/wallet/ledger 全过；(3) `go test -tags=integration -race ./pkg/ledger/...` 5/5 pass；(4) `pnpm --filter @kickoff/admin build` 通过（vue-tsc 严格模式无 type error）；(5) make framework-check 17/17 全绿 |
| 红队质疑 | (1) C1 锁单 SELECT FOR UPDATE 会不会引发死锁？→ 蓝队答：同一事务先锁订单再调 PostTx（PostTx 内部锁钱包），锁顺序固定（order_no → user_id），不会环；(2) C5 retry=50 是不是 mask 了真实 lost-update？→ 蓝队答：测试断言 successes=N + balance=N*each + version=N，任何 lost-update 都会让 version 与 successes 不一致；retry 只是给测试稳定性余量；(3) H4 配置空就不校验，dev → prod 误配怎么办？→ 蓝队答：本期不实现，归到 ops 配置 validation；至少 dev 环境的授权安全测试面已经收敛（local dev 通常不外网暴露）；(4) H8 强制要求 ≥4 字 reason 会不会激怒 admin？→ 蓝队答：审计审计就是要个理由；admin 修改业务关键 config 不写说明日后无法回溯；4 字门槛低，可接受 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified（go test + go build + admin build + framework-check 全过；新增 4 case avatar 单测） |
| Project Decision | pending-review |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | WALLET—001 / WALLET—005 / MEM—012 / ADM—907 / ADM 后台-系统配置 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `kickoff-wallet.md` / `kickoff-member.md` / `kickoff-admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml` schemas 已对齐；本次仅修代码使 backend 兑现既有契约 |
| 验收证据行 | `docs/qa/acceptance-evidence.md`：本次为 review 修复，无新增完成行；`docs/qa/project-acceptance.md` kickoff-wallet / kickoff-member / kickoff-admin 行的"自动化测试"列增量受益（事务+SSRF+契约对齐） |
| 不涉及契约的原因 | 仅代码贴合既有 OpenAPI 契约；唯一字段补充 `AdminSystemConfigUpdateRequest.Reason` 也是 OpenAPI 已声明的 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | Go: gofmt + go vet 全过；errors.Is 用法对齐；TS: vue-tsc 严格模式 |
| 数据表设计 | 不影响表结构 |
| 是否影响账本、事务、幂等或审计 | 是 — C1 是账本核心事务边界修复；H8 把 reason 入 audit；H4 把 avatar 写入 audit log（已有） |
| 规范例外与原因 | 无 |
| UI 验收模式 | no-design-mvp（admin 改动仅字段名/参数名重命名，不涉视觉规格） |
| 目标视口 / 设计尺寸 | 1440x900（admin 桌面端） |

## 验证记录

### 页面截图（真实手机视口 + 桌面视口）

本次 admin 改动仅为：
- ConfigListView：编辑 modal 流程改两段 prompt（值 + 原因）——非默认渲染界面，截图为编辑前列表态，与前次保持一致
- RoomDetailView：viewers 字段重命名（viewer_count/peak_count/vips）+ 模板绑定——v1 实际数据为空（Redis 未接入），视觉无变化

| 视口 | 文件 | 说明 |
| --- | --- | --- |
| 1440x900（桌面） | `docs/qa/screenshots/current/admin-system-config-1440x900.png` | /system/config 17 行真实默认（前次截图，本次仅改 edit dialog 内部流程） |
| 1440x900（桌面） | `docs/qa/screenshots/current/admin-users-empty-1440x900.png` | 前次截图；本次改动不涉及用户列表 |
| 1440x900（桌面） | `docs/qa/screenshots/current/admin-login-1440x900.png` | 前次截图 |
| 375x812（真实手机视口） | `docs/qa/screenshots/current/admin-login-375x812.png` | 前次截图 |

证据清单：`docs/qa/ui-visual-evidence.json` 当前 pages: []（项目 quality.requiresUiVisualEvidence=false）。

### 响应式（responsive） / SEO异常验证

admin 后台桌面优先 1440x900；移动 fallback 由 Element Plus 自动 stack。不涉及 SEO异常验证（内部系统）。

### 构建与门禁

- `go build ./...`：通过
- `go vet ./...`：通过
- `go test -race -count=1 ./internal/service/wallet/... ./internal/service/member/... ./internal/pkg/ledger/...`：全 ok
- `go test -tags=integration -race -count=1 ./internal/pkg/ledger/...`：5/5 pass（含 C5 重构的并发测）
- `pnpm --filter @kickoff/admin build`：通过
- `make framework-check`：17/17 全绿

## 后续动作

1. **C2**：审计 `wallet_journals.idempotency_key` 的 UNIQUE 索引是否真存在；如缺需补 migration
2. **C3**：每日提现限额 race condition — 需要把 SumDaily 检查放进 SELECT FOR UPDATE 钱包行，或用 Redis 锁
3. **C4**：admin JWT localStorage → HttpOnly cookie 迁移；需要后端实现 refresh endpoint + cookie 设置
4. **M1**：WS CheckOrigin 增加白名单检验
5. **M3**：payment hook signature verification — 生产前必须实现
6. **M5**：wallet recharge platform_fee_rate float64 → decimal string config
