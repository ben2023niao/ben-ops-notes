---
id: "doc-55ed9d134d41"
title: "start-scheduler.sh"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/start-scheduler.sh_68650282.html"
---

# start-scheduler.sh

```bash
#!/bin/bash
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
# start schedule servicecd $(dirname $(dirname $0))
if [ -f ./venv/bin/activate ]; then
source ./venv/bin/activate
fiif command -v python3 &> /dev/null; then
PYTHON=python3
else
PYTHON=python
fiexec $PYTHON manage.py runscheduler
```
