---
id: "doc-c5206d334096"
title: "【优化】全量厂家 CDN 预热与机器人发布预热按钮上线记录"
date: "2026-09-02T20:57:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "自动化", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-02-2057-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E5%85%A8%E9%87%8F%E5%8E%82%E5%AE%B6CDN%E9%A2%84%E7%83%AD%E4%B8%8E%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%8F%91%E5%B8%83%E9%A2%84%E7%83%AD%E6%8C%89%E9%92%AE%E4%B8%8A%E7%BA%BF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-02-2057-【优化】全量厂家CDN预热与机器人发布预热按钮上线记录.md"
sourceSha256: "daa70ab2e474981da77fba8bbd2e7088597a3a177135dbe5e0985735c9e428eb"
sourceSystem: "project-doc"
---

# 【优化】全量厂家 CDN 预热与机器人发布预热按钮上线记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-02-2057-【优化】全量厂家CDN预热与机器人发布预热按钮上线记录.md`

> 整理日期：2026-09-02 20:57｜日期依据：文件名日期

时间：2026-09-02 20:57（Asia/Manila）
项目：某业务公司 / PGServer master（巴西生产静态链路 + ben-bot）
状态：✅ 全量预热完成 + 机器人按钮已上线

## 一、任务

```text
1) 现在把全部厂家游戏资源整体预热一遍（14 个静态前缀 × 20 zone）；
2) ben-bot 主页新增“发布预热”按钮，发布时可随时触发预热；
3) 验证、文档、清理、本地提交，全程逐步发群。
```

## 二、全量预热执行与结果

```text
范围：337 个游戏入口（pg 系列 136 / vendor_a 83 / pp 1 / ppk 1 /
vendor_c 50 / vendor_d 53 / g759 13）× 20 zone = 6,740 入口
执行：宝塔 GRU 本机，32 并发；日志：
  /var/log/cdn_full_warm_20260902.log（第一轮入口）
  /var/log/cdn_full_warm_20260902_assets.log（第二轮入口+同源 JS/CSS）
  /var/log/cdn_full_warm_20260902_retry.log（瞬时失败重试）

结果：
  第一轮入口：6740/6740 HTTP 200，68s；
  第二轮入口+页面同源 JS/CSS：ok=13140；瞬时 ERR 1560（高并发下大入口
  超时，如 pg3/2040102、vendor_a/bh 等）-> 低并发(12)重试 1560/1560 恢复；
  根 health.json：14 前缀 × 20 zone = 280/280（1s）；
  回验：逐前缀抽样入口 HIT 28/28、health HIT 28/28（宝塔二次请求）。
```

说明：预热工具资产发现已修复（同源相对 JS/CSS，原只认
storage.googleapis.com 绝对地址，导致第二轮前 assets 漏掉）；并新增
`--health` / `--health-only` 与实时进度输出。

## 三、机器人“发布预热”主页按钮

```text
新增 ben-bot 数据脚本目录：
  docker/ben-bot/data/scripts/发布预热/{.benbot.json,action.py,run.py}
主页：home.py ACTION_PATHS 增加 prewarm；“发布中心”按钮旁新增“发布预热”。
菜单动作：
  - 全部厂家完整预热：python docker/scripts/cdn_warm_static.py
    --assets --health --threads 32（入口 HTML+JS/CSS+根 health，20 zone）
  - 仅根 health.json 预热：--health-only
复用既有“确认页 + 单消息进度卡 + 完整 txt 附件”模式。

部署/运行规则：
  - 文件同步宝塔与备用机 /opt/pgserver；
  - 活动轮询实例为备用机 bizops-ben-bot-standby（poll），重建后主页已含
    “发布预热”并重新发送启动通知；
  - 宝塔 bizops-ben-bot 按 DEC-20260807-BENBOT-STANDBY 保持 idle（无轮询）；
  - docker-compose.yml 增加 BEN_BOT_POLL（默认 0=idle，1=接管轮询），
    防止同 token 双轮询。
```

## 四、验证

```text
- 备用机容器内 import benbot.home：ACTION_PATHS 含 prewarm；
  build_start_markup 主页按钮含“发布预热”；
- 宝塔 idle / 备用机 poll，仅一个实例轮询，无 Conflict；
- 预热工具 python3 -m py_compile 通过；
- 全量预热后 HIT 抽样通过（入口 28/28、health 28/28）。
```

## 五、服务器清理复核

```text
- 预热日志保留在 /var/log（今日运维证据）；
- 测试对象此前已清；本次无新增生产对象；
- 宝塔 /tmp 仅保留 cdn_warm_fail.json/retry 清单等过程文件（文档定稿后清理）；
- 磁盘占用无异常（与晚间收尾一致 63%）。
```

## 六、今日文档关联

```text
本文 = 今日第三份晚间事件文档：
  master docker/doc/2026-09-02-2018（发布后 CDN 预热实施）
  master docker/doc/2026-09-02-2033（五项操作审计 + g759 实测）
  master docker/doc/2026-09-02-2057（本文：全量预热 + 机器人按钮）
master/cn 总览均已追加交叉索引。
```

## 七、飞机群通知 message_id

```text
4906 任务开始（1/8）
4907 规模设计与方案（2/8）
4909 预热进度（入口完成，继续 JS/CSS+health）
4915 机器人按钮完成（4/8）
4919 全量预热完成（3/8）
4920 回验通过（5/8）
4921 文档完成（6/8）
4922 汇总 + 事件文档附件（主体提交前）
4923 提交结果（master a7c60ffe / cn 62a1c99a，均未 Push）
```

## 八、本地提交

```text
master：a7c60ffe ops: full-vendor CDN prewarm tooling + ben-bot publish-prewarm button
cn：62a1c99a docs: cross-link master full-vendor prewarm and bot publish-prewarm button
（均未 Push；master 领先 origin/master 21，cn 领先 origin/cn 34）
```
