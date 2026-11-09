---
id: "doc-4531db377f4a"
title: "UAT 环境部署手册"
date: "2026-10-15T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Linux", "Shell", "Python", "Docker", "Nginx", "Redis", "监控告警"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8815%E6%97%A5-UAT%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%E6%89%8B%E5%86%8C/UAT%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%E6%89%8B%E5%86%8C-2026%E5%B9%B410%E6%9C%8815%E6%97%A5-v1.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月15日-UAT环境部署手册/UAT环境部署手册-2026年10月15日-v1.md"
sourceSha256: "91515cc3a5ccc52ba1d58881a0319e48096b4351763c1146a655763953358d0e"
sourceSystem: "project-doc"
---

# UAT 环境部署手册

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610150000-%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E4%B8%8E%E8%87%AA%E5%8A%A8%E5%8C%96%2BBKL%20UAT%2BLinux-UAT%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%E6%89%8B%E5%86%8C.md)

> 整理日期：2026-10-15 00:00｜日期依据：文件名日期

v1　2026-10-15

文中 `xxxx` 换成实际值（IP、域名、账号、密码）。命令用 root 执行或加 sudo。每节标了在哪台做。

## 一、机器规划

堡垒机（服务端，1 台，4C8G）

- 装 JumpServer、Beszel Hub、nginx
- 对外只开 80、443、2222

业务机（客户端，4 台，8C32G）

- 装 Beszel Agent

系统统一 Ubuntu 24.04，服务目录统一放 `/opt`。

资产命名规范：`角色-公网IP`，例如 `UAT-middleware-43.249.251.11`。资产节点分两个：`UAT`（5 台业务机）、`运维管理`（堡垒机自己）。

## 二、每台机器：装 Docker

```bash
apt update
apt install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

ARCH=$(dpkg --print-architecture)
CODENAME=$(. /etc/os-release; echo $VERSION_CODENAME)
REPO="deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $CODENAME stable"
echo "$REPO" > /etc/apt/sources.list.d/docker.list

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker
```

验证：

```bash
docker --version
docker compose version
```

坑：keyring 直接用下载的 `.asc` 文件，不要走 `gpg --dearmor`，否则 apt 报 NO_PUBKEY，源加不上。

业务机如果要从公司内部 Harbor 拉镜像，daemon.json 里要加 `insecure-registries`（见下一节，按项目标准填地址）。

## 三、每台机器：限制容器日志大小

```bash
cat > /etc/docker/daemon.json <<'EOF'
{
  "insecure-registries": ["<内部Harbor地址:端口>"],
  "log-driver": "json-file",
  "log-opts": { "max-size": "100m", "max-file": "3" },
  "live-restore": true
}
EOF
systemctl restart docker
```

不限制会写满磁盘；`live-restore` 让 docker 重启时容器不断。不需要内部 Harbor 的机器，把 `insecure-registries` 那行删掉。

## 四、每台机器：运维账号免密 sudo

```bash
echo "blkuat ALL=(ALL:ALL) [敏感内容已脱敏] > /etc/sudoers.d/90-blkuat-nopasswd
chmod 0440 /etc/sudoers.d/90-blkuat-nopasswd
visudo -c -f /etc/sudoers.d/90-blkuat-nopasswd
```

验证：

```bash
sudo -n -i whoami      # 输出 root 就对了
```

## 五、堡垒机：部署 JumpServer（服务端）

版本用 `jumpserver/jms_all:v4.10.19`，自带 PostgreSQL 17 和 Redis，一个容器搞定。

### 5.1 建目录、生成密钥

```bash
mkdir -p /opt/jumpserver/{data,download,pgdata}
cd /opt/jumpserver
cat > .env <<EOF
[敏感内容已脱敏] rand -hex 32)
[敏感内容已脱敏] rand -hex 12)
[敏感内容已脱敏] rand -hex 16)
[敏感内容已脱敏] rand -hex 16)
EOF
chmod 600 .env
```

### 5.2 初始化数据库目录（关键，别跳过）

```bash
docker run --rm -v /opt/jumpserver/pgdata:/target --entrypoint sh jumpserver/jms_all:v4.10.19 \
  -c "cp -a /var/lib/postgresql/. /target/ && rm -f /target/17/main/inited.txt"
```

不做这步，挂空目录启动会报 No PostgreSQL cluster found。

### 5.3 写 docker-compose.yml

