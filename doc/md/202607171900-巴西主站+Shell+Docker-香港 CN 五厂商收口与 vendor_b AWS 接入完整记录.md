---
id: "doc-278e3fca5e81"
title: "香港 CN 五厂商收口与 vendor_b AWS 接入完整记录"
date: "2026-07-17T19:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "Nginx", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-07-17-1900-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%2B%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E9%A6%99%E6%B8%AFCN%E4%BA%94%E5%8E%82%E5%95%86%E6%94%B6%E5%8F%A3%E4%B8%8Evendor_b-AWS%E6%8E%A5%E5%85%A5%E5%AE%8C%E6%95%B4%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-07-17-1900-【架构改造+网络调整】香港CN五厂商收口与vendor_b-AWS接入完整记录.md"
sourceSha256: "8d1baeae6dc67641e5ae138ebb5969c3f3bdd6d68f4fdcfc58ee6422a093f2f9"
sourceSystem: "project-doc"
---

# 香港 CN 五厂商收口与 vendor_b AWS 接入完整记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-07-17-1900-【架构改造+网络调整】香港CN五厂商收口与vendor_b-AWS接入完整记录.md`

> 整理日期：2026-07-17 19:00｜日期依据：文件名日期

## 目标与最终状态

本次把香港 `cn` 环境收口为：

```text
PG / PP / PPK / PANDA / vendor_b
platform-api / PG verify
```

最终链路：

```text
静态域名 -> Cloudflare DNS-only CNAME -> CloudFront OAC -> 香港私有 S3
动态域名 -> Cloudflare DNS-only CNAME -> CloudFront -> 香港 Nginx -> 外部双后端
```

vendor_a、vendor_c 和 Socket 不再属于 `cn` 当前范围。旧 AWS/S3 资源暂不删除，作为审计与回滚材料保留；对应精确 DNS 和动态 CloudFront 别名已经移除。

## 参考来源与盘点结论

### 巴西宝塔配置

只读检查巴西宝塔 Nginx 后确认：

- 巴西使用统一厂商 upstream + 按 Host 分流的结构。
- PG、PP、PPK、PANDA 已有成熟的反代、CORS 和故障切换方式，可供香港复用。
- 巴西现网没有独立 vendor_b Nginx 站点，因此没有复制不存在的配置。
- `master` 分支将 vendor_b 作为预留服务，端口为 `9093`，入口为 `vendor_a/vendor_b.py`。
- master 历史 vendor_b 域名分三组：`vendor_b-static`、`vendor_b-static1`、`vendor_b-static2`。

### vendor_b 资源来源

vendor_b 游戏代码与静态包沿用历史 vendor_a/vendor_b 共用资源结构，Google 线上桶名称没有改名。迁移到 AWS 时改用独立 vendor_b 目标前缀：

| Google 源桶 | AWS S3 目标前缀 | vendor_b 用途 |
| --- | --- | --- |
| `bizops-gcs-vendor_a-statics` | `vendor_b-static` | 默认游戏组 |
| `bizops-gcs-vendor_a-statics1` | `vendor_b-static1` | SPECIAL_GAMES_v1 |
| `bizops-gcs-vendor_a-statics2` | `vendor_b-static2` | SPECIAL_GAMES_v2 |

这只是资源历史命名兼容，不表示 `cn` 继续启用 vendor_a 域名或 vendor_a `9096/8765` 服务。

## 后端网络与端口

香港入口 Nginx：`192.0.2.14`。

| 服务 | 端口 | 后端一 | 后端二 | 验收 |
| --- | ---: | --- | --- | --- |
| platform-api | 9090 | `192.0.2.18` | `192.0.2.19` | 保持原链路 |
| PG | 9091 | 同上 | 同上 | 保持原链路 |
| vendor_b | 9093 | 同上 | 同上 | TCP 正常，测试接口 200 |
| PP | 9099 | 同上 | 同上 | 保持原链路 |
| PPK | 9098 | 同上 | 同上 | 保持原链路 |
| PANDA | 9018 | 同上 | 同上 | 保持原链路 |

vendor_b 网络验证：

```text
192.0.2.18:9093       TCP OK
192.0.2.19:9093     TCP OK
/game-setting/game-info-list  两台均 HTTP 200，响应 77,297 字节
```

根路径返回 403 是 vendor_b 应用行为，不代表端口未开放。

## Nginx 变更

仓库文件：

```text
docker/deploy/hongkong/nginx-bizops.conf
```

主要变更：

- 新增 `bizops_hk_vendor_b` upstream，双后端端口均为 9093。
- 新增 `vendor_b-api.hkplaycore.com` 与 `vendor_b-games.hkcloudplay01-05.com` 分流。
- 静态兜底映射新增 `vendor_b-static / vendor_b-static1 / vendor_b-static2`。
- 删除 vendor_a 9096、vendor_a WebSocket 8765 和 vendor_c 站点的活动 upstream/server 配置。
- 对 vendor_a、vendor_c、Socket 历史 Host 明确返回 410，避免落入第一个 TLS server 误转 platform-api。
- 保留巴西项目同类 CORS 处理与 PP `customizations.info` 兼容。

