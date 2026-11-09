---
id: "doc-b2769786d9a4"
title: "【配置维护】线上环境 pay.callback 回调域名更新同步记录"
date: "2026-08-20T14:49:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "监控告警", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-1449-%E3%80%90%E9%85%8D%E7%BD%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83pay.callback%E5%9B%9E%E8%B0%83%E5%9F%9F%E5%90%8D%E6%9B%B4%E6%96%B0%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-1449-【配置维护】线上环境pay.callback回调域名更新同步记录.md"
sourceSha256: "1309a1deb48403ffd9e3bae9c770c8b5cc4eaa9505ef39e6b2c01fc12797bae2"
sourceSystem: "project-doc"
---

# 【配置维护】线上环境 pay.callback 回调域名更新同步记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608201449-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E3%80%90%E9%85%8D%E7%BD%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20pay.callback%20%E5%9B%9E%E8%B0%83%E5%9F%9F%E5%90%8D%E6%9B%B4%E6%96%B0%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-20 14:49｜日期依据：文件名日期

文档日期：2026-08-20 14:49
环境：游点涩线上环境（main 分支）
分类：配置维护
标签：线上环境、env、pay.callback、回调域名、配置同步、容器重建

## 工单

```text
平台：youdianse / 后端 / 正式环境
开发/测试：@booter23
运维：@melo_sre @Kermit0824 @jett_yunwei @Ben_Bird @Daviea2
内容：更新 env/.env.prod [pay.callback] urls：
  旧：https://shyssjt.com,https://xinjiangzhilianyun.com,https://feng-gou.com
  新：https://h5.game-app543.com,https://www.youdianse.com
```

## 背景

群内反馈“支付都挂了”“配置没同步”：远端 main 已提交该 env 修改（f285874），
但线上服务器 env/.env.prod 仍是旧值，容器也未生效。

## 未同步根因

```text
1. 服务器工作树存在未提交改动（本次会话的 nginx/监控配置），cicd-web-auto-update 检测到
   dirty 后跳过自动 pull，env 修改未拉取；
2. sed -i 修改文件会换 inode，而 docker bind mount 挂的是旧 inode，
   只改宿主机文件不会反映到容器内（容器内仍是旧值）。
```

## 处理

```text
1. 服务器 env/.env.prod [pay.callback] urls 直接改为新值；
2. docker compose up -d --force-recreate web nginx cron 重新挂载；
3. 验证容器内 .env 为新值；admin/CICD/登录接口 200。
```

## 验证结果

```text
容器内 /var/www/html/youdianse-php/.env：
  [pay.callback]
  urls=https://h5.game-app543.com,https://www.youdianse.com
admin 200 / cicd 200 / 登录接口 200；web/nginx/cron 全部 Up。
```

## 风险提示

```text
h5.game-app543.com 当前被菲律宾访问策略验证页 302 拦截（blocked.sbmd.cicc.gov.ph），
作为支付回调域名可能收不到回调；需与开发确认该域名恢复后再用于支付。
www.youdianse.com 正常。
```

## 经验沉淀

```text
1. 线上 env 修改后必须重建容器（bind mount 按 inode 生效）；
2. 服务器工作树保持干净，避免自动更新跳过配置同步；
3. 支付回调域名上线前应做可达性校验（禁止 302/访问策略验证页）。
```

## 通知记录

```text
步骤 1 pay.callback urls 更新并同步   message_id 10098
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据；env 仅展示回调域名配置节。
