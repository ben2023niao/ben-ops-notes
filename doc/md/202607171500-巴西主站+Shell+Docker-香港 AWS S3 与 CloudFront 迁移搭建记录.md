---
id: "doc-fbc4001c8767"
title: "香港 AWS S3 与 CloudFront 迁移搭建记录"
date: "2026-07-17T15:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "Nginx", "CDN", "DNS", "安全运维", "数据库恢复"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-17-1500-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AFAWS-S3%E4%B8%8ECloudFront%E8%BF%81%E7%A7%BB%E6%90%AD%E5%BB%BA%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-17-1500-【架构改造】香港AWS-S3与CloudFront迁移搭建记录.md"
sourceSha256: "f989cdc292aa02d776887758f1a96546f290f02cf5d8fdd23056a8608ba46fb8"
sourceSystem: "project-doc"
---

# 香港 AWS S3 与 CloudFront 迁移搭建记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-17-1500-【架构改造】香港AWS-S3与CloudFront迁移搭建记录.md`

> 整理日期：2026-07-17 15:00｜日期依据：文件名日期

## 目标与边界

为改善中国大陆访问香港游戏资源时的链路质量，新增一套 AWS 测试架构：

```text
静态资源：CloudFront -> 香港私有 S3（ap-east-1）
动态接口：CloudFront -> 香港 Nginx -> 两台外部后端
```

资源复制、CDN 配置和强制解析验证完成后，已于 2026-07-17 按厂商和域名前缀完成灰度切换。同日稍后按项目要求收口为 PG、PP、PPK、PANDA、JILI + platform-api：当前 50 个静态域名和 33 个动态/核心域名通过 Cloudflare DNS-only CNAME 指向 AWS CloudFront；TADA、PLAYSON、Socket 已退出当前范围。原有通配记录和每批 DNS 备份均保留，可快速回退。最终状态见 `2026-07-17-1900-【架构改造+网络调整】香港CN五厂商收口与JILI-AWS接入完整记录.md`。

## 安全处理

- 已删除此前暴露的 AWS 访问密钥，并确认旧密钥失效。
- 新 AWS 密钥仅配置在香港 Nginx 服务器的 root AWS CLI profile 中，未写入 Git。
- Cloudflare API Token 仅配置在香港 Nginx 服务器，权限为 DNS 编辑、Zone 读取，并限制来源 IP 为 `34.92.13.108`。
- 本地 `docker/cf.api`、AWS CSV 和令牌文件已加入 `.gitignore`，不允许提交。
- S3 开启禁止公网访问、SSE-S3 加密和版本控制；公网直接读取测试返回 `403`。

## AWS 资源

| 资源 | 值 |
| --- | --- |
| AWS 账号 | `517506432530` |
| S3 区域 | `ap-east-1`（香港） |
| 私有桶 | `dbqp-h5-hk-517506432530` |
| CloudFront OAC | `dbqp-hk-static-oac` / `E3B9A5Q6NHFLMX` |
| ACM 证书 | `arn:aws:acm:us-east-1:517506432530:certificate/41cea0e7-c569-4e35-98ee-da253bd464a2` |
| 动态回源域名 | `origin-hk.hkplaycore.com` -> `34.92.13.108`（DNS only） |

ACM 证书覆盖：

```text
*.hkplaycore.com
*.hkcloudplay01.com
*.hkcloudplay02.com
*.hkcloudplay03.com
*.hkcloudplay04.com
*.hkcloudplay05.com
```

## CloudFront 分配

### 动态接口与游戏入口

| 用途 | 分配 ID | CloudFront 域名 | 别名数 |
| --- | --- | --- | ---: |
| API、游戏和 Verify | `E3QV4VIGTRVCVD` | `d1n4qfcp941cy6.cloudfront.net` | 33 |

动态分配使用禁用缓存策略，转发访问者请求头、查询参数和 Cookie，通过 HTTPS 回源 `origin-hk.hkplaycore.com`。

强制解析验证结果：

- `pg-games.hkcloudplay01.com` 返回应用 `200`。
- API、PP 和 Panda 根路径返回各自应用的 `404/403`，响应来自香港 Nginx/后端，不是 CDN 连接失败。
- JILI API 与 5 个 JILI 游戏域名的 `/game-setting/game-info-list` 均返回 200。

### 静态资源

| S3 前缀/域名前缀 | 分配 ID | CloudFront 域名 | 别名数 |
| --- | --- | --- | ---: |
| `pg-static` | `E2JLARIGDV5VZV` | `d1wnhpyrlnptrk.cloudfront.net` | 5 |
| `pg3-static` | `E1MELSI31IM0FQ` | `dd4xwdi3getku.cloudfront.net` | 5 |
| `pg4-static` | `E310K7HLRALCN8` | `d2yq6uqd9314ob.cloudfront.net` | 5 |
| `pg5-static` | `EAUVKSKQC1239` | `d13pn1z85092rw.cloudfront.net` | 5 |
| `pp-static` | `E2B947FD8LP93P` | `d31zz5o17f2qzk.cloudfront.net` | 5 |
| `ppk-static` | `E358927OQC0NKV` | `dj9s4ybduyjlh.cloudfront.net` | 5 |
| `panda-static` | `E11FJTU4P1WOTI` | `d40y8tdqqhbne.cloudfront.net` | 5 |
| `jili-static` | `E2KICAEYOWJ24E` | `d1b9hbqri3a5s2.cloudfront.net` | 5 |
| `jili-static1` | `EIKLXE4BT0I05` | `duwwtt8kps0e1.cloudfront.net` | 5 |
| `jili-static2` | `E38M63JF95BKAL` | `dl70k4sviqmqh.cloudfront.net` | 5 |

