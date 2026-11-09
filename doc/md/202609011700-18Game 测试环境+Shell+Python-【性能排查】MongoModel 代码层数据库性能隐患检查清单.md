---
id: "doc-596495a30b93"
title: "【性能排查】MongoModel 代码层数据库性能隐患检查清单"
date: "2026-09-01T17:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Redis", "监控告警", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-01_1700-%E3%80%90%E6%80%A7%E8%83%BD%E6%8E%92%E6%9F%A5%E3%80%91MongoModel%E4%BB%A3%E7%A0%81%E5%B1%82%E6%95%B0%E6%8D%AE%E5%BA%93%E6%80%A7%E8%83%BD%E9%9A%90%E6%82%A3%E6%A3%80%E6%9F%A5%E6%B8%85%E5%8D%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-01_1700-【性能排查】MongoModel代码层数据库性能隐患检查清单.md"
sourceSha256: "d14d2f4ca07333ef80374cf96454378e79f9a9728fa103ee80aae2fc39e07f81"
sourceSystem: "project-doc"
---

# 【性能排查】MongoModel 代码层数据库性能隐患检查清单

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609011700-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E3%80%90%E6%80%A7%E8%83%BD%E6%8E%92%E6%9F%A5%E3%80%91MongoModel%20%E4%BB%A3%E7%A0%81%E5%B1%82%E6%95%B0%E6%8D%AE%E5%BA%93%E6%80%A7%E8%83%BD%E9%9A%90%E6%82%A3%E6%A3%80%E6%9F%A5%E6%B8%85%E5%8D%95.md)

> 整理日期：2026-09-01 17:00｜日期依据：文件名日期

环境标签：测试环境 / 后端 / MongoDB / MongoModel / 性能隐患

时间：2026-09-01

## 1. 结论速览

后端数据层为自研 `App\Core\Mongodb\MongoModel`（基于 PHP 官方 `MongoDB\Driver`），本次按代码仓库 `root/18game_php.git`（dev 分支，814 个 PHP 文件）做静态扫描，发现以下高危隐患点：

| 隐患 | 命中规模 | 风险等级 |
| --- | --- | --- |
| 全表扫描型查询（limit=9999999/99999999） | 45+ 处 | 高 |
| 无条件 `find()` / `find([])` | 6 处 | 高 |
| 报表聚合（aggregate）未逐条核验 limit | 29 处调用（报表 Job 为主） | 中高 |
| 大内存单次拉取（用户/游戏全量集合） | 多服务多处 | 中高 |
| `findByID` 透传字符串/整型 `_id` | 大量调用（依赖模型约定，需核验） | 中 |
| 大字段进 Redis 缓存（历史 3.6MB 事故同型） | 配置类服务仍整包缓存 | 中 |
| 报表 Job 每任务多次 aggregate（从库） | TotalOldDay/TotalMinute 等 | 中（走从库缓解） |

## 2. 检查方法（可直接复跑）

```bash
# 克隆后端代码（dev）
git clone --depth 1 --branch dev <后端仓库> repo
cd repo

# 1) 全表/超大 limit 拉取
rg -n "9999999|99999999" app --glob '*.php'

# 2) 无条件查询
rg -n "::find\(\[\]\)|::find\(\)" app --glob '*.php'

# 3) 聚合调用（报表类）
rg -n -- "->aggregate\(" app --glob '*.php'

# 4) 按主键查询
rg -n "findByID\(" app --glob '*.php'

# 5) 循环内查库（N+1 粗筛，需人工确认）
rg -n "foreach" app/Repositories --glob '*.php' | wc -l

# 6) 读从库路由
rg -n "::on\(" app --glob '*.php'
```

## 3. 高危项明细（真实命中样例）

### 3.1 超大 limit 全表拉取（45+ 处，风险高）

`find($query, $fields, $sort, $skip, $limit)` 的 limit 被写成 9999999 / 99999999，等于全量拉取。无索引或大集合时会造成长时间 COLLSCAN + 内存暴涨。

典型命中：

