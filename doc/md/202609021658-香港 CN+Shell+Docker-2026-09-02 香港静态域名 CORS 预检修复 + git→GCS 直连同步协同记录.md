---
id: "doc-3db724989291"
title: "2026-09-02 香港静态域名 CORS 预检修复 + git→GCS 直连同步协同记录"
date: "2026-09-02T16:58:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Shell", "Docker", "Nginx", "CDN", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-09-02-1658-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E9%A6%99%E6%B8%AF%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8DCORS%E9%A2%84%E6%A3%80%E4%BF%AE%E5%A4%8D%E4%B8%8Egit%E7%9B%B4%E8%BF%9E%E5%90%8C%E6%AD%A5%E5%8D%8F%E5%90%8C%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-09-02-1658-【网络调整】香港静态域名CORS预检修复与git直连同步协同记录.md"
sourceSha256: "5e32effc5425e9c0e37d747c448ba7edf8448fe58fb25f16eea3ced140294e07"
sourceSystem: "project-doc"
---

# 2026-09-02 香港静态域名 CORS 预检修复 + git→GCS 直连同步协同记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/cn/docker/doc/2026-09-02-1658-【网络调整】香港静态域名CORS预检修复与git直连同步协同记录.md`

> 整理日期：2026-09-02 16:58｜日期依据：文件名日期

时间：2026-09-02 16:58（Asia/Manila）
项目：某业务公司 / PGServer cn（香港入口）
范围：静态域名 .hkcloudplay01-05.com 跨域预检修复（动态域名不动）；与 master 侧
      “全部厂家静态 git→GCS（巴西/香港）直连同步”改造协同
执行：Codex（本地工作区 + 香港入口机 192.0.2.14）

## 一、背景

```text
用户反馈：.hkcloudplay01.com 至 .hkcloudplay05.com 的静态域名要处理跨域，动态域名不用。
扫描结论（2026-09-02）：
  - GET 带 Origin：14 静态前缀 × 5 域名 = 70 个全部已返回 Access-Control-Allow-Origin: *；
  - OPTIONS 预检：仅 pg-static × 5 正常（200 + ACAO），其余 65 个返回 403 且无跨域头。
```

## 二、根因

```text
CloudFront 静态分配的 DefaultCacheBehavior 未配置 OriginRequestPolicy：
OPTIONS 预检的 Origin / Access-Control-Request-Method / Access-Control-Request-Headers
被边缘丢弃，S3 未收到 CORS 预检头，无法应答（403）。
pg-static 分配（某业务公司 HK pg-static test）显式配置了托管策略
CORS-CustomOrigin（88a5eaf4-2fd4-4709-b370-b4c650ea3fcf），因此正常。
```

## 三、修复

```text
新增工具 docker/deploy/hongkong/configure_cloudfront_static_cors.py
（已部署 /opt/bizops-hk-ops，原文件备份 /root/bizops-hk-cors-20260902/backup-*，CI 通过）：
为全部 某业务公司 HK static 分配 DefaultCacheBehavior 设置 OriginRequestPolicyId=
88a5eaf4-2fd4-4709-b370-b4c650ea3fcf（CORS-CustomOrigin）。
共更新 16 个分配：pg3/pg4/pg5/pg6/pg7、pp、ppk、vendor_d、vendor_c、g759、
vendor_b-static×3、vendor_a-statics×3（pg-static 本已正确）。
动态域名、nginx、S3 直连链路均未改动。
```

## 四、验证

```text
部署完成后：
  - OPTIONS 预检 70/70：全部 HTTP 200 且 Access-Control-Allow-Origin: *；
  - GET 带 Origin 70/70：ACAO=* 无回归；
  - 抽查真实文件 200：pg/pg3/pp/vendor_b/g759/pg6 各一个样例均 200；
  - 动态域名未触碰。
```

## 五、架构协同（git→GCS 直连同步改造）

```text
master 侧（并行会话，2026-09-02 推进中，文档初稿 2026-09-02-1550）：
  全部厂家静态资源改为以 client.git master 为唯一源，直连同步到
  巴西 GCS 圣保罗 live（-sa 桶）+ 香港/亚洲东京桶 + backup；
  宝塔 wwwroot 落盘（约 30GB）验证后清理；不再落盘服务器更新。
  已完成：PG 六前缀 76646 文件补齐巴西 -sa 100%；PG asia+backup 云对云 12/12；
  其余厂家差异审计与补齐进行中；随后清理、cron 替换、文档定稿提交。
参照 master 近期记录：2026-09-01 CNAME/Worker 直出、2026-09-02-1307 巴西 PG6/PG7。
cn 侧：香港 GCS 即东京 asia 桶；cn 当前 S3/CloudFront 静态链路保留，
  S3 直连/CloudFront/nginx 三路均已有 CORS；后续静态内容更新将不再依赖
  服务器落盘（由 master git→GCS 管道覆盖巴西与香港两区）。
```

## 飞机群通知 message_id

```text
4759：步骤 1/8 任务开始（CORS + 协同）
4760：步骤 2/8 CORS 现状扫描与根因
4761：步骤 3/8 修复实施完成（16 分配）
4762：步骤 4/8 验证通过（70/70）
4763：文档附件
4764：步骤 5-6/8 汇总
4765：提交结果（本地 commit 4badd660，未 Push）
```

## 回滚 / 遗留

```text
回滚：对 16 个分配将 DefaultCacheBehavior.OriginRequestPolicyId 移除或改回即可；
  脚本幂等，重复执行不产生变更。
遗留：
  - master git→GCS 管道（cron 替换、宝塔 wwwroot 清理、文档定稿提交）由并行会话推进；
  - cn 后续是否把静态服务切到香港 GCS（东京桶）作为主链路，待用户明确（当前 S3 为主）。
```

## 相关文档（互链）

```text
同日总览：2026-09-02-1711-【运维总览】20260902全量操作与架构改造汇总记录.md
演进后续：2026-09-02-1735-【网络调整】香港静态域名CORS显式来源改造与动态还原记录.md、
  2026-09-02-1755-【网络调整】香港静态域名CORS按Origin回显修复记录.md
```