```bash
cat > /opt/jumpserver/docker-compose.yml <<'EOF'
services:
  jms_all:
    image: jumpserver/jms_all:v4.10.19
    container_name: jms_all
    restart: always
    env_file: .env
    environment:
      LOG_LEVEL: ERROR
      DOMAINS: manage.xxxx          # Web SSH 走域名访问时填，用 IP 访问可留空
    ports:
      - "203.0.113.1:8081:80"         # Web 只监听本机，外网由 nginx 反代
      - "2222:2222"                 # 资产 SSH 接入
    volumes:
      - /opt/jumpserver/data:/opt/data
      - /opt/jumpserver/pgdata:/var/lib/postgresql
      - /opt/jumpserver/download:/opt/download
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://203.0.113.1/api/health/ -o /dev/null || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 5
      start_period: 300s
    logging:
      driver: json-file
      options: { max-size: "100m", max-file: "3" }
EOF
```

8081 是给 nginx 腾出 80；不用域名可改回 `80:80`。

### 5.4 启动

```bash
cd /opt/jumpserver
docker compose up -d
```

首次启动要跑数据库迁移，等 1 到 3 分钟，然后验证：

```bash
docker ps                                    # 状态 healthy
curl -s http://203.0.113.1:8081/api/health/    # db_status 和 redis_status 都是 true
```

### 5.5 设置 admin 密码

把 `01-初始化/reset_admin_password.py` 拷进容器再执行：

```bash
docker cp reset_admin_password.py jms_all:/tmp/
docker exec \
  -e DB_ENGINE=postgresql -e DB_HOST=203.0.113.1 -e DB_PORT=5432 \
  -e DB_USER=postgres -e DB_NAME=jumpserver \
  -e [敏感内容已脱敏] \
  -e [敏感内容已脱敏] \
  jms_all /opt/py3/bin/python /tmp/reset_admin_password.py
```

浏览器打开 `http://xxxx:8081` 用 admin / xxxx 登录，第一次会引导绑定 Google Authenticator。

### 5.6 建用户、资产、授权

方式一，跑脚本（幂等，可重复执行）：

```bash
export [敏感内容已脱敏]
export [敏感内容已脱敏]          # 资产的登录密码
python3 01-初始化/setup_uat.py        # 建用户组、用户、资产、账号、授权
python3 01-初始化/setup_uat_sudo.py   # 建 root 提权账号
```

方式二，界面手工做：

- 用户管理 -> 用户组：建 运维组、开发组
- 用户管理 -> 用户列表：建账号，运维给系统管理员，开发给系统普通用户
- 资产管理 -> 资产列表：按 名字-公网IP 命名，填内网 IP，平台选 Linux
- 资产管理 -> 账号列表：每台两个账号，blkuat 登录用，root 提权用（提权自选 blkuat）
- 授权管理 -> 资产授权：运维组授全部资产、账号 @ALL；开发组授应用节点、账号 blkuat

### 5.7 让提权走 sudo（免密的前提）

不改的话默认走 su，要 root 密码，连接会报 EOF。

```bash
python3 02-修复/fix_platform_su.py
```

界面位置：资产管理 -> 平台列表 -> Linux -> 提权方式选 `sudo su -`。

### 5.8 强制 MFA

系统设置 -> 安全设置 -> 全局 MFA，选"全局开启"（值 1 = 全员强制，2 = 仅管理员）。每个用户的 MFA 等级设成强制。用户首次登录会要求扫码绑 GA。

### 5.9 验证审计

普通账号登录，连一台资产，选 root 账号，能看到 root shell 就是通了。后台确认：会话管理有录像可回放；命令记录有命令。

## 六、堡垒机：部署 Beszel 监控（服务端）

### 6.1 起 Hub

```bash
docker run -d --name beszel --restart unless-stopped -p 8090:8090 \
  -v /opt/beszel/beszel_data:/beszel_data \
  -e APP_URL="https://xxxx" \
  henrygd/beszel
```

打开 `http://xxxx:8090` 注册，第一个注册的就是管理员。数据在 `/opt/beszel/beszel_data`，备份这个目录。

`APP_URL` 填监控的对外地址（走域名就填域名）。不填的话，告警通知里的链接会是 `http://localhost:8090`，点不开。

建议：8090 只对内网开放，让机房不要放通公网 8090；用域名访问就走 nginx 反代。

### 6.1.1 中文告警版镜像

官方镜像的告警文案是英文写死在代码里的（例如 `Connection to xxx is down 🔴`），官方没有多语言开关。本项目用一份打过补丁的镜像，告警全部中文：

```
xxx 已断开 🔴 / xxx 已恢复 ✅
xxx CPU 超过阈值 / 低于阈值
xxx 的容器全部正常 / 异常容器 xxx（xxx）
xxx 有服务失败 / 服务已恢复
```

复现方式（在堡垒机上）：

