---
id: "doc-9e053d6eb80c"
title: "【性能排查】线上环境 MongoModel 巡检 · 风险逐条清单"
date: "2026-09-01T17:10:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Redis", "监控告警", "自动化", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-01_1710-%E3%80%90%E6%80%A7%E8%83%BD%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83MongoModel%E5%B7%A1%E6%A3%80-%E9%A3%8E%E9%99%A9%E9%80%90%E6%9D%A1%E6%B8%85%E5%8D%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-01_1710-【性能排查】线上环境MongoModel巡检-风险逐条清单.md"
sourceSha256: "939bcbc17275d593c90bbfa2ff7813fe9226f1a6a9e7e5e2ee1d233aa8bb0c0a"
sourceSystem: "project-doc"
---

# 【性能排查】线上环境 MongoModel 巡检 · 风险逐条清单

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609011710-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E3%80%90%E6%80%A7%E8%83%BD%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20MongoModel%20%E5%B7%A1%E6%A3%80%20%C2%B7%20%E9%A3%8E%E9%99%A9%E9%80%90%E6%9D%A1%E6%B8%85%E5%8D%95.md)

> 整理日期：2026-09-01 17:10｜日期依据：文件名日期

环境标签：线上环境 / 后端 / MongoDB / MongoModel / 性能与安全风险

时间：2026-09-01

扫描对象：`root/18game_php.git` **main 分支（线上发布分支）**，HEAD `d1819cf`（`Merge branch 'feature/cike-2026-06-11-后台渠道包编辑修改' into 'main'`），713 个 PHP 文件。

核心文件：

- `app/Core/Mongodb/MongoModel.php`
- `app/Core/Mongodb/MongoDbConnection.php`

说明：以下为静态扫描 + 源码审阅结果，行号为扫描时点（main HEAD d1819cf）；是否真实触发取决于线上集合数据量与索引，需在线上只读 explain / 压测复核（高风险变更须测试环境验证后随版本发布）。

---

## 风险 1：超大 limit 全表拉取（47 处，高危）

- 代码位置：调用方大量使用 `find(..., 0, 9999999)` / `99999999`，例如：
  - `app/Services/Common/ChannelSyncService.php:83/158`（`ReportChannelDeductedDayLogModel::find([], [], ['date'=>1], 0, 9999999)`）
  - `app/Services/Common/ChannelDeductionService.php:59/106/259/307/341/383/422`（`9999999` 多处）
  - `app/Services/Common/MessageService.php:469/592/721`（`99999999`）
  - `app/Repositories/Api/ApiV1/MessageRepository.php:55/77`（`99999999`）
  - `app/Repositories/Backend/RankLeaderboardRepository.php:245/314`（`UserModel::find(['_id'=>['$in'=>...]], ..., 0, 99999999)`）
  - `app/Repositories/Backend/ProductClickStatRepository.php:54/75/82`（`99999999`）
  - `app/Repositories/Backend/GameDownloadStatRepository.php:46`、`TrackingStatRepository.php:137`、`TrackingGameStatRepository.php:64`
  - `app/Repositories/Api/ApiV1/TrackingPositionConfigRepository.php:27`、`app/Repositories/Backend/TrackingPositionConfigRepository.php:32/142`（`9999999`）
  - `app/Jobs/Report/CoinOverviewDayJob.php:204/329`（`GameModel::find([], ..., 0, 99999999)`）
- 隐患原因：limit 写成近无穷，等于一次性把整个集合（或大范围数据）拉进内存；无索引/大集合时触发 COLLSCAN，长时间占用连接与内存，线上后台/报表接口可能超时或 OOM，甚至拖慢主库。
- 修改优化建议：
  - 业务查询必须分页（limit+skip）或加业务条件（状态/日期/渠道）后再取。
  - 报表/导出等全量场景改为分批游标（时间范围或 `_id` 递增，每批 1000）。
  - `MongoModel::find()` 加 limit 上限（>20000 告警/拒绝），逐条改造 47 处调用，先测试环境验证再上线上。

---

## 风险 2：无条件 find() / find([]) 全表扫描（6 处，高危）

