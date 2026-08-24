---
id: "doc-73444fa9f242"
title: "资源域名替换参考 SQL"
date: "2026-08-25T00:00:00+08:00"
dateSource: "正文日期"
categories: ["基础设施与自动化", "项目文档"]
tags: ["项目文档", "Python", "MySQL", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/ops/aiwork/2026_devops/devops/python/ben-bot/doc/%E8%B5%84%E6%BA%90%E5%9F%9F%E5%90%8D%E6%9B%BF%E6%8D%A2%E5%8F%82%E8%80%83-SQL.md"
sourcePath: "~/Projects/work/ops/aiwork/2026_devops/devops/python/ben-bot/doc/资源域名替换参考-SQL.md"
sourceSha256: "dbb11196812c8f12d6a2084e5ebd2a164423794556722abc523c86fd0aa28e2b"
sourceSystem: "project-doc"
---

# 资源域名替换参考 SQL

> 来源文件：`~/Projects/work/ops/aiwork/2026_devops/devops/python/ben-bot/doc/资源域名替换参考-SQL.md`

> 整理日期：2026-08-25 00:00｜日期依据：正文日期

用途：台子更换资源域名时，按此模式替换数据库中的图片/证件照 URL。**执行前先备份数据库**。

## 参考模式（fb52 示例）

```sql
-- 替换 logo 字段中的域名
UPDATE app
SET logo = REPLACE(logo, 'fb52.faceokk.cc', 'fb52.28966.shop')
WHERE logo LIKE '%fb52.faceokk.cc%';

-- 替换 imgs 字段中的域名
UPDATE app
SET imgs = REPLACE(imgs, 'fb52.faceokk.cc', 'fb52.28966.shop')
WHERE imgs LIKE '%fb52.faceokk.cc%';

-- 替换 plan 计划照
UPDATE plan
SET main_img = REPLACE(main_img, 'fb52.faceokk.cc', 'fb52.28966.shop')
WHERE main_img LIKE '%fb52.faceokk.cc%';

-- 替换 user 证件照
UPDATE user
SET document_photo = REPLACE(document_photo, 'pic52.wngq18enu.top', 'fb52.28966.shop')
WHERE document_photo LIKE '%pic52.wngq18enu.top%';

UPDATE user
SET document_photo = REPLACE(document_photo, 'fb52.faceokk.cc', 'fb52.28966.shop')
WHERE document_photo LIKE '%fb52.faceokk.cc%';
```

## fb59 实际执行（2026-08-25）

老域名 `fb59.28966.shop` → 新域名 `fb59.fbtk2024.com`：

```sql
UPDATE app SET logo = REPLACE(logo, 'fb59.28966.shop', 'fb59.fbtk2024.com') WHERE logo LIKE '%fb59.28966.shop%';          -- 54 行
UPDATE app SET imgs = REPLACE(imgs, 'fb59.28966.shop', 'fb59.fbtk2024.com') WHERE imgs LIKE '%fb59.28966.shop%';          -- 54 行
UPDATE plan SET main_img = REPLACE(main_img, 'fb59.28966.shop', 'fb59.fbtk2024.com') WHERE main_img LIKE '%fb59.28966.shop%';  -- 57 行
UPDATE user SET document_photo = REPLACE(document_photo, 'fb59.28966.shop', 'fb59.fbtk2024.com') WHERE document_photo LIKE '%fb59.28966.shop%';  -- 10 行
```

## 通用步骤

1. `mysqldump` 全库备份。
2. 先查询命中列与行数：`SELECT ... WHERE col LIKE '%老域名%'`。
3. 逐列执行 REPLACE（先替换更长/更特殊域名，避免互相覆盖）。
4. 复检：`SELECT COUNT(*) ... WHERE col LIKE '%老域名%'` 应为 0。
5. 重启对应服务生效。