发布前候选配置使用隔离 Nginx 主配置验证，随后执行正式 `nginx -t` 和 reload。现网备份：

```text
/etc/nginx/sites-available/bizops-hongkong.conf.bak.20260717T094654Z.before-vendor_b
```

发布后强制解析测试 10 个入口，vendor_b/API/五厂商及退役 Host 状态全部符合预期，失败 0。

## Google 到 AWS S3 同步

同步工具：

```text
香港服务器：/usr/local/bin/sync-gcs-to-s3
仓库：docker/deploy/hongkong/sync_gcs_to_s3.py
```

脚本使用 `rclone copy --mevendor_ata`，只复制新增或变化对象，不删除 Google 源数据，也不删除 AWS 其他前缀。

### 当前五厂商活动资源

| AWS 前缀 | Google 源对象数 | AWS 对象数 | 源/目标字节数 |
| --- | ---: | ---: | ---: |
| `pg-static` | 34,242 | 34,242 | 2,932,087,157 |
| `pg3-static` | 3,454 | 3,454 | 306,241,957 |
| `pg4-static` | 5,621 | 5,621 | 438,689,630 |
| `pg5-static` | 384 | 384 | 29,894,767 |
| `pp-static` | 18,860 | 18,860 | 12,859,798,858 |
| `ppk-static` | 8,442 | 8,442 | 2,125,758,610 |
| `vendor_d-static` | 78,664 | 78,664 | 1,316,540,465 |
| `vendor_b-static` | 17,450 | 17,450 | 2,220,113,567 |
| `vendor_b-static1` | 2,620 | 2,620 | 564,873,936 |
| `vendor_b-static2` | 1,072 | 1,072 | 203,719,543 |
| **合计** | **170,809** | **170,809** | **22,997,718,490** |

vendor_b 新增部分合计 21,142 个对象、2,988,707,046 字节，三组源/目标对象数与字节数完全一致。

## CloudFront 变更

### 动态分配

| 分配 ID | CloudFront 域名 | 状态 | 别名数 |
| --- | --- | --- | ---: |
| `E3QV4VIGTRVCVD` | `d1n4qfcp941cy6.cloudfront.net` | Deployed | 33 |

动态别名由原 40 个收口为 33 个：

```text
25 个游戏域名：PG / PP / PPK / PANDA / vendor_b，各 01-05
8 个核心域名：api / games / verify / pg-api / pp-api / ppk-api / vendor_d-api / vendor_b-api
```

vendor_a、vendor_c、Socket 动态别名数量为 0。

### vendor_b 静态分配

| 前缀 | 分配 ID | CloudFront 域名 | 状态 | 别名数 |
| --- | --- | --- | --- | ---: |
| `vendor_b-static` | `E2KICAEYOWJ24E` | `d1b9hbqri3a5s2.cloudfront.net` | Deployed | 5 |
| `vendor_b-static1` | `EIKLXE4BT0I05` | `duwwtt8kps0e1.cloudfront.net` | Deployed | 5 |
| `vendor_b-static2` | `E38M63JF95BKAL` | `dl70k4sviqmqh.cloudfront.net` | Deployed | 5 |

三组均使用现有 OAC `E3B9A5Q6NHFLMX`，桶策略仅授权对应分配读取对应 vendor_b 前缀。S3 保持禁止公网访问，公开直连返回 403。

CloudFront 新分配控制面等待约 38 分钟后全部变为 Deployed；等待期间只做强制解析，不提前写 DNS。

## Cloudflare DNS 变更

### 下线旧范围

删除的精确 DNS：

```text
vendor_a 三组静态域名：15
vendor_c 静态域名：5
socket.hkplaycore.com：1
```

vendor_a/vendor_c 动态域名此前就没有精确记录。删除后复核旧范围精确 DNS 残留为 0；通配记录仍保留，访问旧 Host 时由 Nginx 返回 410。

备份目录：

```text
/root/bizops-cloudflare-dns-backups/20260717T094826Z  # vendor_a/vendor_c 静态
/root/bizops-cloudflare-dns-backups/20260717T094853Z  # Socket
```

### vendor_b 灰度上线

先只切 `hkcloudplay01.com` 和 vendor_b API，完成 DNS、HTTP、CORS、CloudFront 验收后，再分别扩展 02 至 05。

| 备份目录时间戳 | 内容 |
| --- | --- |
| `20260717T102854Z` | vendor_b 01 Zone：三组静态 + 游戏 |
| `20260717T102900Z` | `vendor_b-api.hkplaycore.com` |
| `20260717T103010Z` | vendor_b 02 Zone |
| `20260717T103016Z` | vendor_b 03 Zone |
| `20260717T103022Z` | vendor_b 04 Zone |
| `20260717T103028Z` | vendor_b 05 Zone |

所有记录均为 DNS-only CNAME、TTL 60 秒。

## 验收结果

### 切换前强制解析

