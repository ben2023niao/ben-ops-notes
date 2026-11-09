---
id: "doc-26c3dbc5e750"
title: "nginx 按类型合并 conf 与新增域名指引"
date: "2026-08-12T15:49:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "DNS", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1549-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91nginx%E6%8C%89%E7%B1%BB%E5%9E%8B%E5%90%88%E5%B9%B6conf%E4%B8%8E%E6%96%B0%E5%A2%9E%E5%9F%9F%E5%90%8D%E6%8C%87%E5%BC%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1549-【优化+运维记录】nginx按类型合并conf与新增域名指引.md"
sourceSha256: "53add4a4213e68700f0e80d9bda09fb0b38375ac6186896dce22da8e7b5fafea"
sourceSystem: "project-doc"
---

# nginx 按类型合并 conf 与新增域名指引

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608121549-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-nginx%20%E6%8C%89%E7%B1%BB%E5%9E%8B%E5%90%88%E5%B9%B6%20conf%20%E4%B8%8E%E6%96%B0%E5%A2%9E%E5%9F%9F%E5%90%8D%E6%8C%87%E5%BC%95.md)

> 整理日期：2026-08-12 15:49｜日期依据：文件名日期

环境标签：线上环境 / 游点涩 / nginx / 域名接入 / H5 / PC

时间：2026-08-12 15:49（Asia/Manila）

## 任务来源

用户要求：

- 优化线上服务器 nginx：原来“一个域名一个 conf”，改为按类型合并。
- `www` / `@` 主域名判断 PC/H5 的跳转，合并成一个 conf，新增域名只需加域名。
- 独立一个 H5 conf，新增只需加 H5 域名（方便把老服务器的 H5 域名都加进来）。
- 独立一个 PC conf，方便增加单独的 PC 域名。
- 操作完成后自检查，并写详细说明：`www @` 跳转类新域名如何解析/如何加 conf；单纯 H5 如何解析/加 conf；单纯 PC 如何解析/加 conf。
- 每步操作都发群通知（上线群 + 运维群），最后汇总文档、发群并合并提交本地代码。

## 本轮读取依据

- `AGENTS.md`、`workbench/`、`devops/ai_context/servers.yml`
- 历史接入文档：`2026-08-12_1536-【配置部署+运维记录】线上H5+PC新域名接入.md`

## 优化后 conf 结构（`线上环境-游点涩-新前端配置/nginx/`）

| 文件 | 作用 |
| --- | --- |
| `10-youdianse-prod-maps.conf` | 共享 map：设备判断（UA→h5/pc）、去 www 前缀、域名模式（h5/pc/redirect/ua）、后端选择、upstream H5/PC、resolver |
| `20-youdianse-prod-unified.conf` | 统一入口 conf（一个 server 块）：pc+h5 跳转 / 纯 H5 / 纯 PC / 老域名 UA 分流全部合并 |
| `youdianse-prod-h5pc-ssl-renew.sh` | SSL 自动续期/到期检查脚本（cron 03:10） |

2026-08-12 进一步将 20-redirect/30-h5/40-pc/50-ua 合并为 `20-youdianse-prod-unified.conf`；旧按域名 conf 与分类 conf 均已下线。

证书目录自动选择规则（`10-...maps.conf`）：

```nginx
map $ssl_server_name $h5pc_cert_dir {
    default $ssl_server_name;
    ~^(?:h5|pc|www)\.(?<base>.+)$ $base;
}
```

- `h5.X` / `pc.X` / `www.X` → 使用 `live/X` 目录证书（子域回退主域名证书）。
- 其他主机名 → 使用 `live/<完整主机名>` 目录证书。

## 自检结果（已通过）

| 项目 | 结果 |
| --- | --- |
| `nginx -t` / reload | 通过 |
| PC UA 访问根域/www | 301 → `https://pc.<域名>/` |
| 手机 UA 访问根域/www | 301 → `https://h5.<域名>/` |
| http → https | 301 → 对应 pc./h5. |
| 02/03 域名跳转 | 正常 |
| `https://h5.yds-pc-h5-01.cc/` | 200，版本 915a0d3 |
| `https://pc.yds-pc-h5-01.cc/` | 200，版本 5c1d4ba |
| `pc./h5. /healthz` | 200 |
| TLS SNI 证书 | 根域/www/h5/pc 均返回正确域名证书（01/02/03） |

