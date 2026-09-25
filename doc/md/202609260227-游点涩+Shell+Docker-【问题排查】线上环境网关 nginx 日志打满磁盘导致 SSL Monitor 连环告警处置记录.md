---
id: "doc-2efbf9ffc01b"
title: "【问题排查】线上环境网关 nginx 日志打满磁盘导致 SSL Monitor 连环告警处置记录"
date: "2026-09-26T02:27:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "监控告警", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-26-0227-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E7%BD%91%E5%85%B3nginx%E6%97%A5%E5%BF%97%E6%89%93%E6%BB%A1%E7%A3%81%E7%9B%98%E5%AF%BC%E8%87%B4SSL%20Monitor%E8%BF%9E%E7%8E%AF%E5%91%8A%E8%AD%A6%E5%A4%84%E7%BD%AE%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-26-0227-【问题排查】线上环境网关nginx日志打满磁盘导致SSL Monitor连环告警处置记录.md"
sourceSha256: "64708a32f2366adc6984c81f6f69faffb0ca7b874ccc41e3a6b0c856dfcc4ce6"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境网关 nginx 日志打满磁盘导致 SSL Monitor 连环告警处置记录

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-26-0227-【问题排查】线上环境网关nginx日志打满磁盘导致SSL Monitor连环告警处置记录.md`

> 整理日期：2026-09-26 02:27｜日期依据：文件名日期

文档日期：2026-09-26 02:27（UTC）/ 10:27（CST）
环境：游点涩线上环境（main 分支）
分类：问题排查（E4 生产告警刷屏）
标签：线上环境、网关 nginx、16.208.38.88、磁盘打满、访问日志、SSL Monitor、CC 守卫

## 一、现象

```text
1. 群内 SSL Monitor 连环告警（多条）：
   🚨【网页访问异常】Response ended prematurely —— h5.game-app543.com / feijuka.com / onbrp.com /
   buttonp.com / zjyzsjj.com / txsyds.com / maogoudaxia.com / yundingly.com / wdjxhn.com / wangcaitt.com 等
   （同一时间还有「HTTPS 回源失败、HTTP 仍可访问」与「已恢复」交替出现）
2. Beszel 告警：游点涩-pc-nginx 磁盘使用 在过去的 10 分钟中超过 80%
3. 监控面板：游点涩-pc-nginx = 16.208.38.88，CPU 47.5%、磁盘 100%、负载 5.9~8.5、网络 15.9 MB/s
4. 同期 CC 守卫告警（2026-09-25 06:31 UTC）：负载异常 15.54，TOP 来源为 CloudFront 边缘 IP
```

## 二、根因

```text
1. 磁盘被打满（直接原因）：
   /dev/root 49G 已用 49G，可用 0（100%）；/var 44G，其中 /var/log 31G，/var/log/nginx 28G：
   · access.log    13.8G（当天，仍在增长）
   · access.log.1  12.0G（前一天）
   · access.log.2~7.gz 约 2.5G（滚动压缩日志）
   · journal 3.7G
2. 该机器（16.208.38.88）是 18game H5/PC 统一网关：公网域名 → CloudFront → 本机 nginx →
   H5/PC 前端容器（3003/3004）与 /api 回源宝塔/后端。
3. 磁盘写满后 nginx 无法正常落盘/处理，HTTPS 回源请求中途断开 →
   拨测侧表现为 “Response ended prematurely / HTTPS 回源失败”，触发 SSL Monitor 连环告警。
