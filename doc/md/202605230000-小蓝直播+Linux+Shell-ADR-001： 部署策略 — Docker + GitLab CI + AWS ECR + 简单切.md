---
id: "doc-10e9797e7cf7"
title: "ADR-001： 部署策略 — Docker + GitLab CI + AWS ECR + 简单切"
date: "2026-05-23T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Python", "Go", "Docker", "Kubernetes", "Nginx"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-001-deployment-strategy.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-001-deployment-strategy.md"
sourceSha256: "25f6baca7be76899d6262b789cf5da4e6d54231bc0accd4cf20303c93d1fed55"
sourceSystem: "project-doc"
---

# ADR-001： 部署策略 — Docker + GitLab CI + AWS ECR + 简单切

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-001-deployment-strategy.md`

> 整理日期：2026-05-23 00:00｜日期依据：正文日期

| 状态 | 已采纳 |
|---|---|
| 日期 | 2026-05-23 |
| Owner | 后端 / 运维 |
| 影响范围 | services/go-app（api + admin）、apps/admin（前端 dist）、CI/CD、生产部署 |
| 相关需求 | OPS-001 部署架构、OPS-002 滚动发布、OPS-003 回滚机制 |
| 关联文档 | [`docs/operations/build-vs-runtime-boundary.md`](../operations/build-vs-runtime-boundary.md) |

## 1. 背景

v1 上线需要确定部署架构。当前条件：
- 两台 EC2 ECS（同 region：ap-southeast-1）
- AWS S3 (ap-southeast-1) + CloudFront 已就位
- 数据库走 RDS MySQL 8.0（高可用版）
- Redis 走云托管
- 框架已激活（`.ai-framework` submodule + 17 个 validator）

参考过的三个备选：
- **A. rsync 二进制**：直接把 `bin/api` `bin/admin` rsync 到目标机
- **B. Docker + 镜像仓库**：本地/CI build → 推 ECR → 目标机 pull restart
- **C. k8s / EKS**：完整容器编排平台

## 2. 决定

**采用方案 B：Docker + GitLab CI + AWS ECR + 简单切**。

具体决策点：

| # | 决策点 | 选择 | 备注 |
|---|---|---|---|
| 1 | CI 平台 | **GitLab CI**（自建 GitLab） | git remote `3-1-159-178.nip.io` |
| 2 | 镜像仓库 | **AWS ECR (ap-southeast-1)** | 与 EC2 同 region，内网拉取秒级；与 S3 同账号便于 IAM |
| 3 | CPU 架构 | **arm64 (Graviton)** | 价比 x86 高 20-30%；所有依赖（gin/gorm/redis-go/aws-sdk-go-v2/gorilla-websocket）原生支持 |
| 4 | 镜像 tag 策略 | **双 tag**：`latest` + `<git-commit-sha>` | latest 用于自动 deploy；commit-sha 用于精确回滚 + 审计 |
| 5 | Migration 时机 | **Docker entrypoint 启动时跑**（带 MySQL `GET_LOCK` 互斥防并发）+ **生产首次手动跑** | 防止两机并发 migrate；生产首跑由运维手动 `make migrate-up` 走一遍 |
| 6 | 配置注入 | **环境变量**（systemd EnvironmentFile + docker `--env-file`） | 不打入镜像；JWT / DB / Redis / S3 全部 env；S3 进一步走 IAM Role |
| 7 | 健康检查 | **HTTP `/healthz`** | docker HEALTHCHECK + nginx upstream 检查 |
| 8 | 部署策略 | **简单切**（一台一台 stop → pull → run → 等 healthy）| v1 两台机够用；不上 ALB 滚动；nginx 检测 backend 失败自动剔除 |

## 3. 方案细节

### 3.1 镜像设计

四个 Go 镜像/二进制（独立 deploy）：

| 镜像 | 来源 | 端口 | 用途 |
|---|---|---|---|
| `kickoff-api` | `services/go-app/cmd/api` | 8080 | C 端 Public REST API |
| `kickoff-admin` | `services/go-app/cmd/admin` | 8081 | 运营后台 API |
| `kickoff-ws` | `services/go-app/cmd/ws` | 8082 | C 端 / 主播端 WebSocket |
| `kickoff-worker` | `services/go-app/cmd/worker` | 8083 | 后台任务 + worker health |

前端 `apps/admin/dist/` 通过 nginx 直接 serve 静态文件，**不进 Docker**。

ECR 仓库：
```
12345.dkr.ecr.ap-southeast-1.amazonaws.com/kickoff-api
12345.dkr.ecr.ap-southeast-1.amazonaws.com/kickoff-admin
12345.dkr.ecr.ap-southeast-1.amazonaws.com/kickoff-ws
12345.dkr.ecr.ap-southeast-1.amazonaws.com/kickoff-worker
```

每次 push tag：
- `:latest`（最新主分支）
- `:sha-<commit_sha_7位>`（不可变，回滚用）
- `:v<x.y.z>`（人工打 release tag 时同步）

### 3.2 Dockerfile 多阶段构建（关键样板）

```dockerfile
# infra/deploy/Dockerfile.api
# Build (含 framework / validator / source)
FROM --platform=linux/arm64 golang:1.22-bookworm AS builder

