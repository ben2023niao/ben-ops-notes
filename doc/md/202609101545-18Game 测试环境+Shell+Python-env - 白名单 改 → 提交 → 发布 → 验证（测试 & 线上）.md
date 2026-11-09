---
id: "doc-7616707b0e84"
title: "env / 白名单 改 → 提交 → 发布 → 验证（测试 & 线上）"
date: "2026-09-10T15:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-10_1545-%E3%80%90%E6%93%8D%E4%BD%9C%E6%8C%87%E5%8D%97%E3%80%91%E6%B5%8B%E8%AF%95%E4%B8%8E%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83env%E7%99%BD%E5%90%8D%E5%8D%95%E4%BF%AE%E6%94%B9%E6%8F%90%E4%BA%A4%E5%8F%91%E5%B8%83%E9%AA%8C%E8%AF%81.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-10_1545-【操作指南】测试与线上环境env白名单修改提交发布验证.md"
sourceSha256: "e750da41150dbae7e665efb34d78224b73394c4aaeb86315bd5b233d80f20841"
sourceSystem: "project-doc"
---

# env / 白名单 改 → 提交 → 发布 → 验证（测试 & 线上）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609101545-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-env%20-%20%E7%99%BD%E5%90%8D%E5%8D%95%20%E6%94%B9%20%E2%86%92%20%E6%8F%90%E4%BA%A4%20%E2%86%92%20%E5%8F%91%E5%B8%83%20%E2%86%92%20%E9%AA%8C%E8%AF%81%EF%BC%88%E6%B5%8B%E8%AF%95%20%26%20%E7%BA%BF%E4%B8%8A%EF%BC%89.md)

> 整理日期：2026-09-10 15:45｜日期依据：文件名日期

@Ben_Bird @Kermit0824 @jett_yunwei @melo_sre @Daviea2 @wangyi00001

## 记住一句话

**只改配置仓库，不改服务器；测试自动生效，线上必须点按钮。**

---

## 测试环境

| 项目 | 内容 |
| --- | --- |
| 仓库 | https://18game.18git.com/root/docker-youdianse-php-config-dev |
| 分支 | main |
| 改文件 | env/.env.dev、app-local-files/alb_white.txt、alb_white_secret.txt |
| 按钮 | ⚙️🧪⚙️ 测试环境-游点涩-配置-发版 |
| 怎么发 | 提交 main 后 1-2 分钟自动生效；急/指定版本点按钮选 git id |
| 怎么验证 | last_commit/last_ref = 你发的 id；admin/cicd/h5 = 200 |
| 回滚 | 按钮选上一个正常的 git id 再发 |

验证命令（测试机 15.152.247.196）：

```bash
cd /opt/docker-youdianse-php
sudo cat cicd-web/runtime/config-repo.last_commit
sudo cat cicd-web/runtime/config-repo.last_ref
curl -s -o /dev/null -w 'admin=%{http_code}\n' http://203.0.113.1:8088/admin1866/login
curl -s -o /dev/null -w 'cicd=%{http_code}\n' http://203.0.113.1:18090
curl -s -o /dev/null -w 'h5=%{http_code}\n' https://h5.youdianse-test.xyz/version.json
```

---

## 线上环境

| 项目 | 内容 |
| --- | --- |
| 仓库 | https://18game.18git.com/root/docker-youdianse-php-config-main |
| 分支 | main |
| 改文件 | env/.env.prod、app-local-files/alb_white.txt、alb_white_secret.txt |
| 按钮 | ⚙️🚀⚙️ 线上环境-游点涩-配置-发版 |
| 怎么发 | 不会自动发！必须点按钮选 git id（重建 web/nginx/cron） |
| 怎么验证 | 宿主机/web/cron 的 env sha256 一致；admin/cicd = 200 |
| 回滚 | 按钮选上一个正常的 git id 再发 |

验证命令（线上 16.209.16.108）：

```bash
cd /opt/docker-youdianse-php
sudo cat cicd-web/runtime/config-repo.last_commit
sudo cat cicd-web/runtime/config-repo.last_ref
sudo sha256sum env/.env.prod
sudo docker exec youdianse-main-php-web sha256sum /var/www/html/youdianse-php/.env
sudo docker exec youdianse-main-php-cron sha256sum /var/www/html/youdianse-php/.env
curl -s -o /dev/null -w 'admin=%{http_code}\n' http://203.0.113.1:8088/admin1866/login
curl -s -o /dev/null -w 'cicd=%{http_code}\n' http://203.0.113.1:18090
```

---

## 红线

1. 只改配置仓库；不要直接改服务器 /opt 里的 env（会被覆盖）。
2. 配置值、白名单、token 不发群。
3. 发布失败先看按钮回执，修好再重发。
