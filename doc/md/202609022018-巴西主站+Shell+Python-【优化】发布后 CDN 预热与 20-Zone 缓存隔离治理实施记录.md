---
id: "doc-d4d2b3cb55c8"
title: "【优化】发布后 CDN 预热与 20-Zone 缓存隔离治理实施记录"
date: "2026-09-02T20:18:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "监控告警", "自动化", "CDN", "安全运维"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-02-2018-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E5%8F%91%E5%B8%83%E5%90%8ECDN%E9%A2%84%E7%83%AD%E4%B8%8E20Zone%E7%BC%93%E5%AD%98%E9%9A%94%E7%A6%BB%E6%B2%BB%E7%90%86%E5%AE%9E%E6%96%BD%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-02-2018-【优化】发布后CDN预热与20Zone缓存隔离治理实施记录.md"
sourceSha256: "f2b5b245ab56cbc613e9b8a27d48090d6c3c5b5f5dc27fe19e9f9b4517078145"
sourceSystem: "project-doc"
---

# 【优化】发布后 CDN 预热与 20-Zone 缓存隔离治理实施记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-02-2018-【优化】发布后CDN预热与20Zone缓存隔离治理实施记录.md`

> 整理日期：2026-09-02 20:18｜日期依据：文件名日期

时间：2026-09-02 20:18（Asia/Manila）
项目：DBQP / PGServer master（巴西生产静态链路）
状态：✅ 已实施并验证

## 一、背景与现象

用户反馈：每次发布代码后，游戏静态域名“最初几次点击”加载慢，需要多加载几次后
才能在无痕模式下秒开。

静态链路现状：

```text
浏览器 -> 静态域名 <prefix>.<zone>（每 prefix 20 个 zone）
       -> Cloudflare Worker summer-wave-c94f
       -> 同一 GCS -sa 桶（dbqp-gcs-<prefix>-sa）
```

`platform-api/conf/domains/*.json` 中每个厂家静态前缀的 `static_hosts` 均覆盖
同一 20 个 zone（7 个 domains 文件 union=20，一致）。

## 二、根因（实证 + 官方文档）

```text
1. CF Worker Cache API 按 zone 隔离：
   “Workers operating on behalf of different zones cannot affect each other's
   cache.”（Cloudflare 官方示例文档）。
   即 <prefix>.<zone1> 与 <prefix>.<zone2> 虽然回同一个桶，缓存却是各自独立；

2. 同一 HKG 边缘冷路径对照实验（2026-09-02 20:04-20:13）：
   - pg6-static.xqv9m8.icu/1834850/index.html 预热后 HIT；
   - pg6-static.p8m7xv.cyou 同路径、同 HKG 边缘仍是 DYNAMIC；
   - 改写 Cache API 键（桶+路径、忽略 hostname）后：
     B(zone2) 首访 DYNAMIC -> A(zone1) 同键仍 DYNAMIC -> B 二次 HIT，
     证明“不同 zone 各自缓存分区”，缓存键改写无法跨 zone 共享；

3. 历史全量预热工具 cdn_warm_static.py 只预热 3 个 Argo zone：
   - 即使 5 地区全量跑过，域名池仍有 17 个 zone 未预热；
   - 客户端每次可能随机/轮询使用任意 static_hosts -> “要点几次才秒开”。
```

结论：缓存键归一化思路对跨 zone 无效（已回滚），正确解法是**每次发布后对全部
20 个 zone 增量预热**。

## 三、实施内容

### 1. Worker 保持原版（不做缓存键归一化）

```text
曾尝试把 Worker Cache API 键改为 (bucket,path,query) 忽略 hostname，
实测确认 CF 按 zone 分区后无跨 zone 收益，且会造成原缓存键空间整体作废，
故完整还原线上 Worker：
  线上版本 sha256 fab1334dc40c8b695776041e0dfb70ce349aae9378180b6a336a6db1f86e2440
  备份 /root/dbqp-cf-backups/20260902-prewarm/summer-wave-c94f.before-20260902.js
  PUT 回滚时间 2026-09-02 20:16（modified 2026-09-02T12:16:24Z）
```

### 2. `git_static_gcs_sync.py` 增加 `--warm`（本次核心交付）

