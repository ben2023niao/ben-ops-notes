---
id: "doc-e8fb240fd737"
title: "【问题排查】albwhite.txt / albwhitesecret.txt 缺失导致新游戏回调被拒（线上 + 测试环境已修复）"
date: "2026-10-18T15:15:00"
categories: ["安全与堡垒机", "访问控制"]
tags: ["安全与堡垒机", "访问控制", "Docker", "PHP", "权限管理", "备份恢复", "监控告警", "日志分析"]
source: "03-安全运营与应急/03-安全配置与访问控制/游点涩-网关与白名单/2026-10-18-1515-【问题排查】alb_white 白名单缺失导致游戏回调被拒（线上+测试环境已修复）.md"
---

# 【问题排查】albwhite.txt / albwhitesecret.txt 缺失导致新游戏回调被拒（线上 + 测试环境已修复）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610181515-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%2BDocker%2BPHP-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91albwhite.txt%20-%20albwhitesecret.txt%20%E7%BC%BA%E5%A4%B1%E5%AF%BC%E8%87%B4%E6%96%B0%E6%B8%B8%E6%88%8F%E5%9B%9E%E8%B0%83%E8%A2%AB%E6%8B%92%EF%BC%88%E7%BA%BF%E4%B8%8A.md)

> 来源：本地项目文档 `game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-18-1515-【问题排查】alb_white 白名单缺失导致游戏回调被拒（线上+测试环境已修复）.md`
> 整理：2026-11-09。仅复制到知识库，未改动原项目文件；敏感凭据已脱敏。

- 时间：2026-10-18 15:05 ~ 15:20（北京时间）
- 反馈：番子反馈「正式服 alb_white.txt / alb_white_secret.txt 最新一些游戏的游戏配置都没了」，测试环境同样问题
- 结论：**配置仓库里的文件是全的，但容器里跑的是镜像构建时 COPY 进去的旧副本**（线上 9-23 版本、测试环境同源），新平台主机不在其中 → 回调被拒

## 一、现象与证据

### 错误日志（线上 `runtime/app-logs/error-2026-10-18.log`）

```
10-18 全天（修复前）：check_host_sign_failed 约 8.9 万条
  step：decrypt_host_sign_empty 60,676 条 / host_not_in_whitelist 37,419 条
  platform TOP：xjzx 37,419、xiaochou 23,200、xmbl 15,009、slzwl 7,505

15:14 分（修复前最后一分钟）：154 条
15:15 起：0 条（已恢复）
```

典型报错（注意 `hosts_count`）：

```json
{"type":"check_host_sign_failed","step":"host_not_in_whitelist",
 "platform":"xiaochou","host":"www.dsrasfasd324gsd32fas.com","hosts_count":25}
```

而修复后容器内实际有 **34 条主机**（`grep -v '^#'` 计数）——说明运行中的 PHP 读到的仍是旧文件（25 条）。

### 三处文件版本对比（修复前）

| 环境 | 配置仓库（权威） | app 源码目录 | 容器（web/cron） |

| --- | --- | --- | --- |

| 线上 | `alb_white.txt` **69 行**（md5 17830c89） | 37 行（2f12c2e4，9-23） | 37 行（2f12c2e4） |

| 线上 | `alb_white_secret.txt` **60 行**（ee465eea） | 36 行（4e9bf4d2，6-8/9-7） | 36 行 |

| 测试 203.0.113.1 | `alb_white.txt` **81 行**（b6e416e5） | 37 行（2f12c2e4） | 37 行 |

| 测试 203.0.113.1 | `alb_white_secret.txt` **46 行**（22644a26） | 26 行（68c67118） | 26 行 |

## 二、根因

这两个文件的生命周期有三段，**只有第一段是自动的**：

```
① 配置仓库 config-main/app-local-files/*  →（配置发布 sync_config_repo）→ ② /opt/docker-youdianse-php/cicd-web/runtime/app-local-files/*（宿主机暂存）
③ 容器内 /var/www/html/youdianse-php/alb_white*.txt
```

- 第 ③ 段**不是 bind mount**（`docker inspect` 里只有 .env / php ini / 日志目录四个挂载），而是靠发布流程里的 `docker cp` 写入。
- 镜像本身 `COPY ${APP_SOURCE_DIR}/` 会把 **app 源码目录里的旧副本**打进镜像；容器重建后先是旧文件，只有发布流程执行到 `docker cp` 才会被覆盖成新文件。
- 本次线上容器是 10-17 03:00 由 `main-e5c9883a200a` 重建的，重建后拿到的就是 app 源码目录里 **9-23 的 37 行版本**，之后没有再把配置仓库那份 cp 进去 → 新增平台全部缺失。
- 另外 `cicd-web/core.py:backup_existing_protected_app_local_files()` 的判断是「app 源码目录里的文件与暂存不同 → 视为 dirty → 用 app 源码覆盖暂存」，所以**源码目录里的旧副本会反向污染配置**，必须保持两者一致。

## 三、处置（已完成，线上 + 测试）

1. 以配置仓库为准，写回 app 源码目录（保证后续构建/发布不会再用旧副本）
2. 用 `docker cp` 写入运行中的 web + cron 容器（立即生效，无需重启）
3. 修权限 `root:www-data 0640`（PHP-FPM 以 www-data 运行）
4. 三方一致性校验

### 修复结果

| 环境 | alb_white.txt | alb_white_secret.txt | 校验 |

| --- | --- | --- | --- |

| 线上 | 69 行（17830c89） | 60 行（ee465eea） | 配置仓库 = 源目录 = web = cron ✅ |

| 测试 | 81 行（b6e416e5） | 46 行（22646a26） | 配置仓库 = 源目录 = web = cron ✅ |

### 恢复的平台（线上，`alb_white.txt` 段头差异）

