---
id: "doc-e0151c18c7d4"
title: "【运维记录】CF CDN 费用每日定时统计与群日报上线"
date: "2026-09-03T22:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "CDN", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-03-2200-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91CF%E8%B4%B9%E7%94%A8%E6%AF%8F%E6%97%A5%E5%AE%9A%E6%97%B6%E7%BB%9F%E8%AE%A1%E4%B8%8A%E7%BA%BF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-03-2200-【运维记录】CF费用每日定时统计上线记录.md"
sourceSha256: "dba7cc002720e5d06639b5afb9e95c4b8e3de84767d347030fc3da83d6b70b07"
sourceSystem: "project-doc"
---

# 【运维记录】CF CDN 费用每日定时统计与群日报上线

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609032200-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BPython-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91CF%20CDN%20%E8%B4%B9%E7%94%A8%E6%AF%8F%E6%97%A5%E5%AE%9A%E6%97%B6%E7%BB%9F%E8%AE%A1%E4%B8%8E%E7%BE%A4%E6%97%A5%E6%8A%A5%E4%B8%8A%E7%BA%BF.md)

> 整理日期：2026-09-03 22:00｜日期依据：文件名日期

时间：2026-09-03 22:00-22:15（Asia/Manila）
项目：某业务公司 / PGServer master（宝塔定时任务）
状态：✅ 已上线（cron 每天 08:30 自动跑 + 发群）

## 一、需求

```text
每天定时统计 CF CDN 费用，用“人话、简单易懂”的汇总发飞机群。
```

## 二、实现

```text
新增脚本：
  docker/scripts/cf_billing_daily_summary.py  每日汇总 + 发群（大白话日报）
  （复用 docker/scripts/cf_billing_report.py 生成 billing.json）
宝塔部署：
  /opt/bizops-scripts/cf_billing_daily_summary.py
  /opt/bizops-scripts/cf_billing_report.py
cron（root，Asia/Manila）：
  日报：30 8 * * *   python3 /opt/bizops-scripts/cf_billing_daily_summary.py \
    --frequency daily --state-file /var/tmp/bizops-cf-billing-last.json \
    >> /var/log/cf_billing_daily.log 2>&1
  周报：35 8 * * 1   python3 ... --frequency weekly \
    --state-file /var/tmp/bizops-cf-billing-last-week.json >> /var/log/cf_billing_weekly.log 2>&1
  月报：40 8 1 * *   python3 ... --frequency monthly \
    --state-file /var/tmp/bizops-cf-billing-last-month.json >> /var/log/cf_billing_monthly.log 2>&1
发送：读 /opt/benbot-runtime.env（TG_BOT_TOKEN / BEN_BOT_MONITOR_CHAT_ID）
对比：/var/tmp/bizops-cf-billing-last.json 记录上次总额，日报输出“与上次一致/变化”。
三档折算：按订阅计费周期（2026-08-29 ~ 09-29，30 天）折算，
  每天≈4.67｜每周≈32.67｜每月 140 USD（月报含“本周期已过天数按比例费用”参考值）。
```

## 三、日报内容（人话版）

```text
📊【CF CDN 账单日报/周报/月报】
固定订阅：140.00 USD/月
计费周期：2026-08-29 ~ 2026-09-29（30 天）
折算费用：每天≈4.67 ｜ 每周≈32.67 ｜ 每月=140.00 USD
对比：与上次一致（无变化）
付费域名 5 个：cdn-tokyo-bizops 30 / vendor_a-cdn-2026 30 / xqv9m8 30 /
              q7m9v8 25 / t6qv8m 25
免费域名 37 个
备注：t6qv8m 已下架仍计费建议退订；Workers Paid 5 账户级另计；
     按域名流量拆分需 Analytics 权限 token。
```

## 四、验证

```text
1) python3 -m py_compile 通过；
2) --dry-run 预览正确；
3) 宝塔正式运行 SEND_OK（当天日报已发群）；
4) crontab -l 已确认每天 08:30 记录存在。
```

## 五、飞机群通知 message_id

```text
5078 任务开始（v1）
5091 三档升级任务开始
（升级版日报正式发送 SEND_OK；周报/月报由 cron 定时自动发；
 文档/提交结果见文末回写）
```

## 六、本地提交

```text
master：1fe99737 ops: daily CF billing summary cron script + group report + docs
cn：39765c97 docs: cross-link master daily CF billing summary cron
（均未 Push）
```
