---
id: "doc-29ec6671c813"
title: "Agent 工作日志：ledger 集成测试（真实 MySQL 事务）"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "Docker", "MySQL", "自动化", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-ledger-integration-tests.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-ledger-integration-tests.md"
sourceSha256: "540ddb4a237b0858da30d64e653e092476166145f6d9da657619c8c6e7921aef"
sourceSystem: "project-doc"
---

# Agent 工作日志：ledger 集成测试（真实 MySQL 事务）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605240000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%EF%BC%9Aledger%20%E9%9B%86%E6%88%90%E6%B5%8B%E8%AF%95%EF%BC%88%E7%9C%9F%E5%AE%9E%20MySQL%20%E4%BA%8B%E5%8A%A1%EF%BC%89.md)

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期：2026-05-24
Agent：claude-code
任务：为 `internal/pkg/ledger` 补全基于真实 MySQL 的事务级集成测试，覆盖 happy path / 幂等冲突 / 余额回滚 / 并发乐观锁 / 外层事务回滚 5 条关键路径。

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：WALLET-* 全资金类需求（钱包+流水的核心约束）
- 既有单测：`internal/pkg/ledger/ledger_test.go`（21 cases，覆盖 validateBalance + applyToWallet 纯函数）
- 数据模型：`internal/model/wallet.go`（Wallet / WalletJournal / WalletJournalEntry）
- 运行环境：docker-compose 提供 MySQL 8.0 @ 203.0.113.1:13306（root/root_dev）

## 本次目标

1. 验证 `ledger.Post()` 在真实 MySQL 事务下端到端正确性（journal + entries + wallet 三表同步）
2. 验证幂等键 `uk_idempotency` 唯一约束生效
3. 验证余额不足时事务整体回滚（钱包未变 + 无 journal 入库）
4. 验证乐观锁在并发下不丢更新（version + 余额一致）
5. 验证 `ledger.PostTx()` 跟随外层事务回滚

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/pkg/ledger/integration_test.go` | 新增 5 个 `//go:build integration` 集成测试 |

## 核心决策

1. **不引入 testcontainers-go**：docker-compose 已提供 MySQL；引入 testcontainers-go 会拉镜像、加 6+ 依赖，与现有 dev 流程重复。改用 `//go:build integration` 标签 + 现有容器，CI 触发用 `go test -tags=integration`
2. **默认 DSN 走 root**：业务账号 `kickoff` 只能访问 `kickoff` 库无法 CREATE DATABASE；测试用 `root` 创建临时库，每个测试独立建库 + teardown drop
3. **每测试独立数据库**：库名 `kickoff_test_ledger_<unix_nano>`；t.Cleanup 自动 drop。避免跨测试残留与并行冲突
4. **AutoMigrate 替代 SQL 文件**：用 GORM AutoMigrate(&Wallet{}, &WalletJournal{}, &WalletJournalEntry{}) 生成 schema，与 prod migration 100% 字段一致（同源 struct tag）
5. **并发测试用乐观锁重试**：在 worker 内最多重试 5 次 `ErrConcurrent`；最终断言 `version == N && balance == N*each` — 任何丢更新都会失败
6. **MySQL 不可达时 t.Skipf**：本地无 Docker 时 `go test -tags=integration` 跳过而非失败，配合 CI 走 docker-compose

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 5 cases 全绿；each test 独立库 + drop；并发 20 个 goroutine 各重试 ≤5；version 与 journal 计数严格断言 |
| 红队质疑 | (1) 重试逻辑是否掩盖真实 bug？→ 蓝队答：重试上限 5；超限即 `t.Errorf`；ErrConcurrent 之外的错误直接 fail；(2) Cleanup 失败导致测试库泄漏？→ 用 nanosecond 时间戳 + 显式 DROP IF EXISTS；多跑几次也只是占空间；(3) 默认 root 凭据写死 CI 不可用？→ TEST_MYSQL_DSN env 覆盖；本地默认是 dev-up.sh 同源；(4) 无 MySQL 时自动跳过会掩盖 CI 配置错误？→ skip 文案带"MySQL unavailable"明确，CI 应额外加 step 确认 docker compose up 成功 |
| 合入判断 | 允许合入；CI pipeline 把 `go test -tags=integration ./internal/pkg/ledger/...` 加为门禁后续迭代落地 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified（5/5 测试通过；race detector 全开） |
| Project Decision | pending-review |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | WALLET-* 全资金类需求 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-wallet.md` |
| OpenAPI / Event / DTO | 不影响 — 仅测试代码 |
| 验收证据行 | `docs/qa/project-acceptance.md` kickoff-wallet 自动化测试列已含 ledger_test.go；本日志补强证据 |
| 不涉及契约的原因 | 测试代码不暴露 API |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | gofmt / goimports / go vet 全过 |
| 数据表设计 | 测试通过 AutoMigrate 与 prod struct 同源；prod schema 由 `migrations/00000X_*.sql` 维护 |
| 是否使用表设计模板 | 不涉及（无新表） |
| 是否影响账本、事务、幂等或审计 | 是 — 测试覆盖；ledger 是账本核心，本次集成测包含 journal + entries + wallet 三表事务一致性 |
| 规范例外与原因 | 默认 DSN 走 root 仅限测试环境；prod 业务连接仍用 kickoff 账号最小权限 |

## 验证记录

- `go build ./...`：通过
- `go vet ./...`：通过
- `go test -race ./internal/pkg/ledger/...`：通过（21 cases 纯函数测）
- `go test -tags=integration -race ./internal/pkg/ledger/...`：通过（5 cases 集成测）
- `make framework-check`：17/17 全绿

## 后续动作

1. CI pipeline 启用 `docker compose up -d` + `go test -tags=integration -race ./internal/pkg/ledger/...` 步骤
2. 后续 wallet service 层的 InitRecharge / Withdraw / Tip 业务流也按此模式补集成测
3. 把 settle / refund / bet_lock 等高风险 biz_type 加入集成测覆盖
