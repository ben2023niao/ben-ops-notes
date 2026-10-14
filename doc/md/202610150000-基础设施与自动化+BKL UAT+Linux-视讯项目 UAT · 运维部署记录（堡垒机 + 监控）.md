---
id: "doc-68fd05ec79cc"
title: "视讯项目 UAT · 运维部署记录（堡垒机 + 监控）"
date: "2026-10-15T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Linux", "Shell", "Python", "Docker", "Nginx", "Redis", "监控告警"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8815%E6%97%A5-%E5%A0%A1%E5%9E%92%E6%9C%BA%E4%B8%8E%E7%9B%91%E6%8E%A7%E9%83%A8%E7%BD%B2/2026%E5%B9%B410%E6%9C%8815%E6%97%A5-%E5%A0%A1%E5%9E%92%E6%9C%BA%E4%B8%8E%E7%9B%91%E6%8E%A7%E9%83%A8%E7%BD%B2-%E5%AE%8C%E6%95%B4%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月15日-堡垒机与监控部署/2026年10月15日-堡垒机与监控部署-完整记录.md"
sourceSha256: "cf304995bcd4a135eee123fdc0644158f99259c91a3ac2183a04373f36b599f4"
sourceSystem: "project-doc"
---

# 视讯项目 UAT · 运维部署记录（堡垒机 + 监控）

> 来源文件：`~/Projects/work/ops/devops/devops-bkl/doc/2026年10月15日-堡垒机与监控部署/2026年10月15日-堡垒机与监控部署-完整记录.md`

> 整理日期：2026-10-15 00:00｜日期依据：文件名日期

| 项 | 内容 |
| --- | --- |
| 版本 | v0.3 |
| 日期 | 2026-10-15 |
| 主机 | 管理机 blk-uat-oob / 公网 43.249.251.15 / 内网 203.0.113.1（Ubuntu 24.04.5，4C8G，LVM 剩余 154G 可扩） |
| 部署方式 | 全部容器化（Docker Compose），与项目现有风格一致 |
| 访问入口 | 堡垒机 https://manage.evercare.id ；监控 https://beszel.evercare.id（Cloudflare → nginx → 内部服务） |

## 1. 堡垒机（JumpServer）

| 项 | 值 |
| --- | --- |
| 版本 | jumpserver/jms_all:v4.10.19（all-in-one，内置 PostgreSQL 17 + Redis） |
| 部署目录 | `/opt/jumpserver/`（`docker-compose.yml`、`.env`、`data/`、`pgdata/`） |
| 端口 | 80（Web）、2222（资产 SSH 接入） |
| 控制台 | http://43.249.251.15/core/auth/login/ |
| admin 初始密码 | 见服务器 `/root/jumpserver-admin-initial.txt`（600，仅 root 可读） |
| 启动/重启 | `cd /opt/jumpserver && sudo docker compose up -d` |
| 数据落盘 | `/opt/jumpserver/pgdata`（数据库）、`/opt/jumpserver/data`（附件/录像等） |

### 1.1 组织与账号

| 账号 | 组 | 系统角色 | 权限 |
| --- | --- | --- | --- |
| admin | Default | System Admin | 超级管理员（给 jack） |
| ben / berd | 运维组 | System Admin | UAT 全部资产 + root 提权 |
| ak | 运维组 + 管理员组 | System Admin | 同运维组，并在管理员组 |
| bruce | 开发组 | System Operator | 4 台应用节点，仅连接 + 剪贴板，无 root |

### 1.2 资产与账号

- 节点树：`/DEFAULT/UAT`
- 资产：`UAT-middleware`(203.0.113.1)、`UAT-manager`(.12)、`UAT-worker01`(.13)、`UAT-worker02`(.14)、`UAT-srs`(203.0.113.1)
- 每台两个账号：`blkuat`（登录账号）、`root`（提权账号，`su_from` = blkuat，以 sudo 免密提权）
- 授权：`UAT-运维组-全部资产`（accounts = `@ALL`，全动作）、`UAT-开发组-应用节点`（accounts = `blkuat`）

### 1.3 关键配置项（踩过的坑）

1. **授权里的 accounts 必须写别名**，不是账号 UUID。格式：用户名（如 `blkuat`）、虚拟账号（`@ALL/@SPEC/@USER/@ANON/@INPUT`）、账号模版（`%<模板ID>`）。写 UUID 会导致 `permed_accounts` 为空，连资产时 koko 报 `No account found`。
2. **提权方式配在「平台」上**：`assets.Platform` 的 `su_enabled=True`、`su_method=sudo`（表示执行 `sudo su -`）。留空会走 `su - root`（需要 root 密码，免密环境会失败）。
3. **`SECURITY_MFA_AUTH` 语义**：0 不开启、1 全员强制、2 仅管理员强制（不是"更严格"）。改数据库后需要重启容器才生效。
4. **强制首次改密有 bug**：`[敏感内容已脱敏] 时，v4.10.19 + Python 3.14 登录会 500（`PasswordNeedUpdate` 缺 `detail` 属性）。因此初始密码不设"首次必须修改"，由使用人登录后自行改。
5. **站点 URL**：默认是 `http://203.0.113.1`，已改为 `http://43.249.251.15`。
6. **脚本化配置时的 MFA**：全局 MFA 开启后 API 登录会被拦；用脚本批量配置时需要临时把 `SECURITY_MFA_AUTH` 设为 0 并重启容器，配置完再改回。

## 2. 服务器免密提权

