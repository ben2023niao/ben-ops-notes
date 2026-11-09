---
id: "doc-063fa6eb2d04"
title: "2026-09-24 香港 standby 入口服务器与新域名 hkcloudplay06/07 接入记录"
date: "2026-09-24T14:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Linux", "Shell", "Python", "Docker", "Nginx", "Redis", "监控告警"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-09-24-1400-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AFstandby%E5%85%A5%E5%8F%A3%E4%B8%8E%E6%96%B0%E5%9F%9F%E5%90%8Dhkcloudplay0607%E6%8E%A5%E5%85%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-09-24-1400-【架构改造】香港standby入口与新域名hkcloudplay0607接入记录.md"
sourceSha256: "281e39667f44f3101e9ba256ce5d2f58bacf87b83ab7aef126da02c2f88d0852"
sourceSystem: "project-doc"
---

# 2026-09-24 香港 standby 入口服务器与新域名 hkcloudplay06/07 接入记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609241400-%E9%A6%99%E6%B8%AF%20CN%2BLinux%2BShell-2026-09-24%20%E9%A6%99%E6%B8%AF%20standby%20%E5%85%A5%E5%8F%A3%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8E%E6%96%B0%E5%9F%9F%E5%90%8D%20hkcloudplay06-07%20%E6%8E%A5%E5%85%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-24 14:00｜日期依据：文件名日期

## 一、任务与要求

```text
1. 参考巴西 bizops-saopaulo-nginx-standby-01，部署一台香港 bizops-hongkong-nginx-standby-01
2. 与现有香港项目（入口机 / 两台自建后端）内网相通
3. 新注册域名 hkcloudplay06.com / hkcloudplay07.com（NS 已指向 Cloudflare
   bjorn.ns.cloudflare.com / romina.ns.cloudflare.com）走这台服务器
4. 给这两个域名配置 Worker 与巴西口径的 CDN 配置
5. 老香港域名（hkcloudplay01-05）不做任何变动，不影响老业务
6. 列出新开 3 台服务器的内网/公网 IP 与名称，方便加堡垒机
```

流程：前置核验 → 执行 → 验证 → 文档 → 本地提交；用户明确「不通知群」，本轮不发飞机群通知。

## 二、参考的巴西配置

| 项 | 巴西 `bizops-saopaulo-nginx-standby-01` | 香港 `bizops-hongkong-nginx-standby-01` |
| --- | --- | --- |
| 角色 | 备用流量入口（Docker + Nginx + 备用 ben-bot） | 新域名流量入口（Docker + Nginx） |
| 机型 | `e2-custom-4-8192`（4 vCPU / 8GB） | `e2-custom-4-8192`（4 vCPU / 8GB） |
| 系统盘 | 200GB | 200GB `pd-balanced` |
| 公网 | 固定 IP | 固定 IP（新预留静态地址） |
| 标签 | `http-server;https-server` | `hk-baota,hk-ssh`（对应香港 80/443 + 22 放行规则） |
| 内网 | `192.0.2.1` | `192.0.2.1` |

## 三、执行内容

### 3.1 服务器与网络

```text
实例：bizops-hongkong-nginx-standby-01 | asia-east2-a | e2-custom-4-8192
内网：192.0.2.1（bizops-hongkong-slotsapi-subnet-v2，与入口机 192.0.2.1、后端 192.0.2.1/0.4 同子网）
公网：192.0.2.37（静态地址 bizops-hongkong-nginx-standby-01-ip，固定）
系统：Ubuntu 22.04 LTS、UTC、Docker 29.8.1、Nginx 1.18.0（系统包）
启动脚本：/root/hk-standby-startup.sh（香港入口机保留，899 字节）
  直接写 /etc/ssh/sshd_config.d/00-bizops-password.conf（避免 cloud-init 50- 覆盖）
```

新增 GCP 防火墙规则（不改动旧规则）：

```text
name: bizops-hk-allow-standby-to-backends
network: bizops-hongkong-slotsapi-network-v2
direction: INGRESS | source: 192.0.2.1/32 | target_tags: hk-backend
allow: tcp:8765,tcp:9090-9104
```