```bash
# 1. 下载与线上版本一致的源码，进入目录
tar xzf beszel-main.tar.gz -C /opt/beszel-src --strip-components=1
cd /opt/beszel-src
# 2. 打中文补丁（补丁文件在 code/ops-scripts-运维部署脚本/beszel/beszel-zh-alerts.patch）
patch -p1 < beszel-zh-alerts.patch
# 3. 构建中文版镜像（Dockerfile.zh 也在这个目录）
docker build -f Dockerfile.zh -t beszel-zh:v0.21.0 .
```

然后 `docker-compose.yml` 里把 `image` 换成 `beszel-zh:v0.21.0`，`docker compose up -d`。升级 Beszel 版本时，拿新版本源码重新打一次补丁、重新构建即可（补丁只改告警文案，不碰逻辑）。

### 6.2 建通用 token

Hub -> 设置 -> Tokens/Fingerprints，复制公钥，并生成通用 token。通用 token 所有机器填同一个，agent 起来自动注册到列表。

## 七、每台业务机：装 Beszel Agent（客户端）

```bash
docker run -d --name beszel-agent --restart unless-stopped --network host \
  -v /opt/beszel-agent:/var/lib/beszel-agent \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e KEY="xxxx" -e 敏感凭据：[已脱敏] \
  -e HUB_URL="http://xxxx:8090" \
  henrygd/beszel-agent:alpine
```

- KEY 填 Hub 公钥，TOKEN 填通用 token，HUB_URL 填 Hub 地址
- agent 主动外连，业务机不用开端口
- `/opt/beszel-agent` 存 agent 身份，重建容器不会多出重复机器
- 用 `:alpine` 镜像是因为它自带 smartctl，后面要采磁盘健康数据直接加参数即可

验证：Hub 刷新，机器出现在列表且状态 up。

## 八、Beszel：告警配置（服务端）

Hub -> 设置 -> 通知，Webhook / Push 里填：

```text
telegram://<机器人token>@telegram?chats=<群ID>
```

填完点测试，群里能收到就通了。

坑：在界面改完通知设置点保存后，webhook 有被清掉的情况（实测遇到过），保存完回来看一眼 webhooks 还在不在，再点一次测试。

系统页面开启告警，默认四条：离线、CPU 超 80%、内存超 80%、磁盘超 80%（各持续 10 分钟）。阈值和时长可改，也能把一台的规则复制到其他机器。

**告警带 IP**：监控里的系统名统一按 `角色-公网IP` 命名（如 `UAT-middleware-43.249.251.11`），这样"某某 is down"的告警里直接带公网 IP，一眼知道是哪台。

**通知目标**：监控告警只发这一个报警群；换群只改通知 URL 里的 `chats=`。机器人不主动推送值班信息（2026-10-17 起改为只在点「运维值班表」按钮时查看），启动也不再发在线通知。

## 九、Beszel：S.M.A.R.T. 磁盘健康

如果要采磁盘健康数据，在第七节的命令里加设备映射和能力（alpine 镜像已经自带 smartctl）：

```bash
docker run -d --name beszel-agent --restart unless-stopped --network host \
  -v /opt/beszel-agent:/var/lib/beszel-agent \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --device /dev/sda:/dev/sda \
  --cap-add SYS_RAWIO --cap-add SYS_ADMIN \
  -e KEY="xxxx" -e 敏感凭据：[已脱敏] \
  -e HUB_URL="http://xxxx:8090" \
  henrygd/beszel-agent:alpine
```

设备名填控制器名（sda、nvme0），不要填分区（sda1）。

KVM 虚拟机的 virtio 磁盘（`/dev/vda`）不暴露 SMART，配了也没数据，smartctl 报 `Unable to detect device type`。要拿物理盘健康数据，得在宿主机上监控，或者让机房把虚拟机磁盘换成 virtio-scsi。物理机、直通盘不受影响。

告警自动生效：只要有数据且通知通道配好了，磁盘报故障就会发通知。

## 十、域名和反向代理（服务端）

### 10.1 起 nginx 容器

```bash
mkdir -p /opt/nginx/{conf.d,certs,www/certbot,logs}

cat > /opt/nginx/docker-compose.yml <<'EOF'
services:
  nginx:
    image: nginx:1.27-alpine
    container_name: nginx
    restart: unless-stopped
    network_mode: host          # 直接占宿主 80/443，反代本机服务
    volumes:
      - ./conf.d:/etc/nginx/conf.d:ro
      - ./certs:/etc/nginx/certs:ro
      - ./www:/var/www
      - ./logs:/var/log/nginx
    logging:
      driver: json-file
      options: { max-size: "100m", max-file: "3" }
EOF
```