- 代码位置：
  - `app/Channel/Services/ChannelReportService.php:356/375`（`ChannelDomainModel::find()`、`ChannelMaterialModel::find()`）
  - `app/Channel/Services/DataSyncService.php:102/158`（`ChannelDomainModel::find()`、`ChannelMaterialModel::find()`）
  - `app/Repositories/Backend/UserFeedbackListRepository.php:88`（`UserFeedbackCategoryModel::find([])`）
  - `app/Repositories/Backend/PaymentChannelRepository.php:190`（`PaymentChannelsModel::find()`）
- 隐患原因：无过滤条件直接 find，即使默认 limit=10 也会全表扫描集合（COLLSCAN）再截断；线上集合增长后每次调用都是全表扫描，消耗线上主库 IO。
- 修改优化建议：
  - 确认集合量级，数据量大时补条件或缓存。
  - 在 `MongoModel::find()` 对 `empty($query)` 且未显式传 limit 的调用加 warning 日志（配合风险 1 防线）。

---

## 风险 3：findByID 透传类型，不自动转 ObjectId（165 处调用，中危）

- 代码位置：`app/Core/Mongodb/MongoModel.php` `findByID()`：
  ```php
  public static function findByID($id, $idName = '_id', $fields = array())
  {
      $item = self::findFirst(array($idName => $id), $fields);
      ...
  }
  ```
  调用方：`app/Services/Sdk/UserService.php:287/343/348/624`、`app/Services/Report/ReportAdvLogService.php:37`、`ReportComicsLogService.php:55/62`、`ReportMovieLogService.php:56/63` 等 165 处。
- 隐患原因：入参直接当过滤值，不按模型 `_id` 类型归一。若 `_id` 是 ObjectId 而业务传字符串，会查不到或全表扫描；若 `_id` 是整型自增而传字符串，同样可能不命中索引。
- 修改优化建议：
  - 为每个模型声明 `static $idType = 'int'|'objectid'|'string'`，`findByID` 内按类型自动转换（`new ObjectId($id)` / `intval($id)`）。
  - 统一业务 `_id` 规范，在 findByID 做兼容归一。

---

## 风险 4：aggregate 无 allowDiskUse、异常被吞、未强制时间窗（79 处，中高危）

- 代码位置：
  - `app/Core/Mongodb/MongoModel.php` `aggregate()/aggregates()`：
    ```php
    $cmd = ['aggregate' => $tableName, 'pipeline' => $pipeline, 'cursor' => new \stdClass];
    ...
    } catch (\Exception $exception) {
    }
    return null;  // 异常被静默吞掉
    ```
  - 调用方集中在报表 Job：`app/Jobs/Report/TotalMinuteJob.php`、`TotalOldDayJob.php`、`ReportHourJob.php:61/68`、`ReportServerJob.php:278`、`VipOrCoinTotalMinuteJob.php`、`VipOrCoinTotalOldDayJob.php`、`app/Repositories/Backend/UserSpendRepository.php:121`。
- 隐患原因：
  - 大聚合超过 100MB 内存限制会失败，但异常被 catch 吞掉返回 null，线上报表任务静默失败无告警。
  - 报表 pipeline 无 `$limit` 阶段（本次扫描报表 Job 0 处显式 `$limit`），大范围聚合长时间占用线上从库。
  - 无 `allowDiskUse` 选项，超大聚合直接报内存超限。
- 修改优化建议：
  - aggregate 增加 `allowDiskUse: true` 选项。
  - pipeline 强制要求 `$match` 时间窗（如 create_time >= 昨日零点）并尽量加 `$limit`。
  - 异常不吞：记录完整错误日志并触发告警，报表失败要可见。
  - 报表 Job 错峰执行，避免多个大聚合并发。

---

## 风险 5：update/updateRaw 默认 multi=true 全表更新（242 处调用，中危）

- 代码位置：`app/Core/Mongodb/MongoModel.php` `update()`/`updateRaw()`：
  ```php
  'updates' => [['q' => $where, 'u' => ['$set' => $document], 'multi' => true]]
  ```
- 隐患原因：
  - `multi=true` 且 `$where` 为空或条件过宽时，会批量更新整个线上集合；`updateById` 未做 `_id` 类型归一（同风险 3）。
  - 错误处理弱：`$result[0]['n']==0` 时直接访问 `$result[0]['writeErrors'][0]`，`writeErrors` 为空会报错；且 `n` 是匹配数不是修改数，无法区分“没匹配”与“没变化”。
