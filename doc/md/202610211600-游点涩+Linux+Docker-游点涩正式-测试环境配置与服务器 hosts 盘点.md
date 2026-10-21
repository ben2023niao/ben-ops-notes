---
id: "doc-75a861346637"
title: "游点涩正式/测试环境配置与服务器 hosts 盘点"
date: "2026-10-21T16:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Docker", "Nginx", "Redis", "监控告警", "自动化", "CDN"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-1600-%E3%80%90%E9%85%8D%E7%BD%AE%E6%B8%85%E5%8D%95%E3%80%91%E6%B8%B8%E7%82%B9%E6%B6%A9%E6%AD%A3%E5%BC%8F%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE%E4%B8%8E%E6%9C%8D%E5%8A%A1%E5%99%A8hosts%E5%8F%8A%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E7%9B%98%E7%82%B9.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-1600-【配置清单】游点涩正式测试环境配置与服务器hosts及环境变量盘点.md"
sourceSha256: "35915f30aeaa71d88e3cd5010c833a3284a0fba7499431becc6011795d494f64"
sourceSystem: "project-doc"
---

# 游点涩正式/测试环境配置与服务器 hosts 盘点

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-1600-【配置清单】游点涩正式测试环境配置与服务器hosts及环境变量盘点.md`

> 整理日期：2026-10-21 16:00｜日期依据：文件名日期

## 一、目的

本清单用于开发和管理后台设计统一配置管理，回答三个问题：

1. 当前配置散落在哪里；
2. 每项配置由谁读取、何时生效；
3. 哪些适合迁入业务管理后台，哪些应继续留在基础设施层。

本文只列路径、变量名和配置类型，不记录密码、Token、私钥及敏感值。

## 二、盘点范围

| 环境 | 角色 | 公网 IP | 内网 IP | 主要职责 |
| --- | --- | --- | --- | --- |
| 正式 | 后端 | `16.209.16.108` | `203.0.113.1` | PHP-FPM、php-cron、后端 Nginx、CICD |
| 测试 | 后端 | `15.152.247.196` | 由容器运行环境自动注入 | 测试 PHP-FPM、php-cron、测试 CICD |
| 正式 | 统一网关 | `16.208.38.88` | `203.0.113.1` | H5/PC 路由、证书、限流、UA 规则 |
| 正式 | 宝塔源站 | `16.208.5.147` | `203.0.113.1` | 公网 HTTPS、vhost、前后端反向代理 |
| 正式 | 前端静态资源/SSR | `13.208.101.121` | `203.0.113.1` | H5 Nuxt SSR、Beszel Agent |

数据库服务通过以下逻辑名称访问：

| 名称 | 地址 | 用途 |
| --- | --- | --- |
| `server.db1.com` | `203.0.113.1` | Mongo 主库 |
| `server.db2.com` | `203.0.113.1`、`203.0.113.1` | Mongo 从库兼容名称 |
| `server.db2a.com` | `203.0.113.1` | Mongo 从库 01 |
| `server.db2b.com` | `203.0.113.1` | Mongo 从库 02 |
| Redis | `203.0.113.1:6379` | Session/缓存 |

## 三、服务器 `/etc/hosts`

### 3.1 正式后端 `16.209.16.108`

宿主机：

```text
203.0.113.1 localhost
154.95.24.45 package.18game.local
```

web/cron 容器由 compose `extra_hosts` 注入：

```text
203.0.113.1 server.db1.com
203.0.113.1  server.db2.com
203.0.113.1 server.db2.com
203.0.113.1  server.db2a.com
203.0.113.1 server.db2b.com
```

配置位置：

- `/opt/docker-youdianse-php/docker-compose.yml`
- YAML anchor：`x-youdianse-db-hosts`

### 3.2 测试后端 `15.152.247.196`

宿主机：

```text
203.0.113.1 localhost localhost4 localhost4.localdomain4
::1 localhost6 localhost6.localdomain6
```

当前测试 web/cron 容器没有额外 `extra_hosts`。如果后续测试 `.env` 使用逻辑域名而不是 IP，必须同步增加 `extra_hosts`。

### 3.3 网关 `16.208.38.88`

宿主机：

```text
203.0.113.1 localhost
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
```

H5/PC SSR 使用容器网络地址：

```text
H5 SSR: 203.0.113.1:3003
PC SSR: 203.0.113.1:3004
宝塔 API 上游: 203.0.113.1:443
```

这些地址目前直接写在 Nginx 配置中，不在 `/etc/hosts`。

### 3.4 宝塔源站 `16.208.5.147`

宿主机只有默认 localhost/IPv6 解析，没有业务内网域名映射。

业务路由通过 Nginx 配置中的固定 IP：

```text
H5 前端: 203.0.113.1:3003
PHP 后端: 203.0.113.1:8088
CICD: 203.0.113.1:18090
```

### 3.5 前端 `13.208.101.121`

宿主机只有默认 localhost/IPv6 解析。

H5 容器运行在：

```text
0.0.0.0:3003 -> container:3003
```

## 四、正式/测试后端配置位置

### 4.1 正式后端

| 配置 | 宿主机位置 | 容器位置 | 权限 |
| --- | --- | --- | --- |
| 业务运行配置 | `/opt/docker-youdianse-php/env/.env.prod` | `/var/www/html/youdianse-php/.env` | `root:root 0644`，只读挂载 |
| Docker/运行时编排 | `/opt/docker-youdianse-php/docker-compose.yml` | Compose 配置 | `root:root 0644` |
| 后端 Nginx 站点 | `/opt/docker-youdianse-php/nginx/default.conf` | `/etc/nginx/conf.d/default.conf` | 只读挂载 |
| 后端 Nginx 主配置 | `/opt/docker-youdianse-php/nginx/main.conf` | `/etc/nginx/nginx.conf` | 只读挂载 |
| PHP 配置 | `/opt/docker-youdianse-php/php/dev.ini` | `/usr/local/etc/php/conf.d/dev.ini` | 只读挂载 |
| PHP-FPM pool | `/opt/docker-youdianse-php/php/fpm-pool.conf` | `/usr/local/etc/php-fpm.d/www.conf` | 只读挂载 |
| PHP-FPM 日志配置 | `/opt/docker-youdianse-php/php/fpm-logging.conf` | `/usr/local/etc/php-fpm.d/zz-youdianse-logging.conf` | 只读挂载 |
| 白名单 | `/opt/docker-youdianse-php/cicd-web/runtime/app-local-files/alb_white.txt` | `/var/www/html/youdianse-php/alb_white.txt` | `root:www-data 0640`，只读挂载 |
| 平台私钥 | `/opt/docker-youdianse-php/cicd-web/runtime/app-local-files/alb_white_secret.txt` | `/var/www/html/youdianse-php/alb_white_secret.txt` | `root:www-data 0640`，只读挂载 |
| CICD 页面配置 | `/opt/docker-youdianse-php/cicd-web/config/settings.json` | CICD 进程 | `root:root 0644` |
| CICD 运行密钥 | `/opt/docker-youdianse-php/cicd-web/runtime/secrets.env` | CICD 进程 | `root:root 0600` |
| 独立配置仓库 | `/opt/docker-youdianse-php/config-repo` | CICD 使用 | Git 工作区 |
| 业务代码 | `/opt/docker-youdianse-php/src/youdianse-php` | web/cron 镜像构建源 | Git 工作区 |
| 应用日志 | `/opt/docker-youdianse-php/runtime/app-logs` | `/var/www/html/youdianse-php/runtime/logs` | 可写挂载 |

### 4.2 测试后端

| 配置 | 宿主机位置 |
| --- | --- |
| 业务运行配置 | `/opt/docker-youdianse-php/env/.env.dev` |
| Docker/运行时编排 | `/opt/docker-youdianse-php/docker-compose.yml` |
| 后端 Nginx | `/opt/docker-youdianse-php/nginx/default.conf` |
| PHP 配置 | `/opt/docker-youdianse-php/php/dev.ini` |
| PHP-FPM 日志配置 | `/opt/docker-youdianse-php/php/fpm-logging.conf` |
| 白名单 | `/opt/docker-youdianse-php/cicd-web/runtime/app-local-files/alb_white.txt` |
| 平台私钥 | `/opt/docker-youdianse-php/cicd-web/runtime/app-local-files/alb_white_secret.txt` |
| CICD 页面配置 | `/opt/docker-youdianse-php/cicd-web/config/settings.json` |
| CICD 运行密钥 | `/opt/docker-youdianse-php/cicd-web/runtime/secrets.env` |
| 独立配置仓库 | `/opt/docker-youdianse-php/config-repo` |

测试白名单和平台私钥同样使用只读 bind mount。

## 五、网关配置位置

目录：`/etc/nginx/conf.d/`

| 文件 | 作用 |
| --- | --- |
| `10-youdianse-prod-maps.conf` | 域名、设备、H5/PC 分流 map、upstream、限流、UA/地区判断 |
| `20-youdianse-prod-unified.conf` | H5/PC 统一 server、API 反代、SSR 反代、证书选择 |
| `abuse-blocklist.conf` | 自动维护的恶意来源黑名单 |

关键硬编码：

- H5 SSR：`203.0.113.1:3003`
- PC SSR：`203.0.113.1:3004`
- 宝塔 API 上游：`203.0.113.1:443`
- 后端静态资源：`d391me9s8n5j5s.cloudfront.net`

证书：`/etc/letsencrypt/live/<域名>/fullchain.pem` 与 `privkey.pem`

PM2 配置在容器内：

```text
/app/ecosystem.config.cjs
```

PM2 环境变量名：

```text
BRANCH
DISPLAY_NAME
NODE_ENV
HOST
PORT
SHORT_ID
NODE_OPTIONS
```

## 六、宝塔源站配置位置

### 6.1 Nginx vhost

目录：`/www/server/panel/vhost/nginx/`

重点文件：

```text
new.youdianse.com.conf
h5.youdianse-main.xyz.conf
h5.youdianse.com.conf
admin.youdianse-main.xyz.conf
cicd.youdianse-main.xyz.conf
18h.game.conf
kf.youdianse-main.xyz.conf
extension/new.youdianse.com/00-youdianse-fixed-reverse-proxy.conf
```

扩展配置目录：

```text
/www/server/panel/vhost/nginx/extension/<域名>/
```

### 6.2 面板数据库

```text
/www/server/panel/data/default.db
```

保存站点、域名、端口等宝塔元数据。面板保存时可能重写 vhost，因此长期真值不应只放在这个数据库。

### 6.3 Nginx 全局配置

```text
/www/server/nginx/conf/nginx.conf
/www/server/nginx/conf/proxy.conf
/www/server/panel/vhost/nginx/0.site_total_log_format.conf
```

### 6.4 证书

```text
/www/server/panel/vhost/cert/<域名>/fullchain.pem
/www/server/panel/vhost/cert/<域名>/privkey.pem
```

## 七、前端服务器配置位置

H5 容器内的 PM2 配置：

```text
/app/ecosystem.config.cjs
```

PM2 变量：

```text
PORT=3003
HOST=0.0.0.0
NODE_OPTIONS=--expose-gc --max-old-space-size=1024
```

镜像内构建变量：

```text
BRANCH
DISPLAY_NAME
NODE_ENV
NODE_VERSION
SHORT_ID
YARN_VERSION
```

注意：目前服务器上的 PM2 配置仍是 `max_memory_restart: 500M`；网关侧有运行时守卫，但不能替代前端源码仓库中的正式配置修复。

## 八、正式 `.env.prod` 配置分组

### 8.1 应用与会话

```text
[app]
name
env
timezone
headico
check_admin_ip
single_point_login

