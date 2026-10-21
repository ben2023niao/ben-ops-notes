---
id: "doc-9cde3b7f4c29"
title: "【安全事件】客服工单 SQLi 探测、MongoDB 正则注入取证及修复建议"
date: "2026-10-21T19:05:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "MySQL", "监控告警", "自动化", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-1905-%E3%80%90%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%E3%80%91%E5%AE%A2%E6%9C%8D%E5%B7%A5%E5%8D%95SQLi%E6%8E%A2%E6%B5%8B-MongoDB%E6%AD%A3%E5%88%99%E6%B3%A8%E5%85%A5%E5%8F%96%E8%AF%81%E5%8F%8A%E4%BF%AE%E5%A4%8D%E5%BB%BA%E8%AE%AE.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-1905-【安全事件】客服工单SQLi探测-MongoDB正则注入取证及修复建议.md"
sourceSha256: "2ec193d867a76dc64df8388395b3f71c6f2ed885a889adf59e58823126c46ed0"
sourceSystem: "project-doc"
---

# 【安全事件】客服工单 SQLi 探测、MongoDB 正则注入取证及修复建议

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-1905-【安全事件】客服工单SQLi探测-MongoDB正则注入取证及修复建议.md`

> 整理日期：2026-10-21 19:05｜日期依据：文件名日期

- 文档时间：2026-10-21 19:05（CST）
- 环境：游点涩线上环境（main）
- 正式业务版本：`688f43568c2e`
- 事件等级：P1（明确自动化注入授权安全测试；未发现 SQL 注入成功；存在真实 MongoDB 正则注入面及敏感响应/日志问题）
- 授权安全测试身份：`md15183` / `userId=11762221` / 固定 `deviceId=ccd909e8-88be-459d-9bab-382812696928`
- 关联工单：客服工单 `#3648`

## 一、结论先行

1. 这不是一条普通客服工单，而是同一账号、同一设备对登录、社区、评论、工单、充值、用户资料、积分等 **44 个接口**进行的自动化 SQL 注入扫描。
2. 10-21 当天该账号/设备共有 **1,638 条**请求，其中 **429 条**带明确 SQLi 特征；主要授权安全测试窗口内，目标请求全部返回 HTTP `200`。
3. **没有证据证明 `SLEEP(8)` 执行成功**。工单链路使用 MongoDB，不存在 SQL 引擎；payload 被当作普通字符串写入数据库。
4. 但“没有 SQL 后端”不等于没有注入问题：`Post/getPostTagList` 把用户输入直接作为 MongoDB `$regex` 使用，已实际触发 `Regular expression is invalid`，属于**正则注入/潜在 ReDoS**。
5. 工单接口没有阻止恶意 payload 落库。`#3648` 的标题被更新为 `r9' AND (SELECT SLEEP(8))-- `，该工单下同时产生了 10 条测试内容。
6. 另发现独立的高风险问题：`/api/sdk/system/info` 的响应以及 `api_response` 日志中存在明文 `password` 字段。本文不记录实际密码值；开发应立即停止返回密码并给响应日志增加递归脱敏。
7. 2026-10-21 19:20:07 已按授权在生产创建隔离测试工单 `#3649`，接口返回 `HTTP 200 / status=y`，标题和正文都明确标记为 `OPS-SECURITY-TEST-20261021`，用于开发直接查看漏洞效果。测试使用 `userId=0`、专用 deviceId 和一次性临时会话；临时会话已删除。

## 二、事件时间线

