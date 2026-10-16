---
id: "doc-6872b2f82bdc"
title: "【配置变更】修复从库未均分：env 与 hosts 把 slave1 / slave2 指向了同一台机器"
date: "2026-10-17T02:45:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "Nginx", "Redis", "自动化", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-17-0245-%E3%80%90%E9%85%8D%E7%BD%AE%E5%8F%98%E6%9B%B4%E3%80%91%E4%BF%AE%E5%A4%8D%E4%BB%8E%E5%BA%93%E6%9C%AA%E5%9D%87%E5%88%86%EF%BC%88env%20%E4%B8%8E%20hosts%20%E5%88%86%E7%A6%BB%20slave1-slave2%EF%BC%89.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-17-0245-【配置变更】修复从库未均分（env 与 hosts 分离 slave1-slave2）.md"
sourceSha256: "83f170b5f841d057e076d68f92130f2630d88b08e186196ba0e4d50b6b8479c6"
sourceSystem: "project-doc"
---

# 【配置变更】修复从库未均分：env 与 hosts 把 slave1 / slave2 指向了同一台机器

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-17-0245-【配置变更】修复从库未均分（env 与 hosts 分离 slave1-slave2）.md`

> 整理日期：2026-10-17 02:45｜日期依据：文件名日期

- 执行时间：2026-10-17 02:40 ~ 02:45（北京时间）
- 环境：游点涩线上环境（正式环境）
- 变更类型：配置变更（`.env` + `docker-compose.yml` hosts；无代码变更、无需重建容器）
- 回滚方式：见第五节（备份文件已就位）

## 一、变更原因

开发已把只读查询改成随机走 slave1 / slave2，但实测读流量 100% 落在从库01（203.0.113.1），从库02（203.0.113.1）连接数 0、完全空闲。

根因：`slave1` 与 `slave2` 两个配置段的 host **都写 `server.db2.com`**，而容器 `/etc/hosts` 又把 `server.db2.com` 同时映射到两个 IP（44.11 在前），且连接串没有 `replicaSet` 参数 → 驱动按"单机直连"处理，永远只连解析到的第一个地址。

## 二、变更内容

### 1. `env/.env.prod`（线上实际配置，位于 `/opt/docker-youdianse-php/env/.env.prod`）

```diff
 [database.mongodb.slave1]
-host    = server.db2.com
+host    = server.db2a.com
 port    = 27017
 dbname  = 18game

 [database.mongodb.slave2]
-host    = server.db2.com
+host    = server.db2b.com
 port    = 27017
 dbname  = 18game
```

### 2. `docker-compose.yml`（宿主机 `/opt/docker-youdianse-php/docker-compose.yml`，仓库同步修改）

```diff
 x-youdianse-db-hosts: &youdianse-db-hosts
   - "server.db1.com:203.0.113.1"
