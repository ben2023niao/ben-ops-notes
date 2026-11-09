---
id: "doc-11715facb1bf"
title: "【网络调整】全部域名启用 statics-cache-response（operation=set）"
date: "2026-09-04T11:15:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "CDN", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-04-1115-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E5%85%A8%E9%83%A8%E5%9F%9F%E5%90%8D%E5%90%AF%E7%94%A8statics-cache-response%E5%B9%B6%E6%94%B9%E4%B8%BAset%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-04-1115-【网络调整】全部域名启用statics-cache-response并改为set记录.md"
sourceSha256: "097db46c0aba9506ce213f713e180befe852f45243e830cf72766fc449699aef"
sourceSystem: "project-doc"
---

# 【网络调整】全部域名启用 statics-cache-response（operation=set）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-04-1115-【网络调整】全部域名启用statics-cache-response并改为set记录.md`

> 整理日期：2026-09-04 11:15｜日期依据：文件名日期

时间：2026-09-04 11:15（Asia/Manila）
项目：某业务公司 / PGServer master（CF 响应头转换）
状态：✅ 22/22 启用并改为 set，响应头单一 604800

## 一、需求

```text
Worker 代码已访问策略验证浏览器端 Cache-Control 设置：
  // if (response.status === 200) {
  //   newResponse.headers.set('Cache-Control', 'public, max-age=604800, immutable');
  // }
因此把全部域名的 statics-cache-response 重新启用，由 CF 响应头规则补
Cache-Control: public, max-age=604800。
```

## 二、执行

```text
1) 备份（禁用态）：/root/bizops-cf-backups/20260904-statscache-enable-before/
   （22 JSON，tar 已发群 5150）；
2) 22 个域名规则 enabled=true；
3) 实测发现 add 会同时保留源站头导致双 Cache-Control
   （14400 + 604800）-> 全部改为 operation=set（覆盖源站头）；
4) 复核 22/22 enabled & set。
```

## 三、验证

```text
pg-static.{vendor_a-cdn-2026,xqv9m8,q7m9v8}.icu/126/index.html：
HTTP 200 + cf-cache-status HIT + 唯一 Cache-Control: public, max-age=604800
```

## 四、飞机群通知 message_id

```text
5149 任务开始
5150 启用前备份
5151 双头问题说明（add->set）
（最终汇总/提交结果见文末回写）
```

## 五、本地提交

```text
（提交号文末回写；master 领先 origin/master，未 Push）
```
