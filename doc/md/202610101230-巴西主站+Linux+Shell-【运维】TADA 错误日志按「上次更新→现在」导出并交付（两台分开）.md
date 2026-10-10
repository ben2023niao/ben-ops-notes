---
id: "doc-98f1a01fc8ef"
title: "【运维】TADA 错误日志按「上次更新→现在」导出并交付（两台分开）"
date: "2026-10-10T12:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Docker", "监控告警", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-10-1230-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91TADA%E9%94%99%E8%AF%AF%E6%97%A5%E5%BF%97%E6%8C%89%E4%B8%8A%E6%AC%A1%E6%9B%B4%E6%96%B0%E7%AA%97%E5%8F%A3%E5%AF%BC%E5%87%BA%EF%BC%88%E4%B8%A4%E5%8F%B0%E5%88%86%E5%BC%80%EF%BC%89%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-10-1230-【运维】TADA错误日志按上次更新窗口导出（两台分开）记录.md"
sourceSha256: "af1b6307e000d21b99fce34782e610f5956b4d38a57bb5f15bf7b52ab099bb2c"
sourceSystem: "project-doc"
---

# 【运维】TADA 错误日志按「上次更新→现在」导出并交付（两台分开）

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-10-1230-【运维】TADA错误日志按上次更新窗口导出（两台分开）记录.md`

> 整理日期：2026-10-10 12:30｜日期依据：文件名日期

时间：2026-10-10 12:30（北京）/ 04:30（UTC）
需求演进（群里最终确认版）：
　　① 开发 flux py 要 tada 今天的日志排查；
　　② Ben C++：「把 tada 的错误日志发出来给他」「原始日志太大了，不用」；
　　③ 运维提议两台合并成一条时间线 → C++：「你就把两台的分两个文件发过来就行了」；
　　④ C++：「日志是 0 时区，你发的时候要确认一下他们要的时间」→ 运维按 UTC 对照北京时间切。
最终交付：**两台各一个错误日志文件**，窗口 = **TADA 主服务上次更新时间 → 打包时刻**，
　　　　　已发群（7762 = prod-01、7763 = prod-02），另发统计摘要（7764）。

---

## 一、先把「上次更新」定死（窗口起点怎么来的）

不靠记忆，直接从容器元数据取：

```text
prod-01：game-service-tada-prod  镜像 game-service-tada:20261009-ben  启动 2026-10-09 07:50:14 UTC
prod-02：game-service-tada-prod  镜像 game-service-tada:20261009-ben  启动 2026-10-09 07:58:11 UTC
（tada_ws 是另一个镜像 20261003-ben、10/05 起，不算本次窗口起点）

→ 窗口起点取 prod-01 的 07:50:00 UTC（比两台都早一点，避免漏）
→ 窗口终点 = 打包时刻（2026-10-10 04:26 UTC）
```

```text
时区对照（开发特意提醒的点，服务器日志是 UTC）：
  UTC          2026-10-09 07:50 → 2026-10-10 04:26
  北京(+8)     2026-10-09 15:50 → 2026-10-10 12:26
  巴西(-3)     2026-10-09 04:50 → 2026-10-10 01:26
```

## 二、抽取方法（这里有个必须注意的坑）

```text
坑：tada 日志里 **只有「记录首行」带时间戳**，Traceback 的堆栈行（File/^/xxx）没有时间戳。
    如果直接 grep 错误关键字，堆栈会被切散；如果按时间戳行做时间过滤，
    无时间戳的堆栈行会被当成"大于起点"而错误保留。

做法：**按「记录」为单位处理**——遇到带时间戳的行就开始一条新记录，
      把后续无时间戳的行都算作这条记录的续行；只要这条记录里出现错误关键字，
      就整条输出。这样时间窗准确，堆栈也完整。

命令（在 01/02 上，cd /data/server-runtime/logs/tada）：
  awk -v cut="2026-10-09 07:50:00" \
      -v pat="ERROR|CRITICAL|Traceback|Exception|超时|Timeout|rcode1110" '
    /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] / { flush(); cur=substr($0,1,19);
        active=(cur>=cut); buf=$0 ORS; hit=(active && $0 ~ pat); next }
    { if (active) { buf=buf $0 ORS; if ($0 ~ pat) hit=1 } }
    END { flush() }
    function flush(){ if (buf!="" && hit) printf "%s", buf }
  ' 2026-10-09.log 2026-10-10.log > /tmp/tada-errors-<机器号>.txt

  # 抽完直接 gzip 发群（两台各一个文件，未合并）
  gzip -6 -c /tmp/tada-errors-01.txt > /tmp/tada-errors-01.txt.gz
