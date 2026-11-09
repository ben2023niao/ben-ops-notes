---
id: "doc-601cd7d8d172"
title: "【配置维护】线上环境腾讯CDN ql-boss域名env新增与误删段恢复记录"
date: "2026-09-08T18:26:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-08-1826-%E3%80%90%E9%85%8D%E7%BD%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E8%85%BE%E8%AE%AFCDN%20ql-boss%E5%9F%9F%E5%90%8Denv%E6%96%B0%E5%A2%9E%E4%B8%8E%E8%AF%AF%E5%88%A0%E6%AE%B5%E6%81%A2%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-08-1826-【配置维护】线上环境腾讯CDN ql-boss域名env新增与误删段恢复记录.md"
sourceSha256: "f1864efc9bd27530bfaa6d6ca24626ed5cf1af0318d0b21974a468d8dd8e0498"
sourceSystem: "project-doc"
---

# 【配置维护】线上环境腾讯CDN ql-boss域名env新增与误删段恢复记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609081826-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BPython-%E3%80%90%E9%85%8D%E7%BD%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E8%85%BE%E8%AE%AFCDN%20ql-boss%E5%9F%9F%E5%90%8Denv%E6%96%B0%E5%A2%9E%E4%B8%8E%E8%AF%AF%E5%88%A0%E6%AE%B5%E6%81%A2%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-08 18:26｜日期依据：文件名日期

文档日期：2026-09-08 18:26
环境：游点涩线上环境（main 分支）
分类：配置维护
标签：线上环境、env、腾讯CDN、ql-boss、配置误删恢复、容器重建

## 工单

```text
平台：youdianse / 后端 / 正式环境
开发/测试：@booter23
运维：@Kermit0824 @jett_yunwei @Ben_Bird @melo_sre @Daviea2
来源：Davie 发布消息（目标业务 git id：616c296da9cde7f9fdcbb6108ea22067d376629c）
本次执行范围：仅 env 配置落版（新增两个腾讯 ql-boss CDN 域名段），
  业务代码发布不在本次范围（616c296 尚未在线上业务仓库 fetch 到，待用户确认）。
```

## 背景

```text
1. 开发要求线上 env 新增两个腾讯 CDN 段：
   [cdn.tencent.ql-prod-apk1.ql-boss.com]
   [cdn.tencent.ql-prod-apk.ql-boss.com]
2. melo 反馈 GitLab 远端 main 的 env 配置“少了两个”自己之前添加的段：
   [cdn.tencent.eepk-apking.zkifae.cn]
   [cdn.tencent.spj2-apk.showfifa.com]
3. 结论：9/8 GitLab web 编辑新增时误把两个旧段覆盖删除；
   正确落版 = 保留全部旧段 + 追加两个 ql-boss 新段。
```

## 变更内容

线上/本地运维仓库 `env/.env.prod` 最终腾讯 CDN 段集合（key 不写入本记录）：

```text
[cdn.tencent.eep-apking.zkifae.cn]     保留（原有）
[cdn.tencent.eepk-apking.zkifae.cn]    恢复（被误删）
[cdn.tencent.spj2-apk.showfifa.com]    恢复（被误删）
[cdn.tencent.ql-prod-apk1.ql-boss.com] 新增（本次工单）
[cdn.tencent.ql-prod-apk.ql-boss.com]  新增（本次工单）
```

配置格式参考测试环境 `env/.env.dev` 的腾讯 CDN 段：

```ini
[cdn.tencent.<域名>]
domain=<域名>
key=<腾讯 CDN 鉴权 key>
```

## 可手动操作运维手册

以下命令供后续人工复核/复现，均在正式后端服务器
`16.209.16.108`（`/opt/docker-youdianse-php`）执行。

### 1. 核对现状

```bash
cd /opt/docker-youdianse-php
git status --short --branch          # 线上仓库一般存在本地运行改动属正常
git log --oneline -3
sudo docker ps --filter name=youdianse-main-php --format '{{.Names}} | {{.Status}} | {{.Image}}'
```

确认目标为 main 正式环境，避免操作测试配置。

### 2. 查看 env 当前腾讯 CDN 段（不打印 key）

