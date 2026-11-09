---
id: "doc-0fa19e959c1b"
title: "【运维】vendor_a 日志按时间窗导出发群（开发要「今天十点之前」）"
date: "2026-10-10T11:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "监控告警", "故障排查", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-10-10-1150-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_a%E6%97%A5%E5%BF%97%E6%8C%89%E6%97%B6%E9%97%B4%E7%AA%97%E5%AF%BC%E5%87%BA%E5%8F%91%E7%BE%A4%E8%AE%B0%E5%BD%95%EF%BC%88%E5%BC%80%E5%8F%91%E8%A6%81%E4%BB%8A%E5%A4%A9%E5%8D%81%E7%82%B9%E5%89%8D%EF%BC%89.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-10-10-1150-【运维】vendor_a日志按时间窗导出发群记录（开发要今天十点前）.md"
sourceSha256: "f61aab2e5cf50ac452c139f9b8bce49e56b26baa674e9f504fbc0da8add1244c"
sourceSystem: "project-doc"
---

# 【运维】vendor_a 日志按时间窗导出发群（开发要「今天十点之前」）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610101150-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BDocker-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_a%20%E6%97%A5%E5%BF%97%E6%8C%89%E6%97%B6%E9%97%B4%E7%AA%97%E5%AF%BC%E5%87%BA%E5%8F%91%E7%BE%A4%EF%BC%88%E5%BC%80%E5%8F%91%E8%A6%81%E3%80%8C%E4%BB%8A%E5%A4%A9%E5%8D%81%E7%82%B9%E4%B9%8B%E5%89%8D%E3%80%8D%EF%BC%89.md)

> 整理日期：2026-10-10 11:50｜日期依据：文件名日期

时间：2026-10-10 11:50（北京）/ 03:50（UTC）
需求：flux py「@Ben_Bird vendor_a 这个环境今天的日志，可以帮忙发我下」→「今天十点之前的 ok 吗」
　　　运维答复「10 分钟左右给出来」，并要求「最终需要完整日志」
对象机器：后台 01 `192.0.2.1`、后台 02 `192.0.2.1`
结果：4 个压缩包已直发监控报警群（7755/7756 = prod-01 A/B，7757/7758 = prod-02 A/B），
　　　另发一条交付说明（7759）。

---

## 一、先对齐时区（这次最容易踩的点）

```text
服务器日志用 **UTC**，文件名也是 UTC 日期：
  /data/server-runtime/logs/vendor_a/2026-10-10.log
  首行 2026-10-10 00:00:00、打包时最后一行 2026-10-10 03:47 ← 说明确实是 UTC
对照关系（2026-10-10）：
  北京 = UTC+8      北京 10:00  = UTC 02:00
  巴西圣保罗 = UTC-3 巴西 10:00 = UTC 13:00（当天还没到）

所以「今天十点之前」= UTC 00:00–01:59:59（= 北京 08:00–09:59）。
为兼顾「别把范围切窄了」和「要完整日志」，实际交付**今天 00:00 UTC 到打包时刻**的整段，
并按 UTC 02:00 切成两段（正好就是十点这个分界）：
  A 段 = 00:00–01:59:59 UTC = 北京 08:00–09:59  ← 「十点前」整段，末行卡在 01:59:59
  B 段 = 02:00–03:47 UTC    = 北京 10:00–11:47
```

## 二、为什么要切成两段（Telegram 50MB 限制）

```text
今天日志原始体量：prod-01 392MB、prod-02 389MB（到打包时刻为止，还在增长）
整包 gzip -1：prod-01 70.1MB、prod-02 69.4MB → **超过 Telegram sendDocument 50MB 上限**
按 UTC 02:00 切两段后（gzip -6）：
  prod-01 A 38.3MB / 1,112,041 行，B 16.5MB
  prod-02 A 37.9MB / 1,086,819 行，B 16.4MB
→ 4 个包全部 <50MB，可以直发群，不需要再走对象存储链接。
（上一轮 vendor_d 那次是整包 300MB 才用的预签名链接；这次切段就能直发。）
```

## 三、交付内容与注意事项

```text
文件命名：vendor_a-prod-01-A-0010utc-cut.log.gz
          vendor_a-prod-01-B-after.log.gz
          vendor_a-prod-02-A-0010utc-cut.log.gz
          vendor_a-prod-02-B-after.log.gz
解压：gzip -dc 文件名 > 2026-10-10.log

注意 1：vendor_a 主服务(9096) 与 vendor_a_ws(8765) 两个容器把日志写在**同一个目录/同一个文件**里
        （start.sh 里两者 appdir 都是 vendor_a），所以文件里两种服务的行是混在一起的。
注意 2：01/02 是两台独立后端，请求会分到两台，排查具体用户/局时两边都要看。
注意 3：这是打包时刻的**快照**（用 head -c 固定字节 + 按行号切分），不是实时流。
```

## 四、复现命令（下次按时间窗导日志照这个来）

```bash
# 在 01 或 02 上，cd /data/server-runtime/logs/vendor_a
F=2026-10-10.log

# 0) 先确认日志时区（首行时间戳）
head -1 "$F"

# 1) 找切分点：第一条 >= 指定 UTC 时刻的行号
LN=$(grep -n -m1 '^2026-10-10 02:' "$F" | cut -d: -f1)
E=$(wc -l < "$F")

# 2) 按行号切（按行号切不会丢多行的 Traceback 续行；按时间戳 grep 会把续行切散）
head -n $((LN-1)) "$F" | gzip -6 -c > /tmp/vendor_a-A.log.gz
tail -n +$LN     "$F" | gzip -6 -c > /tmp/vendor_a-B.log.gz

# 3) 发群（从有 bot 凭据的机器上）
set -a; . /opt/benbot-runtime.env; set +a
curl -s -X POST "https://api.telegram.org/bot$TG_BOT_TOKEN/sendDocument" \
  -F "chat_id=$BEN_BOT_MONITOR_CHAT_ID" -F "document=@/tmp/vendor_a-A.log.gz" \
  -F "caption=..."
```

```text
小坑：01/02 上没有 bc，别用 bc 算 MB；直接用 ls -la 看字节或用 awk 除。
```

## 五、还能继续提供的（等开发回话）

```text
1) 更早的整天：10/9、10/8、10/7（每天约 1.9~2.4GB 原始）——整天建议走对象存储预签名链接；
2) 更细的时间窗（例如只看某个 5 分钟区间）；
3) 按游戏/用户过滤：给 gameid（如 301 / 563）或用户 id，可以直接 grep 出来；
4) 只看错误/异常（ERROR/Traceback/超时）的汇总包，几分钟内可出。
```

## 六、本次的背景（测试反馈，供对照排查）

```text
· 301 彩金小丑：登录超时、无法登入（P1）
· 563 招财爆竹：近 20 局全输、完全无派奖（P1）
· vendor_a 全部游戏：详情页点击返回键无反应（P2）
以上均为测试同学 Saya 在 Tada 巴西线上、用户 999 提交；开发已答复会在测试环境真实压测。
```

## 七、相关文件

```text
/data/server-runtime/logs/vendor_a/2026-10-10.log       # 日志源（01/02）
/opt/benbot-runtime.env                             # 入口机/后端的群凭据
docker/doc/2026-10-02-2205-【运维】vendor_d近一周日志导出与发群记录.md   # 上一轮同类交付（超大包用预签名链接）
```
