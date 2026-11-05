---
id: "doc-a0101b2e59f7"
title: "【排查】香港项目腾讯云 EdgeOne 域名与文档全量核对记录"
date: "2026-11-06T22:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Docker", "Nginx", "CDN", "DNS", "安全运维"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-11-06-2205-%E3%80%90%E6%8E%92%E6%9F%A5%E3%80%91%E9%A6%99%E6%B8%AF%E9%A1%B9%E7%9B%AE%E8%85%BE%E8%AE%AF%E4%BA%91EdgeOne%E5%9F%9F%E5%90%8D%E4%B8%8E%E6%96%87%E6%A1%A3%E5%85%A8%E9%87%8F%E6%A0%B8%E5%AF%B9%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-11-06-2205-【排查】香港项目腾讯云EdgeOne域名与文档全量核对记录.md"
sourceSha256: "d3e3c8a83b34a4c3a0423af7845a7f292a56b59428e7e66cf592309e2eddc19a"
sourceSystem: "project-doc"
---

# 【排查】香港项目腾讯云 EdgeOne 域名与文档全量核对记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-11-06-2205-【排查】香港项目腾讯云EdgeOne域名与文档全量核对记录.md`

> 整理日期：2026-11-06 22:05｜日期依据：文件名日期

更新时间：2026-11-06 22:05（Asia/Manila）

执行范围：本地 Git、当前 Mac 上的独立 `pgserver/cn` 工作区、老 Mac 导入目录，以及腾讯云 EdgeOne 只读 API。

## 一、请求与边界

```text
1. 查找 cn 分支香港项目的全部文档，确认是否包含腾讯云 CDN / EdgeOne 内容；
2. 在老 Mac 留下的数据中继续查找；
3. 核对 p3w9n5.shop、k8x2v9.shop、m4q7z1.shop、r2v8k4.shop 的实际归属；
4. 本轮不通知群；
5. 只读审计，不修改服务器、DNS、EdgeOne 配置或业务数据。
```

腾讯云账号密码、SecretId、SecretKey、SSH 密码、GitLab 凭据均未写入本文件或仓库。

## 二、开始前 Git 基线

主仓库：

```text
目录：/Users/ben/Projects/work/game/pgserver/master
本地 master：2ddae49f
origin/master：a72f41fb
origin/ben：9f59b4f3
origin/cn：5c3b3de6
工作区：干净
本地 master：领先 origin/master 17 个提交
```

当前 Mac 上另有一份独立的 `cn` 工作区：

```text
目录：/Users/ben/Projects/work/game/pgserver/cn
本地 cn：1fbe688f
origin/cn：5c3b3de6
工作区：干净
本地 cn：领先 origin/cn 142 个提交
```

结论：远程 `origin/cn` 停在 2026-08-12，不能代表当前香港运维历史。只搜索远程分支会漏掉 2026-09-29 以后的全部腾讯 EdgeOne 记录。

## 三、腾讯云实际资源

通过腾讯云官方只读 API 核对，国际站账号下：

```text
CDN DescribeDomains：0 个域名
EdgeOne DescribeZones：4 个站点
已启用：3 个
初始化但未启用：1 个
```

站点与加速域名：

| 站点 | Zone ID | 当前用途 | 加速域名数 |
| --- | --- | --- | ---: |
| `m4q7z1.shop` | `zone-3vm5evyb78ic` | 香港游戏主入口 | 22 |
| `k8x2v9.shop` | `zone-3vm7ccg417yf` | 香港游戏备用入口 | 22 |
| `p3w9n5.shop` | `zone-3vm7chzbxkcb` | 香港商户 / socket 入口 | 2 |
| `r2v8k4.shop` | `zone-3vm7cf444lhw` | 初始化，无加速域名，未承载业务 | 0 |

合计 46 个有效加速域名，全部是 HTTP/80 回源，源站统一为：