### 10.2 站点配置

```bash
cat > /opt/nginx/conf.d/00-map.conf <<'EOF'
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}
EOF

cat > /opt/nginx/conf.d/10-manage.conf <<'EOF'
server {
    listen 80;
    listen 443 ssl;
    server_name manage.xxxx;

    ssl_certificate     /etc/nginx/certs/live/manage.xxxx/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/live/manage.xxxx/privkey.pem;

    location /.well-known/acme-challenge/ { root /var/www/certbot; }

    client_max_body_size 500m;

    location / {
        proxy_pass http://203.0.113.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;        # Web SSH 要用
        proxy_set_header Connection $connection_upgrade;
        proxy_buffering off;
        proxy_read_timeout 3600s;
    }
}
EOF
```

监控和文档站按同样格式再写两个文件，`proxy_pass` 分别指到 `203.0.113.1:8090` 和 `203.0.113.1:8190`。

### 10.3 起 nginx 前先腾出 80 端口

顺序不能反。先把 JumpServer 的 80 改成 `203.0.113.1:8081`（见 5.3），重启：

```bash
cd /opt/jumpserver && docker compose up -d
```

再起 nginx：

```bash
cd /opt/nginx && docker compose up -d
docker exec nginx nginx -t        # 语法检查
docker exec nginx nginx -s reload
```

验证（在服务端本机）：

```bash
curl -s -o /dev/null -w "%{http_code}\n" -H "Host: manage.xxxx" http://203.0.113.1/
```

### 10.4 申请 HTTPS 证书

先确认 `http://manage.xxxx/.well-known/acme-challenge/` 能访问，证书验证走这个路径。

```bash
docker run --rm -v /opt/nginx/certs:/etc/letsencrypt -v /opt/nginx/www/certbot:/var/www \
  certbot/certbot certonly --webroot -w /var/www \
  -d manage.xxxx -d monitor.xxxx \
  --email xxxx@xxxx --agree-tos --no-eff-email --non-interactive
```

`-w` 后面必须是 nginx 里 root 指的那个目录（这里 `/var/www/certbot`），不一致会一直报 404。

自动续期（加到 `/etc/cron.d/certbot-renew`）：

```bash
cat > /opt/nginx/renew-cert.sh <<'EOF'
#!/bin/bash
docker run --rm -v /opt/nginx/certs:/etc/letsencrypt \
  -v /opt/nginx/www/certbot:/var/www \
  certbot/certbot renew --webroot -w /var/www --quiet
docker exec nginx nginx -s reload
EOF
chmod +x /opt/nginx/renew-cert.sh

echo "0 3 * * * root /opt/nginx/renew-cert.sh" > /etc/cron.d/certbot-renew
```

### 10.5 走 Cloudflare 的话

SSL/TLS 模式必须是 Full 或 Full(strict)，否则页面报 521。

记录真实客户端 IP，nginx 里加：

```nginx
set_real_ip_from <Cloudflare 网段>;
real_ip_header CF-Connecting-IP;
```

## 十一、日常运维

重启服务：

```bash
cd /opt/jumpserver && docker compose restart
docker restart beszel
docker restart beszel-agent
cd /opt/nginx && docker compose restart
```

看日志：

```bash
docker logs jms_all --tail 100
docker logs beszel --tail 50
docker logs beszel-agent --tail 50
docker logs nginx --tail 50
```

证书续期脚本：`/opt/nginx/renew-cert.sh`，定时任务在 `/etc/cron.d/certbot-renew`。改完配置先跑一次 `docker exec nginx nginx -t` 再 reload。

备份（每天定时打包，异地存一份）：

```text
/opt/jumpserver/pgdata      堡垒机数据库
/opt/jumpserver/data        堡垒机附件、录像
/opt/beszel/beszel_data     监控数据
/opt/nginx/certs            证书
/opt/jumpserver/.env        密钥，丢了数据解不开
```

升级：改 compose 里的版本号，`docker compose up -d`。先停服务、备份 pgdata。

## 十二、运维机器人（ben-bot 精简版）

三个入口：运维值班表、堡垒机、监控。值班人 @Ben_Bird（运维），工作时间 09:00-19:00，每周日单休。

代码：`/opt/ben-bot`（本地对应 `code/ben-bot-运维机器人/` 目录，含 `deploy.sh`）

### 12.1 部署

```bash
# 把 ben-bot 目录传到服务器后：
cd /opt/ben-bot && bash deploy.sh
docker logs --tail 30 ben-bot     # 出现 ben-bot started 就是起来了
```

