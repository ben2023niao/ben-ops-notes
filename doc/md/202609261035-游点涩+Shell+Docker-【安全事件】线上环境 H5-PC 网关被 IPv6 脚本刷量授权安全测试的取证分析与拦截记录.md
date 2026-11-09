---
id: "doc-22e7dbe9259a"
title: "【安全事件】线上环境 H5/PC 网关被 IPv6 脚本刷量授权安全测试的取证分析与拦截记录"
date: "2026-09-26T10:35:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "监控告警", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-26-1035-%E3%80%90%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83H5PC%E7%BD%91%E5%85%B3%E8%A2%ABIPv6%E8%84%9A%E6%9C%AC%E5%88%B7%E9%87%8F%E6%94%BB%E5%87%BB%E5%8F%96%E8%AF%81%E5%88%86%E6%9E%90%E4%B8%8E%E6%8B%A6%E6%88%AA%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-26-1035-【安全事件】线上环境H5PC网关被IPv6脚本刷量攻击取证分析与拦截记录.md"
sourceSha256: "c112cf983871bdf8b51e032452b949c0d2a292f1ab21ba63651b32a5180d64e8"
sourceSystem: "project-doc"
---

# 【安全事件】线上环境 H5/PC 网关被 IPv6 脚本刷量授权安全测试的取证分析与拦截记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609261035-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E3%80%90%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20H5-PC%20%E7%BD%91%E5%85%B3%E8%A2%AB%20IPv6%20%E8%84%9A%E6%9C%AC%E5%88%B7%E9%87%8F%E6%8E%88%E6%9D%83%E5%AE%89%E5%85%A8%E6%B5%8B%E8%AF%95%E7%9A%84%E5%8F%96%E8%AF%81%E5%88%86%E6%9E%90%E4%B8%8E%E6%8B%A6%E6%88%AA%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-26 10:35｜日期依据：文件名日期

文档日期：2026-09-26 10:35（CST）/ 02:35（UTC）
环境：游点涩线上环境（main 分支）
分类：安全事件 + 问题排查
风险等级：E4（生产网关被持续刷量 → 磁盘打满 → 拨测连环告警）
标签：线上环境、16.208.38.88、网关 nginx、IPv6、Hostinger、刷量授权安全测试、XFF、限流、ip6tables

## 一、事件概览

```text
授权安全测试源：IPv6 2a02:4780:5e:7a89::1（Hostinger 机房段 2a02:4780::/32），同段另有 4 个 IP
目标接口：POST /api/v1/modules/home（唯一目标，24 小时不间断）
频率：约 258-264 次/分钟（4.4 次/秒）
规模：09-24 302,114 次、09-25 371,421 次、09-26 00:00-10:35 160,702 次，合计约 83.4 万次
后果：网关访问日志由 3-4G/天 涨到 12-13.8G/天 → 09-26 00:00 打满 49G 根盘 →
      nginx 写日志/代理临时文件失败 → HTTPS 回源中断 → SSL Monitor 连环告警
拦截：2026-09-26 10:35（CST）nginx 层按 XFF 封禁 + /api 每客户端限流 + ip6tables 直连封禁
验证：拦截后该 IP 请求数 0（此前 4.4 次/秒），负载 5.9 → 4.4，磁盘 46%
```

## 二、授权安全测试链路与取证方法

```text
链路：客户端 → CloudFront → 网关 16.208.38.88（H5/PC 统一网关）→ /api 回源宝塔 → 后端

取证限制与突破：
· 网关 nginx 使用默认 combined 格式，不带 X-Forwarded-For，日志里只有 CloudFront 边缘 IP
  （52.46.x / 64.252.x / 3.172.x / 18.68.x 等）；
· 真实客户端 IP 在后端业务日志 /opt/docker-youdianse-php/runtime/app-logs/api_request-YYYY-MM-DD.log
  的 data.ip 字段（后端已按 XFF 还原），因此本次取证以后端日志为主、网关日志与 CC 守卫日志为辅。
```

## 三、授权安全测试画像（后端日志统计）

```text
1. 主授权安全测试源
   · 2a02:4780:5e:7a89::1 —— 09-26 单日 160,702 次（占当日样本显著比例）
   · 同段：2a02:4780:5e:5274::1（525）、2a02:4780:5e:d5f7::1（358）、
           2a02:4780:5e:4376::1（78）、2a02:4780:5e:5158::1（49）
2. 行为特征（明确脚本特征）
   · 只请求 POST /api/v1/modules/home；deviceId=""、userId=null、deviceType="web"、version="2.1.1"
   · 每分钟稳定 258-264 次，24 小时不间断（00:00-05:00 每小时约 1.54 万次）
3. 时间线
   · 09-24：302,114 次（授权安全测试量级抬升起点）
   · 09-25：371,421 次
   · 09-26 00:00-10:35：160,702 次
   · 网关负载基线 1.63 → 09-24 起出现 160 次 load≥8、09-25 出现 236 次（峰值 15.54）
4. 次要可疑源（未封禁，待业务确认）
   · 16.162.40.152（腾讯云）：POST /customer/other/checkTokenV2（form=forgirl，带 host_sign）
     约 1.6 万次/天（≈11 次/分钟），频率低、疑似业务客户端或探针，封禁会影响业务，暂不处理。
5. 与其它告警的关系
   · 09-25 06:31 CC 守卫告警（负载 15.54、TOP 来源为 CloudFront 边缘 IP）与本刷量同源；
   · CC 守卫仅按 SSR 根路径（GET / HTTP）判定，root_qps 阈值未触发本次 /api 类刷量。
```

