---
id: "doc-46f0c547074b"
title: "ADR-0013： 快速验证阶段 — 两机协作部署(GitLab build runner + 部署机 deploy runner)"
date: "2026-05-25T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Python", "Go", "Docker", "Kubernetes", "MySQL"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0013-quickstart-single-machine-gitlab-ci.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0013-quickstart-single-machine-gitlab-ci.md"
sourceSha256: "ff8c805e3531c204c77b33a5b6df19e33974daa76a74a24962a397d9451ae037"
sourceSystem: "project-doc"
---

# ADR-0013： 快速验证阶段 — 两机协作部署(GitLab build runner + 部署机 deploy runner)

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0013-quickstart-single-machine-gitlab-ci.md`

> 整理日期：2026-05-25 00:00｜日期依据：正文日期

| 状态 | 已采纳(快速验证期生效;扩量后回看 [ADR-001](ADR-001-deployment-strategy.md)) |
|---|---|
| 日期 | 2026-05-25 |
| Owner | 后端 / 运维 |
| 影响范围 | 3.1.159.178(GitLab CE + build runner)、54.151.131.132(部署目标 + deploy runner)、`.gitlab-ci.yml`、`infra/deploy/` |
| 相关需求 | OPS-001 部署架构(快速验证阶段) |
| 关联文档 | [ADR-001](ADR-001-deployment-strategy.md)(生产期 Docker 方案,本阶段不启用)、[`docs/operations/logging-and-alerting.md`](../operations/logging-and-alerting.md) |

## 1. 背景

快速验证阶段资源极度受限:

| 维度 | 现状 |
|---|---|
| GitLab 服务器 | `3.1.159.178`(已部署 GitLab CE,本项目专属,有富余资源跑 build) |
| 部署机 | `54.151.131.132`(只跑业务 + mysql/redis,资源不能被 build 抢) |
| 团队规模 | 单人/极小团队,无专职运维 |
| 业务诉求 | 让产品/测试今天就能看到运行版本,验证流程 + 联调 |

ADR-001 选过的 Docker+ECR+RDS+CloudFront 方案是**生产期目标**,对快速验证阶段过重(还没有 registry / 没有 RDS / 没有多机 HA 需求)。

## 2. 决定

**两机协作 + 两 runner 分工**:
- **build runner**(在 GitLab 服务器 3.1.159.178)跑 quality / vet / test -race / go build,出二进制 artifacts
- **deploy runner**(在部署机 54.151.131.132)跑 deploy job,下载 artifacts → install → migrate → systemctl restart
- **两个 runner 都注册为 project-locked specific runner**,只接本项目 job,不进 GitLab 共享池

### 2.1 物理布局

```
┌────────────────────────────────────────┐         ┌──────────────────────────────────────┐
│  3.1.159.178 (GitLab CE)               │  push   │  54.151.131.132 (部署机)              │
│                                        │ ◄──────│  (开发推 git)                         │
│  [GitLab Web/Git/CI 调度]               │         │                                      │
│                                        │         │                                      │
│  ┌──────────────────────────────────┐  │  job    │  ┌────────────────────────────────┐  │
│  │ gitlab-runner (build)            │  │ ──────► │  │ gitlab-runner (deploy)         │  │
│  │   tag: kickoff-build             │  │  调度   │  │   tag: kickoff-deploy           │  │
│  │   user: kickoff-build            │  │         │  │   user: kickoff                 │  │
│  │   工具链: Go 1.22 + node 20 + py │  │         │  │   工具链: 无 Go,只 systemctl   │  │
│  │                                  │  │         │  │                                 │  │
│  │   quality                        │  │         │  │   download artifacts (bin/)     │  │
│  │   go-vet / go-test -race         │  │         │  │       │                         │  │
│  │   go-build → bin/{api,admin,     │  │         │  │       ▼                         │  │
│  │              migrate}            │  │         │  │   install → /usr/local/bin/     │  │
│  │       │ artifacts (~30MB)        │──┼─────────┼─►│   migrate up                    │  │
│  │       ▼                          │  │         │  │   systemctl restart             │  │
│  └──────────────────────────────────┘  │         │  │       │                         │  │
│                                        │         │  │       ▼                         │  │
│                                        │         │  │   curl /healthz                 │  │
│                                        │         │  └────────────────────────────────┘  │
│                                        │         │                                      │
│                                        │         │  systemd:  kickoff-api  :8080        │
│                                        │         │            kickoff-admin :8081       │
│                                        │         │  docker:   mysql :13306              │
│                                        │         │            redis :16379              │
└────────────────────────────────────────┘         └──────────────────────────────────────┘
```

### 2.2 选型逐条对比

| 维度 | 两 runner 分工(本方案) | 单 runner 全跑部署机 | Docker + registry | k8s/k3s |
|---|---|---|---|---|
| 部署机装 Go | ❌ 不需要 | ✅ 必须 | ❌ 不需要 | ❌ 不需要 |
| build 抢业务资源 | ❌ 不会(在 GitLab 上) | ⚠️ 会 | ❌ | ❌ |
| 首次搭建 | 1.5 小时(两台机各装 runner) | 1 小时 | 半天 | 1 天起步 |
| 一次部署耗时 | ~45s(含 artifact 传输 ~30MB) | ~30s | ~2min | ~3min |
| 回滚 | GitLab retry 老 pipeline | 同左 | docker compose down/up | kubectl rollout undo |
| 跨机依赖 | artifacts(GitLab 自身管,无 SSH key) | 无 | registry + 网络 | etcd + apiserver |
| 工具链 | Go(GitLab 上)+ systemd(部署机) | Go + systemd | Docker + registry | k8s 全家桶 |
| 与本阶段匹配度 | ✅ **最优** | ⚠️ 资源耦合 | ⚠️ 过重 | ❌ 显著过度 |

### 2.3 关键决策点

1. **两 runner 分工**(不让 build 在部署机跑) — 修掉了 v1 方案"runner 抢业务资源"风险
2. **artifacts 传二进制,不走 SSH/scp** — 避免管 SSH key,GitLab artifacts 自身有重试和审计
3. **deploy runner `GIT_STRATEGY: none`** — 不 fetch 源码,只下 artifacts(`infra/deploy/` `services/go-app/{bin,config,migrations}/` 全在 artifact 里)
4. **两个 runner 都 project-locked**(`locked=true` + `--run-untagged=false` + `tag-list`)— 不接其他项目 job,符合"只针对这个项目"
5. **build runner 用独立用户 `kickoff-build`**(与 GitLab 服务进程隔离)
6. **deploy runner 用 `kickoff` 用户 + sudoers NOPASSWD install/systemctl**
7. **APP_ENV=dev,通过 env 覆盖 db host=203.0.113.1** — 复用 `config.dev.yaml`
8. **mysql/redis 用 docker-compose 常驻部署机** — 不污染系统包,一次性 up,后续 `systemctl restart` 不动它
9. **migration 自动跑** — 失败 fail-closed(不重启服务),向前兼容,不向后回滚

### 2.4 触发链路

```
开发推 git push (dev|main)
   ↓