机器人主动轮询 Telegram，不需要开放端口。

### 12.2 使用

- 私聊或群里发 `/start`，显示当前信息（用户、用户ID、身份、权限、聊天ID、聊天类型；群里额外显示群名称）
- 三个按钮：`📅 运维值班表`（显示今天谁值班 + 本周安排）、`🖥 堡垒机`、`📊 监控`
- 堡垒机和监控是链接按钮，点一下直接在 Telegram 内嵌浏览器里打开对应域名，不需要额外登录方式（沿用各自的账号）
- 权限：运维（@Ben_Bird）和后端开发（@SVDSeven、@brenttto、@Markwu999）都是全部权限，能看到三个按钮；其他人在私聊里只能看到值班表
- 通知：机器人**不主动推送**值班信息，启动也不发在线通知；值班表只在点按钮时显示（`duty_status.py` 里 `DUTY_NOTIFY_CHAT_IDS` 为空即关闭定时推送，填群 ID 可恢复）

### 12.2.1 命令

| 命令 | 说明 |
| --- | --- |
| `/start` | 打开菜单（当前信息 + 三个入口） |
| `/help` | 帮助（值班表说明） |
| `/id` | 查看当前聊天 / 用户 ID |
| `/sh 命令` | 在机器人容器里执行命令并返回输出，例：`/sh ls /app/data/scripts`、`/sh df -h` |

`/sh` 的权限：运维和后端开发可用，其他人会被拒绝。

安全策略：`rm` 在黑名单里直接拦截；命令里带 `;`、`&` 等拼接字符会被拒绝；执行范围只在机器人容器内（`/app` 目录和容器里已装的工具），不会碰到宿主机。

### 12.3 改入口和角色

入口按目录注册，一个目录一个按钮：

| 位置 | 说明 |
| --- | --- |
| `data/scripts/运维值班表/.benbot.json` | 值班表按钮，`order` 控制排序 |
| `data/scripts/堡垒机/.benbot.json` | 堡垒机链接按钮，改 `url` 换地址 |
| `data/scripts/监控/.benbot.json` | 监控链接按钮，改 `url` 换地址 |

加新入口：在 `data/scripts/` 下新建目录，放一个 `.benbot.json`（`action` 填 `link`、`url` 填链接），再把目录名加进 `app/benbot/constants.py` 的 `VISIBLE_TOP_LEVEL_DIRS`，重启容器生效。

角色名单同样在 `constants.py`：`OPS_USERNAMES`（运维）、`BACKEND_USERNAMES`（后端开发）；能看哪些入口在 `app/benbot/permissions.py` 的 `ROLE_ALLOWED_PATHS`。

### 12.4 改值班表

改 `/opt/ben-bot/data/scripts/运维值班表/weekend_duty.json`，改完在群里重点一次按钮即可生效，不用重启容器。

| 字段 | 说明 |
| --- | --- |
| member | 值班人姓名、用户名、角色 |
| work.start / work.end | 上下班时间，当前 09:00-19:00 |
| rest_weekday | 每周固定休息日，0=周一 … 6=周日（当前 6，即每周日单休） |
| rest_by_date | 临时多休的日期，例：`{"2026-10-20": "调休"}` |
| duty_by_date | 本该休息但临时值班的日期，例：`["2026-10-18"]` |
| note | 值班表底部的说明文字 |

### 12.5 注意

1. 一个机器人 token 只能有一个实例在轮询。这个 token 同时给监控告警发消息用（那只是单向发送，不冲突），但不要再起第二个 ben-bot。
2. 本地调试用环境变量 `TELEGRAM_API_TOKEN` 换一个机器人 token，避免和服务器上的实例抢更新。
3. 值班信息默认**只在点「运维值班表」按钮时显示**，不自动推送、启动也不发通知（2026-10-17 按要求调整）。要恢复 08:30 / 09:00 / 19:00 的定时提醒，把群 ID 填进 `app/benbot/duty_status.py` 的 `DUTY_NOTIFY_CHAT_IDS` 并重启容器。

### 12.6 代码每日自动备份

每天 09:00（Asia/Shanghai）自动把代码打包成 `ben-bot-代码-YYYY年MM月DD日.zip` 发到报警群。

| 项 | 位置 |
| --- | --- |
| 脚本 | `/opt/ben-bot/scripts/daily_code_backup.sh`（仓库内 `code/ben-bot-运维机器人/scripts/`） |
| 定时任务 | `/etc/cron.d/ben-bot-code-backup`，写 `0 1 * * *`（服务器 UTC，等于 09:00 上海） |
| 产物 | `/opt/ben-bot-backup/`，保留最近 7 份 |
| 日志 | `/var/log/ben-bot-code-backup.log`，记录每次是否发送成功 |

