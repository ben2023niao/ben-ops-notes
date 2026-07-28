---
id: "doc-8a0c25cf3f2d"
title: "线上环境 albwhite 与 albwhitesecret 手动维护笔记"
date: "2026-07-29T15:10:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Docker", "Nginx", "自动化", "安全运维", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-29-1510-%E3%80%90%E6%95%B0%E6%8D%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83alb_white%E4%B8%8Ealb_white_secret%E6%89%8B%E5%8A%A8%E7%BB%B4%E6%8A%A4%E7%AC%94%E8%AE%B0.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-29-1510-【数据维护】线上环境alb_white与alb_white_secret手动维护笔记.md"
sourceSha256: "c0249774be85cf8a7d8c406a81ea8423796c6cd251ec9f6527533d2bfca3d42a"
sourceSystem: "project-doc"
---

# 线上环境 albwhite 与 albwhitesecret 手动维护笔记

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-29-1510-【数据维护】线上环境alb_white与alb_white_secret手动维护笔记.md`

> 整理日期：2026-07-29 15:10｜日期依据：文件名日期

文档日期：2026-07-29 15:10
环境：游点涩线上环境（main 分支）
分类：数据维护
标签：线上环境、后端、配置文件、alb_white、alb_white_secret、手动维护、发布保护

## 什么时候用

后端没有代码更新，只要给平台加白名单 IP 和平台私钥时，用这份笔记。

只改这两份文件：

```text
/opt/docker-youdianse-php/src/youdianse-php/alb_white.txt
/opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt
```

注意：

- `alb_white.txt` 放白名单 IP。
- `alb_white_secret.txt` 放平台私钥，不能发群、不能截图、不能提交到 Git。
- 如果后端正在发布，先等发布完成，再做最后检查。

## 本次艳姬征服已处理

已在正式环境后端完成：

- `alb_white.txt` 追加艳姬征服 IP。
- `alb_white_secret.txt` 追加 `yjzf` 平台配置，私钥值不写入文档。
- 已同步到 web/cron 容器。
- 已等后端发布完成后复核，新容器也验证通过。

备份目录：

```text
/opt/docker-youdianse-php/cicd-web/runtime/app-local-file-backups/manual-yjzf-20260729-150800
```

## 最短操作步骤

### 1. 登录后端服务器

在本地仓库根目录执行：

```bash
ssh -i id_rsa ubuntu@16.209.16.108
cd /opt/docker-youdianse-php
```

意思：进入线上后端服务器和线上运维目录。

### 2. 看一下有没有正在发布

```bash
sudo docker ps
```

看 `youdianse-main-php-web`、`youdianse-main-php-nginx`、`youdianse-main-php-cron`。

如果它们刚启动几十秒，说明可能刚发布，等 1 分钟再继续。

### 3. 先备份

```bash
TS=$(date +%Y%m%d-%H%M%S)
BACKUP=/opt/docker-youdianse-php/cicd-web/runtime/app-local-file-backups/manual-alb-white-$TS

sudo mkdir -p "$BACKUP"
sudo cp -p /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt "$BACKUP/alb_white.txt"
sudo cp -p /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt "$BACKUP/alb_white_secret.txt"

echo "$BACKUP"
```

意思：先保存旧文件。最后输出的目录就是回滚用的备份目录。

### 4. 编辑 alb_white.txt

```bash
sudo vim /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt
```

打开后按大写 `G` 跳到文件最后，再按小写 `o` 新增一行，然后追加：

```text
# ===== 艳姬征服 =====
43.198.102.162
```

保存方式：

```text
按 Esc
输入 :wq
回车
```

以后换平台，就把中文备注和 IP 换成需求单里的值。

### 5. 编辑 alb_white_secret.txt

```bash
sudo vim /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt
```

打开后按大写 `G` 跳到文件最后，再按小写 `o` 新增一行，然后追加：

```text
# ===== 艳姬征服 线上生产服 ===== 格式 平台 + 私钥
yjzf=<这里填需求单给的真实私钥>
```

保存方式：

```text
按 Esc
输入 :wq
回车
```

注意：真实私钥只能写服务器文件里，不要发群，不要写文档。

### 6. 更新发布保护备份

```bash
sudo cp -p /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt /opt/docker-youdianse-php/cicd-web/runtime/app-local-file-backups/alb_white.txt
sudo cp -p /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt /opt/docker-youdianse-php/cicd-web/runtime/app-local-file-backups/alb_white_secret.txt
```

意思：让下次后端发布也能保留最新文件。

### 7. 同步到当前运行容器

```bash
sudo docker cp /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt youdianse-main-php-web:/var/www/html/youdianse-php/alb_white.txt
sudo docker cp /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt youdianse-main-php-web:/var/www/html/youdianse-php/alb_white_secret.txt
sudo docker exec youdianse-main-php-web chgrp www-data /var/www/html/youdianse-php/alb_white.txt /var/www/html/youdianse-php/alb_white_secret.txt
sudo docker exec youdianse-main-php-web chmod 0640 /var/www/html/youdianse-php/alb_white.txt /var/www/html/youdianse-php/alb_white_secret.txt

