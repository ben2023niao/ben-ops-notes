---
id: "doc-05fe782feb76"
title: "albwhite 反复丢失根因与只读挂载永久修复"
date: "2026-10-21T12:40:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "自动化", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-1240-%E3%80%90%E4%BA%8B%E6%95%85%E5%A4%8D%E7%9B%98%E3%80%91alb_white%E5%8F%8D%E5%A4%8D%E4%B8%A2%E5%A4%B1%E6%A0%B9%E5%9B%A0%E4%B8%8E%E5%8F%AA%E8%AF%BB%E6%8C%82%E8%BD%BD%E6%B0%B8%E4%B9%85%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-1240-【事故复盘】alb_white反复丢失根因与只读挂载永久修复.md"
sourceSha256: "64fb9191378f9a829978b3f2f2c4b1c7073beb325d59818d9cc316fe8efe2ec2"
sourceSystem: "project-doc"
---

# albwhite 反复丢失根因与只读挂载永久修复

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-1240-【事故复盘】alb_white反复丢失根因与只读挂载永久修复.md`

> 整理日期：2026-10-21 12:40｜日期依据：文件名日期

## 一、现象

正式环境新上线的约 6～7 个游戏、测试环境若干游戏再次出现游戏配置丢失。

现场数据：

- 配置仓库正式版白名单：54 个有效行
- 配置仓库测试版白名单：84 个有效行
- 正式 web/cron 容器：均回退到镜像内旧版 37 行
- 测试 web/cron 容器：均回退到镜像内旧版 37 行
- 配置仓库源文件本身没有丢失，SHA256 正常

因此新平台域名和平台私钥不在正在运行的容器里，游戏回调再次被拒。

## 二、为什么反复出现

原流程不是挂载配置，而是：

1. 配置发布时把配置仓库文件同步到宿主机；
2. 发布脚本再通过 `docker cp` 临时复制进 web/cron；
3. 镜像和业务代码目录里仍带着旧版 37 行 `alb_white.txt`；
4. 只要容器被 compose 重建，`docker cp` 写入的副本就会消失，恢复成镜像旧文件。

任何一条重建路径都会触发：

- 正常发版重建 web/cron；
- `docker compose up --force-recreate`；
- 队列守护自动重建 cron；
- 数据库或容量问题处置时单独重建 web；
- 手工 compose 重建。

## 三、本次确定的触发证据

### 3.1 正式环境

队列守护日志：

```text
2026-10-21T10:40:01+0800 missing workers=['job:queue'] -> healing（重建 cron 容器）
2026-10-21T10:40:12+0800 docker compose up cron ...
2026-10-21T10:40:29+0800 已自动重建并恢复
```

重建后：

- `youdianse-main-php-cron` 启动时间更新为 `10:40`
- cron 内 `alb_white.txt` 从 54 行变回 37 行
- 正式 web 也在后续 compose 重建中回退到 37 行

### 3.2 测试环境

队列守护日志：

```text
2026-10-21T00:50:02+0000 missing workers=['job:queue'] -> healing（重建 cron 容器）
2026-10-21T00:50:19+0000 已自动重建并恢复
```

重建后：

- `youdianse-dev-php-cron` 启动时间更新
- cron 内白名单回退到 37 行
- dev web 也在 compose 重建时回退到 37 行

结论：队列守护本身没有删配置，它只是重建了 cron；真正的问题是配置采用
`docker cp` 临时注入，任何容器重建都会丢掉。

## 四、已执行的永久修复

### 4.1 白名单和平台私钥改为只读 bind mount

web、cron 均增加：

```yaml
- ./cicd-web/runtime/app-local-files/alb_white.txt:/var/www/html/youdianse-php/alb_white.txt:ro
- ./cicd-web/runtime/app-local-files/alb_white_secret.txt:/var/www/html/youdianse-php/alb_white_secret.txt:ro
```

容器重建后直接看到宿主机配置仓库同步结果，不再依赖 `docker cp`。

### 4.2 配置同步改为原地更新

单文件 bind mount 绑定 inode。如果配置同步继续使用“临时文件 + replace”，
容器会继续看到旧 inode。

因此配置仓库同步改为：

- 原地写目标文件；
- `fsync` 落盘；
- 保持 inode 不变；
- 权限设置为 `0640`；
- 文件组设置为容器 `www-data` GID `33`。

### 4.3 CICD 自动识别挂载

发布和配置同步时，CICD 会检查容器目标路径是否已经是挂载：

- 已挂载：跳过 `docker cp`，只做一致性校验；
- 未挂载：保留旧 `docker cp` 兼容路径。

### 4.4 权限

宿主机源文件：

```text
0640 root:33
```

容器内为只读挂载，业务进程可读但不可修改。

## 五、验证结果

### 5.1 正式环境

- web：`alb_white.txt` 54 行，`alb_white_secret.txt` 42 行
- cron：`alb_white.txt` 54 行，`alb_white_secret.txt` 42 行
- 两个路径均显示 `rw=false`
- 配置仓库再次同步后 inode 不变
- 容器内 SHA256 与宿主机源文件一致
- `check-app-local`：PASS

### 5.2 测试环境

- web：`alb_white.txt` 84 行，`alb_white_secret.txt` 46 行
- cron：`alb_white.txt` 84 行，`alb_white_secret.txt` 46 行
- 两个路径均显示 `rw=false`
- 配置仓库再次同步后 inode 不变
- 容器内 SHA256 与宿主机源文件一致
- CICD 页面：200

### 5.3 重建验证

正式与测试均对 web/cron 执行过 `docker compose up --force-recreate --no-build`：

- 容器重建后白名单行数保持不变；
- 配置同步再次执行后容器内容保持不变；
- 不再回退到镜像里的 37 行。

## 六、彻底防复发的原则

1. 配置仓库是白名单和平台私钥的唯一真值。
2. 容器不再保存可变的配置副本，只读挂载配置仓库同步结果。
3. 任何 compose 重建、队列自愈、发版都不能改变白名单内容。
4. 配置更新必须原地写文件，不能 replace inode。
5. 发布前后必须校验宿主机与 web/cron 内 SHA256 一致。
6. 业务仓库中的旧 `alb_white*.txt` 仅作为镜像兼容占位，不再作为运行真值。
7. 后续新增受保护配置文件时，必须同时加入 compose 只读挂载和校验清单。