WORKDIR /src
COPY . .

# 跑 framework validator（任一不绿 build 失败）
RUN apt-get update && apt-get install -y python3 \
 && bash .ai-framework/scripts/sync-framework.sh --apply \
 && python3 scripts/validate-prd.py \
 && python3 scripts/validate-engineering-standards.py \
 && python3 scripts/validate-capability-gates.py \
 && python3 scripts/validate-completion-claims.py

# 编译 api 二进制
WORKDIR /src/services/go-app
RUN CGO_ENABLED=0 GOOS=linux GOARCH=arm64 \
    go build -trimpath -ldflags="-s -w" -o /out/api ./cmd/api

# Runtime (最小化)
FROM --platform=linux/arm64 gcr.io/distroless/static-debian12:nonroot AS runtime

COPY --from=builder /out/api /app/api
COPY --from=builder /src/services/go-app/migrations /app/migrations
COPY --from=builder /src/infra/deploy/entrypoint.sh /app/entrypoint.sh

USER nonroot:nonroot
WORKDIR /app
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=30s --retries=3 \
  CMD ["/app/api", "healthcheck"]

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/api"]
```

注意：
- `:nonroot` 镜像跑 nonroot 用户，不能跑 shell 命令；HEALTHCHECK 用 binary 自带的 `healthcheck` subcommand
- `migrations/` 拷进来供 entrypoint 启动时跑
- 配置文件**不进镜像**，docker run 时 -e env 注入

### 3.3 Entrypoint Migration 互斥保护

`infra/deploy/entrypoint.sh`：

```bash
#!/bin/sh
set -e

# 1. 用 MySQL GET_LOCK 防两机并发 migration
# 拿不到锁等 30 秒；30 秒后假设另一机已经做完
echo "[entrypoint] acquiring migration lock..."
LOCK_RESULT=$(mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
  -BN -e "SELECT GET_LOCK('kickoff:migration', 30)")

if [ "$LOCK_RESULT" = "1" ]; then
  echo "[entrypoint] running migrations..."
  migrate -path /app/migrations -database "mysql://..." up
  mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
    -e "SELECT RELEASE_LOCK('kickoff:migration')"
  echo "[entrypoint] migrations done"
else
  echo "[entrypoint] another instance is migrating, skip"
fi

# 2. 启动应用
exec "$@"
```

**生产环境保护**：
- 首次部署时运维**手动**先 `make migrate-up` 跑一遍 baseline
- 后续 deploy 时 entrypoint 兜底；正常情况无新 migration → no-op
- 资金类破坏性 migration（如改 ledger 表结构）**必须独立 MR 走 review，不准混在业务 deploy**

### 3.4 GitLab CI 4 Stage 流水线

`.gitlab-ci.yml`：

```yaml
stages: [validate, test, build, deploy]

variables:
  AWS_REGION: ap-southeast-1
  ECR_REGISTRY: 12345.dkr.ecr.ap-southeast-1.amazonaws.com

