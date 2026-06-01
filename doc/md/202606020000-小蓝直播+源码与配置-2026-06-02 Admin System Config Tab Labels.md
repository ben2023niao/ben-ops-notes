---
id: "doc-53ffbde52de3"
title: "2026-06-02 Admin System Config Tab Labels"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-system-config-tab-labels.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-system-config-tab-labels.md"
sourceSha256: "52f800aaf46e94b475746e4b1667ef36dd29afaa88cd44295845f1a686f9c764"
sourceSystem: "project-doc"
---

# 2026-06-02 Admin System Config Tab Labels

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-system-config-tab-labels.md`

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

## Task

用户要求系统配置页 tab 更贴近运营分类：

- `通用` 改为 `基础`
- `钱包 / 充值` 拆成 `钱包` 和 `充值`
- `predict` 改为中文展示

## Changes

- 后台配置页新增展示层虚拟 tab：
  - `wallet`：展示 `category=wallet` 且 key 不以 `wallet.recharge.` 开头的配置
  - `recharge`：展示 `category=wallet` 且 key 以 `wallet.recharge.` 开头的配置
- 充值快捷编辑表单只在 `充值` tab 展示。
- 中英文语言包补充 `recharge` / `predict`，并将 `general` 中文展示改为 `基础`。

## Verification

- `pnpm --filter @kickoff/admin typecheck`
