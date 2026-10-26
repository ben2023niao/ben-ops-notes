---
id: "doc-4501de71fc2a"
title: "aicontext 目录 AI 接手维护 Prompt"
date: "2026-10-27T22:54:14+08:00"
dateSource: "文件创建/修改时间"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "自动化", "CDN", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/ai_context/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/ai_context/doc/prompt.md"
sourceSha256: "d5e704803bb73e529e2aba2c20b4db76bb46d6a44c2e8532378717597cde127e"
sourceSystem: "project-doc"
---

# aicontext 目录 AI 接手维护 Prompt

> 来源文件：`~/Desktop/18game_devops/devops/ai_context/doc/prompt.md`

> 整理日期：2026-10-27 22:54｜日期依据：文件创建/修改时间

你正在接手 `devops/ai_context` 目录。这个目录不是业务代码目录，而是给 AI、运维同事和后续接手者使用的服务器上下文索引。处理服务器、机器人部署、H5 发布、后台配置查看、日志排查和回滚前，应优先读取这里，避免靠猜测连接服务器或误操作环境。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- Python 项目总索引：`devops/python/doc/prompt.md`
- ben-bot 机器人：`devops/python/ben-bot/doc/prompt.md`
- 运维导航站：`devops/work.youdianse.com/doc/prompt.md`
- 周报生成：`work-运维部工作进度-周报/doc/prompt.md`

当任务涉及服务器登录、容器重启、机器人部署、H5 发版、配置查看或线上路径确认时，本目录是上游事实来源；其他项目 prompt 应引用这里，而不是重复维护服务器信息。

## 1. 目录定位

- 目录路径：`devops/ai_context`
- 主要作用：记录服务器用途、登录用户、关键路径、容器、脚本目录、服务路由和注意事项
- 维护对象：AI 运维上下文，不是运行时代码
- 重要文件：
  - `README.md`
  - `servers.yml`
  - `youdianse_h5_s3_rollout.md`
  - `doc/prompt.md`

## 2. 文件说明

### `README.md`

这是本目录的入口说明，告诉接手者：

- 先读 `servers.yml`
- 再读对应脚本目录
- 不确定时先做只读检查
- 不要把密码、token、AWS Key、私钥内容写进这个目录

### `servers.yml`

这是最重要的机器上下文文件。里面按服务器记录：

- `id`
- 公网 IP
- 主机名
- 服务器用途
- 登录用户
- 认证方式说明
- 关键路径
- 容器名
- 常用只读检查命令
- 发布和重启注意事项
- 关联仓库路径

它还包含 `service_routes`，用于快速判断某个服务应该去哪台服务器、哪个脚本目录处理。

### `youdianse_h5_s3_rollout.md`

记录游点涩 H5 静态资源 S3/CDN 发布策略，包括：

- 测试环境策略
- 线上环境策略
- S3/CDN 同步规则
- 回滚点
- 不同环境不能共用 `aws s3 sync --delete` 目录的风险

## 3. 安全规则

本目录可以记录：

- 登录用户名
- 服务器用途
- 公网 IP
- 主机名
- 容器名
- 配置文件路径
- SSH key 文件路径
- 环境变量名
- 只读检查命令

本目录绝不能记录：

- 密码明文
- token 明文
- AWS Access Key 明文
- AWS Secret 明文
- SSH 私钥内容
- `.env` 原文
- 数据库连接串原文
- 生产配置原文

如果用户给了敏感值：

1. 不要写入 `ai_context`。
2. 只写“通过安全渠道配置”或“写入服务器 `.env`”。
3. 如需记录，记录环境变量名和用途，不记录值。

## 4. 当前重点服务

当前 `servers.yml` 里重点包括：

- `ben-bot-deploy`：Telegram `ben-bot` 机器人部署机
- `youdianse-h5-test-baota`：测试环境游点涩 H5 宝塔发布目标
- `youdianse-backend-test`：测试环境后台容器配置查看目标
- `youdianse-h5-prod`：线上环境游点涩 H5 发布目标
- `youdianse-backend-prod`：线上环境后台容器配置查看目标
- `openclaw-new`：OpenClaw 新服务器
- `openclaw-old`：OpenClaw 老服务器，已关机或下线

处理请求前，先确认用户说的是：

- H5 测试发布
- H5 线上发布
- 后台测试配置查看
- 后台线上配置查看
- 机器人部署
- OpenClaw 服务器
- S3/CDN 发布或回滚

## 5. 常用读取顺序

如果用户要求处理服务器或部署问题：

1. 读 `devops/ai_context/README.md`
2. 读 `devops/ai_context/servers.yml`
3. 根据 `service_routes` 找对应脚本目录
4. 读脚本目录里的 README、配置、入口文件
5. 先跑只读检查
6. 确认目标环境后再修改或部署

只读检查示例：

```bash
hostname
pwd
docker ps
git status --short --branch
docker logs --tail 120 <container>
```

## 6. 更新 `servers.yml` 的规范

新增服务器时，建议使用这个结构：

```yaml
- id: "service-env-purpose"
  public_ip: "x.x.x.x"
  hostname_verified: "hostname"
  primary_role: "服务器用途"
  status: "active"
  login:
    user: "ubuntu"
    auth: "ssh_key"
    credential_note: "密钥或密码只走安全渠道，不写入 Git。"
  important_paths:
    repo_root: "/path/to/repo"
  containers:
    - name: "container-name"
      purpose: "容器用途"
  related_repo_paths:
    script_dir: "devops/..."
  common_checks:
    - "hostname && pwd"
```

状态字段建议：

- `active`
- `active_unverified_this_turn`
- `shutdown_or_decommissioned`
- `unknown`

## 7. 常见维护场景

### 机器人部署机变更

需要同步：

- `servers.yml` 的 `ben-bot-deploy`
- `service_routes.ben_bot`
- 机器人部署文档
- 相关脚本中 SSH 目标

### H5 目录迁移

之前 H5 发版脚本目录从 `前端发布/...` 上移到 `data/scripts` 根目录。以后再迁移路径时，必须同步：

- `servers.yml`
- `devops/python/ben-bot/data/scripts/脱敏配置查看/.shared/sanitized_env_viewer.py`
- `ben-bot` 的 README / doc prompt
- 任何 `/script` 示例命令

### 新增配置查看目标

需要记录：

- 服务器 IP
- 用户
- sudo docker 是否需要
- 容器名
- 容器内 `.env` 路径
- 对应机器人脚本目录
- 凭证环境变量名

不要记录 `.env` 内容。

### S3/CDN 发布策略变化

需要同步：

- `youdianse_h5_s3_rollout.md`
- `servers.yml` 里的 `aws_static_split_policy`
- ben-bot H5 发布脚本配置
- 回滚点说明

## 8. 验证清单

改完本目录后至少检查：

```bash
python3 - <<'PY'
import yaml
with open('devops/ai_context/servers.yml', encoding='utf-8') as f:
    data = yaml.safe_load(f)
print('servers:', len(data.get('servers', [])))
print('routes:', sorted(data.get('service_routes', {}).keys()))
PY
```

如果本机没有 PyYAML，可只做文本检查：

```bash
rg -n "password|token|secret|BEGIN .*PRIVATE KEY|AKIA" devops/ai_context
```

确保没有密钥明文。

## 9. AI 接手原则

- 以 `servers.yml` 为事实入口，但不要盲信过期状态。
- 连接服务器前先做只读检查。
- 修改生产配置前必须确认目标服务器和环境。
- 发现文档与实际不一致时，修代码或服务器问题后要回写文档。
- 如果用户要求“记一下”，只记录路径、变量名、用途，不记录敏感值。