sudo docker cp /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt youdianse-main-php-cron:/var/www/html/youdianse-php/alb_white.txt
sudo docker cp /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt youdianse-main-php-cron:/var/www/html/youdianse-php/alb_white_secret.txt
sudo docker exec youdianse-main-php-cron chgrp www-data /var/www/html/youdianse-php/alb_white.txt /var/www/html/youdianse-php/alb_white_secret.txt
sudo docker exec youdianse-main-php-cron chmod 0640 /var/www/html/youdianse-php/alb_white.txt /var/www/html/youdianse-php/alb_white_secret.txt
```

意思：把最新文件复制进正在跑的 web 和 cron 容器。不会重启容器。

### 8. 检查是否成功

检查宿主机文件：

```bash
sudo grep -q '43.198.102.162' /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt && echo 'alb_white host ok'
sudo grep -q '^yjzf=' /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt && echo 'alb_white_secret host ok'
```

检查发布保护备份：

```bash
sudo grep -q '43.198.102.162' /opt/docker-youdianse-php/cicd-web/runtime/app-local-file-backups/alb_white.txt && echo 'alb_white backup ok'
sudo grep -q '^yjzf=' /opt/docker-youdianse-php/cicd-web/runtime/app-local-file-backups/alb_white_secret.txt && echo 'alb_white_secret backup ok'
```

检查 web 容器：

```bash
sudo docker exec youdianse-main-php-web grep -q '43.198.102.162' /var/www/html/youdianse-php/alb_white.txt && echo 'web alb_white ok'
sudo docker exec youdianse-main-php-web grep -q '^yjzf=' /var/www/html/youdianse-php/alb_white_secret.txt && echo 'web alb_white_secret ok'
sudo docker exec youdianse-main-php-web stat -c '%U:%G %a %n' /var/www/html/youdianse-php/alb_white.txt /var/www/html/youdianse-php/alb_white_secret.txt
```

检查 cron 容器：

```bash
sudo docker exec youdianse-main-php-cron grep -q '43.198.102.162' /var/www/html/youdianse-php/alb_white.txt && echo 'cron alb_white ok'
sudo docker exec youdianse-main-php-cron grep -q '^yjzf=' /var/www/html/youdianse-php/alb_white_secret.txt && echo 'cron alb_white_secret ok'
sudo docker exec youdianse-main-php-cron stat -c '%U:%G %a %n' /var/www/html/youdianse-php/alb_white.txt /var/www/html/youdianse-php/alb_white_secret.txt
```

看到这些 `ok` 就算通过。

权限正常应该类似：

```text
root:www-data 640 /var/www/html/youdianse-php/alb_white.txt
root:www-data 640 /var/www/html/youdianse-php/alb_white_secret.txt
```

## 如果刚好有人发布后端

等发布完成后，再做两件事：

```bash
sudo docker ps
```

确认 web/nginx/cron 已稳定运行。

然后重新执行：

1. 第 7 步：同步到当前运行容器。
2. 第 8 步：检查是否成功。

## 通知模板

发群时不要写私钥。

```text
【线上环境｜步骤 N 完成】维护后端白名单和平台私钥
完成内容：已完成艳姬征服正式环境后端配置维护，更新 alb_white.txt 与 alb_white_secret.txt。
验证结果：源文件、发布保护备份、web 容器、cron 容器均验证通过；容器内权限 root:www-data 640；未输出私钥内容。
下一步动作：等待业务方验证。
```

## 回滚

如果改错了，用第 3 步输出的备份目录恢复。

把下面的 `<备份目录>` 换成真实备份目录：

```bash
BACKUP=<备份目录>

sudo cp -p "$BACKUP/alb_white.txt" /opt/docker-youdianse-php/src/youdianse-php/alb_white.txt
sudo cp -p "$BACKUP/alb_white_secret.txt" /opt/docker-youdianse-php/src/youdianse-php/alb_white_secret.txt
```

然后重新执行：

1. 第 6 步：更新发布保护备份。
2. 第 7 步：同步到当前运行容器。
3. 第 8 步：检查是否成功。