| 时间（CST） | 事件 | 证据 |
| --- | --- | --- |
| 2026-10-20 21:20:53 | 授权安全测试账号 `md15183` 注册，注册 IP `203.27.106.138`，`is_test=0` | 线上 `user` 集合 `_id=11762221` |
| 2026-10-21 00:18:31 | 同一账号/设备开始访问线上业务 | `api_request-2026-10-21.log` |
| 00:40:58–12:01:20 | `160.202.167.53` 发起 15 条带 SQLi 特征的早期探测，并伴随大量接口枚举 | 应用日志、Nginx access |
| 13:12:11–13:27:05 | `203.27.106.138` 发起 360 条 SQLi 探测 | 应用日志、Nginx access |
| 13:14:28 | 创建客服工单 `#3648` | MongoDB `user_feedback_list._id=3648` |
| 13:28:26–13:34:23 | 来源切换到 `203.10.98.186`，继续 54 条探测 | 应用日志、Nginx access |
| 13:30:22 | 向 `Post/getPostTagList.keyword` 注入含 `COUNT(*)` 的表达式 | logId `857ce9184a8005d9` |
| 13:31:55 | 再次注入同类表达式 | logId `84a1cd5dac5503de` |
| 13:33:22 | `UserFeedback/addFeedbackList.title` 提交 `r9' AND (SELECT SLEEP(8))-- ` | logId `ae6d0469c972c38a`；工单 `updated_at=13:33:22` |
| 17:00–17:02 | 其他来源继续做 UNION/EXTRACTVALUE 类扫描，未复用同一设备身份 | 应用日志 |

## 三、授权安全测试画像与规模

### 3.1 总量

```text
同一账号/设备请求总数：1,638
带明确 SQLi 特征：429
覆盖 action：44
最早 SQLi 特征：2026-10-21 00:40:58
最晚同一身份 SQLi 特征：2026-10-21 13:34:23
固定设备标识：ccd909e8-88be-459d-9bab-382812696928
```

429 条请求中检测到的特征包括：

| 特征 | 次数 |
| --- | ---: |
| `SLEEP(...)` | 221 |
| 布尔条件 `'1'='1` / `'1'='2` | 111 |
| `UNION SELECT` | 55 |
| `EXTRACTVALUE(...)` | 25 |
| `information_schema` | 19 |

> 注：一条 payload 可能同时包含多个特征，因此特征次数不能直接相加。

### 3.2 来源与响应

| 来源 IP | SQLi 特征请求 | 时间范围 | 窗口内 Nginx 请求/状态 | UA 特征 |
| --- | ---: | --- | --- | --- |
| `203.27.106.138` | 360 | 13:12:11–13:27:05 | 668 / `200=668` | 主要是 Chrome 136 Windows |
| `203.10.98.186` | 54 | 13:28:26–13:34:23 | 152 / `200=152` | Chrome 136、HeadlessChrome、Dart 交替 |
| `160.202.167.53` | 15 | 00:40:58–12:01:20 | 816 / `200=414, 404=400, 400=2` | 大量接口枚举与通知接口探测 |

补充：

- `203.27.106.138` 是该账号注册 IP。
- `203.10.98.186` 与前一 IP 复用同一登录账号和设备 ID，说明来源 IP/UA 在轮换，但授权安全测试身份没有变化。
- `203.27.106.138` 在授权安全测试窗口内 668 条请求全部返回 `200`，表示应用层没有统一拒绝恶意参数。
- `160.202.167.53` 窗口内有 400 条 `404`，符合路径/接口字典扫描特征。

### 3.3 目标接口

