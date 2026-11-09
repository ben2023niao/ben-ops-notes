---
id: "doc-d88410088fc0"
title: "【竞品分析】docker 浏览器方案全量测试记录（ff789p3 未开放，H5 兜底）"
date: "2026-08-28T19:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "Nginx", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-08-28-1930-%E3%80%90%E7%AB%9E%E5%93%81%E5%88%86%E6%9E%90%E3%80%91docker%E6%B5%8F%E8%A7%88%E5%99%A8%E5%85%A8%E9%87%8F%E6%B5%8B%E8%AF%95%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-08-28-1930-【竞品分析】docker浏览器全量测试记录.md"
sourceSha256: "2f78ba1499241f492dd6c1a0a7b53b67102cc30768d62b14f62618694ee57da9"
sourceSystem: "project-doc"
---

# 【竞品分析】docker 浏览器方案全量测试记录（ff789p3 未开放，H5 兜底）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608281930-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BDocker-%E3%80%90%E7%AB%9E%E5%93%81%E5%88%86%E6%9E%90%E3%80%91docker%20%E6%B5%8F%E8%A7%88%E5%99%A8%E6%96%B9%E6%A1%88%E5%85%A8%E9%87%8F%E6%B5%8B%E8%AF%95%E8%AE%B0%E5%BD%95%EF%BC%88ff789p3%20%E6%9C%AA%E5%BC%80%E6%94%BE%EF%BC%8CH5%20%E5%85%9C%E5%BA%95%EF%BC%89.md)

> 整理日期：2026-08-28 19:30｜日期依据：文件名日期

时间：2026-08-28 19:30（Asia/Manila）
项目：某业务公司 / PGServer master
执行人：Codex（本地工作区 + 备用机 bizops-saopaulo-nginx-standby-01 / 192.0.2.13）

## 一、任务与背景

使用 docker 浏览器方案（Playwright Chromium，备用机巴西本地），手机 UA 模拟，
完成「登录 → 点击同游戏 → 点击继续 → 等游戏完整加载」的分阶段计时录屏对比：

- 我方：ff789p3.com（接 API 包网）；若游戏未开，直测 7 个 H5 入口
  （PG/vendor_a/PP/PPK/vendor_c/PANDA/G759，`ind-h5.bizopsplus999.com/<厂家>bronline*`）；
- 竞品：m6kk678n.com；
- 账号/密码：11955336688 / 11955336688。

## 二、执行过程与发现

### 1. ff789p3 状态（实测）

- `probe_ff789_open.py` 返回 OPEN：该 probe 实际探测的是 **PG H5 入口**（可视为
  平台游戏可用性），不是 ff789p3 站点本身；
- ff789p3.com 实测：大厅可登录（R$ 109.35 余额），但点击任意游戏卡
  （article.game-card）不跳转、无画布 → **游戏确实未开放**（站点侧问题）。

按用户预案切换：我方直测 7 个 H5 入口；竞品正常登录对比。

### 2. 脚本修复（新标签页 + 卡片点击）

- 游戏可能**新开标签页**打开：`wait_visible_canvas` 原只扫当前页 frames，
  Fortune Tiger 被误判为打不开；改为扫描 context 全部页面 + iframe；
- ff789p3 大厅按文本点击无效：`open_our` 改为点击 `article.game-card`（含标题）卡片本体；
- `label_game_videos.py`：results.json 匹配键改为支持 `file` 字段，
  使 H5 多厂家视频的水印描述能正确带上分阶段耗时。

### 3. 我方 7 个 H5 入口实测（手机 UA 390x844，点卡→画布→继续→可玩）

```text
厂家    画布出现    点继续→可玩   网络稳定    结果
PG      12.3s      7.1s         23.8s      ok
vendor_a    9.2s       9.7s         24.3s      ok
PP      8.3s       7.5s         20.5s      ok
PPK     10.0s      7.0s         21.6s      ok
vendor_c 13.2s      3.0s         45.0s      ok
PANDA   8.8s       6.8s         20.2s      ok
G759    8.2s       7.1s         20.1s      ok
```

全部 7 个厂家 H5 入口均可加载并进入可玩（手机 UA 解决设备识别/继续按钮）。

### 4. 竞品 m6kk678n.com 实测（登录→同游戏→继续→可玩）

```text
游戏              登录     点游戏    画布     点继续→可玩   渲染
Fortune Tiger    20.0s    22.1s    24.8s    7.3s        ✅
Mahjong Ways     16.0s    16.7s    21.4s    7.0s        ✅
Aztec Gold       16.0s    17.6s    20.7s    7.6s        ✅
Wild Bounty      17.6s    19.2s    29.4s    7.6s        ✅
Dragon Hatch     17.9s    19.4s    22.2s    7.0s        ✅
```

- `rendered_ok` 启发式返回 False（120s 窗口末画面静止），但帧分析证明是
  **真实完整渲染的游戏画面**（与对标游戏色彩统计一致），静止只是停在待开始界面；
- 全部视频已抽帧验证（avg/std/unique colors 与已渲染画面一致）。

## 三、结论

1. docker 浏览器方案（备用机巴西 + Playwright Chromium + 手机 UA）可以完整跑通
   「点卡→画布→继续→可玩」并产出带水印 MP4，无需 CF token；
2. 我方 7 厂家 H5 入口全部可用（画布 8-13s，点继续→可玩 3-9.7s）；
3. 竞品登录+进游戏链路稳定（登录 16-20s，画布 20-29s，继续→可玩 7.0-7.6s）；
4. ff789p3 站点未开放是站点侧问题，cron（每 30 分钟）探测到开放后自动跑
   登录版完整对比（`game_login_compare_mobile.py --side both --mobile`）。
   （注：该 cron 已于 2026-08-29 取消，见【运维】取消ff789p3定时探测任务记录）

## 四、变更文件

- `docker/scripts/game_load_video_compare.py`：新标签页画布识别；
- `docker/scripts/game_login_compare_mobile.py`：新标签页识别 + ff789p3 卡片点击；
- `docker/scripts/h5_vendor_full_render_test.py`：新增 7 厂家 H5 完整加载测试脚本
  （手机 UA + 水印 field）；
- `docker/scripts/label_game_videos.py`：results 匹配支持 `file` 字段；
- 备用机 `/opt/pgserver/docker/scripts/` 已同步。

## 五、产物

- 我方：`/tmp/bizops-h5-20260828_1110/`（7 MP4 + PNG + results.json）
- 竞品：`/tmp/bizops-comp-20260828_1116/`（5 MP4 + PNG + results.json）
- 12 条视频已带水印（域名/账号/服务器/分阶段耗时/画面变化点）发飞机群。