- 修改优化建议：
  - `update` 增加 `$multi` 参数，默认 `false`，只有明确批量场景传 `true`；`$where` 为空时拒绝执行。
  - 修正错误分支：先判断 `writeErrors` 非空再读取；返回值用 `nModified` 而不是 `n`。

---

## 风险 6：insert 自增 id 兜底与 ObjectId 转字符串（中危）

- 代码位置：`app/Core/Mongodb/MongoModel.php` `insert()`：
  ```php
  if ($document['_id'] <= 0) { $document['_id'] = 1; }   // 自增失败兜底为 1
  ...
  $objectId = new ObjectId();
  $document['_id'] = strval($objectId);                   // ObjectId 转成字符串
  ```
- 隐患原因：
  - 自增 id 获取失败时兜底为固定值 1，多条记录会 `_id=1` 冲突或互相覆盖。
  - 非自增模式把 ObjectId 转字符串存储，与风险 3 的 `findByID` 透传叠加，查询类型不匹配。
- 修改优化建议：
  - 自增失败应抛异常而不是兜底 1。
  - ObjectId 保持对象类型存储（不 `strval`），或统一按字符串规范存取并在 findByID 归一。

---

## 风险 7：delete 默认 limit=0 清空匹配文档（90 处调用，中危）

- 代码位置：`app/Core/Mongodb/MongoModel.php` `delete()`：
  ```php
  public static function delete(array $query = array(), $limit = 0)
  {
      'deletes' => [['q' => $query, 'limit' => $limit]]
  ```
- 隐患原因：MongoDB `delete.limit=0` 表示删除全部匹配文档；若调用方传 `delete([])` 或条件过宽，会清空整个线上集合，且无任何二次确认。
- 修改优化建议：
  - 默认 `limit=1`，批量删除显式传 `0` 并加日志。
  - `$query` 为空时拒绝执行或强制二次确认。

---

## 风险 8：count 无条件全表统计（171 处调用，中危）

- 代码位置：`app/Core/Mongodb/MongoModel.php` `count()`；无条件命中：
  - `app/Services/Report/ReportTotalDayLogService.php:38/40/42/170`（`AppLogModel::count()`、`UserModel::count()`、`UserDownloadModel::count()`、`UserChargeModel::count()`）
  - `app/Services/Common/ChannelDeductionService.php:404`（`ReportChannelDeductedDayLogModel::count([])`）
  - `app/Repositories/Sdk/SystemRepository.php:218`、`app/Repositories/Api/SystemRepository.php:220`、`app/Repositories/ApiV1/SystemRepository.php:221`（`ReportServerLogModel::count()`）
  - `app/Repositories/Backend/ReportRepository.php:92/93/130`（`UserModel/UserDownloadModel/UserChargeModel::count()`）
  - `app/Repositories/Backend/ConfigDictRepository.php:28`（`ConfigDictModel::count([])`）
- 隐患原因：无条件 count 在大集合上执行全表统计，耗时随数据量线性增长，线上后台/报表页面可能卡顿，且多次 count 占用主库资源。
- 修改优化建议：
  - 能加条件就加条件；只判断“是否存在”的场景用 `findFirst` + 索引或 `$limit=1`。
  - 大集合统计改用估算（`estimatedDocumentCount`）或预聚合计数表。

---

## 风险 9：连接串密码拼接进 URI（安全，需确认配置来源）

- 代码位置：`app/Core/Mongodb/MongoDbConnection.php` `getClient()`：
  ```php
  $uri = "mongodb://";
  if ($this->config['username']) {
      $uri .= "{$this->config['username']}:{$this->config['password']}@";
  }
  ```
- 隐患原因：密码直接拼进连接串，若线上配置/日志/异常信息泄露 URI 会连带泄露口令；特殊字符未做 URL 编码。
- 修改优化建议：
  - 使用 `MongoDB\Driver\Manager` 的 authMechanism/authSource 参数化配置或至少对密码做 URL 编码。
  - 确认 `.env` 密码不进入日志、不进入错误输出、不写入 Git。

---

## 风险 10：JSON 序列化往返丢类型（中危）

- 代码位置：`app/Core/Mongodb/MongoDbConnection.php` `executeCommand()`：
  ```php
  return json_decode(json_encode($result), true);
  ```
