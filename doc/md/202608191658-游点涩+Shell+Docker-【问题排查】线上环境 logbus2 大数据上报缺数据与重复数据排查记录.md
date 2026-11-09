---
id: "doc-d18de1ecddd2"
title: "【问题排查】线上环境 logbus2 大数据上报缺数据与重复数据排查记录"
date: "2026-08-19T16:58:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Redis", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-19-1658-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83logbus2%E5%A4%A7%E6%95%B0%E6%8D%AE%E4%B8%8A%E6%8A%A5%E7%BC%BA%E6%95%B0%E6%8D%AE%E4%B8%8E%E9%87%8D%E5%A4%8D%E6%95%B0%E6%8D%AE%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-19-1658-【问题排查】线上环境logbus2大数据上报缺数据与重复数据排查记录.md"
sourceSha256: "773a17af32faa56b68f2479d51e4bcc68733a8b2898e0657606e46d50756243e"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境 logbus2 大数据上报缺数据与重复数据排查记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608191658-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20logbus2%20%E5%A4%A7%E6%95%B0%E6%8D%AE%E4%B8%8A%E6%8A%A5%E7%BC%BA%E6%95%B0%E6%8D%AE%E4%B8%8E%E9%87%8D%E5%A4%8D%E6%95%B0%E6%8D%AE%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-19 16:58｜日期依据：文件名日期

文档日期：2026-08-19 16:58
环境：游点涩线上环境（main 分支）
分类：问题排查
标签：线上环境、后端、logbus2、大数据上报、te.log、缺数据、重复数据、去重

## 背景与目标

大数据团队反馈：每次线上发布版本后都会出现大量重复提交数据和缺数据。用户要求：

1. 排查 logbus2（ta-logbus-v2）线上日志上报问题；
2. 验证 08-18 te.log 是否存在订单号 `GAC202608181426341787034394178`；
3. 给出“防止发布后重跑产生重复数据”和“去重”的方案。

通知群：18game 数据系统优化（本次任务指定聊天ID）。

## 排查过程与证据

### 1. logbus2 容器与配置

```text
容器：logbus-v2，thinkingdata/ta-logbus-v2:latest，Up 5 天，restart=always
挂载：/opt/docker-youdianse-php/runtime -> /prod-data
      /data/logbus/conf -> /ta/logbus/conf
      /data/logbus/log  -> /ta/logbus/log
      /data/logbus/runtime -> /ta/logbus/runtime
配置 daemon.json：
  datasource: file，app_id=3fd59ce3c7744642a22d77d45260c619
  file_patterns: /prod-data/app-logs/te.log.*
  push_url: https://te-receiver.shushuda.com
状态：transporter.log 持续“messages sent”（1000 条/批次，network time 约 76-462ms），无 ERROR；
      offset.json 覆盖到 08-18 22:08 及更早文件。
结论：logbus2 本身运行正常、消费正常、上报正常。
```

### 2. 订单号验证（用户指定订单）

```text
订单：GAC202608181426341787034394178（08-18 14:26:34，cash_order_created，order_status=0，wechat）
te.log：全量扫描 08-13~08-19 所有 te.log* 文件，命中 0 次（不存在）
big_data_recharge-2026-08-18.log：存在，Job 完整成功（track + success 两条记录，无异常）
结论：订单数据已进入业务 Job 日志，但未进入 te.log，未上报到 TE —— 漏数据确认。
```

### 3. 08-18 充值类事件整体缺失

```text
big_data_recharge-2026-08-18.log：146 万行（约 73 万单充值 Job，均有 track+success，0 异常）
te.log.2026-08-18：cash_order 事件命中 0（抽样 14_1 / 14_2 / 23_16 均为 0）
同期注册类事件正常写入 te.log（14_1 含 platform_register_success 24.7 万条 + game_first_enter）
结论：08-18 充值类上报事件整体未进入 te.log。
```

### 4. SDK 与 logbus 链路实测（当前版本）

