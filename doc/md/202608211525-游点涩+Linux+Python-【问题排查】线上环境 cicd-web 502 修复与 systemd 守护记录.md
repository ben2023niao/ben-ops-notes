---
id: "doc-5ce958c4b743"
title: "【问题排查】线上环境 cicd-web 502 修复与 systemd 守护记录"
date: "2026-08-21T15:25:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Python", "Docker", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-21-1525-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83cicd-web502%E4%BF%AE%E5%A4%8D%E4%B8%8Esystemd%E5%AE%88%E6%8A%A4%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-21-1525-【问题排查】线上环境cicd-web502修复与systemd守护记录.md"
sourceSha256: "77fdb7ec7b00fe4816bd5b593573fb54e84a16eb3bad0f5b168bedc7d72fa77f"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境 cicd-web 502 修复与 systemd 守护记录

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-21-1525-【问题排查】线上环境cicd-web502修复与systemd守护记录.md`

> 整理日期：2026-08-21 15:25｜日期依据：文件名日期

文档日期：2026-08-21 15:25
环境：游点涩线上环境（main 分支）
分类：问题排查 / 高可用加固
标签：线上环境、cicd-web、502、扩容、systemd、自启守护

## 背景

2026-08-21 线上后端服务器扩容（4核7.5G -> 16核30G，实例重建）后，
`https://cicd.youdianse-main.xyz` 返回 502（宝塔反代到后端 18090 失败）。

## 根因

```text
cicd-web 此前由 nohup 手动启动（无守护、未加入开机自启），
AWS 扩容重建实例后进程未自动拉起：进程不存在、18090 未监听，
宝塔反代 upstream 不可达 -> 502。
pid 文件仍为旧实例 4151104（重启后失效）。
```

## 处置

```text
1. 重新启动 cicd-web（PID 18931），18090 监听恢复，本地 200；
2. 外网 https://cicd.youdianse-main.xyz 恢复 200（宝塔反代链路正常）；
3. 新增 systemd 守护 /etc/systemd/system/cicd-web.service：
   - ExecStart=cicd-web/runtime/venv/bin/python cicd-web.py --host 0.0.0.0 --port 18090
   - WorkingDirectory=/opt/docker-youdianse-php
   - Restart=always、RestartSec=5、User=root
   - systemctl enable cicd-web（开机自启）+ start
```

## 验证

```text
1. systemctl is-active cicd-web = active；
2. 18090 监听正常（PID 19252），本地 curl 200；
3. 宝塔 -> 后端 18090 open；外网 https://cicd.youdianse-main.xyz 200。
```

## 后续

```text
1. 扩容/重启实例后 cicd-web 由 systemd 自动拉起，不再出现 502；
2. 进程崩溃自动重启（Restart=always）；
3. 后续巡检可纳入 systemctl status cicd-web。
```

## 通知记录

```text
步骤 1：cicd 502 根因（扩容重启后 cicd-web 未自动拉起）
步骤 2：cicd 502 修复成功，外网访问恢复 200
步骤 3：cicd-web 已纳入 systemd 守护
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据。
