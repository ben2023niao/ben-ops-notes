---
id: "doc-712bdcb4c75a"
title: "【排查+维护】巴西新游戏开放、香港 TADA 接入与数据库卡顿停服记录"
date: "2026-11-03T21:18:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Nginx", "Redis", "监控告警", "自动化", "CDN", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-11-03-2118-%E3%80%90%E6%8E%92%E6%9F%A5%2B%E7%BB%B4%E6%8A%A4%E3%80%91%E5%B7%B4%E8%A5%BF%E6%96%B0%E6%B8%B8%E6%88%8F%E5%BC%80%E6%94%BE%E9%A6%99%E6%B8%AFTADA%E6%8E%A5%E5%85%A5%E4%B8%8E%E6%95%B0%E6%8D%AE%E5%BA%93%E5%8D%A1%E9%A1%BF%E5%81%9C%E6%9C%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-11-03-2118-【排查+维护】巴西新游戏开放香港TADA接入与数据库卡顿停服记录.md"
sourceSha256: "a7f2e68d0c5c72c61ad757bc09a7948a5d965ade873fe4b0abbecb75da2417c7"
sourceSystem: "project-doc"
---

# 【排查+维护】巴西新游戏开放、香港 TADA 接入与数据库卡顿停服记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-11-03-2118-【排查+维护】巴西新游戏开放香港TADA接入与数据库卡顿停服记录.md`

> 整理日期：2026-11-03 21:18｜日期依据：文件名日期

更新时间：2026-11-03 21:18（Asia/Manila）

执行范围：本地 master、ben 分支、巴西 01/02/03/04/05、香港 01/02。

## 一、当前状态

巴西 01/02/04/05 的 `game-service*` 业务容器已全部关闭，四台服务器主机
保持在线。当前等待 DBA 完成数据库维护；收到明确恢复通知前不会启动容器。

恢复顺序固定为：

```text
BR01 金丝雀验证
-> BR02
-> BR04
-> BR05
```

每台恢复后都要核对容器、端口、镜像 ID、日志和数据库/钱包调用，再处理下一台。

## 二、开始前基线

```text
本地 master HEAD：95bb698b
origin/master：a72f41fb
本地 ben HEAD：4ec7f188
origin/ben：4ec7f188
03 仓库 HEAD：4ec7f188
03 工作区：干净
```

master 开始处理本次历史文档前有 10 个与本轮架构更新相关的未提交文件；
ben 分支本轮改动已提交并推送。

## 三、25 款新游戏核对与开放

### 3.1 巴西

`platform-api/conf/domains` 已显式包含以下游戏：

```text
PP 6 款：
5770, 5648, 5955, 5787, 5963, 5899

TADA 8 款：
610, 674, 40, 49, 403, 43, 678, 720

G759 11 款：
6900, 6138, 6145, 6901, 6118, 6112, 6146, 6125, 6142, 6130, 6131
```

PP、G759 和 TADA 的 `40/49/403/43` 写入
`SPECIAL_GAMES_OPEN_20261028`；TADA `610/674/678/720`
保留在 `SPECIAL_GAMES_v5`。

### 3.2 香港

`platform-api/conf/domains-hk` 同步包含全部 25 款游戏。香港使用独立的
静态、动态和 CDN Host，不复用巴西域名。原 `tada-static5-aws.cxkerui.com`
无法解析，因此只保留已验证的 Ali/CF 静态 Host；TADA 动态 Host 使用
`tada-games.hkcloudplay01/02.com`。

### 3.3 校验

`scripts/validate_domains.py` 已增加规则，要求 20261028 新游戏在巴西和
香港都必须显式出现，并校验 TADA 已知静态/动态分流。

```text
DOMAIN_CONFIG_OK
BR_PP_MATCH
BR_TADA_MATCH
BR_G759_MATCH
HK_PP_MATCH
HK_TADA_MATCH
HK_G759_MATCH
```

线上 `open_game_list` 已包含全部 25 款游戏，本次未修改该清单。

从巴西 03 网络对 25 款静态入口抽测，全部返回 HTTP 200。

### 3.4 Git

```text
6c943e00 fix(games): 显式开放巴西20261028新游戏
4ec7f188 fix(domains): 香港同步开放20261028新游戏
```

两笔提交均已推送至 `origin/ben`；巴西 03 已快进到 `4ec7f188`，
源码与巴西/香港运行目录逐文件一致。

## 四、香港 TADA 接入与 Nginx 修复

排查发现香港 Nginx 的动态 upstream 仍指向旧公网地址：

```text
18.163.34.9
43.198.52.147
```

当时香港后端实际内网地址为：

```text
203.0.113.1
203.0.113.1
```

这会让 PP/TADA/G759 动态请求返回 502。已把全部香港动态 upstream
切换为当前内网地址，并增加 TADA HTTP `9096` upstream。

