---
id: "doc-8e6b8be63383"
title: "【发布】PG + share.so V20260905 滚动发布记录"
date: "2026-09-05T15:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "自动化", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-05-1545-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91PG%E4%B8%8Eshare.so%20V20260905%E6%BB%9A%E5%8A%A8%E5%8F%91%E5%B8%83%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-05-1545-【发布】PG与share.so V20260905滚动发布记录.md"
sourceSha256: "dacb3fa3c94e61538ef5d2d234dca620ef2abbdc208166e2d0e88b33438c9b44"
sourceSystem: "project-doc"
---

# 【发布】PG + share.so V20260905 滚动发布记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-05-1545-【发布】PG与share.so V20260905滚动发布记录.md`

> 整理日期：2026-09-05 15:45｜日期依据：文件名日期

时间：2026-09-05 15:45（Asia/Manila）
项目：某业务公司 / PGServer master（后端发布）
状态：✅ 完成（滚动更新，用户影响最小）

## 一、内容

```text
origin：71b7ee6b（更新 PG 部分游戏数值）+ 176fa9b3（V20260905 share.so）
1) api 接口返回数据格式修正；
2) 返奖接口倍数限制修正：超限强制普通返奖；
3) PG 数值配置：48/98/1492288/1543462/1695365/113/126/67/84；
4) share.so 6290944B md5 30ff370b9bc698ab4042736771544c39（全部厂家更新）。
```

## 二、发布过程（尽量不掉线）

```text
1) 02/03 仓库同步 origin 176fa9b3 + 单域配置；
2) 02/03 PG 重建启动（master-176fa9b3）；
3) nginx pg_game_backend 恢复 02/03（三台上游）承接 PG 流量；
4) 01 PG 重建更新（02/03 兜底）；
5) 01 其余厂家容器写入新 share.so 并逐个短重启。
```

## 三、验证

```text
1) PG 3 台：/app/share.so md5 30ff370b…，server.py 2653b6d7…，
   风险配置 48 md5 14af8b21…；
2) 01 全部厂家容器 share md5 30ff370b…；
3) health：api/pg-games/vendor_a/pp/g759 .cdn-tokyo-bizops 全 200；
4) platform-api 仍单域 cdn-tokyo（29 条，vendor_a/xqv=0）。
```

## 四、注意

```text
02/03 非 PG 容器因 update_pgserver 的 docker prune 被清理；
恢复三机模式时需逐个重建启动（不影响当前 PG 三台与 01 全厂家）。
```

## 五、飞机群通知 message_id

```text
5204 方案
5209 进度（PG 02/03 接入 + 01 更新）
5210 发布完成
```

## 六、本地提交

```text
（提交号文末回写；本地已含 origin merge 7ffa3ee4，未 Push）
```

## 七、回切单机 01（15:50 追加）

```text
用户要求线上保持 01 单机便于观察日志：
1) 02/03 PG 容器 docker stop（Exited，保留新版镜像）；
2) nginx 还原 bak-20260905-pg-rolling -> pg_game_backend 仅 01；
3) 验证 api/pg-games .cdn-tokyo-bizops /health 200。
后续恢复三机：nginx 去掉 down + 启动/重建 02/03 容器。
```