注意：**这台机器的 cron 不认 `CRON_TZ`**（实测），要按服务器本地时间（UTC）换算；脚本内部仍用 Shanghai 时区取日期。

### 12.7 堡垒机域名的访问密码（nginx Basic Auth）

> 历史：2026-10-16 曾做过"机器人里开关堡垒机账号 + 管理放行 IP"的面板，当天下午按团队决定**撤销**（理由：堡垒机不需要这些花活，且有安全隐患，统一收敛到域名访问控制）。机器人的堡垒机菜单节点、IP 输入 handler 和专用 API 账号 `botapi` 都已移除/停用（归档在服务器 `/opt/_removed_20261016/`）。菜单回到三个入口：`📅 运维值班表` / `🖥 堡垒机` / `📊 监控`。

现在采用 nginx 层保护：打开 `https://manage.evercare.id` 会先弹一个 HTTP Basic 认证，输入运维内部约定的账号密码才能看到登录页。

配置在 `code/ops-scripts-运维部署脚本/nginx/`：

```nginx
# conf.d/10-manage.conf 里 server 段
auth_basic "BKL UAT";
auth_basic_user_file /etc/nginx/auth/manage.htpasswd;

location /.well-known/acme-challenge/ {
    root /var/www/certbot;
    auth_basic off;     # 证书续期路径必须免密，否则 90 天后续期失败
}
```

```yaml
# docker-compose.yml 增加挂载
volumes:
  - ./auth:/etc/nginx/auth:ro
```

操作步骤：

```bash
# 1. 生成密码（不用装 apache2-utils）
PW=$(openssl rand -base64 15 | tr -d '/+=' | head -c 12)
sudo mkdir -p /opt/nginx/auth
printf 'ops:%s\n' "$(openssl passwd -apr1 "$PW")" | sudo tee /opt/nginx/auth/manage.htpasswd
sudo chmod 644 /opt/nginx/auth/manage.htpasswd
# 2. 生效
cd /opt/nginx && sudo docker compose up -d && sudo docker exec nginx nginx -t && sudo docker exec nginx nginx -s reload
```

验证：不带密码 → 401；带账号密码 → 200；`/.well-known/acme-challenge/` 免密；监控域名不受影响。

注意：密码是团队共享的，人员变动要换（改 `/opt/nginx/auth/manage.htpasswd` 后 reload）；服务器上另存了一份 `/root/nginx-manage-password.txt`（600）。

### 12.7.1 运维工作台页面（work.evercare.id）

把常用入口收在一个静态页面上，团队成员收藏一个网址即可。页面基于团队原有的导航页改造，放在 `code/work-console-运维工作台页面/`，服务器目录 `/opt/nginx/www/work`。

按钮：堡垒机 / 监控 / 文档（Google Drive 共享文件夹）/ 运维机器人 / 报警群 / Cloudflare。

其中「文档」用的是 Google Drive 的**内嵌文件夹视图**（`https://drive.google.com/embeddedfolderview?id=1_jl0zo_lQahhZunI-rieO9UABs5dOZt0#list`）：普通 Drive 链接带 `X-Frame-Options: SAMEORIGIN` 不能内嵌，这个视图是 Google 专门给嵌入用的。限制是浏览器必须已登录有权限的 Google 账号，否则 iframe 里是登录页；要完整界面就用普通链接 `https://drive.google.com/drive/folders/1_jl0zo_lQahhZunI-rieO9UABs5dOZt0` 打开。换文件夹只改这一处 URL。

打开方式由每个按钮的 `openInNewWindow` 决定（双击图标触发）：监控、文档用**内嵌面板**（`false`，在工作台页面里弹出可拖动窗口）；堡垒机、Telegram 机器人、报警群、Cloudflare 用**新窗口**（`true`）。堡垒机改新窗口是使用体验决定的（要输访问密码 + 后续跳转），Telegram / Cloudflare 则是外部服务发 `X-Frame-Options` 禁止被 iframe 嵌入，只能新窗口。

想内嵌的站点如果自带 `X-Frame-Options`，需要在对应反代里加一行 `proxy_hide_header X-Frame-Options;`（监控和文档的配置已加）。

nignx 站点配置 `conf.d/40-work.conf`：

```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name work.evercare.id;

    ssl_certificate     /etc/nginx/certs/live/work.evercare.id/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/live/work.evercare.id/privkey.pem;

    auth_basic "BKL UAT";                      # 与堡垒机同一套密码
    auth_basic_user_file /etc/nginx/auth/manage.htpasswd;

    location /.well-known/acme-challenge/ { root /var/www/certbot; auth_basic off; }

    root /var/www/work;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
```