-  - "server.db2.com:203.0.113.1"
-  - "server.db2.com:203.0.113.1"
+  - "server.db2a.com:203.0.113.1"     # 从库01（同机运行 Redis）
+  - "server.db2b.com:203.0.113.1"    # 从库02
+  - "server.db2.com:203.0.113.1"      # 兼容旧配置：仍然指向从库01
```

说明：`server.db2.com` 保留为单条别名（指向 44.11），避免其他历史引用被破坏；重复映射已消除。

### 3. 运行中容器的 `/etc/hosts`

为避免重建容器造成流量中断，本次直接把两个新域名追加进 web / cron 容器的 `/etc/hosts`（容器重启后由 compose 的 `extra_hosts` 自动接管，两者一致）：

```
203.0.113.1  server.db2a.com
203.0.113.1 server.db2b.com
```

## 三、验证结果（变更前 → 变更后）

### 1. 连接分布（web 容器 TCP 连接）

| 节点 | 变更前 | 变更后 |
| --- | ---: | ---: |
| 203.0.113.1（从库01） | 23 | 32 |
| 203.0.113.1（从库02） | **0** | **31** |
| 203.0.113.1（主库） | 23 | 31 |

### 2. 逐节点读速率（20 秒窗口）

| 节点 | 变更前 | 变更后 |
| --- | --- | --- |
| 主库 28.142 | 出 2.5 MB/s（放大 1,047 倍） | 出 1.1 MB/s |
| 从库01 44.11 | 出 59~80 MB/s | **出 15.2 MB/s** |
| 从库02 39.177 | 出 0 MB/s（空闲） | **出 23.6 MB/s** |

从库02 已开始承接读流量，两台从库实现分流。

### 3. 稳定性

- 应用错误日志：变更后（02:35 之后）**无新增 Mongo/连接类报错**
- 后端 nginx：最后一条 `connect() failed` 停留在 02:04:30（本次变更前），变更后无新增 upstream 失败
- 后端 ens5 仍在 60 MB/s 左右：总读量不变，只是从"全压从库01"变成"两台分摊"

## 四、遗留（需要开发侧处理）

1. **主库仍有个 ~244 query/s 的重查询**：主库出流量已降到 1.1 MB/s，但它仍在做大量扫描（返回文档 667/s）。说明部分只读查询没有走 `on('slave')`，或位于写路径上，需要开 profiling 定位（指南 D1）。
2. **读放大没解决**：即使均分成功，单台从库仍在 15~24 MB/s 量级；要真正降下来仍需配置类集合缓存 + 投影（指南 B1/B3）。
3. **可选加固**：若希望具备自动故障转移，可按指南把 `replica = youdianse` 与 `readPreference=secondaryPreferred` 一起打开（两者必须同时设置，否则读会被导回主库）。

## 五、回滚

```bash
cd /opt/docker-youdianse-php
sudo cp -a env/.env.prod.bak.<时间戳>-slavefix env/.env.prod
sudo cp -a docker-compose.yml.bak.<时间戳>-slavefix docker-compose.yml
# 容器 /etc/hosts 中的两行会在容器重建时自动消失；如需立即清理可重建 web/cron
```

本次备份文件：

```
/opt/docker-youdianse-php/env/.env.prod.bak.20261017-022104-slavefix
/opt/docker-youdianse-php/docker-compose.yml.bak.20261017-022104-slavefix
```

---

## 六、已同步到仓库（防止下次「配置发布」回退）

配置发布（CICD 运行配置同步）的实际流程是：

```python
# cicd-web/config_repo.py
git -C config-repo fetch --prune origin main
git -C config-repo reset --hard origin/main      # ← 只认远程 main，本地改动会被冲掉
# 再把 config-repo/env/.env.prod 写入 /opt/docker-youdianse-php/env/.env.prod
```

也就是说，**只改宿主机上的 `.env.prod` 是不够的**——下次配置发布会按 `origin/main` 重置。本次已把改动提交并推送到两个仓库：

| 仓库 | 内容 | 提交 |
| --- | --- | --- |
| `docker-youdianse-php-config-main`（独立配置仓库，CICD 配置发布的数据源） | `env/.env.prod`：slave1 → `server.db2a.com`、slave2 → `server.db2b.com` | `fe3810b`（已 push，`2d8e9d0..fe3810b main -> main`） |
| `docker-youdianse-php`（运维仓库，容器 hosts 定义与文档） | `docker-compose.yml` 的 `x-youdianse-db-hosts`（server.db2a/db2b + 兼容别名）+ 本文档 | `18057ce`（已 push，`eaa309e..18057ce main`） |

### 验证（模拟配置发布后的结果）

```
git -C /opt/docker-youdianse-php/config-repo show origin/main:env/.env.prod 与
/opt/docker-youdianse-php/env/.env.prod                              → ✅ 完全一致

app-local-files（alb_white.txt / alb_white_secret.txt）
  配置仓库 = CICD 源目录 = 容器内                        → ✅ 三方一致（同步不会覆盖业务白名单）
```

结论：以后执行「配置发布」时，`reset --hard origin/main` 拿到的就是修复后的值，线上不会再回退成 `server.db2.com` 的老配置。
