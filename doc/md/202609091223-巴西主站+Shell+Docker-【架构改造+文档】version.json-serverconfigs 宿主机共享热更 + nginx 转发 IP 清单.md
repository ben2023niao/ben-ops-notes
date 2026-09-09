---
id: "doc-1698d6812079"
title: "【架构改造+文档】version.json/serverconfigs 宿主机共享热更 + nginx 转发 IP 清单"
date: "2026-09-09T12:23:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "Nginx", "自动化", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-09-1223-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%2B%E6%96%87%E6%A1%A3%E3%80%91version.json%E4%B8%8Eserver_configs%E5%AE%BF%E4%B8%BB%E6%9C%BA%E5%85%B1%E4%BA%AB%E7%83%AD%E6%9B%B4%E5%8F%8Anginx%E8%BD%AC%E5%8F%91IP%E6%B8%85%E5%8D%95%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-09-1223-【架构改造+文档】version.json与server_configs宿主机共享热更及nginx转发IP清单记录.md"
sourceSha256: "f87d7bf55293af564904ff4ec5b06a5f51133a7b98f48be9c23cc843ae2da9a9"
sourceSystem: "project-doc"
---

# 【架构改造+文档】version.json/serverconfigs 宿主机共享热更 + nginx 转发 IP 清单

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-09-1223-【架构改造+文档】version.json与server_configs宿主机共享热更及nginx转发IP清单记录.md`

> 整理日期：2026-09-09 12:23｜日期依据：文件名日期

时间：2026-09-09 12:23（Asia/Manila）
项目：DBQP / PGServer master（巴西生产后端 01 单节点运行容器）
结果：✅ 共享配置挂载落地并热更验证通过；巴西/香港 nginx 转发 IP 已整理发用户与群

## 一、目标

```text
1. server_configs、version.json 不再“只打包在 docker 镜像里”：
   所有厂家容器共享宿主机 /opt/pgserver/{server_configs,version.json}；
   后续更新只需覆盖机器上这两个文件，无需 docker cp、无需重启容器。
2. 整理巴西与香港 nginx 转发服务器内网/外网 IP，发给用户并同步群。
```

## 二、仓库代码改造

```text
1. docker/services/*/service.env（10 个含模板）：
   VOLUME_MOUNTS 统一追加
   /opt/pgserver/version.json:/app/version.json
   /opt/pgserver/server_configs:/app/server_configs。
2. .dockerignore：排除 server_configs 与 version.json，不再打进镜像。
3. Dockerfile 与 docker/Dockerfile：移除对 /app/version.json、
   /app/server_configs 的 build 期 test（share.so 校验保留）。
4. docker/scripts/hot_update_runtime_config.py：
   从“docker cp 到各容器”改为“覆盖 01/02/03 宿主机共享文件”；
   若对应容器运行则校验共享挂载内 sha，不重启、不 docker cp。
   服务名列表补 dbqp-g759-release / dbqp-tada-ws2-release。
5. ben-bot 同步维护 run.py 文案同步为宿主机共享文件热更。
```

## 三、线上迁移（后端 01 现有 8 容器一次性重建）

```text
当前仅后端 01 运行 8 个厂家容器：
  pg / tada(HTTP+WS2) / pp / popok(ppk) / playson / panda / g759 /
  platform-api。

过程：
1. 先按旧容器重建（第一次脚本漏带顶层 Mounts，已修正）。
2. 最终按“原日志/结果集绑定 + 新增两个共享文件挂载”重建 8 个容器：
   docker inspect 备份：后端01 /root/dbqp-mount-migration-backup-20260909/*.json。
3. 容器内文件与宿主机一致：
   version.json=c0d5e53f…，server_configs=cb6408ca…，全部 8/8 匹配；
   RestartCount=0；结果集挂载可见（pg 159 / pp 130 / tada 175 / panda 51 /
   g759 48），日志无 DB/结果集错误。
```

## 四、热更验证（不重启）

```text
使用新版 hot_update_runtime_config.py 对 version.json + server_configs 执行
正式热更（内容与线上一致，仅验证链路）：
- host 文件 mtime = 容器内 mtime（2026-09-09 04:22:03Z），说明 bind mount 即时生效；
- 三台宿主机 sha 全部一致；
- 后端 01 8 个运行容器 shared_mount_ok，RestartCount 全部 0；
- 容器 StartedAt 早于热更时间，确认未重启。
```

## 五、巴西/香港 nginx 转发服务器 IP 清单

```text
巴西：
  宝塔 nginx（域名/管理）
    hostname：dbqp-saopaulo-game-results-data-bt
    内网：203.0.113.1
    外网：35.247.205.6
    说明：2026-09-01 切流后非主流量入口，仍为域名/Nginx 管理源站。
  备用 nginx（当前主流量入口）
    hostname：dbqp-saopaulo-nginx-standby-01
    内网：203.0.113.1
    外网：34.151.249.53

香港：
  香港入口 nginx
    hostname：dbqp-hongkong-game-results-data-bt
    内网：203.0.113.1
    外网：34.92.13.108

以上 hostname 与内网 IP 已于 2026-09-09 实时核验；外网 IP 与
线上服务器信息/README.md、servers.json 一致。
```

## 六、回滚/后续

```text
回滚：
  后端 01 容器重建前 inspect 保留在
  /root/dbqp-mount-migration-backup-20260909/；
  旧热更机制可从 Git 历史恢复 hot_update_runtime_config.py。
后续：
  1) 本地提交尚未 Push；后端 /opt/pgserver 与 /workspace/pgserver 需要在本
     提交推送后同步 master，使下一次发布按新 service.env/Dockerfile 落地；
  2) 下次正式重打镜像时 .dockerignore/Dockerfile 生效，镜像不再包含这两个文件；
  3) 02/03 暂无容器，宿主机共享文件已同步；后续在这些机器启动容器时服务.env
     会挂载同一宿主机文件。
```

## 七、群通知回执

```text
5331 任务开始
5332 代码改造完成+迁移开始
5333 迁移修正（补回原挂载）
5334 热更验证开始
5335 热更验证完成 + nginx IP 清单
5336 汇总与文档
5337 本地提交结果
```
