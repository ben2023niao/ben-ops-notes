---
id: "doc-ff1b1624e7bc"
title: "【测试方案】docker 浏览器方案验证 + Cloudflare Browser Rendering 评估"
date: "2026-08-28T18:56:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "Nginx", "CDN", "DNS", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-08-28-1856-%E3%80%90%E6%B5%8B%E8%AF%95%E6%96%B9%E6%A1%88%E3%80%91docker%E6%B5%8F%E8%A7%88%E5%99%A8%E6%96%B9%E6%A1%88%E9%AA%8C%E8%AF%81%E4%B8%8ECFBrowserRendering%E8%AF%84%E4%BC%B0%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-08-28-1856-【测试方案】docker浏览器方案验证与CFBrowserRendering评估记录.md"
sourceSha256: "3a89baddadb4aa74f747dacebb61c45ff9949b84319cd09a1080597f88f1298b"
sourceSystem: "project-doc"
---

# 【测试方案】docker 浏览器方案验证 + Cloudflare Browser Rendering 评估

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608281856-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BPython-%E3%80%90%E6%B5%8B%E8%AF%95%E6%96%B9%E6%A1%88%E3%80%91docker%20%E6%B5%8F%E8%A7%88%E5%99%A8%E6%96%B9%E6%A1%88%E9%AA%8C%E8%AF%81%20%2B%20Cloudflare%20Browser%20Rendering%20%E8%AF%84%E4%BC%B0.md)

> 整理日期：2026-08-28 18:56｜日期依据：文件名日期

时间：2026-08-28 18:56（Asia/Manila）
项目：某业务公司 / PGServer master
执行人：Codex（本地工作区 + 备用机 192.0.2.13）

## 一、背景

为在巴西本地完成「登录 → 同游戏 → 点击继续 → 完整加载」的录屏对比，
之前评估过多个方案：

- Docker-Android（redroid）：不可用（GCP 内核缺 binder/ashmem，无 KVM）；
- Cloudflare Browser Rendering：边缘 Chromium 方案，但需要「Browser Rendering - Edit」
  自定义 token，当前账户仅有 DNS 权限 token（Zone DNS Edit / Zone Read），API 调用
  `GET /accounts/{id}/entitlements` 返回 403 Authentication error，方案被 token 阻塞；
- docker 起浏览器（Playwright Chromium 容器/本机）：备用机（巴西圣保罗）本机已装
  Playwright + Chromium + ffmpeg，即「docker 浏览器方案」的实际载体。

本次任务：验证 docker 浏览器方案能否完整渲染游戏（进度条 → 点击继续 → 出游戏画面），
并出带水印视频发群。

## 二、执行与验证

### 1. ff789p3 开放状态

`probe_ff789_open.py`（备用机运行）：返回 `CLOSED`——ff789p3 游戏今天确实未开放
（维护中）。cron `*/30 * * * *` 已挂：开放即自动跑完整对比，未开放每 30 分钟群通知。

### 2. docker 浏览器渲染验证（我方 PG 入口）

备用机运行 `game_load_video_compare.py --side our --games 126,65`：

```text
游戏            画布出现  点击继续→可玩  渲染判定
Fortune Tiger   12.6s    8.6s          ok=true
麻将胡了        18.1s    8.3s          ok=true
```

- 静态资源走圣保罗桶（or=pg4-static-sa），无跨洲瓶颈；
- 两个游戏均成功通过设备检测「继续游戏」并渲染到可玩；
- 输出 webm → MP4（H.264 + faststart），Playwright Chromium 桌面视口 1280x800。

### 3. 水印标注

`label_game_videos.py` 增加 `--domain` 参数（默认 ff789p3.com，可指定实际入口域名），
水印内容：域名 | 账号/密码 | 测试服务器 | 分阶段耗时 + 画面变化点（帧差分）。
本地仓库与备用机 `/opt/pgserver/docker/scripts/` 已同步。

本次视频标注：

```text
域名：ind-h5.bizopsplus999.com/pgbronline/
账号/密码：11955336688 / 11955336688
服务器：bizops-saopaulo-nginx-standby-01 / 192.0.2.13
```

两个 MP4 已通过 Telegram bot 发群（send: True）。

## 三、结论

1. docker 浏览器方案可行：备用机（巴西）Playwright Chromium 已能完整渲染我方游戏
   （继续→可玩），无需 Cloudflare token、无需新开服务器；
2. Docker-Android（redroid）不可行：GCP 内核缺少 binder/ashmem 且无 KVM；
3. Cloudflare Browser Rendering 需账户创建「Browser Rendering - Edit」token 后即可
   接入（免费额度 10 分钟/天，按量 $0.09/小时），作为备用/边缘方案保留；
4. ff789p3 未开放：等待 cron 探测到 OPEN 后自动执行完整对比（登录→同游戏→点击继续→
   完整加载 + 手机 UA + 录屏发群）。

## 四、变更

- `docker/scripts/label_game_videos.py`：新增 `--domain` 参数，水印/描述支持自定义
  我方入口域名。

## 五、待办

- [ ] 用户提供 CF Browser Rendering token 后接入边缘浏览器录制（可选增强）；
- [ ] ff789p3 开放后复核完整对比视频（cron 自动）；
- [ ] 如需多机复现：把 Playwright 测试打成 Docker 镜像（python + chromium + ffmpeg），
      可部署到任意巴西新服务器。
