---
id: "doc-a6d9d567f783"
title: "【发布】platform-api pg3 分组扩充至 13 款（01 单机）"
date: "2026-09-04T13:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "自动化", "CDN", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-04-1345-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91pg3%E5%88%86%E7%BB%84%E6%89%A9%E5%85%8513%E6%AC%BE%E4%B8%8A%E7%BA%BF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-04-1345-【发布】pg3分组扩充13款上线记录.md"
sourceSha256: "e47655e2f9570b60e134267a42d53a77c6890dabbfdff957988f7d1ce49d7eba"
sourceSystem: "project-doc"
---

# 【发布】platform-api pg3 分组扩充至 13 款（01 单机）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609041345-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BDocker%2B%E8%87%AA%E5%8A%A8%E5%8C%96-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91platform-api%20pg3%20%E5%88%86%E7%BB%84%E6%89%A9%E5%85%85%E8%87%B3%2013%20%E6%AC%BE%EF%BC%8801%20%E5%8D%95%E6%9C%BA%EF%BC%89.md)

> 整理日期：2026-09-04 13:45｜日期依据：文件名日期

时间：2026-09-04 13:45（Asia/Manila）
项目：某业务公司 / PGServer master（platform-api domains/pg.json）
状态：✅ 完成（01 热更验证通过）

## 一、变更

```text
pg.json special_games.pg3.game_ids：
旧 5 款 -> 13 款
新增：1950910, 1997301, 2009635, 2024510, 2035783,
      2040102, 2058347, 2081892（保留 2100928/1849515/1981965/67/71）
static/game hosts 维持三 Argo 域（vendor_a-cdn-2026/xqv9m8/cdn-tokyo-bizops）。
```

## 二、发布

```text
备份：/root/bizops-pg3-update-before/（baota + 01 宿主 + 01 容器 pg.json）
本地修改 -> 01 同步 -> docker cp pg.json -> restart platform-api。
```

## 三、验证

```text
1) 容器内 pg3.game_ids=13 且包含 2081892 ✅；
2) 无重复、hosts 三域完整；
3) api.vendor_a-cdn-2026.icu/health rcode=0。
```

## 四、飞机群通知 message_id

```text
5160 任务开始
5161 发布完成
```

## 五、本地提交

```text
（提交号文末回写；master 领先 origin/master，未 Push）
```
