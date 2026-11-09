---
id: "doc-914428fe8b5c"
title: "【运维】vendor_d 一周日志（北京时间）导出 + 上传 S3 交付"
date: "2026-10-12T15:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Docker", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-10-12-1530-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_d%E4%B8%80%E5%91%A8%E6%97%A5%E5%BF%97%28%E5%8C%97%E4%BA%AC%E6%97%B6%E9%97%B4%29%E5%AF%BC%E5%87%BA%E5%B9%B6%E4%B8%8A%E4%BC%A0S3%E4%BA%A4%E4%BB%98%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-10-12-1530-【运维】vendor_d一周日志(北京时间)导出并上传S3交付记录.md"
sourceSha256: "6bf1cc55e360a0e29f27dd4f13ff9a6dbeaf0616b46117baab9e44e62d2ec4e4"
sourceSystem: "project-doc"
---

# 【运维】vendor_d 一周日志（北京时间）导出 + 上传 S3 交付

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-10-12-1530-【运维】vendor_d一周日志(北京时间)导出并上传S3交付记录.md`

> 整理日期：2026-10-12 15:30｜日期依据：文件名日期

时间：2026-10-12 15:30（北京）/ 07:30（UTC）
需求：
```text
· 开发需要巴西线上 vendor_d「一个星期的、2 台后端」的日志
· 需要转换为北京时间后上传到 AWS S3 给开发下载
· 顺带问：每日错误日志的定时任务怎么没正常工作？
```
---

## 一、先回答「定时任务怎么没正常工作」

```text
结论：**任务本身一直在正常工作**，只是没有发群消息 —— 因为它还带着 `--no-notify`，
      原因是「后端技术群」的 chat_id 一直没拿到（这一点从 10-10 起就在等）。

证据（巴西 01/02 的 /var/log/bizops-error-pack.log，2026-10-12 07:03~07:07）：
  07:03:26  合计错误记录 31572 条
  07:03:56  已上传 8 个厂家（失败 0），s3://…/error-packs/br/prod01/2026-10-11/
  07:03:56  --no-notify：不发送群消息
  （02 机器同样：07:06:57 合计 32372 条 → 07:07:26 上传完成）
→ 10-11、10-12 两天都按时跑过、也都成功上传，只是按设计没发群。

顺手修掉一个小毛病：cron 把 stdout 重定向到了脚本自己的日志文件，
  而脚本内部又写同一个文件 → 日志里每行出现两次。已把 cron 的重定向改成
  /var/log/bizops-error-pack.cron.log（四台都改了）。
```

```text
要让群消息真正发出来，只差一个 chat_id：把四台 cron 里的 `--no-notify` 换成
`某业务公司_ERROR_PACK_CHAT_IDS=<群id>` 即可（我可以直接改）。
群 id 的获取办法见 docker/doc/2026-10-10-1340-…-S3预签名链接方案记录.md 第五节。
```

## 二、vendor_d 一周日志交付

### 1. 范围与体积

```text
取数：/data/server-runtime/logs/vendor_d/2026-10-04.log ~ 2026-10-11.log（8 个 UTC 整天）
      对应北京时间窗口：2026-10-04 08:00 ~ 2026-10-12 07:59（+0800）—— 正好 7×24 小时
说明：vendor_d 日志按 UTC 日期切文件，转北京时间后首行会落在北京 08:00，
      所以取 8 个 UTC 文件才能覆盖完整的 7 个北京日。

原始体量：prod-01 10213 MB、prod-02 10053 MB（各约 10GB）
转换+压缩：prod-01 229s → 1062 MB；prod-02 285s → 1047 MB（gzip level 6）
行数：prod-01 35,862,488 行；prod-02 35,335,221 行
```

### 2. S3 位置与下载链接

```text
桶：bizops-backend-game-logs-176528004422（ap-northeast-3）
key：
  full-logs/br/prod01/2026-10-04_to_2026-10-11/vendor_d-bjt.log.gz   （1,113,834,574 B）
  full-logs/br/prod02/2026-10-04_to_2026-10-11/vendor_d-bjt.log.gz   （1,097,538,147 B）