| 接口 action | 探测次数 |
| --- | ---: |
| `UserFeedback/addFeedbackList` | 31 |
| `Post/getPostTagList` | 29 |
| `comment/doComment` | 23 |
| `post/addPost` | 21 |
| `system/track` | 18 |
| `UserFeedback/addFeedbackContent` | 18 |
| `User/bindEmail` | 18 |
| `post/getPostList` | 17 |
| `login/upPass` | 16 |
| `tracking/record` | 14 |
| `User/doUpdate` | 13 |
| `User/getCommunityInfo` | 12 |
| `pointMall/index` | 12 |
| `userTask/claimReward` | 12 |
| `user/bindParent` | 12 |
| `Recharge/create` | 12 |
| `login/account` | 11 |
| `login/username` | 11 |
| `User/getUserFollowList` | 10 |
| `game/detail` | 9 |
| `login/email` | 9 |
| `system/gameTrack` | 8 |
| `UserProduct/getProductList` | 7 |
| `game/zoneList` | 7 |
| `userSign/doSign` | 6 |
| `post/meJoinPostList` | 5 |
| `pointMall/gPointList` | 5 |
| `vipGrowth/getGrowthLogList` | 5 |
| `TransactionLog/lists` | 5 |
| `userTask/getTaskList` | 5 |
| `userTask/getPointLogs` | 5 |
| `User/getUserDownloadList` | 5 |
| `Recharge/history` | 5 |
| `post/getAllPost` | 5 |
| `post/doLove` | 5 |
| `user/info` | 5 |
| `configDict/getConfigDict` | 4 |
| `user/bindEmail` | 4 |
| `recharge/history` | 2 |
| `game/buy` | 2 |
| `announcement/getAnnouncement` | 2 |
| `spend/create` | 2 |
| `game/download` | 1 |
| `spend/create2` | 1 |

## 四、工单 #3648 的落库证据

应用原始请求：

```json
{
  "logId": "ae6d0469c972c38a",
  "data": {
    "method": "POST",
    "url": "/api/v1/UserFeedback/addFeedbackList",
    "action": "UserFeedback/addFeedbackList",
    "ip": "203.10.98.186",
    "deviceType": "web",
    "deviceTypeNew": "h5_web",
    "deviceId": "ccd909e8-88be-459d-9bab-382812696928",
    "version": "2.1.1",
    "userId": 11762221,
    "params": {
      "title": "r9' AND (SELECT SLEEP(8))-- ",
      "content": "r9ctl",
      "game_id": 685,
      "category_code": "game",
      "images": []
    }
  },
  "time": "2026-10-21 13:33:22"
}
```

Nginx 同一秒的访问记录：

```text
203.10.98.186 - - [21/Oct/2026:13:33:22 +0800]
"POST /api/v1/UserFeedback/addFeedbackList HTTP/1.1" 200 88
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/136.0.0.0 Safari/537.36"
peer=203.0.113.1
```

MongoDB 最终记录（只展示安全相关字段）：

```json
{
  "_id": 3648,
  "user_id": 11762221,
  "game_id": 685,
  "category_code": "game",
  "title": "r9' AND (SELECT SLEEP(8))-- ",
  "content": "r9probe feedback content",
  "account": "md15183",
  "status": 0,
  "created_at": "2026-10-21 13:14:28",
  "updated_at": "2026-10-21 13:33:22"
}
```

同工单的内容集合共有 **10 条**测试内容，其中可见：

```text
r9probe feedback content
r9x' UNION SELECT 1--
r9ctl feedback content
r9x' AND '1'='1
r9x' AND (SELECT SLEEP(3))--
r9ctl
```

结论：

- payload 以普通字符串落库，数据库未把 `SLEEP` 当作 SQL 执行。
- 工单接口没有把该请求识别为授权安全测试或拒绝。
- 当前逻辑会更新同一用户的最后一条工单，随后追加内容，导致授权安全测试测试反复污染同一工单。

## 五、为什么不是 SQL 注入成功

### 5.1 工单链路是 MongoDB

```text
UserFeedbackController
  -> UserFeedbackListRepository
  -> UserFeedbackListService::addFeedbackList()
  -> UserFeedbackListModel
  -> MongoModel
  -> MongoDB\Driver\Manager::executeCommand()
```

工单模型是 `user_feedback_list` MongoDB 集合，代码中没有把 `title/content` 拼接成 SQL 字符串，也没有 MySQL/PDO/SQL Server 调用。

### 5.2 SLEEP(8) 未触发慢请求

```text
PHP-FPM request_slowlog_timeout = 3s
13:12–13:35 PHP-FPM slow.log 对应时间段条目 = 0
13:33:22 工单请求最终 HTTP 200，MongoDB 在 13:33:22 更新成功
```