```text
公网：34.150.1.185
内网：203.0.113.1
机器：dbqp-hongkong-nginx-standby-01
```

### 3.1 游戏域名结构

`m4q7z1.shop` 与 `k8x2v9.shop` 各 22 个：

```text
动态 8 个：
  pg-games
  api
  jili-games
  pp-games
  ppk-games
  panda-games
  playson-games
  g759-games

静态 14 个：
  pg-static
  pg3-static
  pg4-static
  pg5-static
  pg6-static
  pg7-static
  pp-static
  ppk-static
  panda-static
  playson-static
  g759-static
  jili-static
  jili-static1
  jili-static2
```

动态域名经香港 standby Nginx 转发到香港 01/02 后端容器；静态域名经同一 Nginx 回源 AWS 大阪 S3 桶。

### 3.2 商户域名结构

`p3w9n5.shop` 的 2 个加速域名：

```text
p3w9n5.shop
socket.p3w9n5.shop
```

两者回源香港 standby Nginx，再转发 `platform-api:9090`，对应旧 Cloudflare 渠道的 `hk-socket.com` / `socket.hk-socket.com`。

## 四、当前公网验收

DNS 已解析到腾讯 EdgeOne 节点，8 个抽样地址全部 HTTP 200：

| 地址 | 结果 | 远端节点 |
| --- | --- | --- |
| `https://p3w9n5.shop/healthz` | 200 | `43.159.98.75` |
| `https://socket.p3w9n5.shop/healthz` | 200 | `43.159.99.79` |
| `https://pg-games.m4q7z1.shop/health` | 200 | `43.159.99.79` |
| `https://pg-static.m4q7z1.shop/health.json` | 200 | `43.159.98.75` |
| `https://jili-games.m4q7z1.shop/health` | 200 | `43.159.98.75` |
| `https://pg-games.k8x2v9.shop/health` | 200 | `43.159.99.79` |
| `https://pg-static.k8x2v9.shop/health.json` | 200 | `43.159.99.79` |
| `https://jili-games.k8x2v9.shop/health` | 200 | `43.159.98.75` |

静态健康文件响应头已出现 EdgeOne 缓存命中：

```text
server: nginx/1.18.0 (Ubuntu)
content-type: application/json
eo-cache-status: HIT
eo-log-uuid: <每请求唯一值>
```

## 五、cn 工作区文档核对

当前 `cn` HEAD 共有 99 份 Markdown/TXT：

```text
全部文档：99
明确命中腾讯云 / EdgeOne / 三个香港域名的文档：35
其中事件文档：29
其中工作台文档：5
其中 EdgeOne 备份说明：1
全仓库命中上述关键词的受版本控制文件：76
```

命中关键词包括：

```text
腾讯云 / 腾讯 CDN / Tencent Cloud / EdgeOne
m4q7z1.shop / k8x2v9.shop / p3w9n5.shop
```

### 5.1 时间线结论

```text
2026-09-29：确定香港大陆加速采用多家 CDN、免备案优先；
            腾讯国际站 EdgeOne 作为渠道 A。
2026-09-30：完成 standby 回源、m4q7z1.shop 建站、22 个二级域名、
            动态不缓存 / 静态缓存 7 天 / JILI WebSocket / 22 个 CNAME。
2026-10-02：完成 k8x2v9.shop 22 个加速域名并切换香港 01/02；
            完成 p3w9n5.shop 商户入口；
            香港 01/02 的域名文件写入 m4q7z1 / k8x2v9 / p3w9n5。
2026-10-05：修复 JILI / PP 静态资源、CORS、Worker 路径对齐和启动页兜底。
2026-10-08：修复 EdgeOne HTTP 回源导致 X-Forwarded-Proto=http、
            目录跳转被写成 HTTP 导致的 JILI / PP 故障。
2026-10-14：记录香港 PP 静态资源 EdgeOne 缓存清理。
```

### 5.2 关键文档