链接：aws s3 presign --expires-in 604800（7 天，到 2026-10-19 07:22 UTC 失效）
      实测匿名 curl -r 0-1023 → **http=206**，链接可用
解压：gzip -dc 文件名 > vendor_d.log
```

### 3. 内容校验

```text
prod-01 首行：2026-10-04 08:00:00+0800.498 | DEBUG | sanic.app:handle_request …
prod-01 末行：2026-10-12 07:59:59+0800.813 | INFO  | sanic.worker.serve …
prod-02 首/末行同口径（08:00:00+0800 / 07:59:59+0800）
包内前 3 行是换算说明头（源时区 UTC、目标北京时间、只换算行首时间戳）
→ 确认：**所有行首时间戳都已换成北京时间并带 +0800**，Traceback 堆栈续行原样保留、日志内容未改动
```

```text
上传完成后已删除 01/02 本地临时包（/tmp 是内存盘，各占 1GB 没必要留），S3 上保留原件。
```

## 三、这次新加的能力：日志时区换算的 awk 快引擎

```text
问题：一周原始日志 10GB/台，之前的 Python 逐行换算（log_tz_convert.py）在这体量上会非常慢。
做法：给 docker/scripts/log_tz_convert.py 增加 `--engine awk`（默认 auto：源文件 ≥64MB 自动用）：
  · Ubuntu 上的 awk 是 mawk，**没有 mktime/strftime**，所以用 Howard Hinnant 的 civil 日期算法
    手算「UTC → UTC+8」，纯整数运算，mawk 处理 10GB 只需 3~5 分钟（含 gzip）
  · 支持多文件/通配（'2026-10-0[4-9].log 2026-10-1[01].log'）与 --gzip 直出压缩
  · 只改行首时间戳，堆栈续行与非时间戳行原样通过
坑（已修）：
  · header 必须 flush 后再交给 awk，否则会被挤到文件末尾；
  · **不能把 gzip 文件对象当 awk 的 stdout**（子进程直接写底层 fd 会绕过压缩器 → 产出损坏 gz），
    改为「awk → 管道 → gzip 压缩器」；
  · gzip 压缩级别用 6（默认 9 在 10GB 上会慢几十分钟）。
边界用例已测：北京日界（15:59:59/16:00:00 UTC）、跨年、闰年 2 月、月初。
```

## 四、复现命令（以后再导任意厂家/任意区间）

```bash
# 在目标后端上（例：vendor_d 一周，北京时间，直出 gz）
cd /data/server-runtime/logs/vendor_d
nice -n 10 ionice -c2 -n7 /usr/bin/python3 /opt/bizops-scripts/log_tz_convert.py \
  '2026-10-04.log 2026-10-05.log 2026-10-06.log 2026-10-07.log \
   2026-10-08.log 2026-10-09.log 2026-10-10.log 2026-10-11.log' \
  /tmp/vendor_d-week-bjt.log.gz --engine awk --gzip

# 上传 + 出链接
set -a; . /etc/bizops-game-log-s3.env; set +a
aws s3 cp /tmp/vendor_d-week-bjt.log.gz \
  "s3://$某业务公司_LOG_S3_BUCKET/full-logs/br/prod01/2026-10-04_to_2026-10-11/vendor_d-bjt.log.gz"
aws s3 presign "s3://$某业务公司_LOG_S3_BUCKET/full-logs/br/prod01/2026-10-04_to_2026-10-11/vendor_d-bjt.log.gz" \
  --expires-in 604800
```

## 五、相关文件

```text
docker/scripts/log_tz_convert.py               # 时区换算工具（本次新增 awk 快引擎）
docker/scripts/daily_vendor_error_pack.py      # 每日各厂家错误日志（S3 + 预签名链接）
docker/doc/2026-10-10-1340-…-S3预签名链接方案记录.md   # 每日任务的设计与待办（群 id）
```
