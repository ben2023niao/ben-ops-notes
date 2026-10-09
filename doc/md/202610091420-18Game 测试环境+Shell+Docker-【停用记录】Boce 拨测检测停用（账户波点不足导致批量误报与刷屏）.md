---
id: "doc-a10398de5a48"
title: "【停用记录】Boce 拨测检测停用（账户波点不足导致批量误报与刷屏）"
date: "2026-10-09T14:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Docker", "监控告警", "DNS", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/php/doc/2026-10-09_1420-%E3%80%90%E5%81%9C%E7%94%A8%E8%AE%B0%E5%BD%95%E3%80%91Boce%E6%A3%80%E6%B5%8B%E5%81%9C%E7%94%A8%EF%BC%88%E6%B3%A2%E7%82%B9%E4%B8%8D%E8%B6%B3%E5%AF%BC%E8%87%B4%E6%89%B9%E9%87%8F%E8%AF%AF%E6%8A%A5%E5%88%B7%E5%B1%8F%EF%BC%89.md"
sourcePath: "~/Desktop/18game_devops/devops/php/doc/2026-10-09_1420-【停用记录】Boce检测停用（波点不足导致批量误报刷屏）.md"
sourceSha256: "82b2b7956a070ce8d1e275915061971d6f780b72f73695b945f6f98e3b9b358d"
sourceSystem: "project-doc"
---

# 【停用记录】Boce 拨测检测停用（账户波点不足导致批量误报与刷屏）

> 来源文件：`~/Desktop/18game_devops/devops/php/doc/2026-10-09_1420-【停用记录】Boce检测停用（波点不足导致批量误报刷屏）.md`

> 整理日期：2026-10-09 14:20｜日期依据：文件名日期

- 日期：2026-10-09 14:20（北京）
- 范围：监控机 52.79.252.255 的 `php-server` 容器（应用目录 `/opt/18game_devops/devops/php`）
- 分类：误报治理 / 检测任务停用（用户要求：拨测 API 异常、没钱了，先关掉）
- 影响接口：`/boce_check_api.php`（Boce 批量检测 + Telegram 通知）
- **不影响**：`/dns_check.php`（DNS/SNI 检测）、`/boce_balance.php`（余额查询）实测均正常

## 一、现象

```text
数据汇报bot（推送内容）：
  Boce 检测通知：共 10 个域名，异常 10 个
  失败主机：h5.game-app543.com, g654321.com, g9876543.com, jtr4u6j3243w.com, kmjyr543.com,
           lokhjgbfvdcx.com, kfvdcsxx目标示例, d5fr6gt7hy8ju9ki0lo.com, jytfhdgrsfdzd.com, kjghgcfxd.com
  波点：未知或不可用
  时间：2026-10-09 14:04:47
  提醒：@Ben_Bird @Kermit0824 @make6384
```

即：10 个域名**全部**被报异常，且"波点：未知或不可用"——典型的账户额度不可用造成的伪异常。

## 二、根因

1. `public/boce_check_api.php` 对每个域名调 Boce 接口 `task/create/wall`，**任何非 0 返回都计入"异常"**；
   账户波点不足时接口不可用，10 个域名就全部被判成异常 → 批量误报。
2. 该接口的注释写明"每次 API 调用都发送通知（移除防刷）"，即**每次都无条件发 Telegram**；
   调用方触发频率较高（近 3 小时 `/boce_check_api.php` 14 次、`/dns_check.php` 32 次），于是刷屏。
3. 触发方为外部调用（`103.107.199.30`，不在我们的机器清单内），不是本机 cron：

```text
php-server 访问日志（近 3 小时，按调用方统计）：
  103.107.199.30  /dns_check.php       32 次
  103.107.199.30  /boce_check_api.php  14 次
  103.107.199.30  /boce_balance.php     2 次
```

## 三、处置（已生效）

在应用侧加"停用开关"，默认关闭，从根上止住误报与刷屏（无需联系调用方、改动可逆）：

1. `conf/config.php` 新增开关：

