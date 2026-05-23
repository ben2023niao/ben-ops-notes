---
id: "doc-bc1564d233d0"
title: "Agent 工作日志：Code Review Batch #2 修复（C2/C3/H2/H3/H5/H6）"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "Docker", "MySQL", "Redis", "监控告警", "自动化"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-code-review-batch2-fixes.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-code-review-batch2-fixes.md"
sourceSha256: "c019273e218c5d564c37f3f688e6c6651c42f94958cd6bb92562ddd8806db8d1"
sourceSystem: "project-doc"
---

# Agent 工作日志：Code Review Batch #2 修复（C2/C3/H2/H3/H5/H6）

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-code-review-batch2-fixes.md`

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期：2026-05-24
Agent：claude-code
任务：继 Batch #1（C1/C5/H1/H4/H7/H8/H9）之后，完成 Batch #2 的 6 项 critical/high 修复 — 全部聚焦后端安全 + 资金一致性。

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`（提现限额）、`kickoff-admin.md`（按 project.config.json exceptions[apps.admin].exceptionReason 与 `docs/prd/modules/admin.md` 同义；用户管理 / 监控）
- 需求 ID：WALLET-101~107、ADM-401~405、ADM-101
- 接口契约：`docs/api/openapi.yaml`
- 后端归属：services/go-app；adminBearer JWT；audit + 全资金类操作复式记账
- Review 报告：上一轮 3 个 reviewer agent 输出

## 本次目标

1. **C2 验证**（不需修改）：确认 `wallet_journals.idempotency_key` UNIQUE 索引已存在，gorm 处理 `ErrDuplicatedKey` 链路完整
2. **C3 修复**：SubmitWithdraw 日限额 race condition — 包进单事务 + SELECT FOR UPDATE 钱包行序列化
3. **H2 修复**：Redis 不可达时 admin token 撤销名单完全 bypass — admin scope 走 fail-closed
4. **H3 修复**：prod 环境强制非空 `srs.allowed_ips`，防 webhook 对外网开放
5. **H5 修复**：dashboard `queryHourCount` 加白名单守护，防止未来 user input 直传 SQL
6. **H6 修复**：admin user 列表 `keyword` 长度上限 50，防 `LIKE '%超长串%'` 全表扫 DoS

## 修改文件

| 文件 | 修复项 | 说明 |
| --- | --- | --- |
| `services/go-app/internal/service/wallet/service.go` | C3 | SubmitWithdraw 改单事务：SELECT FOR UPDATE wallet → SumDailyTx → 限额 check → CreateTx → ledger.PostTx；errcode AppError 透传 |
| `services/go-app/internal/repository/wallet/orders.go` | C3 | WithdrawRepository 新增 `CreateTx` + `SumDailyTx`；SumDaily 提取 `sumDailyOn` 共享实现 |
| `services/go-app/internal/http/adminapi/user.go` | H6 | List handler 拒绝 keyword 长度 > 50 |
| `services/go-app/internal/service/admin/dashboard.go` | H5 | queryHourCount 闭包入口加 `allowedHourQueries` map 白名单 |
| `services/go-app/internal/config/loader.go` | H3 | validate() prod env 强制 `len(c.SRS.AllowedIPs) > 0` |
| `services/go-app/internal/config/loader_test.go` | H3 | 2 case 单测覆盖 prod 拒绝空 / local 允许空 |
| `services/go-app/internal/http/middleware/auth.go` | H2 | admin scope 走 fail-closed：Redis 客户端 nil 或查询错误时拒绝；user scope 仍 fail-open |

## 核心决策

