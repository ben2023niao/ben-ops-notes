---
id: "doc-0c4346de2125"
title: "【发布】platform-api 无感更新（e8dfb381）并恢复单机 01"
date: "2026-09-05T16:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Nginx", "自动化", "CDN", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-05-1620-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91platform-api%E6%97%A0%E6%84%9F%E6%9B%B4%E6%96%B0%E4%B8%8E%E5%8D%95%E6%9C%BA%E6%81%A2%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-05-1620-【发布】platform-api无感更新与单机恢复记录.md"
sourceSha256: "431414297e32e44f71320f061e57b6ad1e7592720e84186b765342b2553ddf9b"
sourceSystem: "project-doc"
---

# 【发布】platform-api 无感更新（e8dfb381）并恢复单机 01

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-05-1620-【发布】platform-api无感更新与单机恢复记录.md`

> 整理日期：2026-09-05 16:20｜日期依据：文件名日期

时间：2026-09-05 16:20（Asia/Manila）
项目：某业务公司 / PGServer master（platform-api）
状态：✅ 完成（滚动无感更新，已回切单机 01）

## 一、内容

```text
origin e8dfb381「修复 api 接口问题」：platform-api/agent_apis.py +9 行。
```

## 二、无感更新流程

```text
1) 02/03 仓库同步 e8dfb381 + 单域配置，构建 platform-api（master-e8dfb381）；
2) nginx socket_backend 接入 02/03（三台上游，与 01 并行承接）；
3) 01 platform-api 构建更新（02/03 兜底，用户无感）；
4) 完成后回切单机：02/03 platform-api stop，nginx socket_backend 仅 01
   （还原 bak-20260905-pg-rolling）。
```

## 三、验证

```text
1) 3 台 agent_apis.py md5 均 4fbfaa67920ee18a7b285dd41669a028（与本地一致）；
2) 回切后 bizops-platform-api-release-01 Up，api.cdn-tokyo-bizops /health 200。
```

## 四、飞机群通知 message_id

```text
5215 任务开始/02-03 同步
5220 01 更新
（完成/提交见文末回写）
```

## 五、本地提交

```text
（提交号文末回写；本地含 merge 48caff3d，未 Push）
```