每个活动静态分配绑定对应的 5 个 `hkcloudplay01.com` 至 `hkcloudplay05.com` 域名。当前 10 个活动前缀分别使用 prefix-scoped OAC 桶策略；TADA/PLAYSON 旧资源和策略暂留作审计与回滚材料，但没有业务 DNS。

## GCS 到香港 S3 同步结果

| 前缀 | 源对象数 | S3 对象数 | 源字节数 | S3 字节数 |
| --- | ---: | ---: | ---: | ---: |
| `pg-static` | 34,242 | 34,242 | 2,932,087,157 | 2,932,087,157 |
| `pg3-static` | 3,454 | 3,454 | 306,241,957 | 306,241,957 |
| `pg4-static` | 5,621 | 5,621 | 438,689,630 | 438,689,630 |
| `pg5-static` | 384 | 384 | 29,894,767 | 29,894,767 |
| `pp-static` | 18,860 | 18,860 | 12,859,798,858 | 12,859,798,858 |
| `ppk-static` | 8,442 | 8,442 | 2,125,758,610 | 2,125,758,610 |
| `panda-static` | 78,664 | 78,664 | 1,316,540,465 | 1,316,540,465 |
| `jili-static` | 17,450 | 17,450 | 2,220,113,567 | 2,220,113,567 |
| `jili-static1` | 2,620 | 2,620 | 564,873,936 | 564,873,936 |
| `jili-static2` | 1,072 | 1,072 | 203,719,543 | 203,719,543 |
| **合计** | **170,809** | **170,809** | **22,997,718,490** | **22,997,718,490** |

同步使用 `rclone copy --metadata`，只复制新增或变化对象，不删除 GCS 源数据。每组完成后同时核对源/目标对象数和总字节数。

## PP 特殊兼容

原香港 Nginx 对 PP 静态域名使用以下兼容规则：

```nginx
location ~* /customizations\.info$ {
    default_type application/octet-stream;
    return 200 "";
}
```

迁移到 S3 后，由 CloudFront Function `dbqp-hk-pp-customizations` 在 viewer-request 阶段保持相同行为，仅挂载到 `pp-static` 分配。

强制解析实测 5 个 PP 静态域名全部返回：

```text
HTTP 200
Content-Length: 0
Content-Type: application/octet-stream
Access-Control-Allow-Origin: *
```

## 最终静态链路验证

在不修改现网 DNS 的情况下，对每个 CloudFront 分配使用强制解析验证：

- 50/50 个静态域名返回 `200`。
- 50/50 个静态域名返回 `Access-Control-Allow-Origin: *`。
- 50/50 个静态域名确认由 CloudFront 响应并命中缓存。
- 10/10 组代表文件的 GCS 与 CloudFront SHA-256 完全一致。
- PP `customizations.info` 特殊规则 5/5 返回空 `200`。
- S3 公开直连返回 `403`。

验证脚本汇总：

```text
domains_passed=50
domains_failed=0
hashes_passed=10
hashes_failed=0
direct_s3_status=403
```

## 运维脚本

香港服务器安装路径与仓库文件对应如下：

| 功能 | 香港服务器 | 仓库文件 |
| --- | --- | --- |
| Cloudflare API | `/usr/local/bin/cf-api` | `docker/deploy/hongkong/cf_api.py` |
| ACM DNS 验证 | `/usr/local/bin/sync-acm-cloudflare` | `docker/deploy/hongkong/sync_acm_cloudflare.py` |
| 动态 CloudFront | `/usr/local/bin/create-cloudfront-dynamic` | `docker/deploy/hongkong/create_cloudfront_dynamic.py` |
| 静态 CloudFront | `/usr/local/bin/create-cloudfront-static-distributions` | `docker/deploy/hongkong/create_cloudfront_static_distributions.py` |
| GCS -> S3 同步 | `/usr/local/bin/sync-gcs-to-s3` | `docker/deploy/hongkong/sync_gcs_to_s3.py` |
| PP 特殊规则 | `/usr/local/bin/configure-cloudfront-pp-customizations` | `docker/deploy/hongkong/configure_cloudfront_pp_customizations.py` |
| 静态链路验证 | `/usr/local/bin/validate-cloudfront-static` | `docker/deploy/hongkong/validate_cloudfront_static.py` |
| Cloudflare 灰度切换与回滚 | `/usr/local/bin/cloudflare-aws-cutover` | `docker/deploy/hongkong/cloudflare_aws_cutover.py` |

所有脚本只引用 AWS profile 或服务器本机令牌路径，不包含明文密钥。

## DNS 切换状态

- 50/50 个 PG、PP、PPK、PANDA、JILI 静态域名已切换到各自的静态 CloudFront 分配。
- 25/25 个五厂商游戏域名已切换到动态 CloudFront 分配。
- 8/8 个 platform-api、Verify 和五厂商 API 域名已切换到动态 CloudFront 分配。
- TADA、PLAYSON、Socket 已退出 `cn` 当前范围，精确 DNS 与动态 CloudFront 别名残留均为 0。
- 精确记录统一使用 DNS-only CNAME、TTL 60 秒；原有通配 A 记录未删除。
- 已实际执行一次删除精确 CNAME 的回滚演练，确认通配记录立即恢复接管，随后重新应用 AWS CNAME。

## 飞机群进度

- 动态 CloudFront 验证完成：`message_id=2701`。
- `pg-static` 首批同步和私有链路验证完成：`message_id=2702`。
- 全量资源、55 个静态域名和 PP 特殊规则验证完成：`message_id=2703`。
- DNS 灰度及回滚演练：`message_id=2704` 至 `2711`。
- 动态域名最终批与总结果：`message_id=2712`。
- 五厂商收口与 JILI 接入：`message_id=2715`、`2716`、`2717`、`2718`、`2722`、`2724`、`2726`。
