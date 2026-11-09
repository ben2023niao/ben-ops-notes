---
id: "doc-b53211107e2c"
title: "【分析】接口响应数据量排行榜（/api/v1 与 SDK 两侧）"
date: "2026-10-19T16:20:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "Redis", "监控告警", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-1620-%E3%80%90%E5%88%86%E6%9E%90%E3%80%91%E6%8E%A5%E5%8F%A3%E5%93%8D%E5%BA%94%E6%95%B0%E6%8D%AE%E9%87%8F%E6%8E%92%E8%A1%8C%E6%A6%9C%EF%BC%88/api-v1%20%E4%B8%8E%20SDK%20%E4%B8%A4%E4%BE%A7%EF%BC%89.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-1620-【分析】接口响应数据量排行榜（/api-v1 与 SDK 两侧）.md"
sourceSha256: "0080c11818b82c630309050ba873d2cadc8dff4382c5f45e0bbf0a74e467835b"
sourceSystem: "project-doc"
---

# 【分析】接口响应数据量排行榜（/api/v1 与 SDK 两侧）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610191620-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BDocker%2BNginx-%E3%80%90%E5%88%86%E6%9E%90%E3%80%91%E6%8E%A5%E5%8F%A3%E5%93%8D%E5%BA%94%E6%95%B0%E6%8D%AE%E9%87%8F%E6%8E%92%E8%A1%8C%E6%A6%9C%EF%BC%88-api-v1%20%E4%B8%8E%20SDK%20%E4%B8%A4%E4%BE%A7%EF%BC%89.md)

> 整理日期：2026-10-19 16:20｜日期依据：正文日期

- 时间：2026-10-19 16:20（北京时间）
- 目的：回答「哪些接口返回的数据变大了」，给出可定位到接口的排行榜
- 数据来源与口径见每节标题（**两侧口径不同，不能混用**）

---

## 一、结论先说

1. **`/api/v1/modules/home` 是绝对大头**：平均 **251.5 KB/次**，当天 56.7 万次调用，合计 **136 GB**，占 `/api/v1` 全部响应量的 **82.5%**。
2. **`/api/v1/game/detail` 第二**：平均 106.5 KB/次，18.4 万次，合计 19 GB，占 11.4%。
3. 两者合计占 `/api/v1` 响应量的 **93.8%**。
4. **SDK 侧不是「响应变大」，而是「调用量变大」**：同小时对比，`/api/sdk/system/info` 调用 7,452 → 36,183（**4.86 倍**），平均响应 6.3 KB 基本不变；只有 `/api/sdk/game/more` 从 56 KB 涨到 62 KB（+11%）。

> 更正上一版说法：10-17 的 `api_response` 行数是 10-16 的 4.3 倍，那是**调用量**增长，不是单条响应变大。真正「单条大」的接口在 `/api/v1` 侧（modules/home、game/detail），而 `api_response` 日志**不记录 `/api/v1`**（实测 0 行）。

---

## 二、/api/v1 接口响应大小排行

数据：**2026-10-19 当天** nginx access 全量（调用次数 ≥ 200），按平均响应大小排序

| 排名 | 接口 | 调用次数 | 平均大小 | 合计 | 占 /api/v1 响应量 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `/api/v1/modules/home` | 567,558 | **251.5 KB** | **139,375 MB** | **82.47%** |
| 2 | `/api/v1/game/detail` | 184,490 | 106.5 KB | 19,186 MB | 11.35% |
| 3 | `/api/v1/community/hotFeed` | 3,909 | 81.4 KB | 311 MB | 0.18% |
| 4 | `/api/v1/community/tagDetail` | 1,030 | 79.3 KB | 80 MB | 0.05% |
| 5 | `/api/v1/game/lists` | 36,810 | 46.6 KB | 1,676 MB | 0.99% |
| 6 | `/api/v1/community/gameDetail` | 7,808 | 41.1 KB | 314 MB | 0.19% |
| 7 | `/api/v1/modules/getModule` | 3,002 | 38.9 KB | 114 MB | 0.07% |
| 8 | `/api/v1/Post/getPostDetail` | 83,860 | 23.1 KB | 1,895 MB | 1.12% |
| 9 | `/api/v1/Article/getArticleDetail` | 20,530 | 18.0 KB | 361 MB | 0.21% |
| 10 | `/api/v1/pointMall/index` | 20,901 | 15.1 KB | 309 MB | 0.18% |
| — | **/api/v1 合计** | **3,674,630** | **47.1 KB** | **165 GB** | 100% |