若 SQL `SLEEP(8)` 被真实执行，请求会超过 3 秒并应出现 PHP-FPM 慢栈。实际未出现对应慢栈。

### 5.3 但存在真实 MongoDB 正则注入

线上 `PostRepository::getPostTagList()`：

```php
$keyword = trim(self::getRequest($request, 'keyword', 'string', ''));
$items = PostTagModel::find(
    ['status' => 1, 'name' => ['$regex' => $keyword, '$options' => 'i']],
    ['_id', 'code', 'name'],
    ['created_at' => -1],
    0,
    50
);
```

`keyword` 未经过 `preg_quote()`、长度上限或字符白名单，直接进入 MongoDB 正则引擎。

已关联的应用错误：

| 时间 | logId | HTTP/错误 | 说明 |
| --- | --- | --- | --- |
| 13:30:26 | `857ce9184a8005d9` | `Regular expression is invalid: nothing to repeat` | payload 中的 `COUNT(*)` 被当作正则语法 |
| 13:31:56 | `84a1cd5dac5503de` | 同上 | 同类表达式再次触发 |

调用栈：

```text
MongoDbConnection.php:68
  -> MongoModel.php:143
  -> PostRepository.php:44
  -> PostController.php:25
```

风险：

- 正则表达式可被授权安全测试者控制，可能导致查询语义改变、异常和潜在 ReDoS。
- 当前至少已确认“非法正则导致接口异常”，授权安全测试者可以继续尝试高复杂度正则造成 CPU 峰值。

## 六、输入校验与日志安全问题

### 6.1 生产输入层

线上 `RequestService::word()` 已将旧的 SQL/XSS 黑名单停用，当前主要返回原始字符串。该做法避免了英文正常文本被整段清空，但意味着不能再用旧黑名单作为安全边界。

工单入口当前只做：

- 非空校验；
- 标题 200 字、内容 1,000 字上限；
- 图片格式校验；
- `basicHtmlFilter()`；
- 固定 key 的 MongoDB 查询。

`basicHtmlFilter()` 不能替代输出编码，也不能证明其他接口安全。

### 6.2 明文密码响应

线上 `/api/sdk/system/info` 和用户信息响应中观察到 `password` 字段，且 `api_response` 日志会记录完整响应。

本文只记录字段路径，不记录任何实际值：

```text
action: system/info
url: /api/sdk/system/info
response.data.user.敏感凭据：[已脱敏]
```

代码位置：

```text
ApiV1/SystemRepository.php:184  'password' => strval($showPass)
ApiV1/UserRepository.php:100    'password' => strval($showPass ?: '')
BaseApiController.php:190-211   sendResult() -> logApiResponse()
```

风险：

- 密码对客户端暴露，扩大账号接管面。
- 完整响应写日志，导致密码、token、邮箱、用户资料进入磁盘；日志被下载、打包或转发时会造成二次泄露。
- 本文档及群通知禁止包含实际密码、token、邮箱值。

## 七、当前数据影响范围

### 已确认

- `user_feedback_list._id=3648` 标题被更新为 SLEEP payload。
- `user_feedback_content` 中该工单关联 10 条测试内容。
- 至少 2 条 `Post/getPostTagList` 请求进入 MongoDB 正则引擎并触发错误。
- 授权安全测试账号 `md15183` 是正式环境普通账号（`is_test=0`）。

### 未确认

- 没有证据表明 SQL 数据库被读取、修改或写入。
- 没有证据表明 Mongo 文档被执行任意脚本；payload 为字符串。
- 由于部分 API 响应日志被路由白名单跳过，无法从响应日志逐条还原所有接口最终业务结果。
- 未对线上数据库做批量删除或修改；所有取证均为只读。

## 八、开发修复顺序

### P0：阻断同类授权安全测试继续落库

1. **工单、帖子、评论等文本入口**
   - 明确字段类型，拒绝数组、对象和 `null` 之外的非预期结构。
   - 增加最大长度、控制字符和异常字符策略。
   - 不要把 SQLi 黑名单当成唯一防线；用户文本应作为数据保存，在输出侧安全编码。