[session]
adapter

[session.Files]
lifetime
prefix
uniqueId

[session.Redis]
host
port
persistent
lifetime
prefix
index
uniqueId
```

### 8.2 Mongo / Redis / Queue / Cache

```text
[database.mongodb.default]
host
port
dbname
username
password

[database.mongodb.channel]
host
port
dbname
username
password

[database.mongodb.slave1]
host
port
dbname
username
password

[database.mongodb.slave2]
host
port
dbname
username
password

[redis]
host
port
index
prefix

[queue]
channel
index

[cache]
adapter
lifetime
host
port
index
prefix
```

### 8.3 模块、搜索、消息

```text
[modules]
Backend
Api
Channel
Customer
ApiV1
Sdk

[elastic]
host
prefix

[rabbitmq]
host
port
user
password
vhost
```

### 8.4 Telegram / 回调 / 第三方

```text
[telegram]
bot_token
hook_token
tg_webhook

[tg]
TG_TOKEN
TG_WEBHOOK
TG_HOOK_TOKEN

[channel]
api_url
secret_key

[other_kf]
kf_key
kf_appid
kf_api_url
ips

[host_check]
check_url

[lsj_ai]
media_url
media_key
media_appid
app_name

[pay.callback]
urls

[cloudflare]
site_key
secret_key

