---
id: "doc-8f3c8ac90afe"
title: "web-recharge-api-align"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-web-recharge-api-align.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-web-recharge-api-align.md"
sourceSha256: "9dfea81aed8dd72f8e7ea1c2fad237dc442cf65bd51d77186674490ec75126bb"
sourceSystem: "project-doc"
---

# web-recharge-api-align

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-web-recharge-api-align.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：前台充值 API 对齐大白鲨聚合支付

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：WALLET-001、WALLET-002、WALLET-005、WALLET-006
- 接口/契约：`packages/contracts/openapi/v1.yaml`
- 前台代码：`apps/web/app/apis/wallet.ts`、`apps/web/shared/types/wallet.ts`

## 本次目标

1. 将 H5 充值下单入参从旧 `amount_rmb + channel=wechat/alipay` 对齐为 `rmb_amount + channel=shark + pay_type + agree_terms`。
2. 增加前台读取充值通道与按金额查询可用支付方式的 API 封装。
3. 修复弹窗充值与二维码页重复创建订单的问题。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/web/shared/types/common.ts` | 更新充值状态、支付通道和大白鲨子通道类型 |
| `apps/web/shared/types/wallet.ts` | 更新充值订单、下单请求、通道查询响应类型 |
| `apps/web/app/apis/wallet.ts` | 新增 `getWalletChannels`、`getRechargePayTypes` |
| `apps/web/app/layouts/default.vue` | 弹窗充值改为跳转付款页，不提前创建订单 |
| `apps/web/app/components/wallet/WalletRechargePanel.vue` | 选择项改为 `pay_type` |
| `apps/web/app/pages/recharge/index.vue` | 充值页跳转携带 `pay_type` |
| `apps/web/app/pages/recharge/qr.vue` | 付款页按新契约创建订单并展示 `pay_url/pay_mode` |
| `apps/web/app/pages/member.vue` | 充值记录适配新字段与状态 |

## 核心决策

1. 订单只在 `/recharge/qr` 创建，避免弹窗和付款页双下单。
2. 保留旧 query `channel` 兼容入口，但内部统一转为 `pay_type`。
3. 当前只做 API 对齐，不做真实大白鲨联调。

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/web typecheck` | 通过 |
| `pnpm --filter @kickoff/web test` | 通过 |
| `pnpm --filter @kickoff/web build` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `npm run check` | 通过 |

## 风险与待办

1. `getWalletChannels` 与 `getRechargePayTypes` 已封装，但充值 UI 仍以本地选项为主，后续可切到动态通道。
2. 真实 `pay_url` 是否是二维码链接、跳转链接或 card JSON，需要大白鲨联调后再细化展示。
