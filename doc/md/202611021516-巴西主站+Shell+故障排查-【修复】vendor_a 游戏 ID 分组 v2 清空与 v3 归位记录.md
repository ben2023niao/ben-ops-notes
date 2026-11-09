---
id: "doc-704df4482cb6"
title: "【修复】vendor_a 游戏 ID 分组 v2 清空与 v3 归位记录"
date: "2026-11-02T15:16:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "故障排查", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-11-02-1516-%E3%80%90%E4%BF%AE%E5%A4%8D%E3%80%91vendor_a%E6%B8%B8%E6%88%8FID%E5%88%86%E7%BB%84v2%E6%B8%85%E7%A9%BA%E4%B8%8Ev3%E5%BD%92%E4%BD%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-11-02-1516-【修复】vendor_a游戏ID分组v2清空与v3归位记录.md"
sourceSha256: "8b7a7b910e718e3d3ba7bf07d8940597d8e279b6022a2392ae00d5baae46b1a6"
sourceSystem: "project-doc"
---

# 【修复】vendor_a 游戏 ID 分组 v2 清空与 v3 归位记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202611021516-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-%E3%80%90%E4%BF%AE%E5%A4%8D%E3%80%91vendor_a%20%E6%B8%B8%E6%88%8F%20ID%20%E5%88%86%E7%BB%84%20v2%20%E6%B8%85%E7%A9%BA%E4%B8%8E%20v3%20%E5%BD%92%E4%BD%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-11-02 15:16｜日期依据：文件名日期

时间：北京 2026-11-02 15:16 ｜ UTC 2026-11-02 07:16

状态：✅ 巴西、香港目录均已修正；ben 已推送，03 两套 runtime 已同步。

## 一、开始前基线

```text
本地 master：952e015d
origin/master：952e015d
origin/ben：f2dbc37c
03：ben/f2dbc37c，工作区干净
```

开发确认 vendor_a 分组应为：

```text
SPECIAL_GAMES_v2 = []
SPECIAL_GAMES_v3 以 [664, 598] 开头
```

## 二、修改

同时修改：

```text
platform-api/conf/domains/vendor_a.json
platform-api/conf/domains-hk/vendor_a.json
```

结果：

```text
SPECIAL_GAMES_v2.game_ids = []
SPECIAL_GAMES_v3.game_ids = [664, 598, ...其余原有游戏 ID]
664 / 598 不在 v2，且在 v3 组内各出现一次
其余游戏 ID 保持不变
```

## 三、防回归校验

`scripts/validate_domains.py` 改为同时检查巴西和香港：

```text
SPECIAL_GAMES_v2 必须为空
SPECIAL_GAMES_v3 必须以 [664, 598] 开头
原有正整数、组内不重复和域名环境隔离检查继续保留
```

`DOMAIN_CONFIG_OK` 通过。

## 四、Git 与 03

```text
ben 提交：04f46fcd
提交说明：fix(domains): 调整vendor_a v2与v3游戏ID分组
远端：origin/ben 已同步
```

03 已快进到 `04f46fcd`，并执行：

```bash
rsync -a --delete --checksum platform-api/conf/domains/ /data/server-runtime/conf/domains/
rsync -a --delete --checksum platform-api/conf/domains-hk/ /data/server-runtime-hk/conf/domains/
```

验证：

| 位置 | v2 | v3 开头 |
| --- | --- | --- |
| 巴西源码 | `[]` | `[664, 598]` |
| 巴西 runtime | `[]` | `[664, 598]` |
| 香港源码 | `[]` | `[664, 598]` |
| 香港 runtime | `[]` | `[664, 598]` |

```text
两套源目录与 runtime 逐文件 diff：一致
香港 server_configs / version.json：构建前后 SHA256 一致
DOMAIN_OVERWRITE_OK
HK_MEvendor_aTA_PRESERVED=OK
```

本轮未构建或重启业务容器。

## 五、群通知

```text
最终修正汇总：708
完整事件文档：709
```

## 六、修改文件

### ben

```text
README.md
scripts/validate_domains.py
platform-api/conf/domains/vendor_a.json
platform-api/conf/domains-hk/vendor_a.json
```

### master

```text
workbench/CURRENT_TASK.md
workbench/CURRENT_STATE.md
workbench/ACTIVE_TASKS.md
docs/history/2026-11-02-1516-【修复】vendor_a游戏ID分组v2清空与v3归位记录.md
```
