---
id: "doc-7cdff4024d6f"
title: "PG 香港原始日志导出交付记录"
date: "2026-10-20T15:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "监控告警", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/hongkong/live/2026-10-20-1530-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91PG%E9%A6%99%E6%B8%AF%E5%8E%9F%E5%A7%8B%E6%97%A5%E5%BF%97%E5%AF%BC%E5%87%BA%E4%BA%A4%E4%BB%98%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/hongkong/live/2026-10-20-1530-【运维】PG香港原始日志导出交付记录.md"
sourceSha256: "05c4c86435b55f98fb3df67b53333295799d5457f10bdc5c33534be3899d73ea"
sourceSystem: "project-doc"
---

# PG 香港原始日志导出交付记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610201530-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BPython-PG%20%E9%A6%99%E6%B8%AF%E5%8E%9F%E5%A7%8B%E6%97%A5%E5%BF%97%E5%AF%BC%E5%87%BA%E4%BA%A4%E4%BB%98%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-10-20 15:30｜日期依据：文件名日期

时间：2026-10-20 15:30（北京）｜2026-10-20 04:30（巴西圣保罗）
需求：Sean（Python）要香港 PG「这几天的完整日志」，不是只挑错误日志。

## 一、可交付范围

本地日志保留策略是 **48 小时**（2026-10-20 起生效），所以本地现存的 PG 日志只有：

| 文件 | 覆盖时间（UTC） | 对应北京时间 |
| --- | --- | --- |
| `2026-10-18.log` | 10-18 00:00 ~ 23:59 | 10-18 08:00 ~ 10-19 07:59 |
| `2026-10-19.log` | 10-19 00:00 ~ 23:59 | 10-19 08:00 ~ 10-20 07:59 |
| `2026-10-20.log` | 10-20 00:00 ~ 07:22 | 10-20 08:00 ~ 15:22（导出时刻，当天部分） |

更早的日志已按保留策略清理，本地和 S3 都没有更早的 PG 全量包。

## 二、导出与交付

两台分别导出，未合并（开发排查时按机器对齐更方便）：

| 后端 | 原始大小 | 转换+压缩后 | S3 key |
| --- | --- | --- | --- |
| prod-01 `192.0.2.1` | 18G | 2,960,479,309 B（2.96GB） | `full-logs/hk/prod01/2026-10-18_to_2026-10-20/pg-bjt.log.gz` |
| prod-02 `192.0.2.1` | 18G | 2,961,743,319 B（2.96GB） | `full-logs/hk/prod02/2026-10-18_to_2026-10-20/pg-bjt.log.gz` |

处理方式：`log_tz_convert.py --engine awk --gzip`

- 只换算行首时间戳 UTC → 北京时间（+0800）；
- Traceback 堆栈续行原样保留，日志内容未改动；
- gzip level 6，解压：`gzip -dc 文件名 > pg.log`。

下载链接：`aws s3 presign --expires-in 604800`（7 天，到 2026-10-27 07:24 UTC 失效）。
链接已发监控报警群（消息 309），@pythonmichaelxjp @benb6879。

## 三、验证

- prod-01 首行：`2026-10-18 08:00:00+0800.002`
- prod-01 末行：`2026-10-20 15:22:24+0800.993`
- prod-02 首行：`2026-10-18 08:00:00+0800.176`
- S3 对象大小与本地压缩包一致（2,960,479,309 / 2,961,743,319 字节）
- 预签名链接匿名区间下载 `curl -r 0-1023` → **HTTP 206**

上传完成后已删除两台机器 `/tmp` 下的临时包（各约 2.9GB）。

## 四、复现命令

```bash
# 在目标后端
cd /data/server-runtime/logs/server
nice -n 10 ionice -c2 -n7 python3 /opt/bizops-scripts/log_tz_convert.py \
  '2026-10-18.log 2026-10-19.log 2026-10-20.log' \
  /tmp/pg-hk-prod01-bjt.log.gz --engine awk --gzip

# 上传 + 预签名
set -a; . /etc/bizops-game-log-s3.env; set +a
aws s3 cp /tmp/pg-hk-prod01-bjt.log.gz \
  "s3://$某业务公司_LOG_S3_BUCKET/full-logs/hk/prod01/2026-10-18_to_2026-10-20/pg-bjt.log.gz"
aws s3 presign \
  "s3://$某业务公司_LOG_S3_BUCKET/full-logs/hk/prod01/2026-10-18_to_2026-10-20/pg-bjt.log.gz" \
  --expires-in 604800
```