```text
行为（只增量、只预热代码/配置类文件）：
  1) 上传完成后，取本次 changed 文件里 .html/.htm/.js/.css/.json；
  2) 逐 20 zone 预热（CF 缓存按 zone 隔离，少一个 zone 少一块冷缓存）；
  3) 对 HTML 再发现同源 JS/CSS（每页最多 24 个）一并预热；
  4) 二次请求逐 zone 回验 cf-cache-status=HIT；
  5) 任一 zone 预热失败 -> 整体失败，不更新 last-synced marker，
     下一轮 cron 自动重试（重传为无操作 rsync，不会改内容）。
媒体/图片/音频等大文件不预热（首次真实游玩按需缓存），避免大流量。
每 zone 单次上限 120 个 URL（GIT2GCS_WARM_MAX_PER_ZONE 可调）。

20-zone 清单单一来源：platform-api/conf/domains/*.json 的 static_hosts union。
```

### 3. 宝塔 cron 接入（自动）

```text
原 crontab（*/30 分钟 git 直连同步）：
  python3 /root/git_static_gcs_sync.py
改为：
  python3 /root/git_static_gcs_sync.py --warm --warm-threads 12
同步脚本 /root 与 /opt/pgserver/docker/scripts 已更新（sha 与本地一致）。
```

### 4. `cdn_warm_static.py` 修正（手动全量预热）

```text
- --zones 默认从 3 个 Argo zone 改为 20-zone 全池；
- BUCKETS 补充 pg6-static/pg7-static（此前缺漏）；
- 文档注明缓存按 zone 隔离，全量预热必须传全 20 zone。
```

### 5. 发布文档补充

```text
docker/deploy/README.md 新增“发布后 CDN 预热”章节：
  - 静态代码发布自动预热（cron --warm）；
  - 容器/正式版本发布后手动全量预热命令：
    python3 docker/scripts/cdn_warm_static.py --assets
```

## 四、验证结果（20:13-20:17）

```text
宝塔 GRU 逐 zone 回验（第二次请求 cf-cache-status=HIT）：
  pg6-static：health.json + 1834850/index.html + 页面引用的 shared JS
              = 20/20 zone 全 HIT（每 zone 3/3）
  pg-static ：health.json + 85/c445ebb91e.cadb1.json
              = 20/20 zone 全 HIT（每 zone 2/2）

回归：
  静态 health.json：14 厂家 × 2 zone = 28/28，rcode=0
  动态 /health：api/pg-games/tada-games 等 5/5，rcode=0
  本地：python3 -m py_compile 通过；线上 Worker sha 与仓库一致。
```

## 五、使用说明（后续规则）

```text
1. 静态代码发布（client.git master -> GCS）：
   宝塔 cron 每 30 分钟自动同步并逐 20 zone 预热，无需手工操作；
   日志 /var/log/git_gcs_static_sync.log。
2. 容器/正式版本发布（deploy_all_servers.py）：
   不影响 GCS 静态内容时无需预热；若同一批有前端新包，发布后建议：
     python3 docker/scripts/cdn_warm_static.py --assets
   （默认 20 zone，全量常用入口+JS/CSS；按需 --limit/--threads 控制量级）
3. 香港 cn（S3/CloudFront）链路不经过该 CF Worker：
   由 cn 侧 CloudFront invalidation + 香港机预热流程覆盖（并行会话文档）。
4. 新增 zone / 前缀时：同步 domains 配置 + Worker BUCKET_MAP + 本工具
   WARM_ZONES（与 domains static_hosts union 保持一致）。
```

## 六、额度与风险

```text
- 预热按“变更文件 × 20 zone”计费，单次上限可控（每 zone 120 URL）；
- Worker Paid 含 1000 万请求/月，静态监控 ~105 万/月；单次发布增量预热通常
  数千请求量级，安全余量充足；
- 避免与“5 地区全量预热 + 浏览器全量巡检”同时执行（09-01 1027 教训）。
```

## 七、飞机群通知 message_id

```text
4883 任务开始（前置核验）
4884 2/7 现象与链路分析（缓存隔离实证）
4885 3/7 方案设计
4886 4/7 实施开始
4887 4/7 方案修正（缓存键归一化无效 -> 逐 20 zone 预热）
4888 4/7 实施完成
4889 5/7 验证通过
4890 6/7 文档完成
4891 汇总 + 事件文档附件（主体提交前）
4892 7/7 提交结果（master 2d1d2e3d / cn b1d62af5，均未 Push）
```

## 八、本地提交

```text
master：2d1d2e3d ops: per-zone incremental CDN prewarm after static release
cn：b1d62af5 docs: cross-link master 2026-09-02 per-zone CDN prewarm event
（均未 Push；master 领先 origin/master 18，cn 领先 origin/cn 32）
```