```text
静态域名：50/50
Google 与 AWS 代表文件 SHA-256：10/10
静态失败：0
哈希失败：0
S3 公开直连：403
```

### vendor_b 全域名

```text
vendor_b-static / static1 / static2：15/15
vendor_b-games：5/5
vendor_b-api：1/1
合计：21/21
HTTP：全部 200
CORS：全部正常
CloudFront 响应：21/21
失败：0
```

### 五厂商最终状态

| 项目 | 通过 |
| --- | ---: |
| 静态精确 DNS | 50/50 |
| 动态游戏精确 DNS | 25/25 |
| 核心/API 精确 DNS | 8/8 |
| 动态 HTTP 应用状态 | 33/33 |
| 当前有效精确域名 | 83/83 |
| 退役厂商精确 DNS 残留 | 0 |
| 动态 CloudFront 退役别名 | 0 |

PP/PPK/PANDA 根路径的 403/404 是应用正常行为；验证同时检查 CloudFront `Via` 响应头，不把应用状态误判为 CDN 故障。

## 回滚方法

### Nginx

```bash
cp -a \
  /etc/nginx/sites-available/bizops-hongkong.conf.bak.20260717T094654Z.before-vendor_b \
  /etc/nginx/sites-available/bizops-hongkong.conf
nginx -t && systemctl reload nginx
```

### vendor_b DNS

按上线顺序反向执行：

```bash
/usr/local/bin/cloudflare-aws-cutover rollback /root/bizops-cloudflare-dns-backups/20260717T103028Z
/usr/local/bin/cloudflare-aws-cutover rollback /root/bizops-cloudflare-dns-backups/20260717T103022Z
/usr/local/bin/cloudflare-aws-cutover rollback /root/bizops-cloudflare-dns-backups/20260717T103016Z
/usr/local/bin/cloudflare-aws-cutover rollback /root/bizops-cloudflare-dns-backups/20260717T103010Z
/usr/local/bin/cloudflare-aws-cutover rollback /root/bizops-cloudflare-dns-backups/20260717T102900Z
/usr/local/bin/cloudflare-aws-cutover rollback /root/bizops-cloudflare-dns-backups/20260717T102854Z
```

这会删除新增 vendor_b 精确 CNAME，让原通配记录重新接管。回滚后必须重新检查 DNS、HTTP 和业务页面。

### 恢复旧静态/Socket DNS

如确需恢复本次下线记录：

```bash
/usr/local/bin/cloudflare-aws-cutover rollback /root/bizops-cloudflare-dns-backups/20260717T094826Z
/usr/local/bin/cloudflare-aws-cutover rollback /root/bizops-cloudflare-dns-backups/20260717T094853Z
```

注意：恢复 Socket 原 CNAME 前，必须先把 `socket.hkplaycore.com` 重新加入动态 CloudFront 别名；否则只恢复 DNS 会得到 CloudFront 证书/别名错误。当前五厂商范围不需要执行此恢复。

### 服务器脚本备份

```text
/usr/local/bin/sync-gcs-to-s3.bak.20260717T093943Z
/usr/local/bin/cloudflare-aws-cutover.bak.20260717T094826Z
/usr/local/bin/cloudflare-aws-cutover.bak.20260717T102753Z
/usr/local/bin/create-cloudfront-dynamic.bak.20260717T094945Z
/usr/local/bin/create-cloudfront-static-distributions.bak.20260717T094945Z
/usr/local/bin/validate-cloudfront-static.bak.20260717T102753Z
```

## 安全边界

- AWS 密钥只保存在香港服务器 AWS CLI profile，未提交 Git。
- Cloudflare Token 只保存在香港服务器 root-only 文件，未提交 Git。
- `docker/cf.api` 被 `.gitignore` 排除。
- 文档不包含密码、Secret Access Key、Cloudflare Token 或 Telegram Token。
- Google 源桶、旧 S3 前缀、旧 CloudFront 分配暂不删除，避免丢失回滚材料。

## 飞机群进度

| 消息 ID | 内容 |
| ---: | --- |
| `2715` | vendor_b 9093 双后端网络验证与五厂商范围 |
| `2716` | Google -> AWS S3 同步与校验 |
| `2717` | 香港 Nginx vendor_b 发布与五厂商收口 |
| `2718` | vendor_b 动态 CloudFront 与静态 OAC 验证 |
| `2722` | vendor_b 首个 Zone 灰度通过 |
| `2724` | vendor_b 21 个域名全量切换完成 |
| `2726` | 五厂商 83 个域名最终验收 |

## 后续优化

- 使用真实中国大陆网络继续测试首包、完整资源加载和进入游戏速度。
- 观察 CloudFront 4xx/5xx、缓存命中、流量和费用。
- 验证稳定一段时间后，再决定是否禁用/删除没有 DNS 的 vendor_a、vendor_c 旧 CloudFront 分配和旧 S3 前缀。
- 静态资源更新时继续运行增量同步；不要直接删除 Google 源数据。
- 如果未来增加厂商，先完成后端端口、静态源映射、CloudFront 强制解析和单 Zone 灰度，再扩大 DNS。
