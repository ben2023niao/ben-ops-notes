---
id: "doc-5197ad8c2b43"
title: "【停用记录】DNS/SNI 巡检停用（功能已废弃 + 被外部高频调用导致告警刷屏）"
date: "2026-10-09T15:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Docker", "Nginx", "监控告警", "DNS", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/php/doc/2026-10-09_1540-%E3%80%90%E5%81%9C%E7%94%A8%E8%AE%B0%E5%BD%95%E3%80%91DNS-SNI%E5%B7%A1%E6%A3%80%E5%81%9C%E7%94%A8%EF%BC%88%E5%8A%9F%E8%83%BD%E5%BA%9F%E5%BC%83%2B%E5%A4%96%E9%83%A8%E9%AB%98%E9%A2%91%E8%B0%83%E7%94%A8%E5%88%B7%E5%B1%8F%EF%BC%89.md"
sourcePath: "~/Desktop/18game_devops/devops/php/doc/2026-10-09_1540-【停用记录】DNS-SNI巡检停用（功能废弃+外部高频调用刷屏）.md"
sourceSha256: "d3f0baab6e9783355945edb649c253cd6551996c9bdff17d094527121892f11f"
sourceSystem: "project-doc"
---

# 【停用记录】DNS/SNI 巡检停用（功能已废弃 + 被外部高频调用导致告警刷屏）

> 来源文件：`~/Desktop/18game_devops/devops/php/doc/2026-10-09_1540-【停用记录】DNS-SNI巡检停用（功能废弃+外部高频调用刷屏）.md`

> 整理日期：2026-10-09 15:40｜日期依据：文件名日期

- 日期：2026-10-09 15:40（北京）
- 范围：监控机 52.79.252.255 的 `php-server` 容器（应用目录 `/opt/18game_devops/devops/php`）
- 分类：误报/刷屏治理 + 废弃功能停用（用户要求：一直被刷、已废弃，直接关掉）
- 影响接口：`/dns_check.php`（DNS/SNI 深度巡检 + HTML 报告 + Telegram 告警）
- **不影响**：`/boce_check_api.php`（13:20 已停用，仍为 disabled）、`/boce_balance.php` 均正常

## 一、现象

```text
数据汇报bot 连续推送（同一分钟内多条）：
  🚨 DNS/SNI 异常告警
  🔗 完整报告详情: http://52.79.252.255:8080/dns_check/dns_report_2026-10-09_23-27-29.html
  （23:27:29 / 23:27:40 / 23:27:52 / 23:28:03 / 23:28:16 / 23:28:27 / 23:28:39 / 23:28:50 / 23:29:02 / 23:29:13 / 23:29:25 …）
  👤 呼叫负责人: @jett_yunwei @Ben_Bird @Kermit0824
```

## 二、核查结果

1. **该功能已废弃**：用户明确“已经废弃了的”，先关掉停止打扰。
2. **调用方不是我们自己的机器**：实测近 6 小时 `/dns_check.php` 共 87 次，来源统计：

```text
85 次  103.107.199.30   ← 外部来源，非我方任何已知机器
 2 次  203.0.113.1       ← 本机 docker 网关照（运维验证/自测）
```

   已逐个核对我方主力机器出口 IP（ben-bot 52.79.252.255、网关 16.208.38.88、后端 16.209.16.108、
   宝塔 16.208.5.147、测试 EC2 15.152.247.196）均不等于该 IP。
3. **接口本身很"重"且每次都会产生副作用**：每次调用会
   → 调检测服务（`http://52.79.252.255:59000/dns_check`，对 17 个域名做 DNS 污染/SNI 探测）
   → 写一个 HTML 报告到 `public/dns_check/`
   → 无条件发送 Telegram 告警。
4. **实测频率与产物增长**：

```text
近 6 小时：87 次     近 1 小时：42 次     近 10 分钟：26 次（突发式）
近 30 分钟新增报告文件：38 个（目录累计 81 个 / 332K）
```

   也就是说：外部来源在按 10 秒级频率刷这个公开接口，等于持续消耗检测服务并发 + 生成报告 + 刷群。

