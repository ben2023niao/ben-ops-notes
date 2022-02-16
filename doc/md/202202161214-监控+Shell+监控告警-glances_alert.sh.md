---
id: "doc-aeeadf89d0db"
title: "glances_alert.sh"
date: "2022-02-16T12:14:26.168000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["可观测性", "监控"]
tags: ["监控", "Shell", "监控告警", "Telegram", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/jian-kong/glances-jian-kong-bu-shu/glances_alert.sh.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "fc2225c46065f7a5439aa646c2c4ffd6866cc6515665bb080455175034a97d07"
---

# glances_alert.sh

> 原文：[glances_alert.sh](https://xn--6o0a585a.gitbook.io/devops/jian-kong/glances-jian-kong-bu-shu/glances_alert.sh.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-02-16 12:14｜日期依据：GitBook 页面更新时间

```bash
#!/bin/bash
API="https://api.telegram.org/bot5035739927:AAEoN_prxkaWf7aapWH0Lgi5T8deAt4Ailk" GID="chat_id=-747209743" MSG="${API}/sendMessage?${GID}&text="
for ip in "203.0.113.1" "203.0.113.1" "203.0.113.1";do #监控服务器 IP
	if [ `curl -s "http://$ip:61208/api/3/alert" | md5sum | awk '{print $1}'` != "d751713988987e9331980363e24189ce" ];then $MSG"有报警 http://$ip:61208";fi
done
```
