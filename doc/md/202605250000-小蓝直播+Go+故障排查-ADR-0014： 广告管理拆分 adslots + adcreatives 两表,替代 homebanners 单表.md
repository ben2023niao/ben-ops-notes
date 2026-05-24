---
id: "doc-b80ea38d98e0"
title: "ADR-0014： 广告管理拆分 adslots + adcreatives 两表,替代 homebanners 单表"
date: "2026-05-25T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0014-ads-slot-creative-split.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0014-ads-slot-creative-split.md"
sourceSha256: "29de18b505543777d3ce140fcb0a69446a5825a236b890c9230875d4b4185071"
sourceSystem: "project-doc"
---

# ADR-0014： 广告管理拆分 adslots + adcreatives 两表,替代 homebanners 单表

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0014-ads-slot-creative-split.md`

> 整理日期：2026-05-25 00:00｜日期依据：正文日期

| 状态 | 已采纳 |
|---|---|
| 日期 | 2026-05-25 |
| Owner | 后端 / 运营 |
| 影响范围 | DB schema、admin API、admin UI、public read API、`home_banners` 表 deprecation |
| 关联文档 | `services/go-app/migrations/0012*`、`0013*`、`services/go-app/internal/service/admin/ads*` |

## 1. 背景

v0.3 时期 admin 用单表 `home_banners` 管理所有广告位,`position` 字段(`home_top` / `home_middle` / `live_top` / `h5_sticky` / `h5_corner` / `h5_bubble` / `h5_theater_topbar` 7 个值)区分广告位类型。admin UI `/system/banner` 只暴露 `home_top`,其余 6 个位运营建不了内容(只能 admin 直接 SQL 改库)。

业务诉求(2026-05-25):
- 运营需要管理**所有 7 个广告位** + 未来可能加新位
- 不同位有不同**渲染规则**(轮播 / 单图 / 跑马灯文字 / 浮窗气泡 / 角标)
- 不同位有**条数上限**(首页轮播最多 5 条,角标永远 1 条等)
- 位本身应该可启用/禁用(整位关闭后所有内容不显示),独立于内容级 enable
- admin UI 应是**位 + 内容**两层视图,而不是平铺所有 banner

## 2. 决定

**拆 `home_banners` 为 `ad_slots`(位定义)+ `ad_creatives`(位内容)两表**。

### 2.1 表结构

```sql
-- 广告位定义(管理员配置,业务前端按 slot_code 拉)
ad_slots:
  id            BIGINT UNSIGNED PRIMARY KEY    (snowflake)
  slot_code     VARCHAR(64)  UNIQUE NOT NULL    -- 业务 key,前端拉接口按此过滤
  name          VARCHAR(128) NOT NULL           -- 中文显示名,如"首页顶部轮播"
  description   VARCHAR(255) NOT NULL DEFAULT ''
  render_type   VARCHAR(32)  NOT NULL DEFAULT 'carousel'
                -- carousel / single / marquee / bubble / sticky / corner_badge
  max_items     INT UNSIGNED NOT NULL DEFAULT 5
  enabled       TINYINT      NOT NULL DEFAULT 1
  created_by    BIGINT UNSIGNED NOT NULL
  updated_by    BIGINT UNSIGNED NULL
  created_at/updated_at/deleted_at
  UNIQUE KEY uk_slot_code (slot_code, deleted_at)
  KEY idx_enabled (enabled, deleted_at)

-- 广告内容(挂在 slot 下)
ad_creatives:
  id            BIGINT UNSIGNED PRIMARY KEY    (snowflake)
  slot_id       BIGINT UNSIGNED NOT NULL        -- FK ad_slots.id
  title         VARCHAR(128) NOT NULL
  image_url     VARCHAR(512) NOT NULL DEFAULT ''-- 图广告 URL
  text_content  VARCHAR(255) NOT NULL DEFAULT ''-- 文字广告(跑马灯 / 气泡)
  link_type     VARCHAR(16)  NOT NULL DEFAULT 'none'  -- none/external/route/match/predict
  link_target   VARCHAR(512) NOT NULL DEFAULT ''
  start_at      DATETIME(3)  NULL               -- NULL = 立即生效
  end_at        DATETIME(3)  NULL               -- NULL = 永久
  enabled       TINYINT      NOT NULL DEFAULT 1
  sort_order    INT UNSIGNED NOT NULL DEFAULT 100
  click_count   BIGINT UNSIGNED NOT NULL DEFAULT 0
  created_by    BIGINT UNSIGNED NOT NULL
  updated_by    BIGINT UNSIGNED NULL
  created_at/updated_at/deleted_at
  KEY idx_slot_enabled_sort (slot_id, enabled, sort_order, deleted_at)
  KEY idx_validity (start_at, end_at)
  FOREIGN KEY (slot_id) REFERENCES ad_slots(id) ON DELETE RESTRICT