[trtc]
enabled
sdk_app_id
secret_key
admin_identifier
audit_name
api_host

[te_sdk]
app_id
log_path
```

### 8.5 AWS / CDN / 加密

```text
[aws]
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
AWS_BUCKET
AWS_DOMAIN
AWS_DOMAIN_ENCRYPT_KEY
AWS_DISTRIBUTION_ID
AWS_CDN_ACCESS_KEY
AWS_CDN_KEY_ID
AWS_CDN_REGION

[cdn]
tencent
kingshan
aws

[cdn.aws.gp]
domain
keyId
keyPath

[cdn.aws.18game]
domain
origin_domain
backend_cdn_domain
keyId
keyPath
channel_s3_domain

[aes.pass]
pass_key

[check_white_token_ip]
ips
```

### 8.6 动态 CDN 分组

正式配置还包含多个：

```text
[cdn.tencent.<业务域名>]
[cdn.aliyun.<业务域名>]
[cdn.jixing.<业务域名>]
[cdn.maoyun.<业务域名>]
```

每个分组通常包含：

```text
domain
key
```

部分腾讯云视频分组还包含：

```text
path_prefix
ttl
token_param
time_param
key_file
```

这类动态分组不建议继续扩展成大量独立 section，迁移配置中心时应改为“CDN 配置表 + 业务标识”。

## 九、测试 `.env.dev` 差异

测试配置包含正式环境对应的绝大多数分组，并额外存在：

```text
[modules]
Pc

