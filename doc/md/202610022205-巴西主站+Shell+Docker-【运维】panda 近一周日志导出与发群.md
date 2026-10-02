---
id: "doc-f10fbc83766f"
title: "【运维】panda 近一周日志导出与发群"
date: "2026-10-02T22:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "监控告警", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-02-2205-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91panda%E8%BF%91%E4%B8%80%E5%91%A8%E6%97%A5%E5%BF%97%E5%AF%BC%E5%87%BA%E4%B8%8E%E5%8F%91%E7%BE%A4%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-02-2205-【运维】panda近一周日志导出与发群记录.md"
sourceSha256: "6a2b78996e6fdc3963ac72b4a82363788e78049e2e9038f57d812dff05bfbb91"
sourceSystem: "project-doc"
---

# 【运维】panda 近一周日志导出与发群

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-02-2205-【运维】panda近一周日志导出与发群记录.md`

> 整理日期：2026-10-02 22:05｜日期依据：文件名日期

时间：2026-10-02 22:05（北京）/ 14:05（UTC）
需求：flux py「panda 日志 需要同步一份」→「过去一周的给我试试」
对象机器：后台 01 `203.0.113.1`、后台 02 `203.0.113.1`（日志源）
　　　　　宝塔 `35.247.205.6`（中转 + AWS 凭据 + 上传）
结果：① 错误行汇总包（7 天，两台）已直发飞机群；② 完整 7 天日志已上传对象存储，
　　　并发出 7 天有效期的预签名下载链接。

---

## 一、先量体积，决定怎么给

```text
日志位置：/data/server-runtime/logs/panda/YYYY-MM-DD.log（每天一个文件，UTC）
保留：本地 7 天（更旧的由 dbqp_game_log_archive 上传归档桶）

实测体量（2026-09-25 ~ 2026-10-02，7 个整天）：
  单台原始 约 3.2 GB；两台 约 6.4 GB
  整天 gzip 实测：417 MB → 33.2 MB（约 12.6 倍）
  → 一周单台 gzip 后约 300 MB，两个包合计约 617 MB

关键限制：Telegram 机器人 sendDocument 上限 50 MB，整包发不了。
因此拆成两条路：
  ① 错误行汇总包：单台仅 45 KB，直接发群，先看问题
  ② 完整日志：压缩后传对象存储，给带签名的 7 天有效链接
```

## 二、交付一：错误行汇总包（已直发群）

```text
抽取关键字（与 daily_error_log_pack.py 同一套）：
  ERROR | Exception | Traceback | Timeout | rcode1110 | 超时 | SQL Error | Suspicious

产物（gzip 文本，gzip -dc 即可看）：
  panda-prod-01-errors-20260925-20261002.log.gz   45,330 B   4,421 行
  panda-prod-02-errors-20260925-20261002.log.gz   46,199 B   4,407 行
已用 sendDocument 发到监控报警群（message_id 7562 / 7563）

按日期分布（01 / 02）：
  09-25  138 / 114      09-29  1682 / 1658
  09-26  217 / 201      09-30   176 /  170
  09-27  270 / 273      10-01   138 /  142
  09-28 1230 / 1298     10-02    32 /   25
  → 9/28、9/29 两天错误量明显抬升（各 1600+ 条），其余日期在 100~300 条量级

高频错误签名 Top（01；02 基本一致）：
  2465  ERROR sanic...connection_task - 接口执行超时｜异步函数: pan…
   538  Traceback (most recent call last):
   268  ERROR sanic.http - 业务异常: FREE_PACKAGE required but not found: gameid=11
   238  ERROR __mp_main__:risk_control_spin_new_async - 没有匹配的数据! 21,N,0
   210  ERROR sanic.http - JWT 验证失败: User MyGame-N_YYTYBRL login expired.
   196  ERROR sanic.worker.serve - on_first_recharge_control recharge_range N not found.
```

## 三、交付二：完整 7 天日志（对象存储 + 预签名链接）

```text
压缩（在 01/02 上，nice/ionice 低优先级，避免影响业务）：
  cd /data/server-runtime/logs/panda
  nice -n 10 ionice -c3 tar -czf /tmp/panda-prod-XX-full-20260925-20261002.tar.gz \
       2026-09-2[5-9].log 2026-09-30.log 2026-10-0[12].log
  01：302.9 MB（37s）   02：299.1 MB（49s）

中转：宝塔从两台拉包（内网，1~2 秒）
上传：aws s3 cp → s3://dbqp-backend-game-logs-176528004422/exports/panda-20260925-20261002/
  各 11 秒（桶在 ap-northeast-3 大阪）

链接：aws s3 presign --expires-in 604800（7 天，最长就是这个值）
  已实测：两个链接用 curl -r 0-1023 取前 1KB 均返回 206 → 可用
  发送：监控报警群 message_id 7567
  有效期到 2026-10-09 14:05 UTC；过期需要重新生成

安全说明：链接是带签名的临时地址（不是公开桶权限），只在群里发；日志里含 account/gameid
等业务信息，不要外传。
```

## 四、复现命令（以后要再导一次）

```bash
# 1) 错误包（在 01 或 02 上）
cd /data/server-runtime/logs/panda
grep -hE "ERROR|Exception|Traceback|Timeout|rcode1110|超时|SQL Error|Suspicious" \
     2026-09-2[5-9].log 2026-09-30.log 2026-10-0[12].log \
  | gzip -c > /tmp/panda-errors.log.gz

# 2) 完整包
nice -n 10 ionice -c3 tar -czf /tmp/panda-full.tar.gz 2026-09-*.log 2026-10-0*.log

# 3) 上传 + 出链接（在宝塔上，带 AWS 凭据）
set -a; . /root/dbqp-aws-prod.env; set +a
aws s3 cp /tmp/panda-full.tar.gz \
  s3://dbqp-backend-game-logs-176528004422/exports/panda-<起>-<止>/
aws s3 presign s3://dbqp-backend-game-logs-176528004422/exports/panda-<起>-<止>/panda-full.tar.gz \
  --expires-in 604800
```

## 五、顺带发现（未修，等确认）

```text
daily_error_log_pack.py 的扫描路径已经过期：
  脚本里写的是 LOG_ROOT = /opt/pgserver/logs，并匹配 dbqp-*-release-* 目录，
  这是 9/18 之前的旧发布容器路径。现在：
    · 01/02 的 /opt/pgserver 已清空，容器换成 game-service-*-prod；
    · 日志实际落在 /data/server-runtime/logs/<厂家>/YYYY-MM-DD.log。
  也就是说 01/02 上那两条 `0 7 * * * daily_error_log_pack.py` 目前基本扫不到东西
  （等于每天 07:00 白跑一次，不会有错误包发群）。
  本次导日志是手工按新路径做的；如果希望恢复「每天自动发错误包」，需要把
  LOG_ROOT 与文件名匹配规则改成新路径（/data/server-runtime/logs）。
```

## 六、相关文件

```text
docker/scripts/daily_error_log_pack.py     # 现成的「错误行→tar.gz→发群」脚本（路径需更新）
/data/server-runtime/logs/panda/           # 日志源（01/02）
/root/dbqp-aws-prod.env                    # 宝塔上的 AWS 凭据（600，不入库）
docker/doc/2026-08-07-2100-【运维】机器人日志补03与宝塔bot备用空闲及部署原则记录.md  # 日志归档链路背景
```