```

### 2.2 数据迁移

`migration 0013_migrate_home_banners_to_ads.up.sql`:

1. 插入 7 行到 `ad_slots`(slot_code 复用现有 position 值,name/render_type/max_items 按规约填):
   | slot_code | name | render_type | max_items |
   |---|---|---|---|
   | `home_top` | 首页顶部轮播 | carousel | 5 |
   | `home_middle` | 首页中部广告位 | carousel | 3 |
   | `live_top` | 直播页顶部 | single | 1 |
   | `h5_sticky` | 直播 tab 吸底 | sticky | 1 |
   | `h5_corner` | 赛程 tab 角标 | corner_badge | 1 |
   | `h5_bubble` | 竞猜 tab 气泡 | bubble | 1 |
   | `h5_theater_topbar` | 剧场式 TopBar 跑马灯 | marquee | 5 |

2. 把 `home_banners` 所有 row 写入 `ad_creatives`(slot_id 按 position 查 ad_slots.id),保留 `deleted_at`/`enabled`/`start_at`/`end_at`/`click_count` 等历史。

3. `home_banners` 表**保留**(deprecated),不再写。1 周稳定后下个 PR `DROP TABLE home_banners`。

`down.sql`:
- 回滚需要 `DELETE FROM ad_creatives WHERE created_at >= '<migration_time>'` + `DELETE FROM ad_slots WHERE created_at >= ...`(粗略,不保证 100% 还原)。**破坏性,真要回滚走维护窗口 + 数据库备份恢复**。

### 2.3 API

**admin**:
```
GET    /api/v1/admin/ads/slots                       列广告位
POST   /api/v1/admin/ads/slots                       新建位
PATCH  /api/v1/admin/ads/slots/:id                   改位
DELETE /api/v1/admin/ads/slots/:id                   软删位(有内容关联时拒)
GET    /api/v1/admin/ads/creatives?slot_id=...       列内容
POST   /api/v1/admin/ads/creatives                   新建内容
PATCH  /api/v1/admin/ads/creatives/:id               改内容
DELETE /api/v1/admin/ads/creatives/:id               软删内容
```

**public(通用读取,新增)**:
```
GET /api/v1/ads/slots
GET /api/v1/ads/slots/:slot_code/creatives?limit=...
```

返回规则:
- 只返回 `ad_slots.enabled = 1` 且未软删的广告位。
- 只返回 `ad_creatives.enabled = 1`、未软删、且 `start_at IS NULL OR start_at <= now`、`end_at IS NULL OR end_at > now` 的广告内容。
- `slot_code` 不存在或广告位关闭时,`creatives` 接口返回 200 + `slot: null` + `items: []`,前端按空态处理,避免投放开关变成用户可见错误。
- public 响应不暴露 `created_by`、`updated_by`、`deleted_at`、内部审计字段。
- 排序固定为 `sort_order ASC, created_at DESC`,前端不得自行改排序。
- `limit` 不能超过广告位 `max_items`,服务端二次截断。

public schema:

```json
{
  "slot": {
    "slot_code": "h5_home_hero",
    "name": "H5 首页顶部轮播",
    "render_type": "carousel",
    "max_items": 5
  },
  "items": [
    {
      "id": "10000000000000001",
      "title": "夜场福利",
      "image_url": "https://...",
      "text_content": "",
      "link_type": "predict",
      "link_target": "1234567890",
      "sort_order": 10
    }
  ]
}
```

**public(首页专用)**:
- `GET /api/v1/home/banner` 直接读取 `ad_creatives JOIN ad_slots`,作为首页 Banner 广告接口。
- Web 首页使用 `slot_code = home_top`。
- H5 首页使用 `slot_code = h5_home_hero`。
- 广告位关闭或无生效内容时返回空列表,前端不渲染 Banner。

### 2.3.1 标准 slot_code

| slot_code | 使用页面 | 渲染类型 | 最大条数 | PRD |
|---|---|---:|---:|---|
| `home_top` | Web 首页顶部 banner | carousel | 5 | HOME-002 |
| `home_middle` | Web 首页时间线下方广告 | carousel | 3 | HOME-008 |
| `h5_home_hero` | H5 首页顶部运营 banner | carousel | 5 | H5-002 |
| `h5_home_live_feed` | H5 首页直播列表信息流广告 | single | 1 | H5-019 |
| `h5_sticky` | H5 live tab 吸底广告 A | sticky | 1 | H5-019 |
| `h5_corner` | H5 schedule tab 角标广告 B | corner_badge | 1 | H5-020 |
| `h5_bubble` | H5 predict tab 气泡广告 C | bubble | 1 | H5-021 |
| `h5_theater_topbar` | 剧场式直播间 TopBar 跑马灯 D | marquee | 5 | H5-021b |

### 2.4 admin UI

`/system/banner` → `/ads`:
- 左侧:广告位列表(7 个 + 可建新位),点选某位
- 右侧:该位下的内容列表(可拖拽改 sort_order,可启停,可改时间段,可换图/文)
- 顶部 toolbar:位的"编辑位定义"按钮(改 max_items / enabled / render_type 等)

旧的 `BannerListView.vue` **保留不删**,挂在 `/system/banner-legacy` 路由(给迁移期 fallback,1 周后删)。新主入口是 `/ads`。

## 3. 后果

### 正向

- ✅ 运营自主管所有广告位,不再依赖工程改 SQL
- ✅ 每个位独立的 render_type / max_items 表达力强,前端按位渲染不需写硬编码 if
- ✅ 加新位只是 `INSERT INTO ad_slots`,前端按 slot_code 拉新接口不动后端
- ✅ public API 以当前新项目契约为准,不保留旧模型分支

### 负向

- ⚠️ migration 0013 涉及数据迁移,需要在低峰执行,失败前先备份 home_banners
- ⚠️ 改动文件 ~15 个,review 工作量大
- ⚠️ admin UI 重写一个 view,前端工作量 1-2h

### 灰度策略

1. **PR 1(本 ADR)**:后端 + migration + seed,旧 `/system/banner` UI 不动(它继续调老 API,老 API 直读 home_banners 不受影响)
2. **PR 2**:admin UI 新 `/ads` view 上线,旧 `BannerListView` 移到 `/system/banner-legacy`
3. **PR 3**(1 周后):删除 home_banners 表 + admin SystemService 里 banner CRUD 代码

## 4. 关联

- 取代:`home_banners` 单表方案(原 0007 migration)
- 影响:`SystemService.ListBanners` / `UpsertBanner`(保留 deprecated)、`H5AdsService`(内部改读新表)、`HomeService.GetBanners`(同上)