```text
用该订单同款 payload 在生产容器实测 TDFileConsumer + track + close：
  ops_verify_001 / ops_check：成功写入 te.log.2026-08-19-16_7，logbus 已消费
  ops_verify_002 / cash_order_created（原订单 payload）：成功写入 te.log.2026-08-19-16_8
结论：当前版本（f3f11681，08-19 14:23 部署）SDK 写入与 logbus 上报链路正常。
```

### 5. 历史代码差异（漏数据线索）

```text
08-13 部署的 45af8d1487af 版本 BigDataJobService.php：
  $config = env()->path('te_sdk')->toArray();   // te_sdk 配置缺失/为空时会抛 fatal
  php-error.log 记录：08-13 18:47-18:48 多次 “Call to a member function toArray() on null”
今日部署的 f3f11681 已移除该行（hotfix_0818）。
```

## 结论

```text
1. 订单 GAC202608181426341787034394178 未上报到 TE（缺数据），且 08-18 充值类事件整体缺失；
   根因方向：08-18 运行版本为 45af8d14，其 getTdAnalytics 存在 env() 配置读取隐患；
   另外 TDFileConsumer 内存缓冲 + strict=false 静默丢弃是系统性风险（详见方案）。
2. 当前版本 SDK 写入与 logbus2 上报链路正常（已实测），后续发布应持续验证。
3. 重复数据机制：
   - 上报无业务幂等键，支付/游戏回调重放、发布后重跑会重复触发同一订单事件；
   - TDAnalytics 未开启 #uuid，TE 侧无法按 UUID 去重；
   - 批量任务无断点游标，重跑整段重复。
```

## 防重与去重方案（建议落地）

### A. 源头幂等（推荐，治本）

```text
1. 事件唯一键：充值/消费用 order_id + order_status 组合；注册用 user_id + register_at；
2. 上报前 Redis/DB setNX 记录“order_id+status 已上报”，重复调用直接跳过；
3. 批量任务（AppLog / AccountDetail / Download 等）记录 last_id / 日期游标，断点续跑，
   不整段重扫；重跑时从游标继续。
```

### B. SDK 去重键

```text
1. new TDAnalytics($consumer, true) 开启 #uuid（SDK 自动为每条事件生成 UUID v4）；
   TE 平台侧开启按 UUID 去重（需与大数据/TA 确认其去重配置）。
2. 或业务侧在 properties 显式传 '#uuid'，值建议 md5(order_id + order_status)，
   同订单同状态重复上报时 UUID 相同，可被 TE 去重。
```

### C. 事件语义优化

```text
1. 状态变更类事件（cash_order_created -> cash_order_paid）用 track_update，
   #event_id=order_id，天然覆盖式更新，避免同一订单多状态重复计数；
2. 首事件（如首充）用 track_first，#first_check_id=order_id，天然幂等；
3. #time 必须保证非空合法：pay_time/created_at 为 0 时兜底用当前时间，避免 strict=false 静默丢弃。
```

### D. 漏数据加固

```text
1. 降低 TDFileConsumer bufferSize（默认 100 -> 1~10），减少容器重建时未落盘丢失；
   或每次 track 后统一 flush()/close()（当前各 Job 已 close，批量场景需确认）；
2. 发布前/后校验：发布完成后抽样 grep 最近 te.log 是否含新事件，确保链路贯通；
3. 建议在 TE 平台核对 08-18/19 数据，确认充值事件缺失范围，必要时补传（补传需配合去重键）。
```

## 后续验证建议

```text
1. 大数据/TA 侧确认 08-18 是否收到任何 cash_order 事件（验证“整体缺失”判断）；
2. 上线防重代码后，观察 TE 侧重复率；
3. 下一次发布时执行端到端验证：发布 -> 触发一笔测试充值 -> 确认 te.log + TE 平台收到且不重复。
```

## 通知记录

```text
步骤 1 仓库状态与文档/workbench 就绪   message_id 2802
步骤 2 logbus2 容器与配置核验          message_id 2803
步骤 3 订单号验证结果（te.log 不存在）  message_id 2808
步骤 4 SDK 与 logbus 链路验证           message_id 2809
步骤 5 重复/漏数据机制分析与防重方案    message_id 2810
最终总结                              见群内后续消息
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id（除用户指定通知群）、私钥、Git 凭据；不输出 .env 敏感值。