3.1.159.178 GitLab CE → 调度 .gitlab-ci.yml
   ↓
[3.1.159.178 build runner] 接 quality / vet / test / build job
   ├─ quality:        npm run check
   ├─ go-vet:         go vet ./...
   ├─ go-test:        go test -race -count=1 ./...
   └─ go-build:       make build + go build migrate
                      ↓ artifacts (bin/ + migrations/ + config/ + infra/deploy/)
[54.151.131.132 deploy runner] 接 deploy job
   ├─ download artifacts(GitLab artifact store)
   ├─ bash infra/deploy/deploy.sh
   │     ├─ install bin/* → /usr/local/bin/kickoff-*
   │     ├─ kickoff-migrate up
   │     ├─ systemctl restart kickoff-api kickoff-admin
   │     └─ curl /healthz
   └─ pipeline 绿
```

## 3. 后果

### 正向

- ✅ 最快验证路径 — 1.5 小时内能跑起来
- ✅ 部署机零工具链污染 — 没装 Go,业务进程独享资源
- ✅ 跨机零 SSH key — artifacts 走 GitLab 自身,安全审计/重试全免费
- ✅ 与 [logging-and-alerting.md](../operations/logging-and-alerting.md) docker-compose 方案一致(本阶段是子集)
- ✅ 不引入新厂商 — 完全自建,符合 [CLAUDE.md 第三方服务规则](../../CLAUDE.md)

### 负向

- ⚠️ 多一台机要维护 runner — GitLab 服务器要装 Go + node + python(一次性,见 runner-bootstrap)
- ⚠️ artifact ~30MB 跨机传 — 局域网/同机房可忽略,跨机房注意带宽
- ⚠️ deploy 期间 systemctl restart ~1s 停服 — 接受(快速验证阶段无 SLA)
- ⚠️ 二进制无版本归档 — GitLab artifact `expire_in: 7 days`,7 天外回滚要重新跑 build job

### 升级信号(回到 ADR-001 Docker 方案)

满足**任一**条件:
- 节点数 ≥ 2(需要镜像统一)
- 零停机部署需求(restart 1s 不可接受)
- 单次 build 耗时 ≥ 5min
- 7 天外回滚频繁(artifact 过期成为瓶颈)

## 4. 实施清单

| 步骤 | 物料 |
|---|---|
| 两机准备(一次性) | [`infra/deploy/runner-bootstrap.md`](../../infra/deploy/runner-bootstrap.md) |
| systemd unit(部署机) | [`infra/deploy/systemd/kickoff-api.service`](../../infra/deploy/systemd/kickoff-api.service) + `kickoff-admin.service` |
| 部署脚本 | [`infra/deploy/deploy.sh`](../../infra/deploy/deploy.sh) |
| GitLab CI 配置 | [`.gitlab-ci.yml`](../../.gitlab-ci.yml) |
| 部署指南 | [`infra/deploy/README.md`](../../infra/deploy/README.md) |

## 5. 关联 ADR

- **ADR-001**(部署策略 Docker + ECR): 本 ADR 是其**快速验证阶段的临时降级**,生产期回切。ADR-001 当前状态调整为"已采纳但**暂未启用**"
