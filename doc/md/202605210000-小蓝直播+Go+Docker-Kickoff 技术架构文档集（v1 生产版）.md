---
id: "doc-48347ddfb577"
title: "Kickoff 技术架构文档集（v1 生产版）"
date: "2026-05-21T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Docker", "Kubernetes", "MySQL", "Redis", "监控告警", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/README.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/README.md"
sourceSha256: "3a82c88cab94b28be94502957f185375a97658ad1cf1165acc555fa3ea2a33eb"
sourceSystem: "project-doc"
---

# Kickoff 技术架构文档集（v1 生产版）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605210000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2BDocker-Kickoff%20%E6%8A%80%E6%9C%AF%E6%9E%B6%E6%9E%84%E6%96%87%E6%A1%A3%E9%9B%86%EF%BC%88v1%20%E7%94%9F%E4%BA%A7%E7%89%88%EF%BC%89.md)

> 整理日期：2026-05-21 00:00｜日期依据：正文日期

> 本目录是 Kickoff（小蓝看夜场）平台的**完整技术架构**，对齐 PRD `docs/prd/product-prd.md` v0.1（原型 `2026.05.21评审版.html` v2.32）。
>
> 目标：支撑 **10000 CCU、~50000 注册、~800 万 RMB GMV** 的 32 天世界杯赛事窗口。

## 阅读路线

| 角色 | 必读顺序 |
| --- | --- |
| **技术负责人 / 架构评审** | 1 → 2 → 3 → 4 → 5 → 11 → 12 |
| **后端开发** | 1 → 2 → 4 → 5 → 9 → 10 |
| **直播 / 推流开发** | 1 → 3 → 8 |
| **DevOps / SRE** | 1 → 3 → 7 → 8 |
| **QA / 测试** | 1 → 6 → 7 → 12 |
| **产品 / 运营** | 1 → 6（风控部分） |

## 文档清单

| # | 文档 | 主题 | 状态 |
| --- | --- | --- | --- |
| 1 | [`system-architecture.md`](system-architecture.md) | 总体架构、服务拆分、数据流、组件职责边界 | 已确认 |
| 2 | [`data-model.md`](data-model.md) | 22 张核心表 DDL 要点、索引、分库分表预留 | 已确认 |
| 3 | [`live-streaming-architecture.md`](live-streaming-architecture.md) | 直播链路 **双方案并存**：SRS 自建 + 云直播托管 | 已确认 |
| 4 | [`funds-and-ledger.md`](funds-and-ledger.md) | 资金闭环、复式账本、强一致事务、对账、幂等 | 已确认 |
| 5 | [`messaging-strategy.md`](messaging-strategy.md) | 消息队列演进策略：Redis Streams → Kafka **按量切换** | 已确认 |
| 6 | [`risk-control-rules.md`](risk-control-rules.md) | 风控规则（**严格对齐 PRD 6 条**）+ 建议补入清单 | 已确认 |
| 7 | [`capacity-and-performance.md`](capacity-and-performance.md) | 容量规划、压力分布、压测 SLO、扩容触发 | 已确认 |
| 8 | [`deployment-and-monitoring.md`](deployment-and-monitoring.md) | K8s 部署、监控、告警、运维规范 | 已确认 |
| 9 | [`security-and-auth.md`](security-and-auth.md) | 鉴权、权限、密钥管理、安全防护 | 已确认 |
| 10 | [`implementation-roadmap.md`](implementation-roadmap.md) | 4 阶段 30 天实施路线图 | 已确认 |

## 核心架构决策（待 ADR 落地）

| 决策 ID | 决策项 | 选项 | 推荐 | 文档 |
| --- | --- | --- | --- | --- |
| ADR-0001 | 后端语言与框架 | Go+Gin / Java+SpringBoot / PHP+Laravel | **Go+Gin** | §1 |
| ADR-0002 | 服务拆分形态 | 微服务 / 模块化单体 | **模块化单体 + Worker** | §1 |
| ADR-0003 | 直播链路 | **SRS 自建** / **云直播托管** | **双方案并存待选** | §3 |
| ADR-0004 | 资金账本模型 | 复式记账 / 单式扣减 | **复式记账（DB 强一致）** | §4 |
| ADR-0005 | 消息队列起步形态 | Redis Streams / Kafka / 双轨 | **Streams 起步，按量切 Kafka** | §5 |
| ADR-0006 | 数据库 | MySQL 单库 / MySQL 主从 / TiDB | **MySQL 8 主从（v1）** | §2 |
| ADR-0007 | 缓存形态 | Redis Sentinel / Cluster | **Sentinel（v1）→ Cluster（扩展）** | §2 |
| ADR-0008 | 部署形态 | 单机 Docker / K8s | **K8s（赛季前 1 周上）** | §8 |
| ADR-0009 | CDN 策略 | 单 CDN / 双 CDN | **双 CDN GSLB** | §3 |
| ADR-0010 | 支付通道 | 直签商户 / 聚合支付 | **直签微信+支付宝** | §4 |
| ADR-0011 | KYC 时机 | 注册时 / 提现门槛触发 | **提现 >¥1000 触发** | §9 |
| ADR-0012 | 鉴权方案 | JWT / Session | **JWT + 设备指纹 + Redis 黑名单** | §9 |

ADR 文档逐项落地到 `docs/decisions/ADR-XXXX-*.md`。

## 与 PRD 的关系

- **本目录文档不是 PRD**：PRD 在 `docs/prd/`，定义"做什么"；本目录定义"怎么做"
- **不允许通过技术文档单方面新增业务规则**（如风控规则、限额、状态机）。任何业务规则缺口必须回写 PRD 后再实施
- **技术架构识别的业务缺口** → 写入 `risk-control-rules.md §3 建议补入清单`，由产品评审

## 版本

- v1.0：2026-05-22 基线版，对齐 PRD v0.1
- **v1.1：2026-05-22 PRD v0.2 修订**，主要变更：
  - 主播端模块（kickoff-streamer.md）完全废弃；主播仅 OBS 推流
  - 后台新增"直播间管理"模块（ADM-901-918），引入"房间管理员"角色
  - 登录注册简化为账号+密码（无验证码、无找回密码自助）
  - 直播间数据卡 + 赛事详情实时数据 全部砍掉（无第三方体育数据 API）
  - 比赛数据改为运营手动录入（仅比分 + 进球）
  - 赛事赔率管理 + 内容审核 升级 v1 必上
  - 支付通道方案 TBD，预留抽象层
- 后续每次架构变更必须 bump 文档版本，并在 `docs/decisions/` 留 ADR