**可定位点**：只要把 `modules/home` 的单次响应从 251 KB 降下来（拆分首屏/非首屏、字段裁剪、分页、缓存），就能直接影响 82% 的响应体积。

---

## 三、SDK 接口响应排行（同小时 10-16 vs 10-17 22:00-23:00）

数据：`api_response` 日志（只含 `/api/sdk/*` 与 `/customer/*`），按 10-17 总响应字节排序

| 排名 | 接口 | 10-16 调用 | 10-17 调用 | 调用倍数 | 10-16 合计 | 10-17 合计 | 平均大小 16→17 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `/api/sdk/system/info` | 7,452 | 36,183 | **4.86×** | 45.5 MB | **221.2 MB** | 6.3 → 6.3 KB（不变） |
| 2 | `/api/sdk/game/more` | 58 | 284 | 4.90× | 3.2 MB | 17.2 MB | 56.0 → **62.0 KB（+11%）** |
| 3 | `/api/sdk/UserProduct/getProductList` | 347 | 1,222 | 3.52× | 1.4 MB | 4.8 MB | 4.0 → 4.0 KB |
| 4 | `/api/sdk/user/validateToken` | 4,881 | 20,970 | 4.30× | 0.9 MB | 4.0 MB | 0.2 → 0.2 KB |
| 5 | `/customer/user/queryTestAccounts` | 0 | 121 | **新增** | 0 | 3.5 MB | — → 29.9 KB |
| 6 | `/api/sdk/system/gameTrack` | 3,354 | 13,181 | 3.93× | 0.6 MB | 2.5 MB | 0.2 → 0.2 KB |
| 7 | `/api/sdk/Login/username` | 519 | 2,157 | 4.16× | 0.4 MB | 1.8 MB | 0.9 → 0.9 KB |
| 8 | `/api/sdk/Game/more` | 2 | 20 | 10.0× | 0.1 MB | 1.2 MB | 56.0 → 62.0 KB |
| 9 | `/api/sdk/vipGrowth/getMemberInfo` | 289 | 1,370 | 4.74× | 0.3 MB | 1.2 MB | 0.9 → 0.9 KB |
| 10 | `/customer/other/checkTokenV2` | 1,274 | 3,292 | 2.58× | 0.4 MB | 1.1 MB | 0.3 → 0.3 KB |

**结论**：SDK 侧所有接口调用量整体涨 **3.5~5 倍**，单条响应大小基本不变。要查的是「为什么 SDK 调用量涨 5 倍」——新游戏接入、客户端轮询/重试、还是某个渠道刷量。

---

## 四、给开发的排查建议（按优先级）

1. **`/api/v1/modules/home`**（251 KB × 56.7 万次/天 = 136 GB）
   - 看这个接口一次返回了哪些模块；能否拆分「首屏必需」与「非首屏懒加载」
   - 字段裁剪：列表项只返回卡片需要的字段
   - 首页模块数据加缓存（Redis 已有能力），避免每次实时拼装大 JSON
2. **`/api/v1/game/detail`**（106 KB × 18.4 万次 = 19 GB）
   - 详情页是否把大量关联数据（评论/攻略/礼包）一次性返回；改为分页/按需
3. **SDK 调用量 5 倍**：核对 10-17 是否有新游戏/新渠道接入；检查客户端是否有轮询、失败重试放大
4. **新增的 `/customer/user/queryTestAccounts`**：确认是否测试账号查询被放到了生产高频调用
5. 服务端加「响应体大小」监控：按接口统计 p50/p95 大小，超阈值告警（这次问题就是靠日志人工发现的）

## 五、口径与限制

- `/api/v1` 排行来自 **10-19 当天** nginx access（本地只保留当天；10-16/10-17 的 access 已归档 S3 且对象名不含日期）
- SDK 排行来自 `api_response` 同小时对比（10-16 22:00-23:00 vs 10-17 22:00-23:00）
- `api_response` 实测只记录 `/api/sdk/*`（85,413 行）与 `/customer/*`（3,413 行），**`/api/v1` 为 0 行**，所以两侧必须分开看