### 3.2 Nginx 配置（仅新域名，老域名完全不碰）

配置文件：`docker/deploy/hongkong/nginx-standby.conf`（已落仓库并部署到 standby）

```text
upstream：优先自建后端 192.0.2.1 / 192.0.2.1（failover 到外部双后端 192.0.2.18 /
  192.0.2.19），因此自建后端容器部署前后新域名都可用；
server 块：pg-games / api（-> PG 后端，与老口径一致）、vendor_b / pp / ppk / vendor_d /
  vendor_c / g759-games，全部限定 hkcloudplay0[67].com；
静态兜底：<prefix>-static.hkcloudplay0[67].com -> 香港 S3 公开地址（前缀映射与老口径一致，
  vendor_b-static* 映射 vendor_a-statics*）；
健康检查：/healthz -> 200 ok（80 与 443 均监听，兼容 Cloudflare Flexible/Full；
  SSL 使用自签证书 /etc/nginx/ssl/bizops-hk-standby.{crt,key}，SAN 覆盖
  hkcloudplay06/07 及其通配）。
```

### 3.3 新域名 DNS（Cloudflare）

两个 zone 此前**没有任何记录**；本次各创建 23 条，结构对齐老域名但入口换成 standby：

```text
*.hkcloudplay06.com / *.hkcloudplay07.com        A  192.0.2.37  proxied=True   (通配)
api / pg-games / pp-games / ppk-games / vendor_d-games / vendor_b-games /
  vendor_c-games / g759-games                      A  192.0.2.37  proxied=True   (8 条)
14 个静态前缀（pg、pg3-pg7、pp、ppk、vendor_d、vendor_c、g759、vendor_b-static{,1,2}）
                                                  A  192.0.2.37  proxied=True   (14 条)
```

执行工具：`docker/deploy/hongkong/setup_new_zone.py`（幂等，支持 `--apply/--update`）。

踩坑与修正（重要）：

```text
现象：静态记录最初按老口径配成「灰云 CNAME -> CloudFront」，实测 https 静态域名返回 525。
原因：同一 zone 内存在「橙云通配 *」与「灰云精确 CNAME」混用，Cloudflare 用静态域名的
  SNI 去连该 CNAME 的目标（CloudFront 分配未添加 hkcloudplay06/07 别名，也没有对应证书），
  TLS 握手失败 -> 525。
处理：14 条静态记录统一改为「橙云 A -> 192.0.2.37」，与通配保持一致；静态由 nginx
  兜底回源香港 S3（直连源站带 Host 实测 200、8904 字节、x-amz-version-id 与 S3 对象一致）。
说明：Worker 部署后由 Worker 路由在同一份橙云记录上接管静态，DNS 不需要再改。
```

## 四、验证结果

### 4.1 新域名静态资源（14 前缀 × 2 zone = 28/28 通过）

```text
zone 06：pg-static/pg3/pg4/pg5/pg6/pg7-static、pp/ppk/vendor_d/vendor_c/g759-static、
         vendor_b-static/vendor_b-static1/vendor_b-static2 -> 全部 200
zone 07：同上 14 个前缀 -> 全部 200
抽样路径使用各前缀真实对象（如 pg-static/100/001aacae6a.117d6.json、
pg6-static/1834850/index.html、vendor_b-static1/_nuxt/01e19b71f78691f07a2e.js）。
链路：浏览器 -> Cloudflare（cf-ray 命中）-> standby nginx 192.0.2.1 -> 香港 S3。
```

### 4.2 服务端自检（standby）

```text
hostname bizops-hongkong-nginx-standby-01；UTC；Docker 29.8.1；nginx 1.18.0
/healthz -> 200；内网到入口机 192.0.2.1 ping OK、到后端 192.0.2.1:22 OK
nginx -t 通过；站点配置已生效（pg-games/api/pg-static 三个 Host 均命中对应 server 块）
```

### 4.3 动态域名当前状态（配置就绪，业务未部署）