香港 01、02 已按顺序启动 `game-service-tada-prod`，`9096` 正常监听。
`nginx -t` 通过后完成 reload。

操作前备份：

```text
/etc/nginx/sites-available/dbqp-hongkong.conf.bak-20261103-123139-tada-enable
/etc/nginx/sites-available/dbqp-hongkong.conf.bak-20261103-123247-private-upstreams
```

从巴西 03 复测：

```text
PP/TADA/G759 五个香港动态域名 /health：HTTP 200
25 款新游戏静态入口：HTTP 200
```

## 五、巴西游戏无法进入的排查

### 5.1 已排除

```text
巴西 Nginx：active，配置测试通过，80/443 正常监听
巴西 upstream：均为当前内网 203.0.113.1/.4/.5/.14/.15
近期 Access Log：未发现集中性 502/503/504 上游连接错误
四台后端：停止维护前主机、容器和端口均正常
```

因此，本次不是 JSON 未开放、静态资源缺失或 Nginx upstream 错配导致的
全厂家故障。

### 5.2 后端原始错误归类

以下内容已脱敏，仅保留故障类别：

```text
API：
接口执行超时 | 异步函数: p_login | 耗时约 29.99s
p_register 超时
余额/钱包请求超时

G759：
AuthenticationError 401
读取平台用户缓存超时
WalletOperationError 502
redis.exceptions.TimeoutError: Timeout connecting to server

TADA：
Redis exception: Timeout connecting to server
user_type_conditions not exist
user_level_configs not exist
common_req 超时

PP：
html5Game / gameService / reloadBalance / saveSettings 超时
```

G759 的异常同时影响旧游戏和新游戏，证明问题位于共享缓存、数据库或钱包
依赖，而不是某一批游戏配置。开发随后确认数据库卡住。

TADA 日志还记录了个别智利来源 IP 被地区白名单拦截，但该问题不解释
全厂家、全用户范围的超时，属于并列的局部现象。

## 六、停服操作与恢复边界

开发最初要求依次重启巴西服务器；随后明确更正为“服务器不需要重启，
只重启上面的容器”。BR01、BR02 在更正前已经发生系统重启，BR04、BR05
没有重启；更正后未再重启任何服务器。

随后用户发布数据库维护通知，并要求关闭四台巴西后端的全部业务容器。
最终状态：

| 节点 | 主机 | `game-service*` 运行数 | 主机状态 |
| --- | --- | ---: | --- |
| BR01 | 34.39.183.154 | 0 | 在线 |
| BR02 | 34.95.230.202 | 0 | 在线 |
| BR04 | 34.39.208.57 | 0 | 在线 |
| BR05 | 34.95.187.142 | 0 | 在线 |

监控代理保持运行。业务容器不会自动启动。

### 恢复门禁

必须同时满足：

1. DBA 明确数据库维护完成；
2. 用户明确通知可以恢复巴西业务容器；
3. BR01 启动并通过容器、端口、镜像 ID、日志和业务调用检查；
4. BR01 稳定后，才允许开始 BR02，再依次 BR04、BR05。

任一台失败立即停止后续节点，保留已正常节点，不扩大故障范围。

## 七、群通知

```text
751：巴西 25 款游戏配置开放
752：香港接入进度及 TADA 缺口
753：巴西恢复计划/开始 BR01
754：BR01 重启完成
762：BR01 业务容器关闭
765：BR02 业务容器关闭
766：BR04 业务容器关闭
767：BR05 业务容器关闭，四台全部停止
768：复核四台容器数均为 0，等待 DBA 维护完成
770：本次排查、香港修复与维护状态汇总
771：完整事件文档
```

## 八、回滚与注意事项

- 香港 Nginx 可使用上述两份备份恢复；
- 巴西/香港 JSON 由 ben `4ec7f188` 维护，不使用服务器手工改动作为源；
- 当前不要用旧 stash 覆盖 03 的最新配置；
- 恢复前重新确认当前镜像标签，再执行
  `/data/server-runtime/start.sh all <已确认标签>`；
- 不把 SSH 密码、GitLab 内嵌凭据、Telegram Token、钱包凭据或用户数据写入
  文档和群消息。

## 九、Git 收尾

ben 分支代码已提交并推送。master 分支的架构说明、香港 Nginx 镜像配置、
工作台状态和本文档在本地提交；提交 SHA 和发群结果在完成后补记到工作台。

## 十、后续维护

2026-11-03 BR01 启动验证时，Redis 已手动关闭且 DBA 网络尚未放通，
容器因外部依赖未恢复而发生 Sanic worker 启动超时。随后 BR01 再次全停，
详见：

`docs/history/2026-11-03-2145-【维护】BR01启动验证失败与Redis网络未放通停服记录.md`
