---
id: "doc-aac30bae8abc"
title: "测试环境 Redis 巡检与优化建议"
date: "2026-08-25T15:50:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Redis", "监控告警", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-25-1550-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83Redis%E5%B7%A1%E6%A3%80%E4%B8%8E%E4%BC%98%E5%8C%96%E5%BB%BA%E8%AE%AE.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-25-1550-【运维记录】测试环境Redis巡检与优化建议.md"
sourceSha256: "a10fbc0a83f5b5a7e94a9605dbc93d8a91d1cd38e877fd2daba283b2af79d7fc"
sourceSystem: "project-doc"
---

# 测试环境 Redis 巡检与优化建议

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608251550-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20Redis%20%E5%B7%A1%E6%A3%80%E4%B8%8E%E4%BC%98%E5%8C%96%E5%BB%BA%E8%AE%AE.md)

> 整理日期：2026-08-25 15:50｜日期依据：文件名日期

环境标签：测试环境

时间：2026-08-25 15:50

## 背景

游戏侧反馈 Redis 出过问题，按要求对测试环境 Redis 进行全面巡检（实例配置、键空间、业务代码归因），给出隐患与优化建议。本需求按用户要求不通知飞机群。

## 实例现状

```text
地址：103.207.68.124:6379（应用 env [redis]/[cache]/[session.Redis]/[queue]）
版本：Redis 7.2.5 standalone（单机），运行 53 天
内存：used_memory 2.38M（峰值 32.8M），无大 key（最大 31.3KB prize_pool_marquee_queue）
键空间：db1=2186（2183 有过期）、db0(session)=7（全部无过期）、db3(cache)=40、db2(queue)=0
命中率：keyspace_hits 1,963,939 / misses 279,116（约 87.6%）
过期：expired_keys 267,094；evicted_keys 0
慢日志：仅 4 条且均为毫秒级（GET system_config 12~17ms、SCARD 10ms、INFO 14ms），无严重慢命令
```

## 业务代码归因（key 前缀 ↔ 代码）

```text
18game_token_user（1229，56%）        [敏感内容已脱敏] 天）
18game_tracking_page_visit（304）     TrackingService 页面访问 UV set（7 段 key）
18game_tracking（88）                 tracking 埋点相关 set
18game_report_dau（62）               ReportDauLogService，TTL=86400*31（31 天）
18game_growth（40）                   成长/VIP 相关缓存
18game_risk_reg_*（24）               风控注册设备/IP 计数
18game_msg_click_uv（11）/token_admin（11）/product_click（2）
18game_do_api_record_page_visit_raw_* PageVisitService 每分钟原始埋点缓冲 key
18game_quque                          QueueService::KEY（代码即 “quque” 拼写）
db0 的 mh_*/fa:*（ttl=-1）            疑似其它项目/应用残留键
```

## 隐患清单

```text
1. maxmemory=0 + maxmemory-policy=noeviction：
   无内存上限、写满后所有写操作直接 OOM 报错（游戏侧 Redis 出问题的常见根因之一）。
2. 单机无副本（connected_slaves=0）+ AOF 关闭：
   无高可用；宕机最多丢最近一次 RDB 快照后的写入（save 3600 1/300 100/60 10000）。
3. 多环境/多项目共用实例：
   db0 混有 mh_*/fa:* 等其它项目键（ttl=-1）；慢日志出现 103.207.68.155 等其它服务器客户端；
   一个项目打满内存/误删会影响所有共用方。
4. 配置类缓存 TTL 约 3 年（announcement_detail / sign_config / tracking_position_config）：
   依赖后端手动 cache()->delete 失效，漏删即长期脏数据（与 08-17 cdn_image 配置问题同源风险）。
5. 登录 token 30 天 TTL 且量大（token_user 1229 个）：
   [敏感内容已脱敏] 固定 3600*24*30；token 长期有效、键持续累积。
6. db0 session 键无过期（7 个 ttl=-1）：
   若为本应用 session 应带 lifetime（env session lifetime=3600）；疑似其它项目残留。
7. 孤儿/可疑键：
   do_api_record_page_visit_raw_*（每分钟原始埋点缓冲，未确认消费后清理）、
   quque 拼写不规范、无前缀 md5 键（18game_<md5>）若干。
8. 次要：mem_fragmentation_ratio 5.23（绝对值小，可观察）；timeout=0 连接永不超时（历史连接 89 万）。
```

## 优化建议（按优先级）

```text
1. 配置 maxmemory（建议 4G 起）与淘汰策略（volatile-lru 或 allkeys-lru），
   并加 used_memory > 80% 告警（含 maxmemory 触顶/OOM 拒绝次数监控）。
2. 开启 AOF everysec，或部署从库/托管 Redis；至少确保 RDB 定期备份可恢复。
3. 环境/项目隔离：清理 db0 异类无过期键；按环境拆分实例或独立 db+前缀。
4. 配置缓存 TTL 收敛（建议 300~3600s），后端更新时统一主动失效；
   排查 announcement_detail/sign_config/tracking_position_config 为什么是约 3 年 TTL。
5. token_user 生命周期治理：评估缩短 30 天 TTL / 滑动续期 / 定期清理；
   确认多点登录删除逻辑覆盖所有登录入口。
6. 埋点 raw 键：消费完成后删除或短 TTL（如 10 分钟）；
   quque 命名建议规范为 queue（需业务确认改常量并兼容旧键）。
7. 定期巡检：大 key（当前无）、TTL 分布、key 数量趋势、连接数。
```

## 安全说明

```text
全程只读巡检，未修改任何 Redis 数据/配置；未输出密码/token/chat_id。
```