```text
app/Services/Common/ChannelSyncService.php:83      ReportChannelDeductedDayLogModel::find([], [], ['date'=>1], 0, 9999999)
app/Services/Common/ChannelDeductionService.php:307 ReportChannelDayLogModel::find([], ['date'], [], 0, 9999999)
app/Services/Common/MessageService.php:489           ::find([...], [], ['publish_at'=>-1], 0, 99999999)
app/Channel/Repositories/MaterialRepository.php:25   ChannelMaterialModel::find($query, [], ['created_at'=>-1], 0, 9999999)
app/Channel/Repositories/DomainRepository.php:12/38  ChannelDomainModel::find($query, [], ['created_at'=>-1], 0, 9999999)
app/Services/Sdk/UserProductService.php:47/288       UserProductModel::find([], [], ["sort"=>1], 0, 1000)
app/Services/Sdk/UserService.php:1456-1478           UserCharge/UserSpend/AccountDetail find(..., 0, 10000)
app/Jobs/Report/CoinOverviewDayJob.php:204/329       GameModel::find([], ['_id','title'], [], 0, 99999999)
app/Jobs/Common/GameReserveNotifyJob.php:21/44/56    GameReserveModel::find(..., 0, 99999999)
app/Repositories/Backend/RankLeaderboardRepository.php:245/314  UserModel::find(['_id'=>['$in'=>...]], ..., 0, 99999999)
app/Repositories/Api(V1)/MessageRepository.php       ::find(..., 0, 99999999)
```

处理建议：

- 后端报表/导出等确实需要全量的场景：改为游标/分批（`find` 加时间范围或 `_id` 游标 + 每批 1000），不要一次 99999999。
- 业务查询：加分页 limit + skip；无分页需求的加业务条件（状态、日期、渠道）后再取。
- 全部 `9999999/99999999` 处由开发逐条确认用途后改分批或加条件。

### 3.2 无条件 find（6 处，风险高）

```text
app/Repositories/Backend/UserFeedbackListRepository.php:88  UserFeedbackCategoryModel::find([])
app/Channel/Services/ChannelReportService.php:356           ChannelDomainModel::find()
app/Channel/Services/ChannelReportService.php:375           ChannelMaterialModel::find()
app/Channel/Services/DataSyncService.php:102                 ChannelDomainModel::find()
app/Channel/Services/DataSyncService.php:158                 ChannelMaterialModel::find()
app/Repositories/Backend/PaymentChannelRepository.php:190   PaymentChannelsModel::find()
```

处理建议：

- 确认集合量级；数据量大时无条件 find 即使默认 limit=10 也可能无索引扫描。
- 建议 `MongoModel` 层对 `find([], ...)` 且未显式传 limit 的调用加日志或限制。

### 3.3 报表聚合（29 处调用，风险中高）

命中文件：

```text
app/Jobs/Report/ReportHourJob.php
app/Jobs/Report/ReportServerJob.php
app/Jobs/Report/TotalMinuteJob.php
app/Jobs/Report/TotalOldDayJob.php
app/Jobs/Report/VipOrCoinTotalMinuteJob.php
app/Jobs/Report/VipOrCoinTotalOldDayJob.php
app/Repositories/Backend/UserSpendRepository.php
```

特点：`::on(MONGODB_SLAVE_2)->aggregate($pipeline)` 走从库（读压力分流正确）；但 pipeline 是否带 `$match` 时间窗、`$limit`、`allowDiskUse` 需逐条核验。本次扫描未发现报表 Job 中显式 `$limit` 阶段（0 命中），大范围聚合（如全量留存、全量日报）可能长时间占用从库。

处理建议：

- 每个 pipeline 必须带时间范围 `$match`（如 `create_time >= 昨日零点`）。
- 聚合超过 100MB 内存需显式 `allowDiskUse: true`。
- 报表 Job 错峰执行，避免多个大聚合同时跑。
- 建议开发在 aggregate 调用处统一封装：强制 `$match` 时间窗 + 可选 `$limit`。

### 3.4 findByID 透传类型（需核验，风险中）

`MongoModel::findByID($id, $idName='_id')` 直接把入参当过滤值透传，不自动转 `MongoDB\BSON\ObjectId`。若业务 `_id` 是整型自增（`getInsertId` 生成）则传 `intval()` 正确；若部分是 ObjectId 则传字符串会查不到或全表扫描。

命中样例：

```text
UserModel::findByID($user)                     // 字符串/整型混合，需核验
UserGroupModel::findByID(intval($order['product_id']))
ReportAdvLogModel::findByID($idValue)
MessageCenterModel::findByID($messageId)
```

处理建议：