# Stage 1: 框架自检 + lint
validate:
  stage: validate
  image: python:3.11-slim
  before_script:
    - apt-get update && apt-get install -y git curl
    - git submodule update --init --recursive
    - bash .ai-framework/scripts/sync-framework.sh --apply
  script:
    - python3 scripts/validate-prd.py
    - python3 scripts/validate-engineering-standards.py
    - python3 scripts/validate-capability-gates.py
    - python3 scripts/validate-completion-claims.py
    - python3 scripts/validate-ops-readiness.py
    - python3 scripts/validate-mr-gates.py
    - python3 scripts/validate-openapi.py
    - python3 scripts/validate-contract-testing.py

# Stage 2: 单测 + 集成测试（race detector 必开）
test:
  stage: test
  image: golang:1.22
  script:
    - cd services/go-app
    - go test -race -count=1 ./...

# Stage 3: 构建镜像 + 推 ECR
build-api:
  stage: build
  image: docker:24
  services: [docker:24-dind]
  before_script:
    - aws ecr get-login-password --region $AWS_REGION |
        docker login --username AWS --password-stdin $ECR_REGISTRY
  script:
    - SHA=$(echo $CI_COMMIT_SHA | cut -c1-7)
    - docker buildx build --platform linux/arm64
        -f infra/deploy/Dockerfile.api
        -t $ECR_REGISTRY/kickoff-api:latest
        -t $ECR_REGISTRY/kickoff-api:sha-$SHA
        --push .
  only: [main]

build-admin:
  stage: build
  # 同上，目标 Dockerfile.admin
  only: [main]

# Stage 4: 部署（手动触发，资金类项目不走全自动）
deploy-prod:
  stage: deploy
  image: alpine/curl
  script:
    # 通知 EC2 deploy webhook（或 SSH + docker pull）
    - ssh ec2-user@$PROD_HOST_1 "bash /opt/kickoff/deploy.sh kickoff-api sha-$SHA"
    - sleep 10
    - curl -sf http://$PROD_HOST_1:8080/healthz || (echo "1 号机不健康" && exit 1)
    - ssh ec2-user@$PROD_HOST_2 "bash /opt/kickoff/deploy.sh kickoff-api sha-$SHA"
    - sleep 10
    - curl -sf http://$PROD_HOST_2:8080/healthz
  when: manual
  only: [main]
  environment:
    name: production
```

### 3.5 EC2 部署脚本

`infra/deploy/deploy.sh`（部署到目标 EC2，由 CI 远程执行）：

```bash
#!/bin/bash
set -euo pipefail

IMAGE="$1"      # kickoff-api
TAG="$2"        # sha-abc1234 / latest

ECR="12345.dkr.ecr.ap-southeast-1.amazonaws.com"
FULL_IMAGE="$ECR/$IMAGE:$TAG"

# 0. 资金事务保护：检查是否有 PAYING 状态 withdraw
PAYING=$(mysql -h$DB_HOST -uop -p$DB_PASS kickoff -BN -e \
  "SELECT COUNT(*) FROM withdraw_orders WHERE status=4 AND created_at < NOW() - INTERVAL 1 MINUTE")
if [ "$PAYING" -gt 0 ]; then
  echo "WARN: $PAYING 笔 PAYING 状态出款，延迟 deploy"
  exit 2
fi

# 1. 拉镜像
aws ecr get-login-password --region ap-southeast-1 | \
  docker login --username AWS --password-stdin $ECR
docker pull $FULL_IMAGE

# 2. 旧容器优雅停（30s grace 让连接落地）
OLD=$(docker ps -q --filter "name=$IMAGE")
[ -n "$OLD" ] && docker stop --time 30 $OLD

# 3. 起新容器
docker run -d \
  --name $IMAGE-new \
  --restart unless-stopped \
  --env-file /etc/kickoff/$IMAGE.env \
  --network host \
  --health-cmd "/app/api healthcheck" \
  --health-interval 10s \
  --health-timeout 3s \
  --health-retries 3 \
  $FULL_IMAGE

# 4. 等 healthy（max 60s）
for i in $(seq 1 12); do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' $IMAGE-new)
  [ "$STATUS" = "healthy" ] && break
  sleep 5
done

if [ "$STATUS" != "healthy" ]; then
  echo "FAIL: 新容器未健康，回滚"
  docker stop $IMAGE-new && docker rm $IMAGE-new
  [ -n "$OLD" ] && docker start $OLD
  exit 1
fi