```
小丑、开炮 线上测试服、开炮 线上生产服、时空之契、星姬调教工坊、星梦伴侣 Ai、
桃色西遊、深蓝终末录、绯色魂环、艳姬征服、血姬战线
```

### 效果

- 线上：`check_host_sign_failed` 15:14 的 154 条/分 → **15:15 起 0 条**
- 测试：最后一 条 15:13:56，之后无新增

## 四、防复发

1. **发布流程**：发布/配置同步后必须把 `app-local-files` 里的受保护文件 `docker cp` 进容器（当前缺这一步），或在容器重建后补跑一次。
2. **一致性巡检**：新增脚本 `ops/production/scripts/check-app-local-files.sh`，发布前后各跑一次：

```bash
sudo bash ops/production/scripts/check-app-local-files.sh     # 0=三处一致；1=不一致并给出修复命令
```

3. **源码目录不要手改**这两个文件：以配置仓库为唯一来源；源码目录由脚本同步，避免反向污染暂存。
4. **可选的彻底方案**：把 `app-local-files` 目录整体挂载进容器（注意不能单文件 bind mount——配置同步用 rename 原子写，会导致容器看到旧 inode），或让应用从固定路径读取挂载目录。

---

## 五、彻底修复：把检查做进 CICD 发布（2026-10-18 15:20 已上线）

### 5.1 定位到的真正污染点

翻 CICD 代码发现发布流程里有一个反向覆盖：

```python
# cicd-web/core.py  backup_existing_protected_app_local_files()
if name in dirty_names:
    shutil.copy2(app_source, local_source)   # ← 用「业务源码目录」的旧副本覆盖「服务器本地源」
```

而「服务器本地源」正是配置仓库同步出来的权威副本。也就是说：只要业务源码目录里的 `alb_white.txt` 是旧的且被判定为 dirty，发布就会把权威副本改成旧的，随后 `docker cp` 进容器的自然是旧白名单。

同时还有个隐藏 bug：`git_status_path()` 用固定偏移 `line[3:]` 解析 `git status --porcelain` 输出，而 `run_cmd` 会 strip 掉行首空格 → **dirty 永远检测为空**，逻辑时灵时不灵。

### 5.2 三层修复（均已上线）

**第 1 层：阻断污染源**

- `git_status_path()` 改为正则剥离状态位，脏文件检测恢复正常
- `backup_existing_protected_app_local_files()`：本地源（配置仓库）为唯一权威
  - 业务目录与本地源不一致时：把业务目录版本**留档**到 `cicd-web/runtime/app-local-file-backups/<name>.appdir-dirty.<时间戳>`，并打印 `WARN`
  - 然后用本地源覆盖业务目录（保证后续 `git checkout` 前后内容一致）
  - **不再**把业务目录版本回写本地源

**第 2 层：发布后强制校验（不一致即判发布失败）**

- 新增 `verify_protected_app_local_files_in_containers()`：对每个受保护文件计算源文件 `sha256`，再 `docker exec sha256sum` 取容器内值比对
- 接入两处：`run_deploy()`（正常发布，`up_services` 之后）与 `sync_runtime_config_no_build()`（运行配置同步，force-recreate 之后）
- 不一致 → 抛 `DeployError`，发布状态不会再显示 SUCCESS

**第 3 层：可巡检**

- 新增 CLI：`cicd-web.py check-app-local` → 输出 `本地配置文件校验：PASS / FAIL`，退出码 0/1
- 同一份逻辑也可用于 cron 巡检（监控机定时跑即可）

### 5.3 实测记录（线上）

```
# 只读校验
$ python3 cicd-web.py check-app-local
本地配置文件校验通过：youdianse-main-php-web / alb_white.txt（d17081a1fd96）
本地配置文件校验通过：youdianse-main-php-cron / alb_white.txt（d17081a1fd96）
本地配置文件校验通过：youdianse-main-php-web / alb_white_secret.txt（9121f8801afe）
本地配置文件校验通过：youdianse-main-php-cron / alb_white_secret.txt（9121f8801afe）
本地配置文件校验：PASS

# 污染防护验证（故意往业务源码目录追加一行）
dirty = ['alb_white.txt']
WARN 业务目录中的 alb_white.txt 与服务器本地源不一致；已留档 alb_white.txt.appdir-dirty.20261018-152053，以服务器本地源（配置仓库）为准，不再回写本地源
→ 权威副本 md5 保持不变（17830c89），业务目录已按权威副本恢复
```

### 5.4 部署与回滚

```bash
# 已执行
sudo cp -a /opt/docker-youdianse-php/cicd-web/core.py /opt/docker-youdianse-php/cicd-web/core.py.bak.20261018-151954-applocal
sudo cp -a /opt/docker-youdianse-php/cicd-web/cli.py  /opt/docker-youdianse-php/cicd-web/cli.py.bak.20261018-151954-applocal
# 替换 core.py / cli.py 后
sudo systemctl restart cicd-web.service

# 回滚
sudo cp -a /opt/docker-youdianse-php/cicd-web/core.py.bak.20261018-151954-applocal /opt/docker-youdianse-php/cicd-web/core.py
sudo cp -a /opt/docker-youdianse-php/cicd-web/cli.py.bak.20261018-151954-applocal  /opt/docker-youdianse-php/cicd-web/cli.py
sudo systemctl restart cicd-web.service
```

### 5.5 仍然建议（长期，需应用配合）

把 `app-local-files` **目录**挂载进容器（例如 `/var/www/html/youdianse-php/config-data`），应用改为从该目录读取，镜像内用软链指向；这样连 `docker cp` 都不再需要，重建容器也不会丢。注意不要做单文件 bind mount（配置同步用 rename 原子写，容器会一直看到旧 inode）。
