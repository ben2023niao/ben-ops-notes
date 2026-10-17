---
id: "doc-238582805222"
title: "【取证】albwhite 白名单事故：登录来源与修改来源（多机日志 + 镜像取证）"
date: "2026-10-18T15:45:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Docker", "监控告警", "自动化", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-18-1545-%E3%80%90%E5%8F%96%E8%AF%81%E3%80%91alb_white%20%E4%BA%8B%E6%95%85%E7%99%BB%E5%BD%95%E4%B8%8E%E4%BF%AE%E6%94%B9%E6%9D%A5%E6%BA%90%EF%BC%88%E5%A4%9A%E6%9C%BA%E6%97%A5%E5%BF%97%2B%E9%95%9C%E5%83%8F%E5%8F%96%E8%AF%81%EF%BC%89.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-18-1545-【取证】alb_white 事故登录与修改来源（多机日志+镜像取证）.md"
sourceSha256: "53853f00d478f997ae4c72b503cccc18e159216db7045b3a2aef77867d11cc9a"
sourceSystem: "project-doc"
---

# 【取证】albwhite 白名单事故：登录来源与修改来源（多机日志 + 镜像取证）

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-18-1545-【取证】alb_white 事故登录与修改来源（多机日志+镜像取证）.md`

> 整理日期：2026-10-18 15:45｜日期依据：文件名日期

- 取证时间：2026-10-18 15:25 ~ 15:45（北京时间）
- 范围：后端 16.209.16.108、网关 16.208.38.88、监控机 52.79.252.255、定时任务机 16.208.32.40
- 数据源：各机 `sshd` 登录日志（auth.log*）、`sudo` 命令审计（auth.log 中 `COMMAND=`）、`~/.bash_history`、镜像内容、git 提交历史、CICD 产物
- 结论：**没有开发或外部人员登录线上修改白名单**；问题由「镜像烘焙了旧副本 + 容器重建后未同步权威文件」的流程缺陷造成，叠加运维手工 `docker cp` 用错了来源（源码目录旧副本）。

## 一、登录来源统计（2026-10-16 ~ 10-18）

### 1.1 后端 16.209.16.108

| 来源 IP | 次数 | 性质 |
| --- | ---: | --- |
| 52.79.252.255 | 23,591 | 我们的监控机（CC 守卫 / 巡检自动化） |
| 16.208.32.40 | 5,416 | 线上定时任务机（`ip-172-31-20-69`，跑 `docker exec … shell.php Crontab …`、`docker stats` 巡检） |
| 112.207.100.18 | 142 | 运维本机公网 IP（内部文档 2026-08-18 已记录为「本机真实公网 IP」） |
| （空/本地） | 7 | PAM 内部记录 |

### 1.2 网关 16.208.38.88

| 来源 IP | 次数 | 性质 |
| --- | ---: | --- |
| 52.79.252.255 | 44,000 | 监控机 |
| 16.209.16.108 | 670 | 后端机（自动化调用） |
| 112.207.100.18 | 37 | 运维本机 |

### 1.3 监控机 52.79.252.255

| 来源 IP | 次数 | 性质 |
| --- | ---: | --- |
| 112.207.100.18 | 171 | 运维本机 |

### 1.4 定时任务机 16.208.32.40

| 来源 IP | 次数 | 性质 |
| --- | ---: | --- |
| 112.207.100.18 | 3 | 运维本机 |

> 补充：`112.112.210.164` 只在 **10-15** 出现 8 次（事故窗口之外），与本次无关。
> **没有任何其它 IP** 出现在上述四台机器的成功登录记录里 —— 即没有开发或外部人员登录线上。
> 堡垒机：仓库里只有 `data/scripts/堡垒机/.benbot.json` 入口，没有 JumpServer 审计查询脚本或凭据；本次用各机 sshd/sudo/history 做了等价取证。如堡垒机有会话录像，建议按 `10-17 02:00~03:00` 回放复核一次。

## 二、人工操作痕迹（shell 历史）

### 2.1 root 历史（文件 mtime 2026-10-16 15:28）

```bash
sudo docker exec youdianse-main-php-web chgrp www-data /var/www/html/youdianse-php/alb_white.txt ...
sudo docker cp /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt       youdianse-main-php-cron:/var/www/html/youdianse-php/alb_white.txt
sudo docker cp /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt youdianse-main-php-cron:/var/www/html/youdianse-php/alb_white_secret.txt
```

→ **手工把「源码目录」的副本 cp 进了 cron 容器**，而源码目录那份正是 9-23 的旧版本（37 行）。这是「用错来源」的直接痕迹。

### 2.2 ubuntu 历史（文件 mtime 2026-10-17 02:33）

```bash
sudo echo "tsxy=pord****" >> alb_white_secret.txt     # 值已脱敏
cat alb_white_secret.txt
```

→ 手工往本地 `alb_white_secret.txt` 追加平台密钥（`tsxy`），属于正常补配置动作；该键目前已在配置仓库与容器中（21 个平台键）。

### 2.3 没有找到的证据

- 10-13 ~ 10-18 没有 `vi/vim/nano/tee/install/sed -i` 直接改写线上 `alb_white.txt` 的 sudo 记录（除本次修复）。
- 没有开发者账号（非 ubuntu/root）登录记录。

## 三、事故时间线（关键）

| 时间 | 事件 | 证据 |
| --- | --- | --- |
| 10-13 21:14 | 配置仓库写入最新 alb_white（69 行），CICD 同步到宿主机暂存 | `config-repo.last_ref`、文件 mtime |
| 10-16 15:28 | 运维手工 `docker cp` 源码目录旧副本 → cron 容器 | root `.bash_history` |
| **10-17 02:04:23** | **新镜像 `main-e5c9883a200a` 构建完成**（同时配置同步写入 env/白名单暂存） | `docker image inspect Created`、镜像层时间、`env/.env.prod` mtime 02:04 |
| 10-17 02:33 | 手工追加 `tsxy` 密钥 | ubuntu `.bash_history` |
| **10-17 03:00:02** | **容器重建**（Created/StartedAt） | `docker inspect` |
| 10-17 15:00 起 | 新对接游戏上线，回调 host 不在白名单 → 登录失败 | 番子反馈 + 15:xx 起 `host_not_in_whitelist` 激增 |
| 10-18 15:12~15:15 | 运维以配置仓库为准同步源目录 + web/cron 容器 | 本次处置 |
| 10-18 15:15 起 | `check_host_sign_failed` 归零 | 错误日志按分钟统计 |

## 四、决定性证据：镜像里装的就是旧白名单

```
docker run --rm --entrypoint sh youdianse-php:main-e5c9883a200a -c '...'
  alb_white.txt : 29 条主机 / 37 行   md5 2f12c2e4…（旧）
  alb_white_secret.txt : 13 条 / 36 行（旧）
