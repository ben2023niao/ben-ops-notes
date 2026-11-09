---
id: "doc-fd8cf84a4036"
title: "【优化】线上环境网关日志补充真实客户端 IP 与 CC 守卫 /api 刷量识别封禁改造记录"
date: "2026-09-26T10:44:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "监控告警", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-26-1044-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E7%BD%91%E5%85%B3%E6%97%A5%E5%BF%97%E8%A1%A5%E5%85%85%E7%9C%9F%E5%AE%9E%E5%AE%A2%E6%88%B7%E7%AB%AFIP%E4%B8%8ECC%E5%AE%88%E5%8D%ABAPI%E5%88%B7%E9%87%8F%E8%AF%86%E5%88%AB%E5%B0%81%E7%A6%81%E6%94%B9%E9%80%A0%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-26-1044-【优化】线上环境网关日志补充真实客户端IP与CC守卫API刷量识别封禁改造记录.md"
sourceSha256: "81799d0e16b948d09dd58cd94b0a9adc15ab3c53399146e82ac044213a2ce78c"
sourceSystem: "project-doc"
---

# 【优化】线上环境网关日志补充真实客户端 IP 与 CC 守卫 /api 刷量识别封禁改造记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609261044-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E7%BD%91%E5%85%B3%E6%97%A5%E5%BF%97%E8%A1%A5%E5%85%85%E7%9C%9F%E5%AE%9E%E5%AE%A2%E6%88%B7%E7%AB%AF%20IP%20%E4%B8%8E%20CC%20%E5%AE%88%E5%8D%AB%20-api%20%E5%88%B7%E9%87%8F%E8%AF%86%E5%88%AB%E5%B0%81%E7%A6%81%E6%94%B9%E9%80%A0%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-26 10:44｜日期依据：文件名日期

文档日期：2026-09-26 10:44（CST）/ 02:44（UTC）
环境：游点涩线上环境（main 分支）
分类：优化 + 安全加固
风险等级：P2（生产网关 nginx 日志格式与拦截清单）
标签：线上环境、16.208.38.88、网关 nginx、X-Forwarded-For、CC 守卫、API 刷量、自动封禁

## 一、背景与目标

```text
2026-09-26 的 IPv6 刷量授权安全测试（/api/v1/modules/home，约 83.4 万次）暴露两个短板：
1. 网关访问日志为 nginx 默认 combined 格式，只有 CloudFront 边缘 IP，
   真实客户端 IP 只能到后端业务日志里找，取证链路长；
2. CC 守卫只按 SSR 根路径（GET / HTTP）判定，无法识别「经 CDN 刷 /api」的授权安全测试，
   本次授权安全测试从头到尾没有触发守卫。

本次目标：
  · 网关日志补充 $http_x_forwarded_for（真实客户端 IP）；
  · CC 守卫可识别 /api、/channel、/customer 维度的单客户端刷量，并自动封禁（可经 CDN 生效）。
```

## 二、改造一：网关访问日志补充真实客户端 IP

```text
备份：/root/nginx-xff-backup-20260926-023957/（nginx.conf、20-youdianse-prod-unified.conf）

1. /etc/nginx/nginx.conf 新增格式（保留 combined 全部字段，末尾追加 XFF）：
   log_format youdianse_ext '$remote_addr - $remote_user [$time_local] "$request" '
                            '$status $body_bytes_sent "$http_referer" "$http_user_agent" '
                            '"$http_x_forwarded_for"';
   access_log /var/log/nginx/access.log youdianse_ext;
2. /etc/nginx/conf.d/20-youdianse-prod-unified.conf：
   access_log /var/log/nginx/access.log youdianse_ext if=$log_ssr;
3. nginx -t 通过 → nginx -s reload（优雅生效，服务不中断）

验证：新日志末尾出现真实客户端 IP，例如
  · 64.252.103.202 ... "GET /post-detail/71075 ..." ... "47.79.15.68"
  · 52.46.54.196  ... "POST /api/v1/User/getCommunityInfo ..." ... "2408:826a:e10:163:...:fc26"
  第一列仍为 CloudFront 边缘 IP，二者可对照区分。
```

