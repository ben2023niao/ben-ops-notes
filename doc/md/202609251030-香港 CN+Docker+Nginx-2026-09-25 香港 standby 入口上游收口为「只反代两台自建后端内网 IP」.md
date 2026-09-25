---
id: "doc-f6f19fb41e2e"
title: "2026-09-25 香港 standby 入口上游收口为「只反代两台自建后端内网 IP」"
date: "2026-09-25T10:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-09-25-1030-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AFstandby%E5%85%A5%E5%8F%A3%E4%B8%8A%E6%B8%B8%E6%94%B6%E5%8F%A3%E4%B8%BA%E8%87%AA%E5%BB%BA%E5%90%8E%E7%AB%AF%E5%86%85%E7%BD%91IP%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-09-25-1030-【架构改造】香港standby入口上游收口为自建后端内网IP记录.md"
sourceSha256: "1d13d232813e24f43c22bcf04153349f92e3bcad18be75209f93a664e2e1a406"
sourceSystem: "project-doc"
---

# 2026-09-25 香港 standby 入口上游收口为「只反代两台自建后端内网 IP」

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-09-25-1030-【架构改造】香港standby入口上游收口为自建后端内网IP记录.md`

> 整理日期：2026-09-25 10:30｜日期依据：文件名日期

## 一、任务

```text
用户要求：香港项目 nginx 里面只反向代理到 2 台香港后端的内网 IP。
上下文：standby 入口（dbqp-hongkong-nginx-standby-01）此前为避免新域名在后端容器
  部署前不可用，在每个 upstream 里加了外部双后端（18.163.34.9 / 43.198.52.147）作为 backup；
  现按用户要求收口，只保留 203.0.113.1 / 203.0.113.1。
本轮不发送飞机群通知。
```

## 二、改动内容

仓库文件：`docker/deploy/hongkong/nginx-standby.conf`（部署到 standby `/etc/nginx/sites-available/dbqp-hk-standby.conf`）

```text
8 个 upstream 各移除两行外部后端 backup：
  dbqp_hk_standby_platform_api  9090
  dbqp_hk_standby_pg            9091
  dbqp_hk_standby_jili          9093
  dbqp_hk_standby_pp            9099
  dbqp_hk_standby_ppk           9098
  dbqp_hk_standby_panda         9018
  dbqp_hk_standby_playson       9020
  dbqp_hk_standby_g759          9019
改后每个 upstream 只保留：
  server 203.0.113.1:<port> max_fails=3 fail_timeout=10s;
  server 203.0.113.1:<port> max_fails=3 fail_timeout=10s;
文件头注释同步改为「只反代自建后端内网 IP，容器未部署时 502/504 属预期」。
```

操作：备份原配置（`dbqp-hk-standby.conf.bak-20260925-*`）→ 覆盖 → `nginx -t` 通过 → `systemctl reload nginx`。

## 三、部署后验证

| 验证项 | 结果 |
| --- | --- |
| 配置内外部后端残留 | 仅文件头注释提及，upstream 中已无 `18.163.34.9` / `43.198.52.147` |
| `nginx -t` | syntax is ok / test is successful |
| reload | 成功 |
| `socket.hk-socket.com/healthz` | 200（standby 本机健康检查） |
| `socket.hk-socket.com/`（根路径） | 502 —— 预期：两台自建后端 9090 均未监听（平台 API 容器未部署） |
| `pg-games.hkcloudplay06.com/health` | 502 —— 同上（9091 未监听） |
| 回归：`pg-static.hkcloudplay06.com` 静态 | 200（静态走 CloudFront/Worker，不经 standby 上游） |
| 回归：老域名 `pg-static.hkcloudplay05.com` | 200 |
| 回归：老域名 `pg-games.hkcloudplay05.com` | 200（老入口机 → 外部双后端，未受影响） |

上游实测（standby 上）：

```text
203.0.113.1:9090 / 203.0.113.1:9090  未监听
203.0.113.1:9091 / 203.0.113.1:9091  未监听
=> 动态域名与商户/socket 域名当前返回 502，等后端容器部署后即可恢复。
```

## 四、未改动范围（重要）

```text
老入口机 34.92.13.108（承载老域名 hkcloudplay01-05）**本轮未改动**：
  - /etc/nginx/sites-available/dbqp-hongkong.conf 上游仍是外部双后端
    18.163.34.9 / 43.198.52.147，文件最后修改时间仍是 2026-09-02 11:01:09；
  - 原因：老域名现网业务依赖这两台外部后端，且自建后端容器尚未部署，
    现在切换会直接中断老业务（与「不影响老香港业务」的要求冲突）。
如需把老入口机也切到自建后端，请明确授权并在两台后端容器部署完成后执行，
建议先单域名灰度（例如 pg-games.hkcloudplay01.com）再全量。
```

## 五、待办

```text
1. 在香港 prod-01/prod-02 部署业务容器（9 个厂家 + platform-api），
   动态域名（*-games.hkcloudplay06/07.com、api.hkcloudplay0[67].com）与
   商户域名（hk-socket.com）即自动恢复；
2. 如需要老入口机也切自建后端，另行授权后按「先灰度后全量」执行；
3. 外部双后端如仍需兜底，可让后端团队把 standby 公网 IP 34.150.1.185 加入白名单后
   再决定是否恢复 backup（当前按用户要求不保留）。
```

## 六、关联

```text
docker/deploy/hongkong/nginx-standby.conf
docker/doc/2026-09-25-1000-【架构改造】香港商户socket域名hk-socket.com接入记录.md
docker/doc/2026-09-24-1400-【架构改造】香港standby入口与新域名hkcloudplay0607接入记录.md
```