5 台机器（堡垒机 + 4 台 UAT）均已给 `blkuat` 配置免密 sudo：

```
/etc/sudoers.d/90-blkuat-nopasswd
blkuat ALL=(ALL:ALL) [敏感内容已脱敏]
```

验证：`sudo -n -i whoami` 返回 `root`。Java/Koko 侧使用 `sudo su -` 提权，全程有会话录像与命令记录。

## 3. 监控（Beszel）

| 项 | 值 |
| --- | --- |
| 版本 | hub/agent `henrygd/beszel` + `henrygd/beszel-agent`（v0.21.0） |
| 部署目录 | `/opt/beszel/`（hub）、`/opt/beszel-agent/`（agent） |
| 访问 | http://43.249.251.15:8090/ |

## 0. 域名与反向代理（nginx）

- 域名（Cloudflare 代理，源站 43.249.251.15）：

| 域名 | 用途 | 后端 |
| --- | --- | --- |
| manage.evercare.id | 堡垒机控制台 | 203.0.113.1:8081（JumpServer） |
| beszel.evercare.id | 监控 | 203.0.113.1:8090（Beszel） |
| wendang.evercare.id | 文档站（Confluence） | 203.0.113.1:8190（SVD 部署）；DNS 解析后执行 `/opt/nginx/issue_cert_wendang.sh` 补 HTTPS |
- nginx：容器部署，`network_mode: host`，配置 `/opt/nginx/conf.d`，证书 `/opt/nginx/certs`
- 端口调整：JumpServer 只监听 `203.0.113.1:8081`（不再占用 80），Beszel 8090 由 nginx 反代
- HTTPS：Let's Encrypt（certbot webroot），已加 `/etc/cron.d/certbot-renew` 每天 3 点自动续期
- 已配置 Cloudflare 真实 IP（`real_ip_header CF-Connecting-IP` + CF 网段），审计日志记录真实来源
- 未匹配域名或直接用 IP 访问 → 302 跳转到 `https://manage.evercare.id`
- 注意：Cloudflare SSL/TLS 模式需为 Full 或 Full(strict)，否则报 521
| 管理员 | `[邮箱已脱敏]`（用户名可填 admin），密码见服务器 `/root/beszel-admin.txt` |
| 接入方式 | 通用 token（`universal_tokens` 集合）自动注册，agent 用 WebSocket 主动连 hub |
| 已接入 | UAT-堡垒机、UAT-middleware、UAT-manager、UAT-worker01、UAT-worker02（全部 up） |
| 告警通道 | Telegram（Shoutrrr URL：`telegram://<bot_token>@telegram?chats=<chat_id>`） |
| 默认规则 | 离线告警；CPU / 内存 / 磁盘 超过 80% 持续 10 分钟 |

### 3.1 S.M.A.R.T. 磁盘健康监控（已配置，待机房支持才能出数据）

- 已按官方文档把 5 台机器的 agent 换成 `:alpine` 镜像（自带 smartctl 7.5），并加设备映射与 `SYS_RAWIO` / `SYS_ADMIN` 能力，脚本见 `code/ops-scripts-运维部署脚本/beszel/enable_smart.sh`。
- **实测拿不到数据**：5 台都是 KVM 虚拟机，磁盘为 virtio（`/dev/vda`），虚拟化层不向虚拟机暴露 SMART；容器内与宿主机上 `smartctl -i /dev/vda` 均报 `Unable to detect device type`，`smartctl --scan` 为空。
- 要拿到盘健康数据，需要机房二选一：宿主机侧监控物理盘（推荐）；或把虚拟机磁盘由 virtio-blk 换成 virtio-scsi（盘符变 `/dev/sda`，需重新映射设备）。
- Beszel 的 SMART 告警是自动的：只要有数据且已配置通知通道，磁盘报故障即触发，无需额外配置。

Agent 安装（每台执行，见 `beszel/install_agent.sh`）：

```bash
sudo ./install_agent.sh "<hub 公钥>" "<通用 token>" http://203.0.113.1:8090
```

## 4. 脚本清单（工作目录）

| 文件 | 用途 |
| --- | --- |
| `jumpserver/setup_uat.py` | 建用户组 / 用户 / 资产 / 账号 / 授权（幂等） |
| `jumpserver/setup_uat_sudo.py` | 建 root 提权账号（su_from=blkuat） |
| `jumpserver/fix_permission_accounts.py` | 修正授权里的账号别名 |
| `jumpserver/fix_platform_su.py` | 把平台提权方式改成 sudo |
| `jumpserver/add_admin_group.py` | 用户加入管理员组 |
| `jumpserver/_verify_db.py` / `_verify_audit.py` | 只读核对配置 / 会话录像 / 命令记录 |
| `beszel/add_systems.py` | 创建被监控系统（或改用通用 token 自动注册） |
| `beszel/install_agent.sh` | 被监控机器一键装 agent |
| `telegram/get_chat_ids.py` | 取机器人所在群的 chat_id |

## 5. 待办

1. 交接前把全局 MFA 恢复为「全员强制」并把 admin / ben 的 MFA 等级调回强制（当前为调试期临时关闭）。
2. 各账号首次登录绑定 Google Authenticator；初始密码登录后自行修改。
3. 如需独立报警群（SVD 提到），把新群 chat_id 发运维，改 Beszel 通知 URL 即可。
4. SRS(203.0.113.1/28) 私网路由待机房确认；确认后可正常纳管与监控。
5. 报警规则可按需细化：容器异常退出、端口/接口存活、带宽阈值等。