```php
// 2026-10-09 停用开关：Boce 账户波点不足导致批量误报与刷屏，由运维关闭检测与 Telegram 通知
$boceCheckEnabled = filter_var(getenv('BOCE_CHECK_ENABLED') ?: '0', FILTER_VALIDATE_BOOLEAN);
```

2. `public/boce_check_api.php` 在**调用 Boce API 之前**短路返回：

```php
if (empty($boceCheckEnabled)) {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode([
        'success' => false,
        'disabled' => true,
        'message' => 'Boce 检测已停用（账户波点不足，2026-10-09 由运维关闭）；充值后设置 BOCE_CHECK_ENABLED=1 可恢复',
    ], JSON_UNESCAPED_UNICODE);
    exit;
}
```

3. 部署（容器 `php-server` 以 bind mount 方式挂载该目录，替换文件即生效，无需重启容器）：

```text
备份：/root/php-config-backup-20261009-141100.php
      /root/boce-check-api-backup-20261009-141100.php
目标：/opt/18game_devops/devops/php/conf/config.php
      /opt/18game_devops/devops/php/public/boce_check_api.php
```

## 四、验证

| 验证项 | 命令/方式 | 结果 |
| --- | --- | --- |
| 语法 | `docker exec php-server php -l /app/conf/config.php`、`…/boce_check_api.php` | 均 `No syntax errors detected` |
| 开关落地 | 容器内 `grep -c boceCheckEnabled` | 两个文件各 1 处 |
| 主接口行为（用调用方真实 URL 的 10 个域名） | `curl 'http://203.0.113.1:8080/boce_check_api.php?notify_format=summary_link&hosts=…'` | 返回 `{"success":false,"disabled":true,"message":"Boce 检测已停用…"}`，**未调用 Boce API、未发送 Telegram** |
| 无参数调用 | `curl 'http://203.0.113.1:8080/boce_check_api.php'` | 同样返回 disabled（不是报错） |
| 其它接口不受影响 | `dns_check.php?h5.game-app543.com`、`boce_balance.php?format=json` | 均 HTTP 200 |

（短路逻辑位于任何发送动作之前，因此不会再产生 Boce 告警消息。）

## 五、影响与说明

- 调用方（`103.107.199.30`）**仍可继续调用**该接口，但只会拿到"已停用"的 JSON，不再触发 Boce API 调用与群消息；
- DNS/SNI 检测（`/dns_check.php`）**未受影响**，仍按原逻辑推送（本次用户只要求关闭 Boce 拨测）；
- Boce 余额查询接口保留，便于充值后确认额度恢复。

## 六、恢复方式（充值后）

```bash
# 方式一：给容器加环境变量后重启（推荐，不动代码）
#   在 php-server 的启动参数/compose 中设置 BOCE_CHECK_ENABLED=1，然后重建容器
# 方式二：直接改默认值
sudo sed -i "s/getenv('BOCE_CHECK_ENABLED') ?: '0'/getenv('BOCE_CHECK_ENABLED') ?: '1'/" \
  /opt/18game_devops/devops/php/conf/config.php
curl -s "http://203.0.113.1:8080/boce_balance.php?format=json"   # 确认波点已恢复
```

## 七、回滚

```bash
sudo cp -a /root/php-config-backup-20261009-141100.php /opt/18game_devops/devops/php/conf/config.php
sudo cp -a /root/boce-check-api-backup-20261009-141100.php /opt/18game_devops/devops/php/public/boce_check_api.php
```

## 八、后续建议

1. **接口补保护**：`boce_check_api.php` 建议增加"余额不足/波点不可用时不判定为异常、不发通知"
   的分支，避免同类误报（本次为快速止血，采用了整站停用开关）。
2. **告警限流**：该接口目前"每次调用都发通知"，建议恢复时加回节流（同一批域名 N 分钟内只发一次）。
3. **确认调用方**：`103.107.199.30` 上的调度方若能改，建议同步降低频率或在充值前暂停；
   它同时还在调用 `/dns_check.php`（近 3 小时 32 次），如果 DNS/SNI 告警也想收敛，可以一并评估。
