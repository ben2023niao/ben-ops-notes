---
id: "doc-6af963293543"
title: "【运维记录】CF 分域名费用查询脚本与账单报告"
date: "2026-09-03T21:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "CDN", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-03-2150-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91CF%E5%88%86%E5%9F%9F%E5%90%8D%E8%B4%B9%E7%94%A8%E6%9F%A5%E8%AF%A2%E8%84%9A%E6%9C%AC%E4%B8%8E%E8%B4%A6%E5%8D%95%E6%8A%A5%E5%91%8A.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-03-2150-【运维记录】CF分域名费用查询脚本与账单报告.md"
sourceSha256: "b6c30bfefc81266ca6a27516535c7becd6afd03ad1b6763f2aa855f20581a608"
sourceSystem: "project-doc"
---

# 【运维记录】CF 分域名费用查询脚本与账单报告

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-03-2150-【运维记录】CF分域名费用查询脚本与账单报告.md`

> 整理日期：2026-09-03 21:50｜日期依据：文件名日期

时间：2026-09-03 21:50（Asia/Manila）
项目：某业务公司 / PGServer master（Cloudflare 账户账单统计）
状态：✅ 脚本完成并实跑出报告；已发群；本地提交

## 一、需求

```text
写脚本查询 Cloudflare CDN 详细费用、各域名费用，方便统计账单。
```

## 二、实现

```text
脚本：docker/scripts/cf_billing_report.py
数据源：Cloudflare REST API（token 从 /root/bizops-cf-workers.env 读取，不回显）
  - GET /zones?per_page=50（全部 42 域名）
  - GET /zones/{id}/subscriptions（每域名真实订阅：Pro/Argo 等价格与周期）
  - GET /zones/{id}/argo/smart_routing + tiered_cache（开关标注）
  - GET /accounts/{id}/subscriptions（账户级订阅，如 Workers Paid）
  - GraphQL analytics 探测（当前 token 无 zone analytics 权限 -> 注明）
输出：billing.json / billing.csv / billing.md；支持 --skip-features /
--probe-analytics / --workers 并发等参数。
```

## 三、账单结果（2026-09-03 实跑）

```text
42 个域名合计 140 USD/月（付费 5 个）：
  xqv9m8.icu            Pro 25 + Argo 5 = 30（Argo/Tiered on）
  cdn-tokyo-bizops.icu    Pro 25 + Argo 5 = 30（Argo/Tiered on）
  vendor_a-cdn-2026.icu     Pro 25 + Argo 5 = 30（Argo on，Tiered off）
  q7m9v8.icu            Pro 25（无 Argo）
  t6qv8m.icu            Pro 25（无 Argo；已下架，建议确认是否退订）
其余 37 个 Free = 0
注意：
  1) Workers Paid $5/月为账户级另计（当前订阅接口未见，需面板核对）；
  2) 按域名请求量/带宽统计需要带 zone analytics read 的 token；
  3) t6qv8m.icu 已下线仍计费 25 USD/月，建议关闭/退订省钱。
```

## 四、验证

```text
1) python3 -m py_compile 通过；
2) 实跑 42 zone 全部返回订阅（0 失败）；
3) 金额交叉验证：5×Pro(25) + 3×Argo(5) = 140 USD/月 ✅
4) GraphQL 探测明确返回无 analytics 权限（如实标注）。
```

## 五、飞机群通知 message_id

```text
5063 任务开始 + API 探测结论
5067 费用汇总
5068 billing.md 附件
5069 billing.csv 附件
5070 事件文档附件
（提交结果见文末回写）
```

## 六、本地提交

```text
master：ae66e58a ops: CF per-zone billing report script (42 zones, 140 USD/mo) + docs
cn：dde78916 docs: cross-link master CF per-zone billing report script
（均未 Push）
```
