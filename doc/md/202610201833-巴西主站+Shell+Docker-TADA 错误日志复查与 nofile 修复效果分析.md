---
id: "doc-030d4971cd3b"
title: "TADA 错误日志复查与 nofile 修复效果分析"
date: "2026-10-20T18:33:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-20-1833-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91TADA%E9%94%99%E8%AF%AF%E6%97%A5%E5%BF%97%E5%A4%8D%E6%9F%A5%E4%B8%8Enofile%E4%BF%AE%E5%A4%8D%E6%95%88%E6%9E%9C%E5%88%86%E6%9E%90.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-20-1833-【运维】TADA错误日志复查与nofile修复效果分析.md"
sourceSha256: "83660a904676a56f5589986a00453fca054e6e324d752a1ae29978aeaf671431"
sourceSystem: "project-doc"
---

# TADA 错误日志复查与 nofile 修复效果分析

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-20-1833-【运维】TADA错误日志复查与nofile修复效果分析.md`

> 整理日期：2026-10-20 18:33｜日期依据：文件名日期

时间：2026-10-20 18:33（北京）｜2026-10-20 07:33（巴西圣保罗）
背景：18:29 把全部容器 `nofile` 软限制从 1024 提到 65535，本次复查 TADA 错误日志。

## 一、本次导出

| 后端 | 行数 | 压缩后 | S3 key |
| --- | --- | --- | --- |
| prod-01 | 36,310 | 967,496 B | `exports/br/prod01/2026-10-18_to_2026-10-20/tada-errors-utc-1031.txt.gz` |
| prod-02 | 4,203 | 778,256 B | `exports/br/prod02/2026-10-18_to_2026-10-20/tada-errors-utc-1031.txt.gz` |

范围：2026-10-18 00:00:00 → 2026-10-20 10:31 UTC（北京 10-18 08:00 → 10-20 18:31）。
时间戳保持 UTC；7 天预签名链接已发群（消息 326），匿名区间下载实测 HTTP 206。

## 二、nofile 修复效果

`Too many open files`（`common_req error:[Errno 24]`）：

| 机器 | 总条数 | 最后一条（UTC） | 10:29 之后 |
| --- | --- | --- | --- |
| prod-01 | 2,352 | 2026-10-20 10:04:47 | **0** |
| prod-02 | 17 | 2026-10-20 04:56:59 | **0** |

prod-01 修复前按小时分布（10-20）：

| 小时（UTC） | 05 | 06 | 07 | 08 | 09 | 10 |
| --- | --- | --- | --- | --- | --- | --- |
| EMFILE 次数 | 36 | 13 | 18 | 13 | 17 | 15 |

10:29 完成 `prlimit` 后，两台都没有再出现该错误；
10:29–10:31 期间 prod-01 只有 1 条 `tada_request_rejected`，prod-02 为 0。

**结论：nofile 提升已止血。** 但 TADA worker 当前仍持有约 1023 个 fd，
说明句柄泄漏还在，开发仍需修 `/app/tada/data/<game>/GameInfoAck.json` 的关闭逻辑。

## 三、最近错误构成

按小时统计（ERROR/CRITICAL）：

| 小时（UTC） | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prod-01 | 77 | 33 | 45 | 15 | 22 | 16 | 117 | 29 |
| prod-02 | 23 | 40 | 10 | 2 | 5 | 4 | **804** | 11 |

最近两小时 TOP：

| 类型 | prod-01 | prod-02 |
| --- | --- | --- |
| `[IP Blocked] 拒绝访问` | 86 | 776 |
| `Too many open files` | 45 | 0 |
| `tada_request_rejected` | 10 | 12 |
| `connection_task` 异常 | 9 | 10 |
| `Suspicious private IP` | 7 | 21 |

prod-02 在 09 点（UTC）那 804 条里 776 条是 IP Blocked，属于批量/扫描请求被拦截，
不是服务自身报错；prod-01 同时段 117 条也以为主。

## 四、后续

1. 继续观察 24 小时，确认 EMFILE 是否彻底归零（现在窗口只有 2 分钟）。
2. 开发修 `GameInfoAck.json` 句柄未关闭问题。
3. 若要让进程重启后也保持新限制，必须由发布脚本创建容器——脚本已改好；
   直接 `docker restart` 仍会沿用旧容器的 ulimit，需要用 `start.sh` 重建。

## 五、复核

```bash
f=/tmp/tada-errors-01-new.txt
grep -c "common_req error:\[Errno 24\]" "$f"
grep "common_req error:\[Errno 24\]" "$f" | tail -1
grep -E "\| (ERROR|CRITICAL) " "$f" | cut -c1-13 | sort | uniq -c | tail
```