[lsj_ai]
open_url
open_app_id
open_app_secret

[cdn.tencent._default]
path_prefix
ttl
token_param
time_param
key
key_file

[own_drama]
url
api_key

[te_sdk]
server_url
```

测试环境当前没有任何容器 `extra_hosts`，说明测试 `.env` 的数据库连接依赖目前配置中的实际值或网络解析，不能与正式环境假设混用。

## 十、CICD 运行配置

### 10.1 正式 CICD

`secrets.env` 变量名：

```text
TG_CHAT_IDS
```

配置文件和运行密钥：

```text
/opt/docker-youdianse-php/cicd-web/config/settings.json
/opt/docker-youdianse-php/cicd-web/runtime/secrets.env
```

### 10.2 测试 CICD

`secrets.env` 变量名：

```text
TG_BOT_TOKEN
TG_CHAT_ID
TG_EXTRA_CHAT_IDS
TG_PUBLISH_CHAT_IDS
YOUDIANSE_HEALTH_TG_CHAT_ID
YOUDIANSE_PUBLISH_PASSWORD
YOUDIANSE_WEBHOOK_TOKEN
```

## 十一、当前配置分散的核心问题

| 问题 | 典型位置 | 风险 |
| --- | --- | --- |
| 业务配置在 INI 文件 | `env/.env.prod`、`env/.env.dev` | 无审计、无灰度、无法在线回滚 |
| 平台白名单在 TXT | `config-repo/app-local-files/*.txt` | 格式弱、容易重复/漏项，前后环境不同步 |
| 容器网络主机名在 Compose | `docker-compose.yml` | env 改了但 hosts 没改会直接报错 |
| 路由写死在 Nginx | 网关 `10/20-*.conf`、宝塔 vhost | 新增域名要改多处，容易一处漏 |
| SSR PM2 参数在镜像内 | `/app/ecosystem.config.cjs` | 运行时修改后重建镜像会回退 |
| 密钥散落 | `.env`、`secrets.env`、PM2、Nginx | 轮换困难、权限边界不统一 |
| 测试/正式结构不一致 | 正式有 `extra_hosts`，测试没有 | 发布验证结果不可直接复用 |

## 十二、建议的统一配置分层

不建议把所有配置塞进同一个后台页面。应按权限和生效方式分三层：

### 12.1 业务配置中心

建议进入业务管理后台或 Nacos：

- Mongo/Redis/队列/Cache；
- CDN/支付/第三方/Telegram；
- 功能开关、超时、限流阈值；
- 白名单和平台映射。

必须具备：

- 正式/测试 namespace 隔离；
- 变更历史、操作人、前后值 diff；
- 灰度发布、版本回滚；
- 发布前格式校验；
- 敏感字段加密；
- API 供 PHP/H5/PC/SDK 统一读取；
- 客户端本地缓存和配置中心故障兜底。

### 12.2 基础设施配置

继续留在 Git/部署系统：

- Docker Compose；
- Nginx；
- PHP-FPM/Sysctl；
- 证书路径；
- 容器镜像、端口、启动参数。

这些配置不适合在线热改，必须经过语法检查、灰度 reload 和回滚。

### 12.3 密钥中心

独立存放：

- 数据库密码；
- AWS/腾讯云密钥；
- Telegram Token；
- 平台私钥；
- SSH/TLS 私钥；
- 支付密钥。

业务后台只引用密钥 ID，不直接展示明文。

## 十三、推荐迁移顺序

### 第一阶段：建立总台账

- 把本文件作为初始清单；
- 每项配置标记 owner、环境、消费端、敏感级别；
- 删除无人使用的历史 section 和 CDN 分组。

### 第二阶段：业务配置只保留一个来源

- 业务管理后台维护结构化配置；
- 由后台生成 `.env` 快照给尚未改造的 PHP；
- 同时提供配置 API 给已改造模块；
- 配置文件仍保留版本号和回滚能力。

### 第三阶段：代码接入

- PHP 启动时加载不可变快照；
- 动态配置通过 SDK/API 获取；
- 读取失败回退最后一次成功快照；
- 禁止业务代码读取 `/etc/hosts` 参与业务开关。

### 第四阶段：基础设施收敛

- 新增域名只录一次，由配置生成网关和宝塔路由；
- service registry/DNS 替代手工 hosts；
- PM2 参数进入前端源码仓库；
- Nginx 配置全部版本化。

## 十四、结论

当前问题的根源不是单个 TXT，而是业务配置、基础设施配置和密钥没有边界：

- 一部分在 `.env`；
- 一部分在 Compose hosts；
- 一部分在 TXT；
- 一部分在 Nginx；
- 一部分在 PM2；
- 一部分在宝塔数据库和证书目录。

正确目标不是一个“大而全后台”，而是：

```text
业务配置 → 配置中心/管理后台
基础设施 → Git + CI/CD
密钥 → 独立密钥中心
服务地址 → DNS/服务发现
```

这样才能做到统一管理、可审计、可回滚，并避免配置修改和容器重建互相踩踏。
