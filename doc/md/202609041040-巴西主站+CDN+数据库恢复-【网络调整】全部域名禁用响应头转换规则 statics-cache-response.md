---
id: "doc-d882fa937981"
title: "【网络调整】全部域名禁用响应头转换规则 statics-cache-response"
date: "2026-09-04T10:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "CDN", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-04-1040-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E5%85%A8%E9%83%A8%E5%9F%9F%E5%90%8D%E7%A6%81%E7%94%A8statics-cache-response%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-04-1040-【网络调整】全部域名禁用statics-cache-response记录.md"
sourceSha256: "2f2d5ad1a8c951eae3cdafa6c1b2a24875ea5f8a9fc52676fe658a30a03ae66f"
sourceSystem: "project-doc"
---

# 【网络调整】全部域名禁用响应头转换规则 statics-cache-response

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-04-1040-【网络调整】全部域名禁用statics-cache-response记录.md`

> 整理日期：2026-09-04 10:40｜日期依据：文件名日期

时间：2026-09-04 10:40（Asia/Manila）
项目：某业务公司 / PGServer master（Cloudflare 响应头转换）
状态：✅ 22/22 禁用完成

## 一、需求

```text
参考 q7m9v8.icu：响应标头转换规则 statics-cache-response
（Cache-Control public,max-age=604800）在全部域名都禁用。
```

## 二、操作

```text
1) 全量扫描：22 个域名含该规则（17 启用 + 5 已禁用）；
2) 操作前全量备份：每域名 response_headers / cache_settings /
   worker_routes（66 JSON）-> /root/bizops-cf-backups/
   20260904-statscache-disable-before/（tar 已发群 5137）；
3) 逐个域名 PUT entrypoint：statics-cache-response enabled=false
   （其它规则保持原样；已禁用域名复核 enabled=false）；
4) 逐域复核 22/22 disabled，0 失败。
```

## 三、域名清单

```text
6qv8m/6xv8q/7m9v8/7v8k3/8m7xv/cdn-manila-bizops.cyou/.icu/
cdn-tokyo-bizops.cyou/.icu/m6xv8q/m7v8k3/p8m7xv/q7m9v8/qv9m8/
t6qv8m/vendor_a-cdn-2026/vendor_a-cdn-game/vendor_a-cf-2026/vendor_a-cf-game/
vendor_a-host-2026/vendor_a-host-game/xqv9m8
```

## 四、恢复

```text
备份 JSON 中 rules[].enabled=true 后 PUT 回 entrypoint 即可恢复。
```

## 五、飞机群通知 message_id

```text
5135 任务开始
5136/5137 备份说明 + 备份包
5138 22/22 禁用完成
```

## 六、本地提交

```text
（提交号文末回写；master 领先 origin/master，未 Push）
```