1. **C2 不需修改**：迁移 000002 line 54 已声明 `UNIQUE KEY uk_idempotency (idempotency_key)`，live DB 验证 `Non_unique=0` 索引在位。`ledger.postInTx` Create 时撞 unique 会进入 `errors.Is(err, gorm.ErrDuplicatedKey)` 分支返回 `"idempotency key conflict"`，由 SettleRechargePaid 包装为 ErrConflict。整链完整，无需修改
2. **C3 锁粒度 = 钱包行（per user）**：序列化同一用户的并发提现 submit；不同用户互不阻塞。SELECT FOR UPDATE wallet 在事务首步执行，SumDaily 在锁后读取，保证看到完整已提交（含飞行中事务的写）
3. **C3 ledger.PostTx 在同事务重新锁同行不死锁**：MySQL InnoDB 同事务对同行 SELECT FOR UPDATE 是可重入的，不会自死锁
4. **C3 AppError 透传**：事务闭包返回 `*errcode.AppError` 时（如 ErrWithdrawLimit），外层用 `errors.As` 检测并原样返回；只有非 errcode 错误才包成 ErrInternal
5. **H2 admin fail-closed / user fail-open 双标准**：admin 后台是授权安全测试高价值目标（资金操作 / 用户冻结 / 提现审批），登出后的 token 仍能用是不可接受的；user 端容忍 Redis 抖动以保业务流，敏感写另靠 idempotency_key + ledger 兜底
6. **H3 仅强制 SRS allowed_ips，不强制 pay**：项目当前只有 SRS hook 配置实际启用；payment hook 在 ADR-0010 决策前是 placeholder（M3 风险已在 review 中标记，留给后续批次）。生产 fail-closed 范围与实际开放面对齐
7. **H5 用 map 而非 switch 守护**：5 个允许的 (table, field) 二元组以字符串 key 进 map，复杂度 O(1) 且语义直观；以后扩展只需加 key

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | (1) go build / go vet 全过；(2) go test -race -count=1 ./...（全模块）全 ok；(3) go test -tags=integration -race ./pkg/ledger/... 5/5 pass，C1 重构没破坏既有；(4) config validate 单测 2/2 pass；(5) make framework-check 17/17 全绿 |
| 红队质疑 | (1) C3 多个用户并发会不会因锁钱包行影响吞吐？→ 蓝队答：锁粒度是 per user，不影响跨用户；同一用户连发提现按业务设计就应该串行；(2) C3 锁了钱包但授权安全测试者用不同 idempotency_key 多次提交是否仍可绕？→ 蓝队答：所有 submit 都 SELECT FOR UPDATE 同一行，第二个 submit 拿不到锁，等第一个事务完成后 SumDailyTx 已看到上一笔，限额检查必拒；(3) H2 admin fail-closed 会不会让 Redis 短抖导致 admin 集体下线？→ 蓝队答：admin 量级远小于 user，Redis 抖动期间几个 401 重登可接受；后续 M1 中间件可加 fallback 到 DB 黑名单；(4) H3 只管 srs 不管 pay 是否漏？→ 蓝队答：pay generic hook 还没启用，无实际暴露面；启用前会有 ADR-0010 评审，届时一起补 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified（go test 全过 + framework-check 17/17 全绿） |
| Project Decision | pending-review |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | WALLET-101 (提现 daily limit) / ADM-401~402 (用户列表) / ADM-101 (dashboard) / 后台运行环境 / Auth |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `kickoff-wallet.md` / `kickoff-admin.md` |
| OpenAPI / Event / DTO | 无契约变化；纯实现层加固 |
| 验收证据行 | `docs/qa/acceptance-evidence.md` / `docs/qa/project-acceptance.md`：本次为 review 修复，无新增完成行 |
| 不涉及契约的原因 | 全部为内部实现加固，不影响外部 API 形状 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | Go: gofmt + go vet 全过；errors.As / errors.Is 用法正确；事务边界清晰 |
| 数据表设计 | 不影响表结构；C2 验证既有 UNIQUE 索引在位 |
| 是否影响账本、事务、幂等或审计 | 是 — C3 是提现核心事务边界改造；H2 加固 token 撤销审计链 |
| 规范例外与原因 | 无 |

## 验证记录

- `go build ./...`：通过
- `go vet ./...`：通过
- `go test -race -count=1 ./...`：member / wallet / config 全 ok
- `go test -tags=integration -race ./internal/pkg/ledger/...`：5/5 pass（无 regression）
- `docker exec kickoff-mysql ... SHOW INDEX FROM wallet_journals`：`uk_idempotency` 索引 `Non_unique=0` 在位
- `make framework-check`：17/17 全绿

## 后续动作（剩余 review 项）

待下批：
- **C4**：admin JWT localStorage → HttpOnly cookie 迁移（需后端 refresh endpoint）
- **M1**：WS CheckOrigin Origin 校验
- **M3**：payment hook signature verification（ADR-0010 决策后实现）
- **M4**：SettleRechargePaid 比对回调金额 vs 原单金额
- **M5**：wallet recharge platform_fee_rate float64 → decimal string
- **M6**：删除 member service.go 中 `var _ = sha256.New / hex.EncodeToString` 死代码
