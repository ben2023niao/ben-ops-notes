---
id: "doc-81914f1e9a42"
title: "新域名接入与 SSL 制作快速指南（16.208.38.88）"
date: "2026-08-12T16:21:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "CDN", "DNS", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1621-%E3%80%90%E5%BF%AB%E9%80%9F%E6%8C%87%E5%8D%97%E3%80%91%E6%96%B0%E5%9F%9F%E5%90%8D%E6%8E%A5%E5%85%A5%E4%B8%8ESSL%E5%88%B6%E4%BD%9C%EF%BC%8816.208.38.88%EF%BC%89.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1621-【快速指南】新域名接入与SSL制作（16.208.38.88）.md"
sourceSha256: "9969c18fb5eaa8b422663d4d5aade88fd5a1cf5b0fc8c368e4f93b736a18afe1"
sourceSystem: "project-doc"
---

# 新域名接入与 SSL 制作快速指南（16.208.38.88）

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1621-【快速指南】新域名接入与SSL制作（16.208.38.88）.md`

> 整理日期：2026-08-12 16:21｜日期依据：文件名日期

环境标签：线上环境 / 游点涩 / nginx / 域名接入 / SSL / 快速参考

时间：2026-08-12 16:21（Asia/Manila）

> 目标：让有经验的同事一眼就会。通用三步：① DNS A 记录指向 `16.208.38.88` → ② 在对应 conf 的 `server_name` 加域名 → ③ 证书 + `nginx -t && reload`。

## 服务器与 conf 对应关系

已统一合并为一个 conf（`/etc/nginx/conf.d/20-youdianse-prod-unified.conf`），按域名模式 + UA 自动分流：

| 场景 | 在 `20-youdianse-prod-unified.conf` 的 `server_name` 加 | `10-youdianse-prod-maps.conf` 的 `$h5pc_mode` 标注 |
| --- | --- | --- |
| `www/@` 主域名自动跳 pc/h5 | `<域名> www.<域名>` | `redirect` |
| 纯 H5 | `h5.<域名>` | 可不标注（默认 h5） |
| 纯 PC | `pc.<域名>` | `pc.*` 自动识别，可不标注 |
| 老 H5 域名按 UA 分流 | `<老域名>` | `ua` |

## 一、pc+h5 跳转类（www/@ 自动跳 pc./h5.）

```bash
# 1) DNS（4 条 A 记录）
#    @  www  pc  h5  都 A -> 16.208.38.88

# 2) 改 conf：20-youdianse-prod-unified.conf
#    server_name ... <域名> www.<域名>;
#    并在 10-youdianse-prod-maps.conf 的 $h5pc_mode 加：
#    <域名> redirect;  www.<域名> redirect;

# 3) 证书（覆盖根域/www/pc/h5）
sudo certbot certonly --webroot -w /var/www/html -d <域名> -d www.<域名> -d pc.<域名> -d h5.<域名>
sudo ln -sfn /etc/letsencrypt/live/<域名> /etc/letsencrypt/live/www.<域名>
sudo ln -sfn /etc/letsencrypt/live/<域名> /etc/letsencrypt/live/pc.<域名>
sudo ln -sfn /etc/letsencrypt/live/<域名> /etc/letsencrypt/live/h5.<域名>

# 4) 生效
sudo nginx -t && sudo systemctl reload nginx
```

## 二、纯 H5

```bash
# 1) DNS：h5.<域名>  A -> 16.208.38.88

# 2) 改 conf：20-youdianse-prod-unified.conf
#    server_name ... h5.<域名>;
#    （默认即为 h5 模式，无需改 maps）

# 3) 证书（二选一）
#    A. 独立签发：
sudo certbot certonly --webroot -w /var/www/html -d h5.<域名>
#    B. 主域名证书已覆盖 h5 子域，直接软链：
sudo ln -sfn /etc/letsencrypt/live/<主域名> /etc/letsencrypt/live/h5.<主域名>

# 4) 生效
sudo nginx -t && sudo systemctl reload nginx
```

## 三、纯 PC

```bash
# 1) DNS：pc.<域名>  A -> 16.208.38.88

# 2) 改 conf：20-youdianse-prod-unified.conf
#    server_name ... pc.<域名>;
#    （pc.* 自动识别为 pc 模式）

# 3) 证书（同 H5，二选一）
sudo certbot certonly --webroot -w /var/www/html -d pc.<域名>
# 或
sudo ln -sfn /etc/letsencrypt/live/<主域名> /etc/letsencrypt/live/pc.<主域名>

# 4) 生效
sudo nginx -t && sudo systemctl reload nginx
```

## 四、老 H5 域名按 UA 分流（电脑→PC、手机→H5，域名不变）

```bash
# 1) DNS：老域名 A/CNAME -> 16.208.38.88（或经 CDN 回源到本机）

# 2) 改 conf：20-youdianse-prod-unified.conf
#    server_name ... <老域名>;
#    并在 10-youdianse-prod-maps.conf 的 $h5pc_mode 加：
#    <老域名> ua;

# 3) 证书
sudo certbot certonly --webroot -w /var/www/html -d <老域名>

# 4) 生效
sudo nginx -t && sudo systemctl reload nginx
```

## SSL 通用要点

```bash
# 证书目录约定：每个被服务主机名都要有 /etc/letsencrypt/live/<主机名>/（真实目录或软链）
# nginx 按 SNI 自动选择对应证书

# 签发（webroot 方式，服务器 80 需可访问）
sudo certbot certonly --webroot -w /var/www/html -d <域名> [-d www.<域名> -d pc.<域名> -d h5.<域名>]

# 软链：子域证书与主域一致
sudo ln -sfn /etc/letsencrypt/live/<主域名> /etc/letsencrypt/live/<子域>

# 权限（nginx worker 读取）
sudo chmod 755 /etc/letsencrypt/live /etc/letsencrypt/archive
sudo chmod 755 /etc/letsencrypt/archive/*/
sudo chmod 644 /etc/letsencrypt/archive/*/*.pem

# 自动续期：cron 每天 03:10 自动 certbot renew；新证书如需脚本管理，
# 把域名加入 /usr/local/bin/youdianse-prod-h5pc-ssl-renew.sh 的 DOMAINS 列表
```

## 验证

```bash
curl -sk -o /dev/null -w "%{http_code}\n" https://<域名>/
echo | openssl s_client -servername <域名> -connect 16.208.38.88:443 2>/dev/null | openssl x509 -noout -subject
```

## 备注

- 存量老 H5 域名已全部加入 `30-youdianse-prod-h5.conf`（84 个主机），无需重复添加。
- 未配证书的主机直连 HTTPS 会提示证书不符（占位证书）；对外 TLS 由 AWS CDN 提供，CDN 回源改到本机后生效。
