---
id: "doc-2f2d017b8d28"
title: "vendor_a 错误日志导出与文件句柄排查记录"
date: "2026-10-20T18:28:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "监控告警", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-10-20-1828-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_a%E9%94%99%E8%AF%AF%E6%97%A5%E5%BF%97%E5%AF%BC%E5%87%BA%E4%B8%8E%E6%96%87%E4%BB%B6%E5%8F%A5%E6%9F%84%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-10-20-1828-【运维】vendor_a错误日志导出与文件句柄排查记录.md"
sourceSha256: "281df79713b4373cec963d3d4524c0135046f9486ce576f6f38932ecbeffb135"
sourceSystem: "project-doc"
---

# vendor_a 错误日志导出与文件句柄排查记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-10-20-1828-【运维】vendor_a错误日志导出与文件句柄排查记录.md`

> 整理日期：2026-10-20 18:28｜日期依据：文件名日期

时间：2026-10-20 18:28（北京）｜2026-10-20 07:28（巴西圣保罗）
需求：Ben C++「把 vendor_a 的错误日志发一下」（玩家偶发卡加载 / 进不去游戏）

## 一、导出范围

本地保留 48 小时，vendor_a 现存最早是 10-18：

- 窗口（UTC）：2026-10-18 00:00:00 → 2026-10-20 10:04:47
- 对应北京：2026-10-18 08:00 → 2026-10-20 18:04
- 两台分别导出，不合并（prod-01 / prod-02 各一个文件）

抽取规则：按「记录」为单位，只有记录首行带时间戳，Traceback 续行跟着整条走；
命中 `ERROR|CRITICAL|Traceback|Exception|Timeout|超时|rcode1110` 即整条输出，堆栈完整。
时间戳保持 **UTC**（群里已说明看北京时间 +8），不做二次换算，避免丢续行。

| 后端 | 行数 | 压缩后 | S3 key |
| --- | --- | --- | --- |
| prod-01 `192.0.2.1` | 36,294 | 967,417 B | `exports/br/prod01/2026-10-18_to_2026-10-20/vendor_a-errors-utc.txt.gz` |
| prod-02 `192.0.2.1` | 4,202 | 778,234 B | `exports/br/prod02/2026-10-18_to_2026-10-20/vendor_a-errors-utc.txt.gz` |

下载链接为 7 天预签名，已发监控报警群（消息 317），匿名区间下载实测 HTTP 206。

## 二、关键发现：prod-01 文件句柄被顶满

```
prod-01  game-service-vendor_a-prod  镜像 game-service-vendor_a:20261014-ben
        容器 soft nofile = 1024（hard 524288）
        worker 进程 31 当前持有 1023 个 fd —— 基本等于上限
        报错样例：common_req error:[Errno 24] Too many open files
                  '/app/vendor_a/data/lj500/GameInfoAck.json'
```

错误量：

| 机器 | 条数 | 首次 | 最后 |
| --- | --- | --- | --- |
| prod-01 | 4,877 | 2026-10-18 00:14:59 UTC | 2026-10-20 10:04:47 UTC |
| prod-02 | 36 | 2026-10-20 00:45:42 UTC | 仍在出现 |

prod-01 按天分布：10-18 968 次、10-19 935 次、10-20 448 次（到 10:04）。
这是持续性句柄耗尽，和玩家偶发卡加载/请求失败的时间特征吻合。

### 建议

1. **先缓解**：vendor_a 容器启动参数加

   ```bash
   --ulimit nofile=65535:524288
   ```

   当前只有 1024，对游戏服务明显偏低。
2. **根治**：请开发排查 `/app/vendor_a/data/.../GameInfoAck.json` 是否每次请求打开后没有
   `close()`（报错集中在这些文件）。

## 三、复现命令

```bash
cd /data/server-runtime/logs/vendor_a
for f in $(ls | sort); do
  case "$f" in *.gz) zcat "$f";; *) cat "$f";; esac
done | awk -v pat="ERROR|CRITICAL|Traceback|Exception|Timeout|timeout|超时|rcode1110" '
  /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] / { flush(); buf=$0 ORS; hit=($0 ~ pat); next }
  { buf=buf $0 ORS; if ($0 ~ pat) hit=1 }
  END { flush() }
  function flush(){ if (buf!="" && hit) printf "%s", buf; buf=""; hit=0 }
' > /tmp/vendor_a-errors-01.txt

# 查看句柄
docker exec game-service-vendor_a-prod sh -c 'grep "Max open files" /proc/1/limits; ls /proc/31/fd | wc -l'
```

## 四、备注

- 10-18 是本地现存最早的一天；更早日志已按 48 小时保留策略清理。
- 本次没有重启任何 vendor_a 容器，避免影响线上。