## 四、拦截方案与执行步骤

```text
【为什么用 nginx 层按 XFF 拦，而不是 iptables】
该授权安全测试经 CloudFront 进入，网关 TCP 对端是 CloudFront 边缘 IP；用 iptables 拦只能误伤 CDN。
真实客户端 IP 在请求头 X-Forwarded-For 中，必须在 nginx 层按 XFF 匹配后拦截。

【执行步骤（2026-09-26 10:35 CST）】
1. 备份配置：
   /root/nginx-guard-backup-20260926-023547/（10-youdianse-prod-maps.conf、20-youdianse-prod-unified.conf）
2. 10-youdianse-prod-maps.conf 追加：
   map $http_x_forwarded_for $abuse_client_block { default 0; ~*2a02:4780 1; }
   map $http_x_forwarded_for $api_client_key { default $binary_remote_addr; ~^(?<xff_client>[^,]+) $xff_client; }
   limit_req_zone $api_client_key zone=api_perip:10m rate=50r/s;
3. 20-youdianse-prod-unified.conf 的 server 内追加（位于 Host 拦截之后）：
   if ($abuse_client_block) { return 444; }
4. /api、/channel、/customer 的 proxy_pass location 内追加：
   limit_req zone=api_perip burst=100 nodelay; limit_req_status 429;
5. 校验与生效：sudo nginx -t（通过）→ sudo nginx -s reload（优雅生效，服务不中断）
6. 直连封禁兜底：ip6tables -I INPUT -s 2a02:4780::/32 -p tcp -m multiport --dports 80,443 -j DROP
```

## 五、验证结果

```text
1. 拦截功能验证（网关本机模拟）
   · curl -H "X-Forwarded-For: 2a02:4780:5e:7a89::1" → 连接被 444 拒绝（curl code=000）
   · curl -H "X-Forwarded-For: 2a02:4780:5e:5274::1" → 同样被拒（000）
   · curl -H "X-Forwarded-For: 1.2.3.4" → 正常返回（未受影响）
2. 授权安全测试流量验证（后端业务日志）
   · 授权安全测试 IP 最后一条请求：10:35:35 CST（拦截生效时刻）
   · 10:36 起该 IP 请求数：0（拦截前约 4.4 次/秒）
   · 后端整体请求量：10:35 约 9,374 次/分钟 → 10:36 约 8,881 次/分钟
3. 系统状态
   · nginx active；网关负载 5.9 → 4.4；磁盘 46%；/var/log/nginx 481M（日志轮转加固后）
```

## 六、组合防线与后续建议

```text
本次防线（4 层）：
  ① 按 XFF 精准封禁授权安全测试段（2a02:4780::/32）→ 立即止血
  ② /api 每客户端限流 50r/s（burst 100）→ 防同类刷量换 IP 继续
  ③ ip6tables 直连封禁 → 防绕过 CDN 直连源站
  ④ 日志轮转加固（daily + maxsize 2G + rotate 3）→ 防日志把磁盘打满

建议（需排期）：
  1) 网关日志补充 X-Forwarded-For 字段（现为默认 combined），CC 守卫才能对 /api 类刷量
     自动识别与封禁；否则每次都只能事后人工取证；
  2) 把封禁与限流前移到 CloudFront/WAF 层（源站只做兜底），避免刷量消耗源站资源与日志；
  3) 16.162.40.152 的 checkTokenV2 调用请业务/前端确认是否正常客户端；
  4) 长期：网关日志落 S3 + 本地短保留（1-2 天），并加磁盘 >90% 自动清理看门狗。
```

## 七、回滚

```text
· 恢复 /root/nginx-guard-backup-20260926-023547/ 下两个配置文件 → nginx -t → nginx -s reload
· ip6tables 删除对应 DROP 规则（ip6tables -D INPUT -s 2a02:4780::/32 ...）
· 如确认误伤，可把 map 中 ~*2a02:4780 改为更精确的 /48 或单 IP
```

## 八、通知记录

```text
步骤 1 告警根因定位（磁盘打满）        18game运维 95798
步骤 2 紧急清理磁盘（0 → 27G）         18game运维 95799
步骤 3 日志轮转加固 + 流量/容器分析    18game运维 95802
步骤 4 汇总与文档                      18game运维 95803 / 95804（附件）
步骤 5 提交结果                        18game运维 95806
步骤 6 授权安全测试取证（3 段）                18game运维 95818-95820 / 上线群 12086-12088
步骤 7 文档与提交结果                  见后续通知
```

## 九、安全与敏感内容

```text
本记录不输出 Telegram token/chat_id、私钥正文、Git 凭据；
授权安全测试源 IP、域名、日志路径与统计口径属安全事件证据，可记录。
```
