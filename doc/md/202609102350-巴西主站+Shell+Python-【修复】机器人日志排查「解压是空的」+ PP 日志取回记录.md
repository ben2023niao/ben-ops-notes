---
id: "doc-620ddfa1f06a"
title: "【修复】机器人日志排查「解压是空的」+ PP 日志取回记录"
date: "2026-09-10T23:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "故障排查", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-10-2350-%E3%80%90%E4%BF%AE%E5%A4%8D%E3%80%91%E6%9C%BA%E5%99%A8%E4%BA%BA%E6%97%A5%E5%BF%97%E6%8E%92%E6%9F%A5%E8%A6%86%E7%9B%96%E5%8C%BA%E9%97%B4%2BPP%E6%97%A5%E5%BF%97%E5%8F%96%E5%9B%9E%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-10-2350-【修复】机器人日志排查覆盖区间+PP日志取回记录.md"
sourceSha256: "529d5299788eaffa5006377fdcbd8af771c99276bfc43173f2b925f9248467e9"
sourceSystem: "project-doc"
---

# 【修复】机器人日志排查「解压是空的」+ PP 日志取回记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609102350-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BPython-%E3%80%90%E4%BF%AE%E5%A4%8D%E3%80%91%E6%9C%BA%E5%99%A8%E4%BA%BA%E6%97%A5%E5%BF%97%E6%8E%92%E6%9F%A5%E3%80%8C%E8%A7%A3%E5%8E%8B%E6%98%AF%E7%A9%BA%E7%9A%84%E3%80%8D%2B%20PP%20%E6%97%A5%E5%BF%97%E5%8F%96%E5%9B%9E%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-10 23:50｜日期依据：文件名日期

时间：2026-09-10 23:50（Asia/Manila）
项目：某业务公司 / PGServer master
结果：✅ 定位并修复机器人日志列表的「小时标签 ≠ 文件实际覆盖区间」缺陷；
✅ PP 2026-09-10 00:17:12.798 ±10 分钟日志已打包发群

## 一、需求

Ben(C++) 要 PP 在 `2026-09-10 00:17:12.798` 前后 10 分钟的日志；
运维从机器人「日志排查」取了 `7天内 prod-01 pp 2026-09-10 00:00`，
C++ 反馈「日志里面什么都没有」。

## 二、先排除取数链路（完整复现机器人代码）

`docker/scripts/dbg_bot_logfetch.py` 在 bot 容器内直接调用插件的
`_list_items` / `_cache_items` / `_fetch_item`：

```text
本地7天内  pp.log-20260910-000412.gz  -> 48950B，gzip 魔数对，解压 6561 行
S3 历史    pp.log-20260903-090531.gz  ->  8380B，解压 1870 行
```

文件本身没坏、也不是 0 字节；SFTP 与 S3 两条路径都正常。

## 三、真因：小时标签 ≠ 实际覆盖区间

轮转文件的命名时刻是**轮转发生的时刻**，文件内容区间是
「上一次轮转 ~ 本次轮转」。PP 在 09-10 的 00 点这一小时被切成两份：

```text
pp.log-20260910-000412.gz 覆盖 09-09 23:5x ~ 00:04:12   6561 行
pp.log-20260910-000841.gz 覆盖 00:04:12  ~ 00:08:41      512 行
pp.log-20260910-010041.gz 覆盖 00:08:41  ~ 01:00:41     9474 行   <- 00:17 在这里
```

旧实现把 `stamp` 格式化成 `%Y-%m-%d %H:00`，于是这三份被标成
`00:00 / 00:00 / 01:00`，且列表按 mtime 倒序 →
「00:00」里排第一的是那份 512 行、**完全不含 00:17** 的小尾巴文件。
运维点它发给 C++，就成了「日志里面什么都没有」。

## 四、修复

改 `docker/ben-bot/data/scripts/日志排查/action.py`：

```text
1) 远端列目录时按 (目录, base) 记录上一份轮转时刻，算出每份文件的
   cover_start / cover_end / cover（"MM-DD HH:MM~MM-DD HH:MM"）
2) 列表排序：同一小时内先按覆盖起点升序（覆盖更长），再按小时倒序
3) 按钮标签追加覆盖区间；附件 caption 也带上覆盖区间
4) 菜单提示补充「按覆盖区间挑文件」的说明
```

修复后实测（bot 容器内渲染）：

```text
[prod-01 7天内] 2026-09-10 09:00 (09-10 08:08~09-10 09:02)  37.1KB
[prod-01 7天内] 2026-09-10 09:00 (09-10 09:02~09-10 09:06)   2.5KB
...
FETCHED pp.log-20260910-000412.gz: 48950 bytes   （不再是小尾巴）
```

部署：`/opt/pgserver/docker/ben-bot/data/scripts/日志排查/action.py` 已更新并
`docker restart bizops-ben-bot`；重启后验证新标签生效。

用法：找某时刻的日志，点覆盖区间包含该时刻的那一项。
例如 00:17 → `2026-09-10 01:00 (09-10 00:08~09-10 01:00) 107.4KB`。

## 五、PP 日志取回（手工补齐）

新增 `docker/scripts/game_log_time_window.py`：按**时间窗口**（而不是行窗口）
从后端轮转 gz 里取日志，文件选择规则与上文一致（S 时刻文件覆盖
「上一次轮转 ~ S」）。

```bash
python3 /opt/bizops-scripts/game_log_time_window.py --vendor pp \
    --ts "2026-09-10 00:17:12.798" --minutes 10 \
    --hosts 192.0.2.1,192.0.2.1 --outdir /root/vendor_a-zips/pplog
```

结果：

```text
prod-01: 用到 2 个轮转文件（00:08:41、01:00:41），5773 行
         时间跨度 00:07:14.532 ~ 00:27:11.382，窗口内 ERROR 56 条
prod-02: pp 日志最后一条是 09-09 08:30（未在跑），仅 3 行
打包   : pp-log-20260910-001712-pm10m.tar.gz（含两个 txt）
```

目标时刻上下文：

```text
00:17:12.798 INFO  load .../risk_control/default/control_2_0.json ok.
00:17:12.798 ERROR .../default/control_2_1.json not exist.
...（control_X_1..4 全部 not exist，只有每组的 control_X_0.json 是 ok）
```

## 六、本轮新增工具

```text
docker/scripts/game_log_time_window.py      按时间窗口取后端日志（多后端）+ 打包
docker/scripts/dbg_bot_logfetch.py          在 bot 容器内复现日志排查取数（排障用）
docker/scripts/check_pp_rotation_coverage.sh 列出每份轮转文件的实际覆盖区间
```