4. 日志暴涨的驱动是网关侧的请求量：实测网关约 546 req/s（TOP 路径全部为 /api/v1/*：
   Tracking/recordPageVisit、system/info、configDict/getConfigDict、AppVersion/latestVersion、modules/home），
   而 logrotate 原配置为 daily + rotate 7（无大小上限）→ 单日 13G 日志、7 天≈28G，必然打满 49G 根盘。
5. 该机器就是 CC 守卫（ben-bot cron 每分钟）监控对象；本次其 root_qps 阈值未触发（当前 root_qps=4.7），
   守卫仅按 SSR 根路径（GET / HTTP）判定，不覆盖 /api 类接口流量。
```

## 三、处置

### 3.1 紧急释放磁盘（2026-09-26 02:24~02:26 UTC）

```text
1. 删除 Sep 22-23 旧滚动日志（access.log.3~7.gz）
2. 清空昨日 access.log.1（12G）→ 可用空间 0 → 14G
3. 保存告警证据样本：/root/nginx-attack-sample-20260926-022459.log.gz（5.5MB，末 30 万行）
4. 清空当前 access.log 并执行 nginx -s reopen（保持句柄、服务不中断）
结果：根盘 49G → 已用 22G、可用 27G（使用率 100% → 46%）
```

### 3.2 日志轮转加固（防止再次打满）

```text
备份：/root/logrotate-nginx-backup-20260926-022636.conf
新配置 /etc/logrotate.d/nginx：
  daily + maxsize 2G + rotate 3 + compress + delaycompress + notifempty + create 0640 www-data adm
  （相对原配置：无大小上限、rotate 7 → 改为单文件超 2G 即轮转、仅保留 3 份压缩）
执行 logrotate -d 干跑校验通过后 logrotate -f 强制轮转一次：
  /var/log/nginx 由 28G → 481M（access.log 7.8M / access.log.1 13.7M / 其余压缩）
```

## 四、验证

```text
· 磁盘：/dev/root 已用 22G、可用 27G（46%），/var/log/nginx 481M
· 服务：nginx active；H5/PC 前端容器 Up 38~39 小时；本机回源复测
  h5.yds-pc-h5-01.cc = 200（0.16s）、pc.yds-pc-h5-01.cc = 200（0.12s）
· 公网复测：feijuka.com / onbrp.com / buttonp.com / maogoudaxia.com / wangcaitt.com = 200
  （h5.game-app543.com 在本机所在地被菲律宾侧访问策略验证，属已知问题，非本次故障）
· 负载：由峰值 8.57 回落至 4.98（仍偏高，见遗留）
· 后端：16.209.16.108 负载 0.77，容器正常，近 5 分钟 0 个 5xx，磁盘 40%
· 请求量对比：后端今天 10:22–10:27 约 6.9k~10.0k 请求/分钟（≈120–165 req/s），
  低于昨天晚间 23:54–23:59 的 17.6k~18.5k 请求/分钟（≈300 req/s）→ 后端量级未异常
```

## 五、结论（回答“是不是有授权安全测试或前端容器异常”）

```text
1. 前端容器正常：H5/PC 容器持续 Up，本机与公网复测均 200；PC 容器日志里的
   “SSR 请求失败 … terminated UND_ERR_SOCKET”是磁盘打满期间的下游表现，非容器自身故障。
2. 本次群内连环告警的直接原因是「网关 nginx 日志打满磁盘」，已修复并加固轮转。
3. 网关侧确有较大请求量（约 546 req/s 的 /api 流量）与大量短连接（TIME_WAIT 1.7 万），
   但后端量级低于昨日峰值、无 5xx，暂不支持“正在被打挂”的判断；
   CC 守卫仍在运行（累计封禁 843 条 iptables 规则，封禁对象为真实客户端 IP，非 CloudFront 边缘）。
```

## 六、遗留与建议

```text
1. 【建议】网关 49G 根盘 + 13G/天日志仍有风险：除本次 maxsize 2G + rotate 3 外，
   建议把网关访问日志纳入「S3 归档 + 本地短保留」（既有日志归档脚本按 7 天保留，需同步调整为 1-2 天）。
2. 【建议】为网关增加磁盘看门狗：>80% 告警（Beszel 已有）+ >90% 自动清理最旧日志/截断当前日志，
   参考后端 ops/production/scripts/youdianse-disk-auto-clean.py。
3. 【建议】/api 类流量缺少防护：CC 守卫目前只按 SSR 根路径判定，建议补充
   /api 维度的 QPS/来源画像（网关日志目前用默认 combined 格式，不含 X-Forwarded-For，
   需先补 XFF 或从 CloudFront 日志侧关联真实客户端）。
4. 【观察】网关负载仍在 5 左右、TIME_WAIT 1.7 万，建议持续观察是否随业务高峰回落。
5. 本次仅改网关 logrotate 与清理日志，未改动 nginx 站点配置与业务容器；证据样本留存
   /root/nginx-attack-sample-20260926-022459.log.gz、logrotate 备份 /root/logrotate-nginx-backup-20260926-022636.conf。
```

## 七、通知记录

```text
步骤 1 告警根因定位（磁盘打满）        18game运维 95798
步骤 2 紧急清理磁盘（0 → 27G）         18game运维 95799
步骤 3 日志轮转加固 + 流量/容器分析     见后续通知
步骤 4 文档 / 5 提交结果               见后续通知
```

## 八、安全与敏感内容

```text
本记录不输出 Telegram token/chat_id、私钥正文、Git 凭据；
服务器 IP、域名、日志路径与统计口径属基础设施信息，可记录。
```