```

对比权威版本：`alb_white.txt` 69 行 / 34 条主机、`secret` 60 行 / 21 个平台键。

也就是说：**只要从这个镜像重建容器，白名单就会回到 9-23 的旧版**；除非发布流程在容器起来后把配置仓库那份 `docker cp` 进去（本次没有发生）。

## 五、结论与建议

### 5.1 结论

1. **不是授权安全测试、不是开发登录改动**：四台机器近三天只有监控机、定时任务机、运维本机三类来源。
2. 直接原因是**镜像烘焙旧副本**（源码目录那份 9-23 版本被打进镜像），容器重建后没有再用配置仓库的权威文件覆盖。
3. 加重因素是**运维手工 `docker cp` 时用了源码目录（旧）而不是配置仓库（新）**。
4. 15:00 起新游戏上线才暴露，是因为新平台的 host 不在旧名单里。

### 5.2 已做的防复发

- CICD 发布流程已加**强制校验**：`sync → verify sha256`，不一致直接判发布失败（`0a6af01`）
- 新增 `cicd-web.py check-app-local`（PASS/FAIL），可挂 cron
- 新增 `ops/production/scripts/check-app-local-files.sh` 三方一致性巡检
- 修复 `git_status_path` 脏检测失效、以及「业务目录反向覆盖本地源」的逻辑

### 5.3 权限与流程建议（回应「只给研发查看权限」）

1. **研发不再给线上 SSH**：需要日志就走日志系统/机器人拉取（当前已具备 S3 归档 + 机器人取日志能力）
2. 运维侧也尽量禁止手工 `docker cp` 白名单：统一走配置仓库 + CICD
3. 白名单只允许在配置仓库改，服务器上禁止 `vi/echo >>`
4. 长期：把 `app-local-files` 目录挂载进容器（不要单文件 bind mount），彻底摆脱「镜像烘焙 + docker cp」

---

## 六、追到具体会话：是哪次登录、从哪台机器、几点做的

### 6.1 两条人工会话（都在后端 16.209.16.108 的 wtmp 里）

| 会话 | 起止（北京时间） | 来源 IP | 终端 | 与历史文件的对齐 |
| --- | --- | --- | --- | --- |
| A | 2026-10-16 15:11:44 → **15:28:53** | **16.208.32.40** | pts/0 | `/root/.bash_history` 写入时间 **2026-10-16 15:28:53**，完全一致 |
| B | 2026-10-17 01:00:05 → **02:33:03** | **16.208.32.40** | pts/0 | `/home/ubuntu/.bash_history` 写入时间 **02:33**，完全一致 |

### 6.2 会话 A 里做了什么（root 历史 1239~1252 行，按时间顺序）

```bash
mv .alb_white_secret.txt.swp /tmp          # vim 异常退出的交换文件
vim alb_white_secret.txt                   # 手工编辑
sudo cp -p /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt         …/app-local-file-backups/
sudo cp -p /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt  …/app-local-file-backups/
sudo docker cp /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt        youdianse-main-php-web:/var/www/html/youdianse-php/alb_white.txt
sudo docker cp /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt youdianse-main-php-web:/var/www/html/youdianse-php/alb_white_secret.txt
sudo docker exec youdianse-main-php-web chgrp www-data … && chmod 0640 …
sudo docker cp …/src/…/alb_white.txt        youdianse-main-php-cron:/var/www/html/youdianse-php/alb_white.txt
sudo docker cp …/src/…/alb_white_secret.txt youdianse-main-php-cron:/var/www/html/youdianse-php/alb_white_secret.txt
sudo docker exec youdianse-main-php-cron chmod 0640 …
sudo grep -q '43.198.102.162' …/src/…/alb_white.txt && echo 'alb_white host ok'
sudo grep -q '^yjzf='         …/src/…/alb_white_secret.txt && echo 'alb_white_secret host ok'
```

→ 就是这次操作把**源码目录（9-23 的旧副本）**推进了 web 与 cron 容器，属于「用错来源」。

### 6.3 会话 B 里做了什么（ubuntu 历史）

```bash
sudo echo "tsxy=pord****" >> alb_white_secret.txt   # 值已脱敏
cat alb_white_secret.txt
docker exec … find / -name "alb_white*.txt"         # 核对文件位置
docker exec … awk '$1=="slzwl" …' alb_white_secret.txt
docker exec … cat alb_white.txt / alb_white_secret.txt
```

### 6.4 来源机器 16.208.32.40 是什么

| 项目 | 值 |
| --- | --- |
| 主机名 | `ip-172-31-20-69`（AWS EC2 ap-northeast-3） |
| 角色 | 线上定时任务机（`cron.youdianse-main.xyz` 回源），同时也被当跳板使用 |
| 时区 | UTC（日志时间需 +8 换算成北京时间） |
| 近 10 天登录来源 | **112.207.100.18 × 5**（运维本机公网 IP）、16.209.16.108 × 1、16.208.32.40 × 2（自身/回环） |
| 是否会 SSH 到后端 | 有：`~/.bash_history` 里存在 `ssh root@16.209.16.108` |

### 6.5 归因链与一处审计盲区

```
运维本机 112.207.100.18  →  跳板机 16.208.32.40 (ip-172-31-20-69)  →  后端 16.209.16.108
                                                          ├─ 10-16 15:11~15:28  手工 vim + docker cp（用 src 旧副本）
                                                          └─ 10-17 01:00~02:33  追加 tsxy 密钥
```

**审计盲区**：后端 sshd 对来自 16.208.32.40 的连接统一使用同一把公钥
`SHA256:z2NQHKo2a8ujuR74v0izJHdlq/sChmvpup009nEO3vE`，而这把钥匙同时被定时任务使用（近两天 14,036 次），
因此**无法用密钥指纹区分「人工操作」与「定时任务」**。人工会话只能靠 wtmp 的交互式 TTY 记录 + history 写入时间对齐来识别。

建议：

1. 跳板机/后端为人工操作使用**独立密钥或独立账号**，与自动化密钥分离
2. 跳板机开启会话审计（堡垒机录像或 `script`/`auditd`），保留 30 天以上
3. 后端启用 `auditd` 监控 `/opt/docker-youdianse-php/{src,config-repo,cicd-web/runtime}/**/alb_white*.txt` 的写入
4. 禁止在服务器上直接 `vim` 白名单，统一走配置仓库 + CICD（发布已加强制校验）