## 三、改造二：CC 守卫支持 /api 刷量识别与自动封禁

```text
改动文件：devops/scripts/cc_guard/youdianse_cc_guard.py（ben-bot 运行机同名路径）
备份：/root/cc_guard-backup-20260926-104122.py

1. 新增 api_flood_suspects()：
   采样网关访问日志最近 6 万行（约 3-4 分钟窗口），
   对 /api、/channel、/customer 请求按 XFF 真实客户端计数，
   单客户端 ≥900 次（≈4 次/秒）判定为刷量。
2. 新增 write_gateway_blocklist()：
   把命中客户端写入网关 /etc/nginx/conf.d/abuse-blocklist.conf
   （map $http_x_forwarded_for $abuse_client_block { ... }），
   随后 nginx -t + nginx -s reload，命中客户端直接 444。
3. 网关侧结构调整：
   原 10-youdianse-prod-maps.conf 内联的拦截 map 抽成独立清单 abuse-blocklist.conf，
   由守卫自动维护（maps 文件改为 include），保留原有 /api 每客户端限流 zone=api_perip。
4. 防误伤设计：
   · 仅写入 IP 形态条目（IPv4 正则 / IPv6 字符集校验），从根上排除 UA 等字符串；
   · 跳过 CloudFront 与云厂商网段（3. / 52.46. / 64.252. / 130.176. / 204.246. 等）；
   · 已被固定网段清单覆盖的 IP 不重复写入；
   · 已在封禁清单的客户端不再重复触发告警（避免 90 秒一次刷屏）。

过程说明（如实记录）：第一版中间态脚本在 02:41 被 cron 执行过一轮，
将 UA 字符串（Dart / node / Mozilla/5.0 等）误写入拦截清单；发现后立即清理
（状态文件与网关清单均还原为仅含授权安全测试网段 2a02:4780），并加入 IP 形态校验 + 写入前二次过滤。
```

## 四、验证

```text
1. 自动封禁链路端到端
   · 写入测试 IP 203.0.113.9 → 带该 XFF 的请求 444（被拦）；正常 IP 正常返回（404 = 正常应答）
   · 清理测试条目成功，网关清单恢复为只含 2a02:4780
2. 刷量识别（真实日志）
   · 2a02:4780:5e:7a89::1 窗口内 1019 次 → 命中阈值被识别；其他客户端未达阈值，未误伤
3. 告警抖动修复
   · 连续两轮守卫日志：api_flood=0/1（0 新增）→ 已封禁来源不再重复告警
4. 运行状态
   · 授权安全测试段请求被 444 拒绝、后端日志 0 命中；网关负载 1.7-2.0（峰值 8.57）；磁盘 46%
```

## 五、回滚

```text
· 网关日志格式：恢复 /root/nginx-xff-backup-20260926-023957/ 下两个文件 → nginx -t → nginx -s reload
· 守卫脚本：恢复 /root/cc_guard-backup-20260926-104122.py → 覆盖 ben-bot 同名文件
· 拦截清单：编辑 /etc/nginx/conf.d/abuse-blocklist.conf 删除对应条目 → nginx -t → nginx -s reload
```

## 六、后续建议

```text
1. 把封禁前移到 CloudFront/WAF 层（源站只做兜底），减少源站资源与日志消耗；
2. 网关日志落 S3 + 本地短保留（1-2 天），并加磁盘 >90% 自动清理看门狗；
3. 守卫阈值（900/窗口）上线观察 1-2 天，按误报情况微调；
4. 16.162.40.152 的 checkTokenV2 高频调用待业务确认是否正常客户端。
```

## 七、通知记录

```text
步骤 1 网关日志补 XFF          18game运维 95827 / 上线群 12093
步骤 2 CC 守卫升级与部署       18game运维 95828 / 上线群 12094
步骤 3 验证结果                18game运维 95829 / 上线群 12095
步骤 4 文档与提交结果          见后续通知
```

## 八、安全与敏感内容

```text
本记录不输出 Telegram token/chat_id、私钥正文、Git 凭据；
服务器 IP、域名、日志路径与统计口径属基础设施与安全事件信息，可记录。
```
