---
id: "doc-15a5ce057149"
title: "【优化】platform-api 接入 CF CDN 静态域 + Argo 根域后对比记录"
date: "2026-08-29T20:10:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Python", "Docker", "Nginx", "自动化", "CDN", "故障排查", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-08-29-2010-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91platform-api%E6%8E%A5%E5%85%A5CF%20CDN%E9%9D%99%E6%80%81%E5%9F%9F%E4%B8%8EArgo%E5%AF%B9%E6%AF%94%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-08-29-2010-【优化】platform-api接入CF CDN静态域与Argo对比记录.md"
sourceSha256: "9847812b02b8d6a1e19bd4ed7747c8caa577356e3f627db50bb75f51e114331e"
sourceSystem: "project-doc"
---

# 【优化】platform-api 接入 CF CDN 静态域 + Argo 根域后对比记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608292010-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BPython%2BDocker-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91platform-api%20%E6%8E%A5%E5%85%A5%20CF%20CDN%20%E9%9D%99%E6%80%81%E5%9F%9F%20%2B%20Argo%20%E6%A0%B9%E5%9F%9F%E5%90%8E%E5%AF%B9%E6%AF%94%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-29 20:10｜日期依据：文件名日期

时间：2026-08-29 20:10（Asia/Manila）
项目：某业务公司 / PGServer master
执行人：Codex（本地工作区 + 备用机 + 三台后端）

## 一、背景

巴西静态域名已全部黄云（CF CDN）并经 nginx 改写 Host 回源 GCS 圣保罗桶；
xqv9m8.icu 测试套已升级 Pro + Argo on。本次把：

1. CF CDN 静态域配置进 platform-api `static_hosts`（替代桶直出）；
2. Argo 根域 xqv9m8.icu 保持在 `game_hosts` 第一位；

发布后实测我方 vs 竞品游戏「点击图标 → 完整加载」差异。

## 二、配置变更

`platform-api/conf/domains/*.json`（pg/vendor_a/pp/popok/vendor_c/vendor_d/g759 7 厂商）：

- `static_hosts`：`bizops-gcs-*-sa.storage.googleapis.com`（桶直出）
  → `<vendor>-static.xqv9m8.icu` 等 CF CDN 静态域（沿用各厂商 game_hosts 根域轮换，
  首项 xqv9m8.icu）；
- `special_games` 分组同步：pg3/4/5-static、vendor_a-statics1/2；
- `game_hosts` 不变（xqv9m8.icu 第一 = Argo 套）。

提交：`d879d5bd`（已 push origin/master，发布要求配置进构建镜像）。

## 三、发布

```text
python3 docker/deploy/deploy_all_servers.py platform-api
镜像：pgserver:master-d879d5bd；后端 01/02/03 全部成功（3/3）
```

注意：部署在远端 `git pull origin master` 构建，本地配置必须先 push。

## 四、验证与对比（备用机，Fortune Tiger）

### 配置生效

launcher 返回静态域 `or=pg4-static`（CF CDN 域名），不再返回桶直出
`bizops-gcs-pg4-static-sa.storage.googleapis.com`。

### 点击图标 → 完整加载（3 轮）

```text
我方（H5 + Argo + CF CDN）：
  10.9s / 10.9s（r1 异常 25.9s ok=False，剔除）；画布 1.2s
竞品（m6kk678n）：
  16.0s / 15.0s / 16.2s；画布 4.4-5.0s
```

结论：

- 我方均值约 10.9s vs 竞品约 15.7s，快约 4.8s；
- 画布出现我方 1.2s vs 竞品 4.4-5.0s，CF CDN 静态 + Argo 生效明显；
- 6 条带水印视频已发群（我方 3 + 竞品 3）。

## 五、文件与状态

- 配置：`platform-api/conf/domains/{pg,vendor_a,pp,popok,vendor_c,vendor_d,g759}.json`；
- 文档：本记录；
- 本地 master = `d879d5bd`（已 push origin/master）。