```bash
cd /opt/docker-youdianse-php
python3 - <<'PY'
names = [
  "[cdn.tencent.eep-apking.zkifae.cn]",
  "[cdn.tencent.eepk-apking.zkifae.cn]",
  "[cdn.tencent.spj2-apk.showfifa.com]",
  "[cdn.tencent.ql-prod-apk1.ql-boss.com]",
  "[cdn.tencent.ql-prod-apk.ql-boss.com]",
]
data = open("env/.env.prod", encoding="utf-8").read()
for n in names:
    print(n, data.count(n))
PY
```

正常结果应为每段各 `1`。

### 3. 更新 env（先备份，只追加不删除）

```bash
cd /opt/docker-youdianse-php
sudo cp -p env/.env.prod "env/.env.prod.bak.$(date +%Y%m%d_%H%M%S)"
```

在文件末尾腾讯 CDN 段区域追加以下两个段（key 从开发/测试 env 获取，
不要覆盖任何旧段，不要写进文档/群聊）：

```ini
[cdn.tencent.ql-prod-apk1.ql-boss.com]
domain=ql-prod-apk1.ql-boss.com
key=<开发提供 key>

[cdn.tencent.ql-prod-apk.ql-boss.com]
domain=ql-prod-apk.ql-boss.com
key=<开发提供 key>
```

### 4. 让线上容器重新挂载生效

```bash
cd /opt/docker-youdianse-php
sudo docker compose --env-file .ops-build.env --profile cron up -d \
  --force-recreate --no-build web nginx cron
```

说明：`env/.env.prod` 是 bind mount 进 web/cron 容器的单文件，必须重建容器
才会挂载到最新 inode；加 `--no-build` 避免误重建镜像、改变业务版本。

### 5. 验证

```bash
cd /opt/docker-youdianse-php
sudo sha256sum env/.env.prod
sudo docker exec youdianse-main-php-web sha256sum /var/www/html/youdianse-php/.env
sudo docker exec youdianse-main-php-cron sha256sum /var/www/html/youdianse-php/.env
# 三个 sha256 应一致

sudo docker ps --filter name=youdianse-main-php --format '{{.Names}} | {{.Status}} | {{.Image}}'
curl -s -o /dev/null -w 'admin=%{http_code}\n' http://203.0.113.1:8088/admin1866/login
curl -s -o /dev/null -w 'cicd=%{http_code}\n' http://203.0.113.1:18090
```

### 6. 回滚

```bash
cd /opt/docker-youdianse-php
# 选择更新前备份文件（例如 .env.prod.bak.<时间戳>），恢复后重建容器
sudo cp -p "env/.env.prod.bak.<时间戳>" env/.env.prod
sudo docker compose --env-file .ops-build.env --profile cron up -d \
  --force-recreate --no-build web nginx cron
```

## 本次执行与验证结果

```text
线上 env 备份：/opt/docker-youdianse-php/env/.env.prod.bak.20260908_182409
宿主机与容器内 .env sha256：14e0fa6fc3af7ab1d1d44bcb64f33a37b32eb1017046733bbd41bf14b3e0c1cb
宿主机/web/cron 五段计数：每段均 1（唯一、无重复）
容器状态：web/nginx/cron 全部 Up，镜像 youdianse-php:main-a321bb2457d1（未重建镜像）
健康检查：本机 admin 200 / CICD 200
本地运维仓库：已同步 origin/main 并修正 env（merge 888ae45 + env 修正待提交）
```

## 通知记录

```text
已按 AGENTS.md 逐步向 18GAME_ 上线群（正式環境）发送步骤通知：
步骤 1 仓库状态与最新提交核对
步骤 2 需求与环境配置差异分析
步骤 3 线上服务器现状只读核验
步骤 4 本地 Git 同步与 env 落版
步骤 5 线上 env 文件落版
步骤 6 线上容器配置生效（no-build 重建）
步骤 7 配置与运行最终验证
步骤 8 文档更新与汇总（本文档）
后续：汇总及文档发群 / 本地 Git 提交 / 提交结果最终总结
```

## 风险提示与遗留

```text
1. 远端 GitLab main 目前仍缺 eepk-apking / spj2-apk 两段（9/8 web 编辑误删）；
   本地已完成修正但按仓库规则仅本地 Commit、未 Push，需用户确认后再推送。
2. 业务 git id 616c296 未在本次范围发布；若后续需要发布业务代码请单独走 CICD。
3. env key 属敏感配置：不得打印、不得写入文档/工作台/Git。
4. 服务器工作区存在线上本地运行改动（env、cicd 配置等），auto-update 因 dirty
   跳过自动 pull 属预期；人工操作时避免整仓覆盖这些本地改动。
```
