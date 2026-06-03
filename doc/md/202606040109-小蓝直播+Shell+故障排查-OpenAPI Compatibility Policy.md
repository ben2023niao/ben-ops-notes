---
id: "doc-7f75e332fe76"
title: "OpenAPI Compatibility Policy"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/api/openapi-compatibility.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/api/openapi-compatibility.md"
sourceSha256: "b4ed67baf7724a4a6f241343e9a3733b5e6849a7727aff2a01a11cb232d7822b"
sourceSystem: "project-doc"
---

# OpenAPI Compatibility Policy

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/api/openapi-compatibility.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

OpenAPI 是前端、后端、测试和 Agent 的契约源头。

## 1. Breaking Change Definition

以下变化默认视为 breaking change：

1. 删除 path。
2. 删除 HTTP method。
3. 删除 response status code。
4. 删除 schema。
5. 给已有 schema 增加新的 required 字段。
6. 修改鉴权、幂等、分页、错误码语义但没有 ADR。

## 2. Baseline Check

项目可通过以下任一方式启用 breaking change 检查：

```bash
OPENAPI_BASELINE=packages/contracts/openapi/baseline.yaml npm run check:openapi
```

或在默认路径放置：

```text
packages/contracts/openapi/baseline.yaml
```

没有 baseline 时，校验器会明确输出兼容性 diff 已跳过，不能把它说成“已完成 breaking change 检查”。

## 3. Change Rules

1. 非 breaking change 可以直接进入当前版本契约。
2. breaking change 必须写 ADR，说明迁移窗口、客户端兼容、灰度和回滚。
3. 删除接口前必须有 deprecated 版本或兼容期说明。
4. 请求字段改动必须同步 mock server、测试用例和生成类型。