```

## 三、交付结果

| 文件 | 窗口（UTC） | 实际首/末行 | 行数 | 压缩后 |
| --- | --- | --- | --- | --- |
| tada-errors-01.txt.gz（7762） | 10-09 07:50 → 10-10 04:26 | 07:54:04 → 04:26:42 | 10,714 | 0.86 MB |
| tada-errors-02.txt.gz（7763） | 同上 | 08:00:13 → 04:26:04 | 10,601 | 0.91 MB |

```text
内容：ERROR / CRITICAL / Traceback / 超时 相关记录，整条抽出（含完整堆栈），
      DEBUG/INFO 的正常业务行不含 → 从 1.8GB/台 压到 0.9MB，可直接发群。
```

## 四、Top 错误签名（两台基本一致，摘要已发群 7764）

```text
prod-01                                        prod-02
 851  [IP Blocked] 国家: US 路径 /web…          824  [IP Blocked] 国家: US
 849  common_req error: login expired           817  common_req error: login expired
 263  接口执行超时（connection_task）            287  接口执行超时
 189  gamespin skipped (locked)                 182  gamespin skipped (locked)
  92  getSpinResponse: 0 in items               118  on_first_recharge_control recharge_range not found
  88  on_first_recharge_control …                104  getSpinResponse: 0 in items

错误量按小时仍集中在 UTC 21:00–01:00（北京 05:00–09:00 / 巴西 18:00–22:00），符合当地晚高峰。
```

```text
给排查的三条提示（已写进群消息）：
1) login expired 约 830 条/台，与测试反馈「301 彩金小丑 登录超时」高度相关，优先看；
2) [IP Blocked 国家: US] 约 840 条/台是国家白名单拦截（正常风控），排查时应先排除，
   否则会占掉近一半行数；
3) gamespin skipped (locked) / getSpinResponse: 0 in items 可能与
   「563 招财爆竹 近 20 局全输无派奖」有关，重点看这两段。
```

## 五、下次照抄即可

```bash
# 1) 定窗口起点：看容器启动时间与镜像
docker inspect game-service-tada-prod --format '{{.Config.Image}} {{.State.StartedAt}}'

# 2) 用上面的 awk 抽（改 cut 的值即可）

# 3) 发群（两台各一个文件）
set -a; . /opt/benbot-runtime.env; set +a
curl -s -X POST "https://api.telegram.org/bot$TG_BOT_TOKEN/sendDocument" \
  -F "chat_id=$BEN_BOT_MONITOR_CHAT_ID" -F "document=@/tmp/tada-errors-01.txt.gz" \
  -F "caption=..."
```

## 六、还可按需提供（等开发回话）

```text
· 排除 IP Blocked 的「纯业务错误」版（行数减半，更好读）
· 按 gameid（301 彩金小丑 / 563 招财爆竹）或按用户定向抽取
· 按 UTC 时间把两台合并成一条时间线（本次按开发要求没合并，做了两台分开）
· 任意时间窗重新切（含更早整天；整天建议走对象存储预签名链接）
```

## 七、相关文件

```text
/data/server-runtime/logs/tada/2026-10-09.log、2026-10-10.log    # 本窗口的源日志（01/02）
docker/doc/2026-10-10-1150-【运维】TADA日志按时间窗导出发群记录（开发要今天十点前）.md
      # 上一轮：按「今天十点前」整段给完整日志（含时区对齐与切段规则）
docker/scripts/daily_error_log_pack.py   # 现成的每日错误包脚本（路径仍指向老目录，待修）
```

---

## 八、追加：按开发要求改出「北京时间版」（本文件已含最终口径）

开发在群里补充：「日志是 0 时区……那就要转换一下，比如北京时间 9 点，日志时间是 1 点」，
运维答复「我写代码把日志更改北京时间」。于是新增**可复用的时区换算工具**并重发一份。

### 1. 新增工具 `docker/scripts/log_tz_convert.py`

```text
作用：把日志**行首**时间戳从源时区换算到目标时区（默认 UTC → 北京），
      没有时间戳的 Traceback 堆栈续行原样保留（不会把堆栈切散）。
输出：时间戳后带 +0800 标记，文件头写明「源时区 / 目标时区 / 换算提示 / 堆栈未改动」。
为什么不用 gawk：Ubuntu 默认 awk 是 mawk，没有 mktime/strftime；
      本工具用 python3 标准库 zoneinfo（取不到时回退固定偏移 +8 / -3 / 0）。
用法：
  python3 log_tz_convert.py <输入> [输出] [--from-tz UTC] [--to-tz Asia/Shanghai]
  python3 log_tz_convert.py /tmp/tada-errors-01.txt            # 输出 /tmp/tada-errors-01.txt.bjt