2. **MongoDB 正则接口**
   - 所有 `$regex` 输入使用 `preg_quote($keyword, '/')`。
   - 设置长度上限，例如 64 或 100 字符。
   - 禁止空正则、超长正则和未经转义的用户输入直接进入 `MongoDB\BSON\Regex`。
   - 建议对搜索结果使用普通文本匹配或前缀匹配；不要允许任意复杂正则。

3. **所有 Mongo 查询参数**
   - 标量字段禁止传数组；例如 `foo=1` 与 `foo[$ne]=1` 必须在入口区分并拒绝后者。
   - 禁止用户控制查询运算符、字段名、`$where`、`$expr`、`$function`。
   - 数值字段统一 `intval/floatval`，枚举字段使用白名单。
   - 如必须接收 JSON，使用严格 schema 校验，不直接透传 `$_REQUEST`。

4. **工单接口增加滥用控制**
   - 按 `userId + deviceId + IP` 组合限流，不只按 userId。
   - 检测同一 payload 在 1 分钟内跨多个接口重复出现，直接返回 400/403 并写安全审计。
   - 对工单标题/内容做“重复内容、控制字符、超长表达式、注入特征”审计；不要静默丢弃证据。
   - 同一用户频繁测试时，应将请求放入隔离审计队列，不得覆盖正常客服工单。

### P0：停止泄露敏感响应

1. 从所有面向客户端的响应中删除 `password`、`show_pass`、token、验证码、内部密钥等字段。
2. `api_response` 日志增加递归脱敏：

```text
password / passwd / show_pass / token / access_token / refresh_token
authorization / cookie / secret / secret_key / private_key
email / phone（按业务要求掩码）
```

3. 日志只保留 `action`、`url`、状态、耗时、响应大小、错误码、payload 哈希和安全审计 ID；不要默认记录完整响应体。
4. 对已有响应日志做敏感字段扫描和隔离，禁止直接整包发群或发开发；如需交付，先脱敏。

### P1：输入输出与审计

1. 管理后台输出工单标题/内容时统一 HTML 转义；不能依赖存储时过滤。
2. 记录安全事件审计：
   - 时间、IP、userId、deviceId、action；
   - payload 的 SHA-256/hash，不打完整敏感内容；
   - 命中规则、响应状态、是否落库；
   - 命中后生成安全事件编号，供客服/开发追踪。
3. 客服工单增加“恶意/测试/授权安全测试”状态，不把探测内容当普通客户问题展示或直接回复。

## 九、网关/WAF 施工建议

不要把单个单引号直接作为全局 444 条件，否则会误伤正常用户输入。建议采用组合规则：

```text
命中高风险表达式（SLEEP(、BENCHMARK(、UNION SELECT、EXTRACTVALUE(、
information_schema、明显的布尔注入组合）
同时满足：同一 IP/设备在短窗口内跨多个接口重复访问
动作：先 400/403 + 记录证据 + 安全告警；确认误伤范围后再自动封禁
```

上线前必须验证：

- 正常中文、英文、单引号、普通富文本不被误伤；
- 恶意 payload 不再返回 `200`；
- 被拦截请求不会写入工单、帖子、评论或其他业务集合；
- 拦截消息不包含 payload 中的个人信息或密码。

## 十、验收清单

### 单元/集成测试

