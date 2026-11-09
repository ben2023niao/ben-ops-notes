---
id: "doc-4b99d67847f9"
title: "【代码整理】Cloudflare Worker summer-wave-c94f 历史版本整理记录"
date: "2026-09-03T02:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "CDN"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-03-0220-%E3%80%90%E4%BB%A3%E7%A0%81%E6%95%B4%E7%90%86%E3%80%91summer-wave-c94f-Worker%E5%8E%86%E5%8F%B2%E7%89%88%E6%9C%AC%E6%95%B4%E7%90%86%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-03-0220-【代码整理】summer-wave-c94f-Worker历史版本整理记录.md"
sourceSha256: "66d604b0e4fd26a635ecc7a9df623d1b002956e04c785fb7519e85799ed87e3f"
sourceSystem: "project-doc"
---

# 【代码整理】Cloudflare Worker summer-wave-c94f 历史版本整理记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-03-0220-【代码整理】summer-wave-c94f-Worker历史版本整理记录.md`

> 整理日期：2026-09-03 02:20｜日期依据：文件名日期

时间：2026-09-03 02:20-02:30（Asia/Manila）
项目：某业务公司 / PGServer master（静态 CDN 链路 Worker）
状态：✅ 整理完成并已发群 + 本地提交；⚠️ 附发现“线上 v16 ≠ 仓库 V4”，
待用户确认是否回滚

## 一、背景

```text
Ben(C++) 问：这个 worker 原本是什么功能？最早用它干嘛？代码被改后没有原版了，
让 AI 查“改之前是什么代码”。
运维侧也不熟悉该 Worker -> 本次把 git 历史 + 历史文档中的各版本代码全部整理，
补齐详细中文注释后发群。
```

## 二、答案（Worker 原本用途）

```text
summer-wave-c94f = “静态子域 → GCS 桶直出”的边缘代理 Worker：
静态域名（pg-static.xxx / vendor_a-statics.xxx 等）经 CF 黄云进入 Worker，
Worker 改写 Host 为对应 GCS 桶域名后直出，替代宝塔 nginx 中转；
api/*-games 等动态域名不在映射表，原样 passthrough，不受影响。
最早形态：2026-08-31 07:00 评估文档里的草案 static-gcs-proxy（V0）。
```

## 三、整理产物

```text
主文件：docker/scripts/summer-wave-c94f-历史版本整理-带中文注释.md
  V0 草案（未部署） -> V1 ff6bd7ed（passthrough+CORS）
  -> V2 b909d84b（Cache API 7 天） -> V3 9d073d1a（health.json 版本盐 v3）
  -> V4 96088c04（pg6/pg7，仓库当前正式版）
  每个版本均有完整代码 + 逐段详细中文注释/演进说明
快照：docker/scripts/summer-wave-static-proxy.v16-dashboard-20260903.js
  （线上 v16 原样快照，用于对比与将来回滚参考）
```

## 四、验证结果

```text
1) 文档内 V1/V4 代码块与 git 历史/仓库源逐字节一致 ✅
2) V0/V1/V4 node --check 语法全部通过 ✅
3) 线上 Worker（GET API）与仓库 V4 比对：
   ❌ 不一致——线上 v16（今天面板 dash 上传 3 次，100% 生效）
   在 V4 基础上把缓存键归一化到 shared-static-pool.internal（去 hostname）。
4) 快照 v16 与线上内容一致（仅文件末尾换行差异）。
```

## 五、风险与待办

```text
1) 缓存键归一化=2026-09-02-2018 文档记录“无效已回滚”的实验，今天被面板重传；
2) 同 zone 多前缀对应多桶，归一化后键只剩路径，存在“不同桶同路径串内容”
   的缓存污染风险（含 health.json 串前缀）；
3) 已发群询问是否回滚为仓库 V4（一条 PUT 命令），未确认前不改线上；
4) 用户若确认回滚，需：PUT V4 -> 验证 242 静态域名字节/HIT -> 更新本文档。
```

## 六、飞机群通知 message_id

```text
5018 任务开始（1/6）
5019 整理完成 + 验证结果 + 线上 v16 差异发现（2/6）
5020 整理文档附件发群
5021 汇总通知
（提交结果见文末回写）
```

## 七、本地提交

```text
master：1a46d566 docs: organize CF Worker summer-wave-c94f history V0-V4
        with Chinese comments + snapshot live v16 drift
cn：4e57ddf9 docs: cross-link master CF Worker history organize
（均未 Push；master 领先 origin/master，cn 领先 origin/cn）
```
