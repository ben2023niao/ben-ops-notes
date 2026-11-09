---
id: "doc-93bf7c5bc058"
title: "前端域名维护脚本 日常操作笔记"
date: "2026-08-12T17:28:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1728-%E3%80%90%E6%93%8D%E4%BD%9C%E7%AC%94%E8%AE%B0%E3%80%91%E5%89%8D%E7%AB%AF%E5%9F%9F%E5%90%8D%E7%BB%B4%E6%8A%A4%E8%84%9A%E6%9C%AC%E6%97%A5%E5%B8%B8%E4%BD%BF%E7%94%A8.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1728-【操作笔记】前端域名维护脚本日常使用.md"
sourceSha256: "072870bdf490f91d49fc767aef55a9b583be54ff299e4fac3d4fb9f59067c05b"
sourceSystem: "project-doc"
---

# 前端域名维护脚本 日常操作笔记

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608121728-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E5%89%8D%E7%AB%AF%E5%9F%9F%E5%90%8D%E7%BB%B4%E6%8A%A4%E8%84%9A%E6%9C%AC%20%E6%97%A5%E5%B8%B8%E6%93%8D%E4%BD%9C%E7%AC%94%E8%AE%B0.md)

> 整理日期：2026-08-12 17:28｜日期依据：文件名日期

环境标签：线上环境 / 游点涩 / 域名维护 / SSL / 16.208.38.88

时间：2026-08-12 17:28（Asia/Manila）

> 脚本：`/usr/local/bin/youdianse-domain-maint.py`（服务器 16.208.38.88）
> 一句话：以后前端加域名 / 做证书 / 续签 / 检查，都走这一个脚本。

## 通用

```bash
sudo python3 /usr/local/bin/youdianse-domain-maint.py <命令> [参数]
```

域名模式：`redirect`（www/@ 自动跳 pc/h5）、`h5`（纯 H5）、`pc`（纯 PC）、`ua`（老域名按设备分流，电脑→PC/手机→H5）。

## 一、增加域名（脚本自动改 conf + maps，改前备份、改后 nginx -t && reload）

```bash
# pc+h5 跳转类（DNS 需 @ www pc h5 四条 A -> 16.208.38.88）
sudo python3 /usr/local/bin/youdianse-domain-maint.py add <域名> --type redirect --cert

# 纯 H5（DNS 需 h5.<域名> A -> 16.208.38.88）
sudo python3 /usr/local/bin/youdianse-domain-maint.py add <域名> --type h5 --cert

# 纯 PC（DNS 需 pc.<域名> A -> 16.208.38.88）
sudo python3 /usr/local/bin/youdianse-domain-maint.py add <域名> --type pc --cert

# 老 H5 域名按设备分流（电脑→PC、手机→H5，域名不变）
sudo python3 /usr/local/bin/youdianse-domain-maint.py add <老域名> --type ua --cert
```

先演练不落盘：加 `--dry-run`。

## 二、制作 SSL 证书

```bash
# 单域名
sudo python3 /usr/local/bin/youdianse-domain-maint.py cert -d <域名>

# 多 SAN（pc+h5 跳转类）
sudo python3 /usr/local/bin/youdianse-domain-maint.py cert -d <域名> -d www.<域名> -d pc.<域名> -d h5.<域名> --subs pc,h5,www
```

脚本会自动：移除占位软链 → certbot webroot 签发 → 把 `live/<域名>` 指到真实证书 → 建 `pc./h5./www.` 软链 → 放通 nginx 读取权限。

## 三、续签 SSL（cron 每天 03:10 也会自动跑）

```bash
sudo python3 /usr/local/bin/youdianse-domain-maint.py renew
```

## 四、检查域名（DNS / HTTPS / 版本 / 证书到期 / 模式）

```bash
# 指定域名
sudo python3 /usr/local/bin/youdianse-domain-maint.py check <域名> [<域名>...]

# 全部域名
sudo python3 /usr/local/bin/youdianse-domain-maint.py check
```

## 验证

```bash
sudo nginx -t
curl -sk https://<域名>/version.json
echo | openssl s_client -servername <域名> -connect 16.208.38.88:443 2>/dev/null | openssl x509 -noout -subject
```

## 备注

- 证书目录约定：每个被服务主机名都要有 `/etc/letsencrypt/live/<主机名>/`（真实目录或软链），nginx 按 SNI 自动选。
- 纯 H5 不用改 maps（默认 h5）；`pc.*` 自动识别 pc；`redirect`/`ua` 由脚本写 `$h5pc_mode`。
- 自动续期脚本 `youdianse-prod-h5pc-ssl-renew.sh`（cron 03:10）已包含全部证书续期与到期检查。

> 2026-08-12 起：`$h5pc_mode` 默认值已从 h5 改为 **ua**（全部域名按设备分流：手机→H5、电脑→PC）。脚本 `mode_of` 已同步默认 ua；新增域名时 h5/pc 类型会显式写入模式（h5→h5、pc→pc），ua/redirect 照旧写模式，避免依赖默认值产生漂移。机器人快速检查的模式列现在会显示 UA适配。

> 2026-08-12 再更新：统一 conf 的 `/api|channel|customer` 上游已改为**宝塔内网 `203.0.113.1` + SNI/Host `www.youdianse.com`**（原 `www.youdianse.com` 的 DNS 切到新 CloudFront 后会自指循环 403）。机器人域名维护/SSL续签不依赖该上游，无需改代码；发布脚本的浏览器端 `VITE_API_URL` 仍为 `https://www.youdianse.com`（链路已通）。