```text
用户确认：两台自建后端「还没部署业务，配置好就行，不需要接口通」。
因此动态域名当前返回 502/504 属预期，不作为故障处理。
链路本身已就绪：
  Cloudflare（橙云）-> standby nginx 192.0.2.1 -> upstream 已指向自建后端 192.0.2.1 / 0.4，
  并配置外部双后端 192.0.2.18 / 192.0.2.19 作为 failover。
  standby -> 自建后端端口实测为「拒绝/未监听」= 防火墙已放行、后端容器未启动（符合预期）。
  外部双后端存在源 IP 白名单（老入口机可用、standby 不可用），本轮不需要打通。
后续：自建后端容器部署完成后，动态域名无需改动配置即可自动走自建后端（upstream 优先自建）。
```

### 4.4 老域名未受影响（对照）

```text
https://pg-static.hkcloudplay05.com/85/c445ebb91e.cadb1.json -> 200
https://pg-games.hkcloudplay05.com/health -> 200
老 zone（01-05）DNS、CloudFront、入口机 nginx 配置本轮均未改动。
```

## 五、Worker 与 CDN 配置（已完成）

```text
状态：DONE（2026-09-24 14:30）
token：/root/.config/cloudflare/workers-token（用户在香港入口机创建的用户 API 令牌）
  权限：Workers 脚本(account)、Workers 路由(zone)、Cache Rules(zone)、区域设置(zone)
  区域资源：hkcloudplay01-07.com（用户保留全部 7 个，便于明天调整老域名）
  账号：eaf1a5f4eb53c8cd384ce9088181b97c（[邮箱已脱敏]'s Account，与巴西同一账号）
  说明：第一版 token（/root/.config/cloudflare/api-token）只有 DNS 权限，
  实测 /accounts、workers/routes、rulesets、zone settings 均 403，故新建了专用 token。
```

执行记录（全部在 hkcloudplay06/07 上，老域名未触碰）：

```bash
# 香港入口机（工具副本 /root/bizops-hk-worker，或从 cn 仓库执行）
# 注意：--account / --token-file / --zones 是顶层参数，必须写在子命令前
python3 docker/deploy/hongkong/deploy_static_worker.py \
    --account eaf1a5f4eb53c8cd384ce9088181b97c \
    --token-file /root/.config/cloudflare/workers-token \
    --zones hkcloudplay06.com,hkcloudplay07.com \
    deploy --backup-dir /root/bizops-hk-worker-backup/20260924
    -> deploy: http=200 success=True（脚本名 bizops-hk-static-proxy，8674 bytes）

python3 ... --token-file <T> --zones <06,07> routes --apply
    -> 28 条路由创建成功（每 zone 14 条，GET 复核 routes=14/14）

python3 docker/deploy/hongkong/static_cdn_config.py apply-cache-rules \
    --zones hkcloudplay06.com,hkcloudplay07.com --token-file <T> --apply
    -> 两个 zone 均 http=200 success=True
    -> ruleset: statics / phase http_request_cache_settings / 1 条规则
       action=set_cache_settings，cache=true，edge_ttl=mode override_origin / default 604800
       表达式：ends_with(http.host,"-static.<zone>") or ends_with(...,"-static1.<zone>")
               or ends_with(...,"-static2.<zone>")

python3 ... --zones <06,07> verify
    -> worker verify summary passed=28 failed=0
```

实测结果：

| 验证项 | 结果 |
| --- | --- |
| 静态资源 14 前缀 × 2 zone | 28/28 HTTP 200 |
| Worker 生效标记 | `x-bizops-worker: hk-static-proxy` |
| 边缘缓存 | 首次 MISS，二次 HIT（`cf-cache-status`） |
| 响应缓存头 | `cache-control: public, max-age=604800, immutable` |
| 目录请求 | `302 -> /1834850/index.html` |
| OPTIONS 预检 | 204（边缘直接应答） |
| 平台 Origin CORS | 精确回显 `https://ind-h5.bizopsplus999.com` |
| 任意 Origin CORS | `*` |
| 老 zone 路由数 | hkcloudplay01-05 全部为 0（未受影响） |
| 老域名访问 | `pg-static.hkcloudplay01.com` / `.hkcloudplay05.com` 均 200 |

本轮踩坑（已修正）：