# 5. 切换：删旧容器 + 重命名新
[ -n "$OLD" ] && docker rm $OLD
docker rename $IMAGE-new $IMAGE

echo "OK: $IMAGE deployed at $TAG"
```

### 3.6 回滚（commit-sha 切回）

```bash
# infra/deploy/rollback.sh
# 用法：bash rollback.sh kickoff-api sha-abc1234
bash deploy.sh "$@"
```

回滚就是 `deploy.sh kickoff-api sha-上次的commit`，因为镜像 commit-sha tag 不可变。

## 4. 不选其他方案的理由

### 不选 A. rsync 二进制
- 编译机 / 运行机环境必须一致（glibc 版本、动态库等）
- 2 台机器 rsync 还行，3 台开始痛
- 没有镜像版本号，回滚靠 git revert + 重新 rsync
- 无 healthcheck，容易 deploy 半成品

### 不选 C. k8s / EKS
- 团队规模小（< 5 人），EKS 学习曲线 + 月费（~$73 control plane + workers）不值
- 2 台机器 + 简单切已经够用
- 真扩到 5+ 机器 + 多服务时再迁移，迁移方案：直接把 docker image push 到 EKS 即可

### 不选 ALB 滚动 / 蓝绿
- v1 阶段：两台机器，简单切 + nginx upstream 自动剔除不健康 backend 足够
- ALB target group 跨 AZ 滚动是 v2 / 流量起来再做
- 蓝绿（双机器全量切）需要 4 台机器才划算

## 5. 风险与缓解

| 风险 | 缓解 |
|---|---|
| **两机同时 migration** | entrypoint 用 MySQL GET_LOCK 互斥；生产首跑由运维手动确认 |
| **breaking migration（如删 ledger 字段）** | 不允许在 docker entrypoint 跑；必须独立 MR + DBA review + 维护窗口 |
| **新版本启动失败死循环** | `--restart unless-stopped`（不是 always）+ healthcheck 失败后保留旧容器 |
| **配置错误导致服务起不来** | env-file 缺密钥时 service 启动期 fatal，不要在运行时延迟报错 |
| **ECR 拉镜像失败** | EC2 attach 含 `AmazonEC2ContainerRegistryReadOnly` 的 IAM Role；不依赖长期 AK/SK |
| **secrets 泄露** | env-file chmod 600 + 不进 git + 不进 image；密钥进 AWS Secrets Manager（v2） |
| **资金类操作部署中断** | deploy.sh 检测 PAYING 状态延迟 deploy；建议 deploy 时段避开赛事 |
| **回滚后 schema 不兼容** | migration 严格向后兼容（addColumn 加默认值 / 不 drop 字段在 N+1 deploy 内） |

## 6. 验收标准

- [ ] CI push main → 自动 build + push ECR（约 5 分钟内）
- [ ] 手动触发 deploy-prod → 两台机器 5 分钟内完成切换
- [ ] healthcheck 失败时自动保留旧容器，不会出现"全死"
- [ ] 回滚命令 1 条：`ssh prod 'docker pull ECR/api:sha-old && deploy.sh ...'`
- [ ] 镜像大小 < 50 MB（distroless + arm64 static binary）
- [ ] 镜像内**无 framework / source / docs**（grep 不到）
- [ ] EC2 attach IAM Role，不再持有 AWS AK/SK

## 7. 后续工作

- [ ] 写 `infra/deploy/Dockerfile.api` + `Dockerfile.admin`
- [ ] 写 `infra/deploy/entrypoint.sh` + `deploy.sh` + `rollback.sh`
- [ ] 写 `.gitlab-ci.yml`（覆盖现有占位）
- [ ] 给 go-app 加 `cmd/api healthcheck` 子命令
- [ ] 文档化：`docs/operations/deployment-strategy.md` 升级为本 ADR 的实操 runbook
- [ ] EC2 IAM Role 创建（ECR 拉取 + S3 / CloudFront 访问）

## 8. 复盘节点

- 首次生产 deploy 后 1 周复盘 deploy 体验、回滚演练结果
- 流量起来 + 3 台机器后评估是否上 ALB 滚动
- 团队 > 5 人或服务 > 8 个时评估迁移 EKS

---

**Owner 签字**：（待 review）
**Reviewers**：后端 owner、运维 owner、安全 owner
