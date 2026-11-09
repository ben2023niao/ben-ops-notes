---
id: "doc-4ae05bd900ff"
title: "后端发布后 CPU 复核与慢请求定位"
date: "2026-10-24T18:55:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "Nginx", "Redis", "监控告警", "自动化"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-24-1855-%E3%80%90%E6%8E%92%E6%9F%A5%E5%88%86%E6%9E%90%E3%80%91%E5%90%8E%E7%AB%AF%E5%8F%91%E5%B8%83%E5%90%8ECPU%E5%A4%8D%E6%A0%B8%E4%B8%8E%E6%85%A2%E8%AF%B7%E6%B1%82%E5%AE%9A%E4%BD%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-24-1855-【排查分析】后端发布后CPU复核与慢请求定位.md"
sourceSha256: "414dd7ca219c455ee6675eed29c4e22fda97d40bdb1a844c6e1c623307fed479"
sourceSystem: "project-doc"
---

# 后端发布后 CPU 复核与慢请求定位

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610241855-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BPython-%E5%90%8E%E7%AB%AF%E5%8F%91%E5%B8%83%E5%90%8E%20CPU%20%E5%A4%8D%E6%A0%B8%E4%B8%8E%E6%85%A2%E8%AF%B7%E6%B1%82%E5%AE%9A%E4%BD%8D.md)

> 整理日期：2026-10-24 18:55｜日期依据：文件名日期

- 时间：2026-10-24 18:00–18:55（Asia/Manila）
- 环境：游点涩正式环境
- 后端版本：`3af017b4cc11`（上一版 `2d448edb5814`，回滚点 `67a561b7d2d4`）
- 结论：Beszel 数据显示发布后整机 CPU 没有上涨；当前 CPU 约 10%–12%、
  load 约 1.5–2.0，属于16核服务器的正常业务负载，不需要回滚或重启。

## 一、发布与版本

- 18:26 后端 web/nginx/cron 重建为 `main-3af017b4cc11`。
- 新 H5/PC 容器启动时间仍为 10-21：H5 `aeb90b6`，PC `0d6c9c7`。
- 因此本次“前端代码发布”没有产生新的 H5/PC 运行容器；如预期新前端版本已发布，需要确认发布目标或静态资源同步流程。
- 线上后端 HTTP、Session、Hosts、Redis、MongoDB、队列均正常。

## 二、CPU 对比

Beszel 发布前后3小时的 1 分钟采样：

| 区间 | 样本 | CPU均值 | CPU峰值 | load均值 | 内存均值 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 发布前 | 78 | 11.22% | 13.64% | 1.81 | 13.62% |
| 发布后 | 30 | 10.87% | 12.49% | 1.77 | 13.44% |

发布后 CPU 反而比发布前低约 0.35 个百分点，没有发现发布引入的持续 CPU 抬头。

即时 `docker stats` 中 web 容器为 63%–131%，是 Docker 的“单核百分比”：

- 16核服务器上的 100% 只等于 1 个核；
- 109% 约等于 1.09 核，占整机约 6.8%；
- 同期整机 CPU 约 5%–15%，PHP-FPM 48/128 个子进程，无进程池耗尽。

## 三、请求量与错误对比

| 指标 | 发布前 18:00–18:19 | 发布后 18:26–18:52 |
| --- | ---: | ---: |
| 请求量 | 199,536 | 276,461 |
| 每分钟 | 9,977 | 10,239 |
| 每秒 | 约166 | 约171 |
| 变化 | - | +3% |

请求结构基本一致，TOP 仍是埋点、`system/info`、配置、首页、游戏详情和 SDK 校验。

发布后错误量没有增加：

- 错误日志：发布前391条/20分钟；发布后166条/26分钟；
- `exposure_collect_log` 重复写错误：141→138，按分钟归一化后下降；
- 支付慢请求：36→24；
- PHP-FPM 慢请求：28→66，按分钟归一化约1.4→2.5条/分钟，仍只占请求约0.024%。

## 四、新功能与数据库

13个新集合全部为0条，`user_group` 只有15条：

`drama`、`drama_episode`、`drama_tag`、`drama_recommend_user`、
`drama_search_history`、`drama_recommend`、`drama_vip_config`、
`drama_watch_day`、`drama_history`、`drama_favorite`、`drama_unlock_log`、
`user_member_benefit` 等。

发布后日志中没有 drama API 请求，因此新剧集功能不是当前 CPU 来源。

MongoDB ReplicaSet：

- 主库：PRIMARY，health=1
- 从库02：SECONDARY，health=1
- 从库01：SECONDARY，health=1
- currentOp 无长查询和锁等待。

## 五、慢请求热点

发布后26分钟共66条慢请求：

- PageVisit `upsertGuest`：17条；
- 支付外部 HTTP：11条；
- 后台报表 `aggregate`：6条；
- 其余为低频后台/管理查询。

建议：

- PageVisit：检查 `page_visit_log` 的查询索引和幂等 upsert 竞争；
- 支付：为第三方 HTTP 设置更严格的连接/总超时并异步化通知；
- 后台报表：限制首页自动刷新频率，聚合查询走缓存或预聚合。

## 六、发布代码中发现的问题

### 1. 请求日志覆盖全部 API

`BaseApiController::logApiRequest()` 中的 `shouldLogApiRoute()` 被注释，导致所有 API 请求都执行
JSON 编码并追加写 `api_request-*.log`；`LogUtil::writeToFile()` 使用 `LOCK_EX`。

当前日志增长速度：

- `api_request`：约237MB；
- `api_response`：约430MB；
- 两者合计在约53分钟内增长约667MB。

建议开发恢复路由过滤或改为异步/采样写日志。该问题会增加一定 CPU 和 I/O，但当前没有把服务器打满。

### 2. 日志脱敏只处理第一层

`maskSensitiveFields()` 只遍历数组第一层。当前当天 `api_response` 中检测到：

- 约60,883行含嵌套 password；
- 约14,722行含嵌套 token。

说明本次发布的日志脱敏未覆盖嵌套用户对象，存在敏感信息落日志风险。
建议递归处理并扩展字段规则，不需要输出任何实际敏感值。

### 3. 旧错误日志信息不完整

`MongoModel.php:238` 相关错误只记录 `" in ... line 238"`，缺少真实的 duplicate key/异常原因，
建议在脱敏后保留异常类型和关键字段，便于后续定位。

## 七、结论与建议

- 当前 CPU 没有异常，不建议回滚。
- 优先开发侧优化：API 日志过滤/异步化、递归脱敏、PageVisit upsert、支付外呼超时。
- 如后续 Beszel 整机 CPU 连续超过60%或 load 超过24，再按容量/数据库/请求热点继续排查。

## 八、可复用只读快照

脚本：

`ops/production/scripts/backend-performance-snapshot.py`

在线上后端执行：

```bash
python3 backend-performance-snapshot.py --sample-seconds 10
```

输出包括：

- 16核整机 CPU、load、内存；
- web 容器单核 CPU%、内存、网络和块设备；
- PHP-FPM 子进程数；
- API 请求 QPS；
- 最近10万行请求的接口分布、唯一IP和登录用户数；
- API request/response 日志大小；
- PHP-FPM 慢日志总条数。

脚本只读，不打印请求体、密码、token 或任何敏感值。
