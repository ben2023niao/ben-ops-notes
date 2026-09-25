---
id: "doc-76f1944d680e"
title: "2026-09-25 香港后端 conf/domains 香港化 + 业务容器启动记录"
date: "2026-09-25T11:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Linux", "Shell", "Python", "Docker", "MySQL", "Redis", "安全运维"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-09-25-1130-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AF%E5%90%8E%E7%AB%AFconf-domains%E9%A6%99%E6%B8%AF%E5%8C%96%E4%B8%8E%E4%B8%9A%E5%8A%A1%E5%AE%B9%E5%99%A8%E5%90%AF%E5%8A%A8%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-09-25-1130-【架构改造】香港后端conf-domains香港化与业务容器启动记录.md"
sourceSha256: "536652471135358940cacfc8c21bc21f20a4970fe6a99d8c46f384c8a4c9d297"
sourceSystem: "project-doc"
---

# 2026-09-25 香港后端 conf/domains 香港化 + 业务容器启动记录

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-09-25-1130-【架构改造】香港后端conf-domains香港化与业务容器启动记录.md`

> 整理日期：2026-09-25 11:30｜日期依据：文件名日期

## 一、任务

```text
1. 把 /data/server-runtime/conf/domains 下的域名配置按香港情况改写：
   hkcloudplay06.com / hkcloudplay07.com / socket.hk-socket.com
2. 参考巴西后端 01/02 启动香港 01/02 的业务容器
3. 观察输出日志
（用户补充：香港 01/02 使用巴西 prod-03 的**公网 IP** 访问镜像仓库；本轮不通知飞机群）
```

## 二、conf/domains 香港化

### 2.1 做法

新增渲染脚本 `docker/deploy/hongkong/render_hk_domains.py`（已部署到香港机 `/opt/dbqp-scripts/`）：

```text
输入：/data/server-runtime/conf/domains（从巴西 prod-03 同步来的原版，指向 *.xqv9m8.icu 等）
输出：香港版 JSON（按用户要求**直接写回 /data/server-runtime/conf/domains**）
规则：
  static_hosts 取原前缀 -> <前缀>.hkcloudplay06.com / .07.com
  game_hosts   同样保留前缀
  api_hosts    -> socket.hk-socket.com（商户/socket 域名）
  JILI 前缀映射：tada-statics* -> jili-static*；jili-static-aws -> jili-static；jili-aws -> jili-games
  其余字段（group_name / game_ids 等）原样保留