部署顺序：先上 HTTP 版配置 → 签证书（`certbot certonly --webroot -w /var/www -d work.evercare.id`）→ 换 443 版 → `nginx -t` + reload。

加新入口只改 `code/work-console-运维工作台页面/index.html` 里的 `icons` 数组，然后把文件传到 `/opt/nginx/www/work/`，不需要改 nginx。

### 12.8 登录来源 IP 管控与全局 MFA（防爆破）

**全局 MFA 已开启**（2026-10-16，按项目要求）：

```
SECURITY_MFA_AUTH = 1     # 0 不开启 / 1 全员强制 / 2 仅管理员强制
```

效果：所有账号下次登录都要扫码绑定 Google Authenticator，之后每次登录输验证码。注意：脚本/接口登录同样会被 MFA 拦住，需要自动化时要先想好怎么处理（例如给服务账号单独放行或临时调整）。

坑：改完设置后**接口读回可能还是旧值**（进程内缓存），别被误导——以数据库 `settings.Setting` 或"重新登录试一次"为准。

2026-10-16 发现公网在暴力破解登录接口（3 个 IP 两天内 3000+ 次失败，导致 admin 反复被锁）。已配置：

| 设置 | 值 | 说明 |
| --- | --- | --- |
| `SECURITY_LOGIN_IP_BLACK_LIST` | 授权安全测试 IP | 黑名单在**验密码之前**拦，不再累计失败次数 |
| `SECURITY_LOGIN_IP_WHITE_LIST` | 自己人的 IP + `203.0.113.1` | 白名单永不限速、永不封禁 |
| `SECURITY_LOGIN_IP_LIMIT_COUNT` | 30 | 原值 99999 等于没限速 |
| `SECURITY_LOGIN_IP_LIMIT_TIME` | 30（分钟） | |

注意：

1. **`203.0.113.1` 必须留在白名单**，它是 nginx → JumpServer 的 docker 网关地址，封了控制台直接打不开。
2. 这些设置**改完要重启 JumpServer 容器**才生效（进程启动时加载）。
3. 账号被临时锁定时，解锁要用 ORM（`LoginBlockUtil.unblock_user`），因为登录接口本身也被锁住了。
4. 长期方案：域名侧加访问控制（Cloudflare Access / WAF）+ 恢复全局 MFA。

## 十三、部署检查清单

- [ ] 每台机器 Docker 装好，daemon.json 配好，docker 开机自启
- [ ] 运维账号 sudo 免密
- [ ] 堡垒机能打开登录页，admin 能登录
- [ ] 用户组、用户、资产、账号、授权都建好
- [ ] 用普通账号连一次资产，能提权到 root
- [ ] 会话有录像，命令有记录
- [ ] 所有账号 MFA 已开
- [ ] Beszel 里所有机器状态 up
- [ ] 告警测试能收到消息
- [ ] 域名 HTTPS 能打开，证书自动续期已配
- [ ] 备份任务已配

## 十四、踩过的坑（按出现顺序）

1. **Docker 源加不上，报 NO_PUBKEY**：别用 `gpg --dearmor`，直接下载 `.asc` 当 keyring。
2. **JumpServer 起不来，日志报 No PostgreSQL cluster found**：挂载的 pgdata 目录是空的，要先从镜像里拷贝初始化好的数据目录（5.2）。
3. **用户连资产提示 No account found，但权限明明给了**：授权里的账号字段要填别名，不是账号 UUID。填 `blkuat`、`root` 这种用户名，或者 `@ALL`。
4. **提权连接报 EOF，目标机日志显示 su 认证失败**：默认走 su，需要 root 密码。要在平台设置里把提权方式改成 sudo。
5. **强制首次改密后，登录报 500**：v4.10.19 + Python 3.14 的已知问题。不要给用户设"首次登录必须改密"。
6. **改了 MFA 相关的数据库配置不生效**：这些配置在进程里是缓存的，改完要重启容器。
7. **80 端口被占用，nginx 起不来**：JumpServer 默认占 80，先把它改到 `203.0.113.1:8081`，再起 nginx。
8. **证书签不下来，报 404**：certbot 的 `-w` 目录和 nginx 里 acme-challenge 的 root 目录要一致。
9. **域名打开报 521**：Cloudflare 的 SSL 模式不是 Full。
10. **Beszel 的 S.M.A.R.T. 一直没数据**：KVM 虚拟机的 virtio 磁盘不暴露 SMART，不是配置问题（见第九节）。
11. **Telegram 机器人给个人发消息失败**：机器人不能主动给没和它对话过的人发消息，让本人先给机器人发一句 `/start`。
12. **告警突然不发了**：去 Hub 通知设置里看 webhook 还在不在，界面上保存过设置可能把它清掉。
13. **容器反复重启，日志报 `Fatal glibc error: CPU does not support x86-64-v2`**：虚拟机的 CPU 型号太老（缺 popcnt），不是 Docker 或应用问题。见第 12.9 节。