已部署：01/02 的 /opt/dbqp-scripts/log_tz_convert.py
实测：UTC 2026-10-09 21:54:04.432 → 北京 2026-10-10 05:54:04.432+0800（跨天正确）
```

### 2. 转换结果与最终交付

| 文件 | 行数 | 带时间戳已换算 | 窗口（北京时间） | 对应 UTC | 压缩后 |
| --- | --- | --- | --- | --- | --- |
| tada-errors-01-bjt.txt.gz（**7765**） | 10,714 | 2,626 行 | 10-09 15:54 → 10-10 12:26 | 10-09 07:54 → 10-10 04:26 | 0.86 MB |
| tada-errors-02-bjt.txt.gz（**7766**） | 10,601 | 2,669 行 | 10-09 16:00 → 10-10 12:26 | 10-09 08:00 → 10-10 04:26 | 0.91 MB |

```text
群里现在两套都在，按需取用：
  UTC 版     7762（prod-01）/ 7763（prod-02）
  北京时间版 7765（prod-01）/ 7766（prod-02）  ← 开发要的口径
换算说明另发一条（7767）。只有行首时间戳被换算，堆栈与内容未改动，
需要回查原始 UTC 日志时把时间减 8 小时即可。
```

---

## 九、按开发的两条要求加保险（源文件只读 + 先截取再换算）

开发在群里明确了两点顾虑：

```text
「不要去替换源文件时间」「那个太大了，容易把服务器搞出问题」
「那你这个脚本先截取，然后再替换时间」
```

### 1. 现状确认：源文件确实没动过（实测证据）

```text
01/02 /data/server-runtime/logs/tada/ 目录：
  · 没有任何 .bjt / .bak / .tmp / .orig / .sed 之类的改写痕迹（find 命中 0）
  · 2026-10-10.log 仍在正常追加（多次采样 size 持续增长，mtime = 当前时间）
  · 宿主机负载 0.86 / 0.82（load average），内存可用 14GB+ → 抽取过程没有压出问题
我产生的东西只有 /tmp/tada-errors-0X.txt 与 -bjt.txt（各约 6MB），源目录零写入。
```

```text
原因：整条链路没有任何一步写源文件——
  awk 只读源日志 → 输出到 /tmp；log_tz_convert.py 读 /tmp 的抽取件 → 再写 /tmp。
  换算从来不是在大文件上做替换，而是在 6MB 的抽取件上做。
```

### 2. 工具加了两道保险（log_tz_convert.py）

```text
① 禁止原地改写：输出路径与输入是同一文件（含硬链接，比较 realpath + inode）时直接拒绝退出，
   退出码 3，并提示正确用法；确实需要原地改必须显式加 --allow-in-place（正常流程不要用）。
   实测：python3 log_tz_convert.py x.txt x.txt → 被拒、源文件 md5 不变。
② 支持流式（stdin → stdout）：输入写 `-` 即可，
   「先 awk 截取时间段 → 管道 → 换算成北京时间」一步到位，中间不用落大文件；
   此时摘要打到 stderr，不会污染管道内容。
```

### 3. 推荐的标准流程（已实测跑通）

```bash
cd /data/server-runtime/logs/tada
awk -v cut="2026-10-09 07:50:00" \
    -v pat="ERROR|CRITICAL|Traceback|Exception|超时|Timeout|rcode1110" '
  /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] / { flush(); cur=substr($0,1,19);
      active=(cur>=cut); buf=$0 ORS; hit=(active && $0 ~ pat); next }
  { if (active) { buf=buf $0 ORS; if ($0 ~ pat) hit=1 } }
  END { flush() }
  function flush(){ if (buf!="" && hit) printf "%s", buf }
' 2026-10-09.log 2026-10-10.log \
| /usr/bin/python3 /opt/dbqp-scripts/log_tz_convert.py - --no-header > /tmp/tada-errors-bjt.txt
```

```text
实测（01，取 04:30 之后的小窗做验证）：
  管道退出码 = 0，产出 4 行，时间戳形如 2026-10-10 12:37:49.722+0800；
  源目录改写痕迹 0 个，源日志继续正常追加。
```

### 4. 更彻底的做法（开发提到的「后端直接输出北京时间」）

```text
开发提过「最终还是要后端代码输出北京时间的日志格式」。两条路：
  A) 保持日志 UTC + 交付时换算（当前做法）：不用改代码、不影响任何既有解析脚本，
     推荐维持；本次已经把「截取 + 换算」做成一条命令。
  B) 让容器输出北京时间：给容器加 TZ=Asia/Shanghai 即可，但要注意连带影响——
     日志文件名按日期滚动、每日错误包脚本、监控里的时间断言、开发自己的解析脚本
     都隐含「UTC」假设，改之前要一起过一遍，否则会出现「文件名日期与内容对不上」这类问题。
建议：先用 A；确实要改 B 的话按上面清单一起改，并先在一台上试跑一天。
```