```text
1) 命令参数位置：--account/--token-file/--zones 必须放在子命令（deploy/routes/...）之前，
   否则 argparse 报 unrecognized arguments。1245 操作手册已同步修正。
2) Cache Rules API：PUT /zones/{id}/rulesets/phases/http_request_cache_settings/entrypoint
   的 body 不接受 "kind" 与 "phase" 字段（报 invalid JSON: unknown field），
   最终只提交 {"name","rules"}。static_cdn_config.py 已按实测修正。
```

后续（可选）：

```text
1) 若要完全对齐巴西：确认 SSL/TLS 模式、Tiered Cache、Browser Cache TTL 等区域设置。
2) 明天调整老域名时复用同一 token，把 --zones 换成 hkcloudplay01-05，建议先单前缀灰度。
3) CACHE_SALT 失效：改 docker/deploy/hongkong/hk_static_worker.js 的 CACHE_SALT 后重新
   deploy 即可全量失效边缘缓存（Cache API 按 zone 隔离，zone purge 清不掉）。
```

## 六、新开的 3 台服务器（堡垒机录入用）

| 角色 | 实例名 | 内网 IP | 固定公网 IP | 可用区 | 规格 | 用途 |
| --- | --- | --- | --- | --- | --- | --- |
| 香港后端 01 | `bizops-hongkong-sanic-prod-01` | `192.0.2.1` | `192.0.2.16` | `asia-east2-b` | e2-standard-8 / 500GB | 业务后端容器（待部署） |
| 香港后端 02 | `bizops-hongkong-sanic-prod-02` | `192.0.2.1` | `192.0.2.17` | `asia-east2-c` | e2-standard-8 / 500GB | 业务后端容器（待部署） |
| 香港 standby 入口 | `bizops-hongkong-nginx-standby-01` | `192.0.2.1` | `192.0.2.37` | `asia-east2-a` | e2-custom-4-8192 / 200GB | 新域名 06/07 入口（Nginx + Docker） |

```text
三台统一：用户 root、密码为本次用户指定值（明文不入库，见第七节）、端口 22、
  与入口机 192.0.2.1 同子网（192.0.2.1/20）、内网互通已验证。
已有入口机（不在本次新建范围）：bizops-hongkong-game-results-data-bt
  192.0.2.1 / 192.0.2.14（老域名 01-05 入口，未改动）。
```

## 七、安全说明

```text
1. root 密码按用户指定值设置，明文未写入仓库、工作台或本文档。
2. 三台机器公网只放行 SSH（hk-ssh）与 standby 的 80/443（hk-baota）；未开放数据库、
   Redis、Docker API 等端口。
3. standby 的 443 使用自签证书，仅用于 Cloudflare 回源；对外证书由 Cloudflare 提供。
4. 执行修复时 gcloud compute ssh 曾向项目 mevendor_ata 写入运维公钥
   （compute.511057654766442468 / compute.2166080764923942857），如不需要可删除。
```

## 八、待办

```text
1. 【需权限】配置 Worker + Cache Rules + 缓存设置（见第五节，两种执行方式任选）。
2. 【待后端业务】自建后端（192.0.2.1 / 192.0.2.1）容器部署；部署完成后动态域名自动
   走自建后端（upstream 优先自建 + 外部 failover），无需改 nginx/DNS。
3. 【可选】standby 的每日快照策略、Beszel 监控 agent。
4. 【可选】静态改走 Worker 后，评估是否保留 nginx 静态兜底（当前保留作为回滚路径）。
```

## 九、关联文件

```text
docker/deploy/hongkong/nginx-standby.conf        standby nginx 站点配置（已部署）
docker/deploy/hongkong/setup_new_zone.py         新 zone DNS 记录创建/更新工具
docker/deploy/hongkong/hk_static_worker.js       香港静态 Worker（待部署）
docker/deploy/hongkong/deploy_static_worker.py   Worker 部署/路由/验证工具
docker/doc/2026-09-24-1300-【架构改造】香港两台后端服务器创建与Docker环境部署记录.md
docker/doc/2026-09-24-1230-【问题排查+架构改造】香港CN静态域名CDN与巴西口径差异清单.md
docker/doc/2026-09-24-1245-【运维记录】香港静态域名上CDN操作手册（运维+后端手动）.md
```