```text
docker/doc/2026-09-29-1808-【架构改造】香港项目大陆加速多CDN渠道免备案优先沟通口径与前置条件.md
docker/doc/2026-09-30-1129-【架构改造】EdgeOne接入香港standby入口回源填写指南.md
docker/doc/2026-09-30-1145-【架构改造】香港项目接入腾讯云EdgeOne架构方案（动态+S3静态）.md
docker/doc/2026-09-30-1300-【架构改造】EdgeOne站点m4q7z1全部二级域名接入（动态+静态走nginx）.md
docker/doc/2026-09-30-1650-【架构改造】香港后端域名配置切换到m4q7z1（腾讯CDN）.md
docker/doc/2026-10-02-1446-【架构改造】EdgeOne站点k8x2v9接入与香港后端域名切换.md
docker/doc/2026-10-02-1500-【架构改造】p3w9n5商户域名接入与香港0102三域名生效.md
docker/doc/2026-10-08-1425-【故障处理】腾讯EdgeOne回源HTTP导致X-Forwarded-Proto为http（JILI进不去）修复.md
docker/doc/2026-10-14-1050-【运维记录】香港PP静态资源CDN缓存清理记录.md
```

## 六、全部 35 份命中文档

```text
docker/deploy/hongkong/cdn-backup/edgeone/README.md
docker/doc/2026-09-29-1808-【架构改造】香港项目大陆加速多CDN渠道免备案优先沟通口径与前置条件.md
docker/doc/2026-09-30-1129-【架构改造】EdgeOne接入香港standby入口回源填写指南.md
docker/doc/2026-09-30-1145-【架构改造】香港项目接入腾讯云EdgeOne架构方案（动态+S3静态）.md
docker/doc/2026-09-30-1147-【运维记录】腾讯云API密钥（子用户）创建与AI调用规范.md
docker/doc/2026-09-30-1205-【架构改造】EdgeOne测试站点m4q7z1shop建站与规则引擎API实践.md
docker/doc/2026-09-30-1216-【架构改造】EdgeOne新增3个测试站点与套餐配额限制.md
docker/doc/2026-09-30-1225-【运维记录】EdgeOne全托管给AI的能力边界与落地方案.md
docker/doc/2026-09-30-1300-【架构改造】EdgeOne站点m4q7z1全部二级域名接入（动态+静态走nginx）.md
docker/doc/2026-09-30-1340-【运维记录】m4q7z1.shop国内测速链接与源站测速文件.md
docker/doc/2026-09-30-1650-【架构改造】香港后端域名配置切换到m4q7z1（腾讯CDN）.md
docker/doc/2026-10-02-1446-【架构改造】EdgeOne站点k8x2v9接入与香港后端域名切换.md
docker/doc/2026-10-02-1500-【架构改造】p3w9n5商户域名接入与香港0102三域名生效.md
docker/doc/2026-10-02-1610-【运维记录】EdgeOne三站点规则中文标注与站点标签方案.md
docker/doc/2026-10-02-1615-【故障处理】香港0102配置被同步覆盖与一键恢复防复发.md
docker/doc/2026-10-02-1630-【架构改造】香港nginx的JILI-TADA静态本地化与index-js修复.md
docker/doc/2026-10-05-1110-【架构改造】香港nginx补齐巴西Worker静态规则（PP进不去修复）.md
docker/doc/2026-10-05-1210-【优化+故障处理】香港同步脚本优化复核与jili崩溃修复.md
docker/doc/2026-10-05-1230-【架构改造】香港nginx的jili静态改为走自己的大阪桶（对齐香港Worker）.md
docker/doc/2026-10-05-1250-【网络调整】香港动态域名CORS兜底（网关错误也带CORS头）.md
docker/doc/2026-10-05-1310-【运维】跨域职责划分-动态归开发静态归运维（撤销动态CORS兜底）.md
docker/doc/2026-10-05-1320-【故障处理】香港JILI游戏资源403定位与TADA前缀兜底修复.md
docker/doc/2026-10-05-1330-【架构改造】香港jili-games游戏启动页nginx兜底（后端无路由回JILI静态桶）.md
docker/doc/2026-10-05-1335-【故障处理】香港JILI动态域名兜底响应补CORS与cdn-cgi静默.md
docker/doc/2026-10-05-1345-【运维】撤销动态域名兜底CORS-重申动态归开发静态归运维.md
docker/doc/2026-10-05-1400-【架构改造】香港JILI静态域名按Worker路径映射并补intro-astarte处理.md
docker/doc/2026-10-08-1425-【故障处理】腾讯EdgeOne回源HTTP导致X-Forwarded-Proto为http（JILI进不去）修复.md
docker/doc/2026-10-08-1440-【故障处理】大厅拉起JILI失败-静态域名根探活403与v2-v5分组404修复.md
docker/doc/2026-10-08-1450-【故障处理】静态域名目录跳转被写成http-absolute_redirect-off修复.md
docker/doc/2026-10-14-1050-【运维记录】香港PP静态资源CDN缓存清理记录.md
docker/workbench/ACTIVE_TASKS.md
docker/workbench/CURRENT_STATE.md
docker/workbench/CURRENT_TASK.md
docker/workbench/MACHINE_ACCESS_MATRIX.md
docker/workbench/PROJECT_RUNTIME_CHAINS.md
```

