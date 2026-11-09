---
id: "doc-5af66f9b17df"
title: "【优化】全容器文件描述符（nofile）检查与优化"
date: "2026-10-20T19:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-20-1930-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E5%85%A8%E5%AE%B9%E5%99%A8%E6%96%87%E4%BB%B6%E6%8F%8F%E8%BF%B0%E7%AC%A6%EF%BC%88nofile%EF%BC%89%E6%A3%80%E6%9F%A5%E4%B8%8E%E4%BC%98%E5%8C%96.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-20-1930-【优化】全容器文件描述符（nofile）检查与优化.md"
sourceSha256: "9aba73a4f9fb478469844b90a1bc8e60c3471c20542b254e7807758667d6003b"
sourceSystem: "project-doc"
---

# 【优化】全容器文件描述符（nofile）检查与优化

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610201930-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E5%85%A8%E5%AE%B9%E5%99%A8%E6%96%87%E4%BB%B6%E6%8F%8F%E8%BF%B0%E7%AC%A6%EF%BC%88nofile%EF%BC%89%E6%A3%80%E6%9F%A5%E4%B8%8E%E4%BC%98%E5%8C%96.md)

> 整理日期：2026-10-20 19:30｜日期依据：文件名日期

- 时间：2026-10-20 19:00 ~ 19:40（北京时间）
- 起因：参考同类项目对全部容器做 nofile 优化的做法，排查本项目是否存在 fd 上限过低或句柄泄漏
- 结论：**未发现句柄泄漏，但生产后端与监控机多个容器上限只有 1024，已全部在线提升到 65535/524288 并做永久化**

## 一、检查方法

对每台可 SSH 主机上的全部容器：

```bash
# 容器创建时的 ulimit（Docker 只在创建时生效）
docker inspect <容器> --format '{{range .HostConfig.Ulimits}}{{.Name}}={{.Soft}}:{{.Hard}}{{end}}'

# 进程实际生效的上限
awk '/Max open files/{print $4, $5}' /proc/<pid>/limits

# 当前句柄占用
ls /proc/<pid>/fd | wc -l
```

并做 **90 秒两次采样** 判断是否存在持续增长（泄漏特征）。

## 二、发现的问题与处置

### 2.1 生产后端 16.209.16.108（已修复）

| 容器 | 原上限 | 当前句柄 | 处置 |
| --- | ---: | ---: | --- |
| youdianse-main-php-web | **1024** | 374→378（35 进程） | prlimit 提升到 **65535**（60 个进程）+ compose 加 ulimits |
| youdianse-main-php-cron | **1024** | 31→31 | 同上 |
| youdianse-main-php-nginx | 16384 | 38 | 同上 |

`docker-compose.yml` 三个服务均已加入：

```yaml
ulimits:
  nofile:
    soft: 65535
    hard: 524288
```

### 2.2 监控机 52.79.252.255（已修复）

| 容器 | 原上限 | 当前句柄 | 处置 |
| --- | ---: | ---: | --- |
| php-server | **1024** | **147**（最高） | prlimit → 65535 |
| ben-bot | **1024** | 6 | prlimit → 65535 |
| telegram-relay | **1024** | 16 | prlimit → 65535 |
| update_php_webhook | **1024** | 4 | prlimit → 65535 |
| dns_monitor_pywebio | **1024** | 7 | prlimit → 65535 |
| beszel / beszel-agent | 524287 | 54 / 9 | 正常 |

> 这 5 个服务由各自的 compose 创建，**永久化需给对应 compose 加 ulimits 并重建**（待低峰执行）；当前已有 prlimit + 兜底 cron。

### 2.3 前端发版脚本（已修复，下次发版生效）

`remote_youdianse_h5_deploy.py`（线上 + 测试两份）里的 `docker run` 没有 `--ulimit`，已补：

```python
"--restart", "unless-stopped",
"--ulimit", "nofile=65535:524288",
```

数据库脚本已做语法检查。

### 2.4 兜底机制（已部署）

新增 `ops/production/scripts/fd-limit-guard.sh`，**后端 + 监控机** 各加 cron 每 5 分钟执行一次：

- 扫描所有属于 Docker 容器的进程
- 发现 `Max open files < 65535` 的进程就地 `prlimit` 提升
- 仅在发生变更时写 `/var/log/yds-fd-limit-guard.log`

> 为什么需要：`prlimit` 的修改在进程重启后会丢失；Docker 的 ulimit 又只能在创建容器时指定（`docker update` 改不了）。cron 兜底可以保证在下次重建容器前不会退回 1024。

## 三、未发现问题的容器（上限充足）

| 主机 | 容器 | 上限 | 当前句柄 |
| --- | --- | ---: | ---: |
| 网关 16.208.38.88 | h5 SSR | 524288 | 455→450 |
| 网关 16.208.38.88 | pc SSR | 524288 | 242→234 |
| 前端 13.208.101.121 | h5 SSR | 524288 | 33 |
| 测试后端 15.152.247.196 | web/nginx/cron/SSR | 32768~65536 | 5~33 |
| 数据库三台 | mongod（宿主机进程） | 65535 | 845 / 829 / 886 |
| 数据库三台 | beszel-agent | 65535 | 9 |
| 定时任务机 16.208.32.40 | spug / spug-db | 10032 / 32184 | 34 / 78 |
| 旧 Spug 103.207.68.124 | spug / spug-db | 10032 / 32186 | 30 / 78 |

MongoDB 三台当前句柄 800~900，上限 65535，余量充足。

## 四、代码层检查（需要开发关注）

### 4.1 统计

```
fopen     10 处
fclose     7 处
curl_init 11 处
curl_close 17 处（含 curl_multi）
proc_open / popen / fsockopen：0 处
```

### 4.2 fopen 后没有 fclose 的文件

| 文件 | 行 |
| --- | ---: |
| `app/Controller/ApiV1/UploadController.php` | 227 |
| `app/Controller/ApiV1/ToolsController.php` | 105 |
| `app/Controller/Api/UploadController.php` | 233 |
| `app/Controller/Api/ToolsController.php` | 105 |

**影响评估**：这四处都是上传接口把文件流塞给 S3 SDK，PHP 请求结束时会自动关闭句柄，**当前不构成泄漏**；但大文件上传并发高时，句柄会在请求生命周期内一直占用，建议显式 `fclose()`（或 `try/finally`）。

### 4.3 无泄漏迹象

90 秒两次采样：

| 对象 | T0 | T+90s | 判断 |
| --- | ---: | ---: | --- |
| 后端 php-web | 374 | 378 | 正常波动（worker 轮转） |
| 后端 php-cron | 31 | 31 | 稳定 |
| 网关 h5 SSR | 455 | 450 | 下降，正常 |
| 网关 pc SSR | 242 | 234 | 下降，正常 |
| 监控 php-server | 147 | 147 | 稳定 |
| ben-bot / telegram-relay | 6 / 16 | 6 / 16 | 稳定 |

## 五、待办

1. 监控机 5 个服务的 compose 增加 `ulimits` 并低峰重建（当前有 prlimit + cron 兜底）
2. 生产后端下一次发布重建容器后，compose 里的 ulimits 自动生效
3. 开发侧：4 个上传控制器补显式 `fclose()`

## 六、文件

- `ops/production/scripts/fd-limit-guard.sh`
- `docker-compose.yml`（web/nginx/cron 增加 ulimits）
- `remote_youdianse_h5_deploy.py`（线上/测试各一份，docker run 增加 --ulimit）
