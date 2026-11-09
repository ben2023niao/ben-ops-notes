---
id: "doc-7195f2ff0d5b"
title: "【网络调整+发布】xqv9m8 CDN 模板同步全域名 + 三 Pro/Argo 域 platform-api 配置记录"
date: "2026-09-03T03:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "自动化", "CDN", "DNS", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-03-0300-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%2B%E5%8F%91%E5%B8%83%E3%80%91xqv9m8%20CDN%E6%A8%A1%E6%9D%BF%E5%90%8C%E6%AD%A5%E4%B8%8E%E4%B8%89Pro%E5%9F%9Fplatform-api%E9%85%8D%E7%BD%AE%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-03-0300-【网络调整+发布】xqv9m8 CDN模板同步与三Pro域platform-api配置记录.md"
sourceSha256: "4efc74e859f6adcd1551174136e3f04257b5e11b10c20246f4cd3534cd525ef5"
sourceSystem: "project-doc"
---

# 【网络调整+发布】xqv9m8 CDN 模板同步全域名 + 三 Pro/Argo 域 platform-api 配置记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-03-0300-【网络调整+发布】xqv9m8 CDN模板同步与三Pro域platform-api配置记录.md`

> 整理日期：2026-09-03 03:00｜日期依据：文件名日期

时间：2026-09-03（Asia/Manila，本记录 03:00 建档）
项目：某业务公司 / PGServer master（CF CDN + platform-api 域名配置）
状态：✅ CDN 同步完成并验证；platform-api 三域发布完成并验证；文档收尾中

## 一、背景与目标

```text
Ben 运维确认 xqv9m8.icu 是手动调试好的“效果最好”域名，要求：
1) 备份 xqv9m8 全部 CDN 配置（完整备份已发群）；
2) 以 xqv9m8 为模板，把 Worker 路由 + 缓存同步到全部域名；
3) 发布前把另外 2 个开了 Argo 的域名也配置进 platform-api；
Ben(C++) 补充：最终 3 个 Pro 域名全部加入 platform-api
（xqv9m8 / cdn-tokyo-bizops / vendor_a-cdn-2026），share.so 发布版本一并纳入本地。
上线窗口：凌晨 5 点商户上线前完成。
```

## 二、xqv9m8 模板备份（已完成并发群）

```text
完整备份：宝塔 /root/bizops-cf-backups/20260903-xqv9m8-template/（15 个 JSON）
  - Workers 路由 4 条：*-static / vendor_a-statics / vendor_a-statics1 / vendor_a-statics2
    -> summer-wave-c94f
  - Cache Rules：statics（cache=true, edge TTL 604800 override_origin）
  - 响应头改写：statics-cache-response
    （静态响应加 Cache-Control: public, max-age=604800）
  - Tiered Cache Smart=ON；Argo smart_routing=ON
  - Settings：Polish=lossy / WebP=ON / Brotli=ON / Early Hints=ON
  - DNS 26 条（静态 CNAME 13）
群发：5037（说明）+ 5038（tar.gz 完整备份）
```

## 三、全域名模板同步（Worker 路由 + 缓存）

```text
盘点（22 个静态 zone）：
- Worker 路由：全 zone 已有模板 4 条（cdn-tokyo 多 1 条冗余 *-statics1，无害）✅
- Cache Rules statics：22 zone 全部一致 ✅
- 响应头缓存规则 statics-cache-response：仅 xqv9m8 / 6qv8m 有；
  其余 20 个 zone 缺失 -> 本次补齐
执行：逐 zone PUT http_response_headers_transform entrypoint（规则 = xqv9m8 模板，
仅替换 zone 后缀），before 快照 /root/bizops-cf-backups/20260903-cdn-sync-before/
结果：20/20 成功（0 失败）
验证：抽检 6 域 HTTP 200 + Cache-Control: public,max-age=604800 ✅
```

## 四、platform-api 三 Pro/Argo 域配置与发布

```text
配置：platform-api/conf/domains 7 份 JSON
（pg/vendor_a/pp/popok/vendor_c/vendor_d/g759）
由 xqv9m8 单域扩展为 3 域：
  xqv9m8.icu（原） + cdn-tokyo-bizops.icu + vendor_a-cdn-2026.icu
规则：static/game/api 均按“同前缀派生”；无单列表重复；校验 7/7 PASS。
发布：3 台后端（192.0.2.1/.4/.11）platform-api 容器
  docker cp 7 份 + docker restart（JSON_VALID 后才重启）
备份：宝塔 /root/bizops-platform-config-backup-20260903c/domains-01/02/03
  （各 10 文件，回滚可用）
验证：
  3 容器 api_hosts 均为 3 域 ✅
  公网 health 6/6 rcode=0（api/pg-games/vendor_a-games/g759-games × 2 新域）✅
  pg-static 两新域 126/index.html 200 ✅
```

## 五、share.so 发布版本（并入本地）

```text
Ben(C++) 推送 share.so（区域限制提示去掉中文）：
origin 36edf969 -> 本地 merge 71df1c2f，随本次提交一并带出（二进制不进后续提交正文）。
```

## 六、飞机群通知 message_id

```text
5032 任务开始
5033 计划更新（3 Pro 域名 + share.so 并入）
5034/5035 模板备份说明 + 摘要附件
5036 CDN 20 zone 响应头规则同步完成
5037/5038 xqv9m8 完整备份（tar.gz）发群
5039 platform-api 发布开始
5040 platform-api 发布成功
5041 汇总通知
5042 事件文档附件
（提交结果见文末回写）
```

## 七、本地提交

```text
master：075250b6 ops: platform-api domains 3 Argo/Pro zones
        (xqv9m8/cdn-tokyo-bizops/vendor_a-cdn-2026) + CDN template sync docs
cn：b351a7a7 docs: cross-link master xqv9m8 CDN template sync
master 已含 share.so merge（71df1c2f）；均未 Push
```
