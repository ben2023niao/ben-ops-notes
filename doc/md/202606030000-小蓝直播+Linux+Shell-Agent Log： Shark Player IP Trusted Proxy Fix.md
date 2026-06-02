---
id: "doc-0afcd6b4cf13"
title: "Agent Log： Shark Player IP Trusted Proxy Fix"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Python", "Go", "Nginx", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-player-ip-trusted-proxy.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-player-ip-trusted-proxy.md"
sourceSha256: "e2f637056583a821d4a0225621095d87f14127cf7b4c9101e2f79aca8caab0a9"
sourceSystem: "project-doc"
---

# Agent Log： Shark Player IP Trusted Proxy Fix

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-player-ip-trusted-proxy.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

- Date: 2026-06-03
- Scope: WALLET-007 / Shark recharge channel matching
- Author: Codex

## Background

大白鲨微信收银台返回“匹配失败 / 未匹配到金额”。重新核对 `/Users/qx/Downloads/大白鲨API文档.pdf` 后，文档明确说明 `info.playerId`、`info.playerIp`、`info.deviceId` 会参与刷单/风控判断；无法获取时必须每次随机，不可固定。

## Finding

Dev 服务器最近充值订单落库显示：

```text
client_ip = 203.0.113.1
client_device = dfp_f37e78980f5e49a987ab3dfb6d42f726
```

Nginx 已向 Go 服务传递 `X-Real-IP` / `X-Forwarded-For`，但 Go 服务 `server.trusted_proxies` 为空，Gin 不信任代理头，导致 `c.ClientIP()` 固定为本机反代地址 `203.0.113.1`。该值随后作为 Shark `info.playerIp` 传给大白鲨。

## Change

- `config.dev.yaml` 默认信任 dev 单机 nginx：`server.trusted_proxies: ["203.0.113.1"]`。
- 支持 `APP_SERVER_TRUSTED_PROXIES` 逗号分隔 env 覆盖。
- dev systemd unit 默认将 API/Admin 监听收紧到 `203.0.113.1`，避免外部绕过 nginx 直连服务。
- `.env.example` 和 `infra/deploy/README.md` 补充运行时配置说明。

## Validation

```bash
go test ./internal/config ./internal/infra/payment/shark ./internal/service/wallet
python3 scripts/validate-runtime-environment.py
python3 scripts/validate-prd.py
python3 scripts/validate-engineering-standards.py
python3 scripts/validate-capability-gates.py
python3 scripts/validate-completion-claims.py
```

All passed.