```text
1. Post/getPostTagList:
   keyword=*
   keyword=(
   keyword=r9' AND (SELECT COUNT(*) FROM information_schema.tables)--
   预期：作为普通文本处理或 400；不得出现 Mongo regex 异常，不得产生慢查询。

2. UserFeedback/addFeedbackList:
   title=r9' AND (SELECT SLEEP(8))--
   预期：400/403；安全审计有记录；user_feedback_list/user_feedback_content 不新增授权安全测试内容。

3. 工单正常输入:
   中文、英文、单引号、换行、正常标点
   预期：按普通文本成功保存，不在入口误删。

4. 数组参数:
   title[$ne]=1、user_id[$gt]=0、category_code[$regex]=.*
   预期：400；禁止数组进入标量 Mongo 查询。

5. 正则复杂度:
   构造 1k/10k 字符输入及高复杂度表达式
   预期：400 或安全截断，CPU 和响应时间有上限。

6. 响应/日志:
   /api/sdk/system/info、登录、用户信息
   预期：响应无 password/token；api_response 无明文敏感字段。
```

### 线上观测

```text
1. 新授权安全测试 payload 返回 400/403/429，不再返回 200。
2. error-YYYY-MM-DD.log 不再出现由用户输入触发的 Regex 语法错误。
3. php-fpm/slow.log 不再出现同类异常查询慢栈。
4. 安全审计可按 userId/deviceId/IP/action 查询。
5. web/cron 容器重启、发布和配置同步后规则仍生效。
```

## 十一、回滚与证据保全

- 本次仅做只读取证，没有修改代码、数据库、网关或防火墙。
- 不得删除工单 `#3648` 及其内容记录，先导出脱敏证据并备份；如业务需要隐藏，先变更为内部隔离状态。
- 修复发布前保留以下证据：
  - 应用 `api_request` 原始行；
  - Nginx access 原始行；
  - `error` 日志及 logId；
  - `slow.log` 的阈值和时间段统计；
  - 工单 MongoDB 记录（不含密码、token 等无关敏感字段）。
- 涉及密码/token 的响应日志必须隔离，不得直接复制到工单、群聊或代码仓库。

## 十二、证据文件位置

正式后端 `16.209.16.108`：

```text
/opt/docker-youdianse-php/runtime/app-logs/api_request-2026-10-21.log
/opt/docker-youdianse-php/runtime/app-logs/api_request-2026-10-21.log-*
/opt/docker-youdianse-php/runtime/app-logs/error-2026-10-21.log
/opt/docker-youdianse-php/runtime/app-logs/php-fpm/slow.log
/opt/docker-youdianse-php/runtime/nginx-logs/access.log
/opt/docker-youdianse-php/runtime/nginx-logs/access.log-*
```

本仓库内已附脱敏证据摘要：

```text
docs/evidence/2026-10-21-1905-客服工单SQLi探测/证据摘要.json
docs/evidence/2026-10-21-1905-客服工单SQLi探测/工单3648证据还原.html
docs/evidence/2026-10-21-1905-客服工单SQLi探测/工单3648证据还原.png
docs/evidence/2026-10-21-1905-客服工单SQLi探测/工单3649生产测试复现.html
docs/evidence/2026-10-21-1905-客服工单SQLi探测/工单3649生产测试复现.png
```

关键关联键：

```text
工单请求 logId: ae6d0469c972c38a
正则异常 logId: 857ce9184a8005d9 / 84a1cd5dac5503de
授权安全测试账号: md15183 / 11762221
设备 ID: ccd909e8-88be-459d-9bab-382812696928
工单 ID: 3648
```

## 十三、群通知记录

| 步骤 | 内容 | 18GAME_ 上线群 | 18game运维 |
| --- | --- | --- | --- |
| 1 | 版本、远程和工作区基线 | 13637 | 118514 |
| 2 | 授权安全测试面与授权安全测试画像 | 13640 | 118518 |
| 3 | 根因定位与开发修复方向 | 13642 | 118519 |
| 4 | 汇总文档 + 脱敏证据摘要 | 13643 | 118521 |
| 5 | Git 提交与验证结果 | 待发送 | 待发送 |

## 十四、敏感信息声明

本文不包含 Telegram token、chat_id、SSH 密码、发布密码、私钥、Git 凭据或任何用户明文密码。授权安全测试 IP、设备 ID、接口名、logId 和统计结果用于安全取证，可在内部安全事件范围内流转。