### 12.9 容器报 `CPU does not support x86-64-v2` 怎么处理

2026-10-16 在 UAT 中间件服务器上遇到：minio、rocketmq-dashboard 反复重启，日志是
`Fatal glibc error: CPU does not support x86-64-v2`（exit 127），同机其它容器正常。

**判断（一条命令）**

```bash
grep -m1 "model name" /proc/cpuinfo
grep -qw popcnt /proc/cpuinfo && echo "CPU 满足 x86-64-v2" || echo "缺 popcnt → 就是这个原因"
```

**原因**：UAT 这几台虚拟机的 CPU 型号是 `Intel Core 2 Duo T7700`（缺 popcnt、无 AVX），达不到 x86-64-v2 基线；而基于 RHEL9 / UBI9 等较新基线构建的镜像要求 v2，启动即退出。与 Docker 版本无关（换 docker-ce 无效）。

**解决**

1. 根治：请机房把虚拟机的 CPU 类型改成 `host`（直通宿主机）或 Skylake 及以上，关机改、开机生效。之后所有新镜像可直接使用。
2. 临时绕行：
   - 能降版本的降版本：`apacherocketmq/rocketmq-dashboard` 2.1.0 → 2.0.1 可直接运行（改 compose 里的 image 后 `docker compose up -d <服务>`）。
   - 不能降版本的自建静态镜像：minio 官方镜像仓库（`minio/minio` 404）和下载站（`dl.min.io` 410）都已下线，镜像站所有 tag 都是新基线；用源码编译静态二进制（Go 静态编译，与 glibc / CPU 指令集无关）：

```bash
# 服务器上 /opt/minio-build/Dockerfile 已就绪
cd /opt/minio-build
sudo docker build --build-arg MINIO_TAG=RELEASE.2025-10-15T17-29-55Z \
  -t minio-uat:RELEASE.2025-10-15T17-29-55Z .
# 改 /home/chili/docker-compose.yml 中 minio 的 image 为 minio-uat:RELEASE.2025-10-15T17-29-55Z
cd /home/chili && sudo docker compose up -d minio
```

**验证**：`docker ps` 两个容器 Up；`curl -s -o /dev/null -w "%{http_code}\n" http://203.0.113.1:9000/minio/health/live` 返回 200；`docker logs --tail 5 rocketmq-dashboard` 能看到 Tomcat started。

### 12.10 UAT → SRS 专线质量监控

UAT 两台 worker 通过 IEPL 专线连 SRS（`203.0.113.1`），监控链路连通性与稳定性。

| 位置 | 文件 | 定时 |
| --- | --- | --- |
| worker01 / worker02 | `/opt/net-quality/check.py` | `*/5 * * * *`（每 5 分钟调度，单次约 3 分钟） |
| 堡垒机 | `/opt/net-quality/report.py` | `0 14 * * *`（每天 22:00 发 24 小时汇总） |

采样内容：到 `203.0.113.1` 执行 `ping -c 180 -i 1 -w 190`（约 3 分钟），记录丢包率、延迟 min/avg/max/mdev（抖动）、1935/1985 端口 TCP 建连。原始数据在 worker 的 `/var/log/net-quality.jsonl`。

告警阈值（`check.py` 顶部）：丢包 ≥ 5%、平均延迟 ≥ 60ms、抖动 ≥ 10ms、1935/1985 不通 → **立刻发群**，同类异常 30 分钟内不重复。

注意：只有 worker01/02 有 `192.168.172.x` 专线地址；中间件和 manager 不在该网段。堡垒机取数据走内网 `203.0.113.1/14`（公网 IP 从堡垒机不可达），用 root 的 `/root/.ssh/net_quality` 密钥。

## 十五、文档信息

版本：v1

编写：Ben

日期：2026 年 10 月 15 日

核对：已按 UAT 实际环境逐项核对（容器、端口、目录、账号、资产、授权、告警、证书），核对日期 2026 年 10 月 15 日

维护：改完在下面的更新记录里追加一行，写清日期、改了什么、谁改的

更新记录

```text
2026 年 10 月 15 日    v1    Ben    首次编写，按当前 UAT 环境核对
```
