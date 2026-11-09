---
id: "doc-8e9565e4d67b"
title: "【补静态资源】PP static 巴西/香港 GCS 双区 + 香港 S3 同步记录"
date: "2026-09-08T18:35:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "CDN", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-08-1835-%E3%80%90%E8%A1%A5%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E3%80%91PP%E5%B7%B4%E8%A5%BF%E9%A6%99%E6%B8%AFGCS%E5%8F%8C%E5%8C%BA%E4%B8%8ES3%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-08-1835-【补静态资源】PP巴西香港GCS双区与S3同步记录.md"
sourceSha256: "3e836cd70d922e61d7a52e3ada29ec7195fde0744265fa06b98db676c7b4ea14"
sourceSystem: "project-doc"
---

# 【补静态资源】PP static 巴西/香港 GCS 双区 + 香港 S3 同步记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609081835-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BCDN-%E3%80%90%E8%A1%A5%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E3%80%91PP%20static%20%E5%B7%B4%E8%A5%BF-%E9%A6%99%E6%B8%AF%20GCS%20%E5%8F%8C%E5%8C%BA%20%2B%20%E9%A6%99%E6%B8%AF%20S3%20%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-08 18:35｜日期依据：文件名日期

时间：2026-09-08 18:35（Asia/Manila）
项目：某业务公司 / PGServer master（巴西 GCS + 香港/东京 asia + 香港 S3/CloudFront）
结果：✅ ppstatic 3012 文件 / 2.47GB 双区三路 + 香港 S3 同步完成并公网验证

## 一、任务与来源

```text
用户要求：巴西和香港都更新静态资源文件。
Ben(C++)：静态资源已推到 client.git master：
  e8556a76（17:26 ppstatic，3012 文件）
  c0c5887c2（17:20 vendor_astatic3，1 文件）
提示涉及目录：ppstatic + vendor_astatic(0-5)。
```

## 二、范围核验

```text
client.git 基线 last-synced b7d5a20d → 新 HEAD e8556a76。
实际差异：
  ppstatic +3012 文件（vs10crownfire / vs10santasl 等新 PP 游戏包，约 2.47GB）；
  vendor_astatic3 +1 文件（cai/assets/game/index.73b5e.js）；
  vendor_astatic/1/2 无差异。

vendor_astatic3/4/5（git 中约 49,158 文件）当前没有线上桶、域名、游戏分组配置：
  GCS 仅 bizops-gcs-vendor_a-statics/1/2(+sa)，无 vendor_a-statics3-5；
  平台配置 vendor_a.json 仅 v1/v2 两组；香港 S3 同步映射同样只到 2。
  因此本次不创建新桶/新域名，未把 3-5 纳入同步（待确认是否上线新 vendor_a 包）。
```

## 三、执行

### 1. GCS 三路上传（pp-static）

```text
官方 git_static_gcs_sync.py 触发增量同步时，git archive 走 blobless 大包
拉取在约 16MB 处持续卡死（多次复现）；且 30 分钟 cron 自动全量巡检会并发。
已暂停 cron 并清场，改为逐 blob 物化后 gcloud rsync：
  3012 文件 / 2,466,810,048 bytes，18s 零失败。
目标：
  巴西 LIVE    bizops-gcs-pp-static-sa      （71.4 MiB/s）
  香港/东京 asia bizops-gcs-pp-static        （23.2 MiB/s）
  backup       bizops-game-statics-gcs/pp-static（23.5 MiB/s）
  合计 3012×3 = 9036 个对象全部完成。
```

### 2. CDN 预热

```text
按 20-zone 全池预热 HTML/JS/CSS/JSON（单 zone 上限 120 URL）：
  20/20 zone，每 zone 120/120 verified cf-cache-status=HIT。
```

### 3. 香港 S3 + CloudFront（hkcloudplay）

```text
香港机执行 sync-gcs-to-s3 pp-static（GCS asia → S3 bizops-h5-hk-517506432530）：
  source_count=28897 / destination_count=28897
  bytes=20,940,357,623 两边一致，sync_complete。
```

## 四、验证

```text
PP 新游戏样例 vs10crownfire/desktop/bootstrap.js：
  -sa 直连 200 / asia 直连 200 / backup 200
  pp-static.cdn-tokyo-bizops.icu 200（当前配置活跃域）
  pp-static.hkcloudplay01-05.com 5/5 200

遗留说明：预探测时在 pp-static.xqv9m8.icu 留下 1 条旧 404 缓存
（cf-cache-status=HIT，当前无 cache-purge 权限 token）；该 zone 不在当前
platform-api 活跃 static_hosts（pp.json 为 cdn-tokyo-bizops），不影响主链路，
后续取得 purge 权限后可定点清除。
```

## 五、收尾

```text
- last-synced-master.sha 已更新为 e8556a76，30 分钟 cron 已恢复；
  下次 cron 会直接判定无变化，不再触发全量巡检。
- 临时目录 /tmp/pp-changed 与测试脚本已清理。
- 本任务无业务代码改动；事件文档与工作台状态本地提交。
```

## 六、已知问题与建议（跟办）

```text
1. git_static_gcs_sync.py 的 git archive 对大批量 blobless 拉取会卡死，
   本次用逐 blob 物化绕过；建议后续给工具增加分块/逐 blob 物化与并发锁。
2. 30 分钟 cron 在“有变更”时会顺带对全部未变更厂家做全量 bucket 审计，
   耗时很长且与手动任务并发无锁；建议改为仅处理变更前缀并加锁。
3. vendor_astatic3-5 是否正式上线需用户确认（建桶/域名/游戏分组/同步映射）。
4. 本机 /root/bizops-cf-workers.env 的 token 验证已失效（Authentication error），
   建议轮换或补回具备 Cache Purge 的 token。
```

## 七、群通知回执

```text
5249 前置与范围确认
5250 开始执行（ppstatic 三路）
5251 并发收敛与修正
5252 GCS 文件就绪、上传开始
5255 上传路径修正
5260 GCS 三路完成、开始预热
5263 香港 S3 同步开始
5266 汇总与文档
5267 本地提交结果
```
