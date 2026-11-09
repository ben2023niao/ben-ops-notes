---
id: "doc-38f8a30a6697"
title: "香港 CN 入口与云资源运维"
date: "2026-07-29T00:00:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN", "DNS"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/hongkong/cn/README-cn-branch.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/hongkong/cn/README-cn-branch.md"
sourceSha256: "5134a1cc66596efb019a82189f268512509a097deed555694afe2bff203906b5"
sourceSystem: "project-doc"
---

# 香港 CN 入口与云资源运维

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607290000-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BPython-%E9%A6%99%E6%B8%AF%20CN%20%E5%85%A5%E5%8F%A3%E4%B8%8E%E4%BA%91%E8%B5%84%E6%BA%90%E8%BF%90%E7%BB%B4.md)

> 整理日期：2026-07-29 00:00｜日期依据：正文日期

`cn` 分支只维护香港入口层，不部署或发布游戏后端代码。

## 保留范围

```text
docker/
├── ci/check.py                  Python 与目录边界检查
├── conf/domains/                PG、PP、PPK、vendor_d、vendor_b、Playson 域名池
├── deploy/hongkong/             Nginx、AWS、CloudFront、S3、Cloudflare 工具
├── doc/                         香港当前架构、验证和回滚记录
├── workbench/                   新会话轻量工作台和跨工具交接模板
└── 线上服务器信息/              香港服务器、登录方式和凭据索引（脱敏）
```

动态链路：

```text
CloudFront -> 香港 Nginx 192.0.2.14 -> 192.0.2.18 / 192.0.2.19
```

静态链路：

```text
CloudFront -> 香港私有 S3 bizops-h5-hk-517506432530 (ap-east-1)
```

## 当前厂商与端口

| 服务 | 端口 |
| --- | ---: |
| platform-api | 9090 |
| PG | 9091 |
| vendor_b | 9093 |
| PP | 9099 |
| PPK | 9098 |
| vendor_d | 9018 |
| Playson | 9020 |
| G759 | 9019 |

当前不提供 vendor_a 动态服务、JDB 和 Socket。vendor_b 的动态服务使用 9093，`vendor_b-static*` 对外域名直接读取 vendor_a 的共享前端资源。Playson 静态域名已接入香港 S3/CloudFront；Playson 动态域名已完成入口配置，业务可用性依赖外部后端 9020 服务监听。G759 静态域名已接入香港 S3/CloudFront（源为 gitlab client 仓库 G759static）；G759 动态域名已完成入口配置，业务可用性依赖外部后端 9019 服务监听。

## Python 工具

| 文件 | 用途 |
| --- | --- |
| `cf_api.py` | 安全调用 Cloudflare API |
| `cloudflare_aws_cutover.py` | DNS 灰度、状态、删除和回滚 |
| `sync_acm_cloudflare.py` | 同步 ACM DNS 验证记录 |
| `create_cloudfront_dynamic.py` | 创建或核对动态 CloudFront |
| `create_cloudfront_static_distributions.py` | 创建静态 CloudFront 与私有桶策略 |
| `configure_cloudfront_pg_static.py` | 配置 PG 静态别名与证书 |
| `configure_cloudfront_pp_customizations.py` | PP `customizations.info` 特殊规则 |
| `sync_gcs_to_s3.py` | Google 静态资源增量同步到香港 S3 |
| `validate_cloudfront_static.py` | 校验哈希、CORS、缓存和私有 S3 |
| `hk_ops_common.py` | 上述工具的共享安全函数 |

服务器安装后继续使用无扩展名命令，例如：

```bash
cf-api GET /user/tokens/verify
ONLY_ZONE=hkcloudplay01.com cloudflare-aws-cutover status vendor_b-static
validate-cloudfront-static
```

## 检查

```bash
python3 docker/ci/check.py
```

检查要求：

- `docker/` 下不得出现 `.sh` 或 `.bash` 文件。
- 所有 Python 文件必须能够编译。
- 不得重新加入 `ben-bot`、`services`、后端发布脚本或巴西宝塔快照。
- 不得提交密码、Token、Access Key、Secret、`.env` 或 `docker/cf.api`。

## 强制飞机群规则

香港项目所有多步骤运维任务必须“完成一步、通知一步”，标题固定为：

```text
【香港项目｜任务名称｜进度 X/Y】
```

每条消息写清实际操作对象、文件与数量、验证结果、现网影响和下一步。失败、等待和权限阻塞也必须及时通知。任务完成后把配置或操作/回滚文档作为文件发群。通知不得包含任何凭证。

飞机群发送方式参考 `master` 分支：

- 优先复用 master/线上 ben-bot 已验证的 Telegram 环境变量。
- 直接脚本发送时使用 `TG_BOT_TOKEN`，`TG_CHAT_ID` 或 `BEN_BOT_MONITOR_CHAT_ID`。
- 香港分支提供 `docker/deploy/hongkong/telegram_notify.py`，成功后输出 `message_id`，必须回写到事件文档。

## 文档命名

`docker/doc/` 运维记录按 master 标准和问题性质命名：

```text
YYYY-MM-DD-HHMM-【分类】问题或事项名称.md
YYYY-MM-DD-HHMM-【分类A+分类B】混合事项名称.md
YYYY-MM-DD-HHMM-【运维记录】长期总览或规范名称.md
```

当前分类：

- `补静态资源`：静态文件缺失、同步、补包、GCS/S3 源资源处理和 CDN 刷新。
- `修复Bug`：访问异常、跨域、404/403、游戏链路修复。
- `架构改造`：入口职责调整、云资源迁移、分支收口和工具改造。
- `优化`：清单整理、可读性提升、运维流程优化。
- `调整网络`：DNS、CloudFront、反代、灰度切流和回滚。
- `问题排查`：只读复核、未闭环问题定位、跨团队边界确认。
- `数据维护`：结果集、数据库文件、数据包、备份恢复和替换。
- `运维记录`：资源汇总、交接总览、规范、通知归档、长期索引类文档。

## 关键文档

- `docker/workbench/START_HERE.md`
- `docker/doc/2026-07-29-1300-【运维记录】某业务公司运维AI交接总览.md`
- `docker/doc/2026-07-29-1310-【运维记录】文档分类命名规范.md`
- `docker/doc/2026-07-29-1926-【补静态资源】香港vendor_d客户端资源同步验证记录.md`
- `docker/doc/2026-07-17-2000-【优化】香港CN五厂商前端可用域名清单.md`
- `docker/doc/2026-07-17-1900-【架构改造+网络调整】香港CN五厂商收口与vendor_b-AWS接入完整记录.md`
- `docker/doc/2026-07-17-1500-【架构改造】香港AWS-S3与CloudFront迁移搭建记录.md`
- `docker/doc/2026-07-17-1700-【网络调整】香港AWS-CloudFront灰度切换与回滚验证记录.md`
- `docker/线上服务器信息/README.md`
