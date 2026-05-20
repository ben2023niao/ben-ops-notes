---
id: "doc-2e23f299e5cf"
title: "Kickoff PRD 模块索引"
date: "2026-05-21T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/README.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/README.md"
sourceSha256: "7cbb8909b8893436100cc979d551f6c9de864bdb750a322cdc41857f3f3da85a"
sourceSystem: "project-doc"
---

# Kickoff PRD 模块索引

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/README.md`

> 整理日期：2026-05-21 00:00｜日期依据：正文日期

本目录是 Kickoff（小蓝看夜场）的业务 PRD 模块拆分。总览见 `../product-prd.md`，需求追踪见 `../requirements.md`。

## 模块清单（10 个，v0.2 已移除主播端）

| 模块文件 | 端 | 需求 ID 前缀 | Owner | 状态 |
| --- | --- | --- | --- | --- |
| [`kickoff-auth.md`](kickoff-auth.md) | Web / H5 | `AUTH` | `@kickoff/frontend` + `@kickoff/backend` | 已确认（v0.2 简化为账号+密码） |
| [`kickoff-home.md`](kickoff-home.md) | Web | `HOME` | `@kickoff/frontend` | 已确认 |
| [`kickoff-live.md`](kickoff-live.md) | Web | `LIVE` | `@kickoff/frontend` + `@kickoff/backend` | 已确认（v0.2 砍掉实时数据卡） |
| [`kickoff-schedule.md`](kickoff-schedule.md) | Web | `SCHED` | `@kickoff/frontend` | 已确认 |
| [`kickoff-match-detail.md`](kickoff-match-detail.md) | Web | `MATCH` | `@kickoff/frontend` | 已确认（v0.2 砍掉实时数据） |
| [`kickoff-predict.md`](kickoff-predict.md) | Web / H5 | `PRED` | `@kickoff/backend` | 已确认 |
| [`kickoff-member.md`](kickoff-member.md) | Web / H5 | `MEM` | `@kickoff/backend` | 已确认 |
| [`kickoff-wallet.md`](kickoff-wallet.md) | Web / H5 | `WALLET` | `@kickoff/backend` | 已确认（v0.2 支付通道 TBD） |
| [`kickoff-admin.md`](kickoff-admin.md) | Web | `ADM` | `@kickoff/admin` + `@kickoff/backend` | 已确认（v0.2 新增"直播间管理"） |
| [`kickoff-h5.md`](kickoff-h5.md) | H5 | `H5` | `@kickoff/frontend` | 已确认 |

> **v0.2 已废弃**：`kickoff-streamer.md`（原"主播端" `STR-*` 17 个需求全部移除）。原因：v1 改为 OBS 推流 + 运营托管模式，主播无任何 web 端交互。原主播端职能由 `kickoff-admin.md §3.3' 直播间管理` 承接。

## 规则

1. `../product-prd.md` 只保留产品总览、跨模块业务规则、非功能需求。
2. 具体功能需求写入 `kickoff-<module>.md`。
3. 做哪个功能，就优先更新对应模块文档。
4. 每个进入开发的需求必须有唯一需求 ID（格式 `<PREFIX>-<3 位数字>`，如 `AUTH-001`、`PRED-002`）。
5. 需求 ID 必须同步登记到 `../requirements.md` 和 `../requirements.index.json`。
6. 模块 PRD 结构参考框架模板 `.ai-framework/docs/templates/prd-module-template.md`，按 Kickoff 需要可适度增减。
7. 业务规则变更需在 `product-prd.md §6 跨模块业务规则` 同步登记。
8. 高风险规则变更（资金、风控、合规）需要写 ADR 到 `docs/decisions/`（项目创建该目录时同步）。

## 验证

```bash
# 在项目根目录运行
PRD_REPO_ROOT=$PWD python3 .ai-framework/scripts/validate-prd.py
```

该校验器会检查 PRD 模块结构、需求 ID 命名、`requirements.index.json` 与 schema 匹配性。

## 版本来源

基线原型：

```
2026.05.21评审版.html（snapshots/v2.32）
```

v0.2 修订（2026-05-22）相对原型的偏离：

| 变更点 | 原型 v2.32 | v0.2 实施版 |
| --- | --- | --- |
| 登录注册 | 手机号/邮箱双模式 + 验证码登录 + 自助找回密码 | 账号+密码，无验证码，客服找回 |
| 主播端 | 5 步流程 + 3 异常态 + 浏览器内推流 | **完全废弃**，主播仅 OBS 推流 |
| 直播间数据卡 | 控球/射门/角球/黄牌 4 项实时数据 | 砍掉，仅保留比分 |
| 赛事详情实时数据 | 进球/红黄牌/换人/越位 + 6 项 stat | 仅保留进球（运营录入）+ 比分 + MVP |
| 后台赛事 & 赔率 | v2 占位 | **v1 必上**（含比分快速录入 + 活动 CRUD） |
| 后台内容审核 | v2 占位 | **v1 必上**（合规底线） |
| 后台直播间管理 | 不存在 | **新模块**（承接主播端职能） |
| 支付通道 | 微信 + 支付宝直签 | 待重新评估，预留抽象层 |

具体偏离动机详见各模块 PRD 顶部 v0.2 说明 + `docs/decisions/ADR-*.md`（待写）。
