---
id: "doc-43c89bb2c5f8"
title: "【运维】vendor_d 近 5 小时日志（北京时间）导出 + S3 交付"
date: "2026-10-15T11:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "监控告警", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-10-15-1140-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_d%E8%BF%915%E5%B0%8F%E6%97%B6%E6%97%A5%E5%BF%97%28%E5%8C%97%E4%BA%AC%E6%97%B6%E9%97%B4%29%E5%AF%BC%E5%87%BA%E4%BA%A4%E4%BB%98%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-10-15-1140-【运维】vendor_d近5小时日志(北京时间)导出交付记录.md"
sourceSha256: "a78b73f8d3196318d8a6a173256f398807a3185639b331f3bb0d7b57c93cd953"
sourceSystem: "project-doc"
---

# 【运维】vendor_d 近 5 小时日志（北京时间）导出 + S3 交付

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-10-15-1140-【运维】vendor_d近5小时日志(北京时间)导出交付记录.md`

> 整理日期：2026-10-15 11:40｜日期依据：文件名日期

时间：2026-10-15 11:40（北京）/ 03:40（UTC）
需求：flux py「巴西线上 vendor_d 今天的日志麻烦给我下」→「过去 5 小时的」（运维答复「好」）。
执行：两台后端 01/02 都取，按既有约定**换算成北京时间**后上传 S3，群里发下载链接。

---

## 一、窗口

```text
发起时服务器时间：2026-10-15 03:35 UTC（= 北京 11:35）
「过去 5 小时」→ 窗口取 UTC 2026-10-14 22:35:00 ~ 2026-10-15 03:35:59
               = 北京时间      2026-10-15 06:35:00 ~ 11:35:59
注意：窗口**跨两个 UTC 日期文件**（2026-10-14.log 的尾部 + 2026-10-15.log 的前部），
      所以导出时两个文件都要传进去。
```

## 二、这次新加的能力：按时间窗导出（--since/--until）

```text
log_tz_convert.py 的 awk 引擎新增 --since/--until（UTC，"YYYY-MM-DD HH:MM:SS"），
把「按记录时间过滤」和「时间戳换算北京时间」**合并成一次 awk 扫描**：

  · 按「记录」处理：带时间戳的行开新记录，其余行（Traceback 的 File/^ 续行）算它的续行；
    只有记录首行时间戳落在窗口内才整条输出 —— 这样堆栈不会被切散、窗口边界也不会串行。
  · 窗口外记录直接丢弃；无时间戳的前导行沿用上一条记录的状态。
  · 不改源文件，输出可 --gzip 直出。

用例（在目标后端上）：
  cd /data/server-runtime/logs/vendor_d
  nice -n 10 ionice -c2 -n7 /usr/bin/python3 /opt/bizops-scripts/log_tz_convert.py \
    "2026-10-14.log 2026-10-15.log" /tmp/vendor_d-5h-bjt.log.gz \
    --engine awk --gzip --since "2026-10-14 22:35:00" --until "2026-10-15 03:36:00"

边界用例已本地验证：窗口前一秒被排除、窗口起点保留、窗口末秒保留、窗口后一秒排除，
Traceback 堆栈续行完整保留、时间戳换成了 +0800。
```

## 三、交付结果

| 机器 | 输出窗口（北京时间，实测首/末行） | 行数 | 文件大小 |
| --- | --- | --- | --- |
| prod-01 | 2026-10-15 06:35:01+0800 → 11:35:58+0800 | 513,277 | 12.4 MB |
| prod-02 | 2026-10-15 06:35:00+0800 → 11:35:58+0800 | 493,888 | 11.9 MB |

```text
S3 位置（桶 bizops-backend-game-logs-176528004422，region ap-northeast-3）：
  full-logs/br/prod01/2026-10-14_2235-to_2026-10-15_0335/vendor_d-5h-bjt.log.gz   (12,989,793 B)
  full-logs/br/prod02/2026-10-14_2235-to_2026-10-15_0335/vendor_d-5h-bjt.log.gz   (12,488,608 B)
链接：aws s3 presign --expires-in 604800（7 天）
      实测匿名 curl -r 0-1023 → 两个链接均 http=206（可下载）
解压：gzip -dc 文件名 > vendor_d.log
已发群（监控报警群 -1004456082456，message_id=212），消息里标注了文件大小与行数。
```

## 四、收尾

```text
· 01/02 本地临时包已删除（/tmp 是内存盘，不在生产机上留大文件）
· 源日志目录全程只读，未做任何写入
```

## 五、相关文件

```text
docker/scripts/log_tz_convert.py          # 本次新增 --since/--until（awk 引擎按时间窗 + 换算）
docker/doc/2026-10-12-1530-【运维】vendor_d一周日志(北京时间)导出并上传S3交付记录.md   # 上次同类交付（一周）
docker/doc/2026-10-10-1340-【架构改造】每日各厂家错误日志发群（巴西+香港）-S3预签名链接方案记录.md
```