注意：变量方式加载证书在 worker 进程握手时读取，需要给 nginx 用户读 `/etc/letsencrypt` 权限，已执行：

```bash
sudo chmod 755 /etc/letsencrypt/live /etc/letsencrypt/archive
sudo chmod 755 /etc/letsencrypt/archive/*/
sudo chmod 644 /etc/letsencrypt/archive/*/*.pem
```

## 新域名接入指引

### 一、`www @` 跳转 PC/H5 类新域名（设备自动判断跳转）

适用：一个主域名同时服务 PC 和 H5，访问 `域名`/`www.域名` 按设备跳 `pc.域名` / `h5.域名`。

1. DNS 解析（都指向线上新服务器）：

```text
@    A   16.208.38.88
www  A   16.208.38.88
pc   A   16.208.38.88
h5   A   16.208.38.88
```

2. 证书：签发 SAN 覆盖 `域名 www.域名 pc.域名 h5.域名`，落到 `/etc/letsencrypt/live/<域名>/`：

```bash
sudo certbot certonly --webroot -w /var/www/html -d <域名> -d www.<域名> -d pc.<域名> -d h5.<域名>
```

3. 修改 `20-youdianse-prod-redirect.conf`，在 `server_name` 追加：

```nginx
server_name ... <域名> www.<域名>;
```

4. 检查并生效：

```bash
sudo nginx -t && sudo systemctl reload nginx
```

5. 可选：把新域名加入 `/usr/local/bin/youdianse-prod-h5pc-ssl-renew.sh` 的 `DOMAINS` 列表，纳入自动续期检查。

### 二、单纯 H5 域名（直接进 H5 站点，不做设备跳转）

适用：老服务器上的 H5 域名直接接入本机 H5 容器。

1. DNS：

```text
h5.域名  A  16.208.38.88
```

2. 证书：

```bash
sudo certbot certonly --webroot -w /var/www/html -d h5.域名
```

证书目录规则：`h5.<主域名>` 可复用主域名证书（`live/<主域名>`，需 SAN 含 h5.子域）；独立域名则按 `live/h5.域名`（完整主机名）。

3. 修改 `30-youdianse-prod-h5.conf`，在 `server_name` 追加：

```nginx
server_name ... h5.域名;
```

4. `sudo nginx -t && sudo systemctl reload nginx`。

### 三、单纯 PC 域名（直接进 PC 站点）

1. DNS：

```text
pc.域名  A  16.208.38.88
```

2. 证书：

```bash
sudo certbot certonly --webroot -w /var/www/html -d pc.域名
```

3. 修改 `40-youdianse-prod-pc.conf`，在 `server_name` 追加：

```nginx
server_name ... pc.域名;
```

4. `sudo nginx -t && sudo systemctl reload nginx`。

## 验证命令

```bash
sudo nginx -t
curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" -A "Mozilla/5.0 (Windows NT 10.0) Chrome" https://<域名>/
curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" -A "Mozilla/5.0 (iPhone) Safari" https://www.<域名>/
curl -s -o /dev/null -w "%{http_code}\n" https://h5.<域名>/
curl -s -o /dev/null -w "%{http_code}\n" https://pc.<域名>/
echo | openssl s_client -servername h5.<域名> -connect 16.208.38.88:443 2>/dev/null | openssl x509 -noout -subject
```

## 结论

- nginx 已从“一个域名一个 conf”优化为按类型 3 类 conf（跳转 / H5 / PC），新增域名只需在对应 conf 的 `server_name` 追加域名并保证证书即可。
- 证书目录按 SNI 自动选择；已放通 nginx 用户读取 `/etc/letsencrypt` 权限。
- 自检全部通过（跳转、页面、版本、healthz、TLS 证书）。

## 后续注意

- 新增域名后记得把域名加入 SSL 续期脚本的 `DOMAINS`（如证书由该脚本管理）。
- 证书到期前由 cron（每天 03:10）自动续期并 reload nginx。
- 老服务器 H5 域名接入时，先确认其证书 SAN；可复用主域名证书或单独签发。
