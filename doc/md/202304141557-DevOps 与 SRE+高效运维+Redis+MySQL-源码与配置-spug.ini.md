---
id: "doc-3f7ff96380c0"
title: "spug.ini"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "Redis", "MySQL", "Nginx", "SQL注入", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/spug.ini_68650150.html"
---

# spug.ini

```
[supervisord]
nodaemon=true[program:nginx]
command = nginx -g "daemon off;"
autostart = true[program:redis]
command = redis-server /etc/redis.conf
autostart = true[program:mariadb]
command = /usr/libexec/mysqld --user=mysql
autostart = true[program:spug-api]
command = sh /data/spug/spug_api/tools/start-api.sh
autostart = true
stdout_logfile = /data/spug/spug_api/logs/api.log
redirect_stderr = true[program:spug-ws]
command = sh /data/spug/spug_api/tools/start-ws.sh
autostart = true
stdout_logfile = /data/spug/spug_api/logs/ws.log
redirect_stderr = true[program:spug-worker]
command = sh /data/spug/spug_api/tools/start-worker.sh
autostart = true
stdout_logfile = /data/spug/spug_api/logs/worker.log
redirect_stderr = true[program:spug-monitor]
command = sh /data/spug/spug_api/tools/start-monitor.sh
autostart = true
startsecs = 3
stdout_logfile = /data/spug/spug_api/logs/monitor.log
redirect_stderr = true[program:spug-scheduler]
command = sh /data/spug/spug_api/tools/start-scheduler.sh
autostart = true
startsecs = 3
stdout_logfile = /data/spug/spug_api/logs/scheduler.log
redirect_stderr = true
```
