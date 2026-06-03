---
id: "doc-b523ca1035de"
title: "Mock Server Contract Rules"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/api/mock-server-contract.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/api/mock-server-contract.md"
sourceSha256: "5d296458d1395b5e49702aed80c13adc204264053908529d1e910694a5dcc38f"
sourceSystem: "project-doc"
---

# Mock Server Contract Rules

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/api/mock-server-contract.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

Mock server 必须由 OpenAPI 契约生成或校验，不能由前端随手写静态假数据冒充。

## 1. Mockable Operation Requirements

每个 OpenAPI operation 必须具备：

1. `operationId`，用于生成客户端、mock handler 和测试名称。
2. `x-prd-id`，追踪到 `docs/prd/requirements.md`；健康检查等非业务接口可写 `x-prd-not-applicable: true`。
3. `responses`，至少定义一个成功或错误响应。
4. `requestBody` 或 parameters 的 schema 引用必须能被 recursive `$ref` 校验解析。
5. 错误响应必须使用项目错误码契约或明确说明。

## 2. Contract Test Requirements

mock server contract test 至少验证：

1. mock handler 覆盖所有 operationId。
2. mock response 能通过对应 OpenAPI schema。
3. 前端 fixture 不能包含 OpenAPI 不存在的字段。
4. 后端接口返回不能少于 OpenAPI required 字段。

## 3. Completion Rule

如果项目还没有接入 mock server，Agent 日志必须写明：

```text
mock server 状态：未接入
原因：
补齐计划：
```

不能把静态 fixture、前端本地数组或 501 handler 说成 mock server contract test。
