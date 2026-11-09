---
id: "doc-76917ff43291"
title: "【运维】vendor_a 缺资源补齐 + 巴西同步香港 + Worker 缓存盐准备记录"
date: "2026-09-10T21:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "CDN", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-10-2100-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_a%E7%BC%BA%E8%B5%84%E6%BA%90%E8%A1%A5%E9%BD%90%2B%E5%B7%B4%E8%A5%BF%E5%90%8C%E6%AD%A5%E9%A6%99%E6%B8%AF%2BWorker%E7%BC%93%E5%AD%98%E7%9B%90%E5%87%86%E5%A4%87%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-10-2100-【运维】vendor_a缺资源补齐+巴西同步香港+Worker缓存盐准备记录.md"
sourceSha256: "79bf04727442f07df5e4e5e5d22cdea98f8c795663574cf5d5198a77205dc094"
sourceSystem: "project-doc"
---

# 【运维】vendor_a 缺资源补齐 + 巴西同步香港 + Worker 缓存盐准备记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609102100-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BDocker%2BCDN-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_a%20%E7%BC%BA%E8%B5%84%E6%BA%90%E8%A1%A5%E9%BD%90%20%2B%20%E5%B7%B4%E8%A5%BF%E5%90%8C%E6%AD%A5%E9%A6%99%E6%B8%AF%20%2B%20Worker%20%E7%BC%93%E5%AD%98%E7%9B%90%E5%87%86%E5%A4%87%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-10 21:00｜日期依据：文件名日期

时间：2026-09-10 21:00（Asia/Manila）
项目：某业务公司 / PGServer master
结果：✅ S3→git→GCS 全链路补齐完成；巴西→香港同步完成；git↔GCS 差异归零；
⏳ CDN 缓存刷新待有效 Cloudflare 令牌

## 一、背景

厂商把 vendor_a 缺失的静态资源放到 AWS S3（`bizops-h5`，圣保罗）：

```text
vendor_astatic_zips.tar.gz / vendor_astatic1_zips.tar.gz / ... / vendor_astatic5_zips.tar.gz
```

需求：补到 git，再补到 GCS；同时刷新 vendor_a 全部游戏 CDN 缓存；
巴西客户端资源全部同步到香港；PP 资源检查并同步香港。

## 二、根因与展开规则

TaDa 是 Cocos 构建，页面读 `config.<hash>.json` 后按 uuid 逐个拉
`<game>/assets/game/import/<xx>/<uuid>.<hash>.cconb`，缺文件即 404 卡加载。

展开规则：**zip 内部路径 = zip 所在目录 + 内部路径**

```text
dad/assets/game/game.ae2d9.zip → dad/assets/game/import/26/….bd3d1.cconb
astarte/3.6/web-mobile/assets/vendor_a/vendor_a.45267.zip
                               → astarte/3.6/web-mobile/assets/vendor_a/import/00/….cconb
static/images/intro/fha.zip     → static/images/intro/fha/line.webp
```

用已正常运行的 `vendor_astatic5/c7d`、`vendor_astatic/astarte/3.6/web-mobile/assets/vendor_a`
对照校验过。

## 三、执行步骤（一步一发群）

```text
5616 ① 从 S3 下载 6 个 zip 包
5617 ② 解包 227 个 zip + 与 git 精确比对（227/227 缺失）
5618 ③ 结构分析 + 落地方案（13500 成员，12155 新增）
5640 ④ GCS 三路上传完成 18/18
5648 ⑤ 巴西→香港 同步开始（含预检差异数）
5650 ⑥ git 提交并推送（e8556a76c0 → e93428a04a）
5652 ⑦ 巴西→香港 7/7 完成，差异归零
5653 ⑧ PP 资源检查 + git↔GCS 对齐结果
```

### 关键数据

```text
S3 zip：227 个，225 可解析，2 个 “No Content” 占位（跳过）
落盘：13500 成员 + 225 zip = 13725 个文件 / 372 MB
git ：新增 12155 个文件，0 修改 0 删除，commit e93428a04a（作者 ben <[邮箱已脱敏]>）
GCS ：6 前缀 × 3 目标 = 18 个桶，全部 rc=0，全部 gsutil cp -n（no-clobber）
```

### 巴西 → 香港（gsutil rsync，增量、不删除）

```text
vendor_a-statics  76 → 0      vendor_a-statics1 19 → 0
vendor_a-statics2 10 → 0      vendor_a-statics3  1 → 0
vendor_a-statics4  2 → 0      vendor_a-statics5  1 → 0
pp-static      3 → 0
排除：88 个历史误建嵌套对象（源桶内 bizops-gcs-*-sa/ 前缀），未同步到香港
```

### git ↔ GCS 全量对齐检查（缺失数）

```text
vendor_a-statics  22195/22453 → 0
vendor_a-statics1  3898/3945  → 0
vendor_a-statics2  1496/1519  → 0
vendor_a-statics3 21019/21065 → 0
vendor_a-statics4 12415/12456 → 0
vendor_a-statics5 21550/21584 → 0
pp-static     28604/28891 → 0（PP 路径为 gs2c/…）
```

## 四、验证

```text
dad/assets/game/import/26/….bd3d1.cconb（此前 404）→ 200
dad/assets/game/import/8b/….868dc.cconb（此前 404）→ 200
vendor_a-statics4/dad/assets/game/game.ae2d9.zip          → 200
vendor_a-statics/aa/assets/game/import/02/02d8eccc0.e4ef5.json（老游戏）→ 200
六前缀各随机 6 个新增文件：36/36 → 200
new_game_static_check.py → 新游戏入口 32/32 OK
```

## 五、遗留事项

```text
1) CDN 缓存刷新未执行：
   提供的 cfat_… 令牌调用 CF API 返回 401 Invalid API Token；
   宝塔 /root/bizops-cf-workers.env 的旧令牌同样失效（此前建议撤销）。
   已把 Worker 源码缓存盐改为 v5-20260910-vendor_a-backfill，并新增
   docker/scripts/cf_worker_deploy.py 与 docker/scripts/cf_purge_urls.py，
   拿到有效令牌（Workers Scripts Edit / Cache Purge）即可一键部署+清理。
   补充：Worker 只缓存 200（Cache API，7 天），404 不缓存；本次只新增、
   未改动既有对象内容，因此不刷新也不会给用户旧内容。
2) vendor_astatic2/astarte2 的 vendor_a.113a3.zip、vendor_aMain.08121.zip 是 100 字节
   “No Content” 占位，需厂商重发。
```

## 六、后续防复发

- `docker/scripts/git_gcs_gap_check.py`：按前缀比对 git 与 GCS，缺失即报。
- `docker/scripts/new_game_static_check.py`：新游戏静态入口定时抽检（`*/10`）。
- `docker/scripts/vendor_a_zips_restore.py`：同样的 S3 补包场景可一键重放。

细节 runbook：`docker/线上服务器信息/vendor_a-missing-static-backfill.md`