## 七、老 Mac 与其他历史副本

老 Mac 导入目录：

```text
/Users/ben/Private/from-oldmac-20261030
Markdown/TXT：0
腾讯云 / EdgeOne 文档命中：0
```

但该目录的 SSH `known_hosts` 保留了 `34.150.1.185` 的连接指纹，说明老 Mac 确实连接过香港 standby 入口；相关说明文档没有随老 Mac 导入。

另一个 PGServer 旧归档：

```text
/Users/ben/Projects/work/game/archive/pgserver-backup-20260715
腾讯云文档命中：0
```

Mac 上的 `18game_devops` 确有另一套腾讯 COS / EdgeOne 历史文档，但域名是 `hbabaxb.cn`、`zkifae.cn` 等，不属于 DBQP 香港项目，不能混入本次香港资产清单。

## 八、安全检查

```text
1. 提供的完整腾讯云 SecretId / SecretKey 在主仓库、cn 工作区、老 Mac 导入目录中均未命中；
2. cn 文档只记录凭据路径、权限建议和脱敏示例，未发现本轮提供密钥的完整明文；
3. 历史文档明确要求主账号密钥只用于临时操作，长期应使用仅含 EdgeOne/TEO 权限的子用户；
4. 本轮只调用 DescribeDomains、DescribeZones、DescribeAccelerationDomains 等只读 API；
5. 未创建、修改、删除任何腾讯云资源；
6. 未修改服务器、Nginx、DNS、容器或业务数据；
7. 按要求未发送群通知。
8. 本轮对话出现过腾讯云主账号 SecretKey；按历史文档的安全规范，应尽快轮换，
   并改用仅授予 QcloudTEOFullAccess 的子用户密钥。
9. 本机独立 cn 仓库的 old-gitlab remote 配置仍内嵌旧凭据；
   本轮未输出凭据值。建议轮换该凭据并改用 Git credential helper/SSH key。
```

## 九、结论

```text
香港项目确实有腾讯云 EdgeOne/CDN 内容，而且不是零散提及，
是一套已上线并运行的正式游戏与商户加速入口：

m4q7z1.shop + k8x2v9.shop -> 香港游戏动态/静态双入口
p3w9n5.shop               -> 香港商户/socket 入口
34.150.1.185              -> 三站的统一 Nginx 回源

当前 3 个站点、46 个加速域名均在线，抽样动态与静态端点全部 200，
静态资源返回 eo-cache-status: HIT。

r2v8k4.shop 只是早期创建的空站点，当前无加速域名、无业务用途。
```