- 隐患原因：结果先 json_encode 再 json_decode，ObjectId、日期、Binary 等 BSON 类型会丢失或被转成字符串，导致上层比较/查询类型错乱（与风险 3/6 叠加）。
- 修改优化建议：
  - 直接返回 BSON 对象或按需转换；如必须数组，用 `MongoDB\BSON\toPHP` / `fromPHP` 显式映射，避免 json 往返。

---

## 风险 11：on('slave') 读路由依赖静态可变连接（中危）

- 代码位置：`app/Core/Mongodb/MongoModel.php` `on()` 匿名类：
  ```php
  $old = $class::$connection;
  $class::$connection = $this->connection;   // 静态属性切换
  try { return $class::$method(...$args); }
  finally { $class::$connection = $old; }
  ```
- 隐患原因：通过静态属性临时切换连接，PHP-FPM 短生命周期下风险低，但 CLI/常驻进程（线上报表 Job、队列）并发或协程下可能串连接（A 任务切 slave，B 任务读到 slave）。
- 修改优化建议：
  - 改为传连接上下文参数（如 `find($query, ..., $connection='default')`）或每次查询显式传入 Manager，避免静态可变状态。

---

## 风险 12：配置类整包缓存 + 99999999 TTL（历史 3.6MB 事故同型，中危）

- 代码位置：
  - `app/Services/Common/ConfigService.php`（`getAll()` 整包合并缓存）
  - `app/Services/Common/ConfigDictService.php:30`（`cache()->set($cacheKey, $dict, 99999999)`）
  - `app/Services/User/UserTaskService.php:92/160`（`cache()->set(..., 99999999)`）
  - `app/Repositories/Api/ApiV1/TrackingPositionConfigRepository.php:52`、`AnnouncementRepository.php:43`、`MarqueeRepository.php:32`
- 隐患原因：配置类把全量配置合并进单个 Redis key 且 TTL 近永久；若混入富文本/大 JSON（历史 `vip_growth_rule` 3.6MB 事故），单 key 膨胀会让每次 GET 变慢、线上全站 504。
- 修改优化建议：
  - 缓存单 key 大小上限（>200KB 告警）；富文本/大字段不合并进统一配置 key。
  - `99999999` 改合理 TTL（5-30 分钟）+ 主动失效；定期 `--bigkeys` 巡检。

---

## 汇总表

| # | 风险 | 调用规模 | 等级 |
| --- | --- | --- | --- |
| 1 | 超大 limit 全表拉取 | 47 处 | 高 |
| 2 | 无条件 find 全表扫描 | 6 处 | 高 |
| 3 | findByID 类型不归一 | 165 处 | 中 |
| 4 | aggregate 吞异常/无 limit/无 allowDiskUse | 79 处 | 中高 |
| 5 | update 默认 multi=true | 242 处 | 中 |
| 6 | insert 自增兜底/ObjectId 转字符串 | 核心类 | 中 |
| 7 | delete limit=0 清空风险 | 90 处 | 中 |
| 8 | count 无条件全表 | 171 处 | 中 |
| 9 | 连接串密码拼接 | 核心类 | 中 |
| 10 | JSON 往返丢类型 | 核心类 | 中 |
| 11 | on('slave') 静态可变连接 | 核心类 | 中 |
| 12 | 配置整包缓存 + 长 TTL | 多处 | 中 |

## 与测试环境差异说明

线上 main（d1819cf）与测试 dev 分支核心 `MongoModel` 源码一致，风险项相同；仅调用规模略有差异（线上 findByID 165 处 / 测试 171 处，线上 aggregate 79 处 / 测试 88 处等）。线上集合数据量更大，风险 1/2/8 的实际影响预计更高。

## 建议落地顺序

1. 核心类加固（风险 3/4/5/6/7/10/11）：`MongoModel` 增加 idType 归一、limit 上限、aggregate allowDiskUse、delete/update 安全默认。
2. 高发调用治理（风险 1/2/8）：超大 limit、无条件 find/count 逐条改造。
3. 缓存与安全（风险 9/12）：连接串参数化、缓存大小上限与 TTL。
4. 每项先在测试环境 explain + 压测验证，再随版本发布线上；线上变更前备份、发布后验证并回滚点就绪。