```

执行记录（两台 prod-01 / prod-02 一致）：

```text
1) 渲染到 /data/hk-domains（10 个 json + _origin_br_domains 原始备份）
2) 备份 /data/server-runtime/conf/domains -> conf/domains.br-backup-YYYYMMDD-HHMM
3) 覆盖写入 /data/server-runtime/conf/domains/*.json，chown 1000:1000
```

### 2.2 写入结果（抽样）

| 文件 | static_hosts | game_hosts | api_hosts |
| --- | --- | --- | --- |
| `pg.json` | `pg-static.hkcloudplay06/07.com` | `pg-games.hkcloudplay06/07.com` | **socket.hk-socket.com** |
| `jili.json` | `jili-static.hkcloudplay06/07.com` | `jili-games.hkcloudplay06/07.com` | — |
| `pp.json` | `pp-static.hkcloudplay06/07.com` | `pp-games.hkcloudplay06/07.com` | — |
| `ppk/panda/playson/g759.json` | 同名前缀 | 同名前缀 | — |

（`tada.json` 的 static 前缀复用 jili-static；`fc.json`/`jdb.json` 保留渲染结果，cn 不启用。）

### 2.3 后续同步口径（用户确认）

```text
/root/hk-runtime-sync.sh 已收窄为**只同步 share.so**（prod-03 -> prod-01 -> prod-02），
不再全量同步 /data/server-runtime，避免覆盖香港本地的 conf/domains 等配置。
旧脚本已备份为 hk-runtime-sync.sh.bak-*。
```

## 三、业务容器启动（参考巴西 01/02）

新增 `docker/deploy/hongkong/start_hk_backends.py`（部署到香港机 `/opt/dbqp-scripts/`），
按 standby 入口 8 个 upstream 端口对齐，在 prod-01 / prod-02 各启动 8 个容器：

| 容器 | 端口 | 镜像 : tag | CURRENT_VENDOR / MAIN_ENTRY |
| --- | ---: | --- | --- |
| `game-service-api-prod` | 9090 | game-service-api:20260923-ben | platform-api / main.py |
| `game-service-pg-prod` | 9091 | game-service-pg:20260921-ben | pg / server.py |
| `game-service-jili-prod` | 9093 | game-service-jili:20260916-ben-cb8f2c55 | **tada / jili.py**（见踩坑） |
| `game-service-ppk-prod` | 9098 | game-service-ppk:20260916-ben-cb8f2c55 | ppk / ppk.py |
| `game-service-pp-prod` | 9099 | game-service-pp:20260923-ben | pp / pp.py |
| `game-service-panda-prod` | 9018 | game-service-panda:20260919-ben | panda / panda.py |
| `game-service-g759-prod` | 9019 | game-service-g759:20260916-ben-cb8f2c55 | g759 / g759.py |
| `game-service-playson-prod` | 9020 | game-service-playson:20260916-ben-cb8f2c55 | playson / playson.py |

统一参数（与巴西一致）：`--user appuser`、`--restart unless-stopped`、
7 个挂载（share.so / server_configs / version.json / xxxxxx.mmdb /
`/data/server-runtime/conf/domains` / game_result_datas/<vendor> / logs）、
env（PYTHONPATH / VERSION_FILE_PATH / GAME_RESULT_DATAS_PATH / GAME_DOMAINS_PATH /
SERVER_CONFIGS_PATH / CURRENT_VENDOR / MAIN_ENTRY）。
TADA（9096）与 TADA-WS（8765）不在 cn 范围，未启动。

镜像来源（按用户要求用公网 IP）：registry `34.39.180.82:5000`（巴西 prod-03 公网），
两台 daemon.json 的 `insecure-registries` 也只有该公网地址；共 8 个镜像、两台已全部拉取完成。

## 四、启动后观察结果

```text
容器状态（prod-01 / prod-02 各 8 个）：全部 running，restarts ≤ 3；
端口监听：宿主 9090/9091/9093/9098/9099/9018/9019/9020 全部 LISTEN；
standby 入口到两台后端：9090/9091 端口均可达（内网 203.0.113.1 / 203.0.113.1）。
```

日志观察（`docker logs`）：

```text
1) 正常项：各容器都完成 Sanic 启动链路 —— 配置加载成功（[pg] 配置加载成功 ...）、
   GeoIP 库 /app/config/xxxxxx.mmdb 加载、trusted_proxy 设置、
   Redis 成员变量池与 MySQL 连接池集群「成功同步预加载 / 异步预热」；
   JILI 容器日志显示 [Init] 当前服务工作目录已成功锁定为: /app/tada。
2) 噪音项：日志里有 multiprocessing resource_tracker 的
   `KeyError: '/mp-xxxx'` / ConnectionResetError，属容器内多进程清理噪音（巴西同款镜像也有）。
3) 业务可用性：通过 standby 访问 `https://socket.hk-socket.com/` 返回 404
   （platform-api 根路径的正常形态，与巴西 socket.<root> 一致）、`/healthz` 返回 200；
   但 `pg-games.hkcloudplay06.com/health` 等仍为 000/502 ——
   与用户说明的「数据库没开权限」一致，属预期，非容器/配置问题。
```

## 五、踩坑记录

```text
1) JILI 容器入口：按 vendor=jili 传 MAIN_ENTRY=jili.py 会报
   `can't open file '/app/jili/jili.py'` 并无限重启；
   该镜像代码实际在 /app/tada（复用 TADA 代码），镜像自带
   CURRENT_VENDOR=tada + MAIN_ENTRY=jili.py，结果集目录仍是 jili。
   => jili 容器必须用 CURRENT_VENDOR=tada / MAIN_ENTRY=jili.py。
2) 复制脚本内容到远端时 `<<<` 与 sshpass 组合会把文件写成 0 字节，
   改用 heredoc（`ssh 'cat > file' <<'EOS'`）或本地重定向才可靠。
3) /data/server-runtime/server_configs 是**文件**不是目录（早前按目录建导致同步失败）。
```

## 六、待办

```text
1. 数据库权限开通后复测：各厂商 HTTP（/health、业务接口）应从 000/502 恢复；
   届时用 `python3 /opt/dbqp-scripts/start_hk_backends.py --status|--logs` 复查。
2. share.so 更新流程：跑 /root/hk-runtime-sync.sh（已收窄为只同步 share.so）+ 重启容器。
3. 老入口机 34.92.13.108 的上游仍是外部双后端（老域名现网），如需收口另行授权。
```

## 七、关联

```text
docker/deploy/hongkong/render_hk_domains.py     conf/domains 香港化渲染脚本
docker/deploy/hongkong/start_hk_backends.py     香港后端容器启动/状态/日志工具
docker/doc/2026-09-25-1030-【架构改造】香港standby入口上游收口为自建后端内网IP记录.md
docker/doc/2026-09-24-1730-【架构改造】香港后端接入巴西容器仓库与容器启动测试记录.md
```