## 三、处置（已生效）

在接口入口加"停用开关"，默认关闭，命中即返回，不再做任何检测/写文件/发消息：

```php
// public/dns_check.php（紧接基础配置区之后）
// 2026-10-09 停用开关：该 DNS/SNI 巡检功能已废弃，且被外部来源持续调用
//   （实测：外部 IP 103.107.199.30，近 6 小时 87 次 / 近 10 分钟 26 次、突发式，
//     30 分钟生成 38 个报告文件）→ 群告警刷屏 + 无效的检测开销。
$dnsCheckEnabled = filter_var(getenv('DNS_CHECK_ENABLED') ?: '0', FILTER_VALIDATE_BOOLEAN);
if (empty($dnsCheckEnabled)) {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode([
        'success' => false,
        'disabled' => true,
        'message' => 'DNS/SNI 巡检已停用（功能已废弃，2026-10-09 由运维关闭）；如需恢复请设置 DNS_CHECK_ENABLED=1',
    ], JSON_UNESCAPED_UNICODE);
    exit;
}
```

部署（`php-server` 以 bind mount 挂载该目录，替换文件即生效，**未重启容器**）：

```text
备份：/root/dns-check-backup-20261009-153513.php
目标：/opt/18game_devops/devops/php/public/dns_check.php
```

## 四、验证

| 验证项 | 方式 | 结果 |
| --- | --- | --- |
| 语法 | `docker exec php-server php -l /app/public/dns_check.php` | `No syntax errors detected` |
| 主接口（真实 17 域名 URL） | `curl 'http://203.0.113.1:8080/dns_check.php?<域名列表>'` | 返回 `{"success":false,"disabled":true,"message":"DNS/SNI 巡检已停用…"}` |
| 是否仍产生报告 | 调用前后统计 `public/dns_check/*.html` | 81 → 81，**没有新增** |
| 单域名调用 | `curl '…/dns_check.php?h5.game-app543.com'` | 同样返回 disabled |
| 不影响其它接口 | `curl …/boce_check_api.php` | HTTP 200（仍为 disabled 逻辑） |

## 五、影响与说明

- 外部调用方仍可访问该 URL，但只会立刻拿到"已停用"的 JSON：**不再消耗检测服务、不再生成报告、不再发群**；
- 历史报告页（`http://52.79.252.255:8080/dns_check/*.html`，81 个 / 332K）保持可查，未删除；
- `dns_monitor_pywebio` 容器（59000 检测 API、59999 UI）在停用后**已无调用方**，本次未停，等确认。

## 六、恢复方式

```bash
# 给 php-server 设置环境变量 DNS_CHECK_ENABLED=1（或把 dns_check.php 里默认值 '0' 改为 '1'）
curl -s -m 60 "http://203.0.113.1:8080/dns_check.php?h5.game-app543.com"   # 恢复后自测
```

## 七、回滚

```bash
sudo cp -a /root/dns-check-backup-20261009-153513.php /opt/18game_devops/devops/php/public/dns_check.php
```

## 八、安全建议（本次未执行，待确认）

1. **限制调用来源**：`103.107.199.30` 不是我方已知机器，且以 10 秒级频率调用我们的运维接口。
   建议在监控机防火墙或 nginx 层直接封禁该 IP（至少禁止其访问 `/dns_check.php`、`/boce_*.php`）。
2. **运维接口加访问控制**：这些接口（`/dns_check.php`、`/boce_check_api.php`、`/boce_balance.php`）
   公网可达且无鉴权，建议加 IP 白名单或 Basic Auth，从根上避免被外部当免费资源刷。
3. **报告页暴露**：`/dns_check/*.html` 公网可访问且内容包含我们的域名清单，
   很可能是被外部抓取后用来按清单刷接口的来源；建议确认后清理或下线（保留到本地/内网）。
4. **停用空闲服务**：`dns_monitor_pywebio` 容器已无调用方，可一并 `docker stop`（保留镜像便于恢复）。