- 明确各集合 `_id` 类型（自增 int / ObjectId），在 `findByID` 内部按模型声明做类型归一，避免透传。
- 建议 `MongoModel` 增加 `$idType = 'int'|'objectid'|'string'` 静态属性，`findByID` 自动转换。

### 3.5 大字段/全量配置进 Redis 缓存（风险中）

- 历史事故：`config.vip_growth_rule` 3.6MB 富文本被整包合并进 `18game_system_config` 单 key，Redis GET 单次 93s，全站 504（2026-08-17 已修复，缓存降至 8.6KB）。
- 现状仍存在配置类服务 `getAll()` 整包缓存 + `cache()->set(..., 99999999)` 长 TTL 模式：

```text
app/Services/Common/ConfigService.php（getAll 整包合并缓存）
app/Services/Common/ConfigDictService.php:30   cache()->set($cacheKey, $dict, 99999999)
app/Services/User/UserTaskService.php:92/160    cache()->set($cacheKey, $config/tasks, 99999999)
app/Repositories/Api(V1)/TrackingPositionConfigRepository.php:52  cache()->set(..., 99999999)
app/Repositories/Api(V1)/AnnouncementRepository.php:44            cache()->set(..., 99999999)
app/Repositories/Api(V1)/MarqueeRepository.php:32                 cache()->set(..., 99999999)
```

处理建议：

- 配置类缓存设置单 key 大小上限（如 >200KB 告警），富文本/大 JSON 不合并进统一配置 key。
- `99999999` 长 TTL 改为合理 TTL（如配置类 5-30 分钟 + 主动失效），避免脏数据永久滞留。
- 定期用 `redis-cli --bigkeys` + `MEMORY USAGE` 巡检。

### 3.6 循环内查库（N+1，需人工确认）

Repositories 层 `foreach` 出现 350 处，不能直接判定全部是 N+1，但以下模式需重点核验：

```text
foreach (...) { Model::findByID(...) }      // 逐条主键查询
foreach (...) { Model::findFirst([...]) }   // 逐条条件查询
foreach (...) { cache()->get(...) }         // 逐条缓存读（可接受但可批量化）
```

处理建议：

- 批量化：`find(['_id' => ['$in' => $ids]])`、`find(['user_id' => ['$in' => $ids]])` 代替循环查库。
- 循环内缓存读可接受，但热点接口建议 pipeline 批量。

## 4. MongoModel 兜底防线（建议 C1 改动，需测试环境验证）

```php
// app/Core/Mongodb/MongoModel.php 增加统一拦截
public static function find($query = [], $fields = [], $sort = [], $skip = 0, $limit = 10)
{
    // 防线 1：无条件且未显式 limit 时告警（默认 limit 已是 10，但避免隐式全表）
    if (empty($query) && func_num_args() < 5) {
        LogUtil::warning('mongo_find_without_filter', [
            'model' => static::class,
            'trace' => debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 5),
        ]);
    }
    // 防线 2：limit 超大时拒绝（除显式白名单的批量任务）
    if ($limit > 20000) {
        LogUtil::warning('mongo_find_huge_limit', [
            'model' => static::class, 'limit' => $limit,
        ]);
        // 可配置成 throw 或仅告警
    }
    // 防线 3：findByID 按 $idType 归一化
    ...
}
```

说明：该改动属于 C1 级（测试环境验证、备份、可回滚），上线前先在测试环境跑全量回归，确认无业务依赖超大 limit 后放开。

## 5. 建议落地动作

1. 在测试库开启 profiling（`slowms=150`）跑一周，导出 `system.profile` 按 collection 归因 Top 慢查询。
2. `redis-cli --bigkeys` + `INFO memory/stats` 扫大 key 与无 TTL key。
3. 代码层按本文档 3.1-3.6 逐条核验，输出《高危查询修复清单》给开发。
4. 修复顺序建议：3.1 超大 limit → 3.2 无条件查询 → 3.5 配置缓存 → 3.3 聚合 → 3.4/3.6。
5. 在测试环境对每个修复项做 explain + 压测对比，确认后随后端发版。

## 6. 说明

- 本清单基于 `root/18game_php.git` dev 分支静态扫描，行号为扫描时点，后续代码变动请以最新仓库为准。
- 未接入真实库执行 explain；具体集合数据量、索引情况需在测试库二次确认。
- 不涉及线上写操作，全部为只读检查与建议。
