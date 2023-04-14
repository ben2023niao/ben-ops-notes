---
id: "doc-1d7cd9b7c796"
title: "start-api.sh"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/start-api.sh_68650278.html"
---

# start-api.sh

```bash
#!/bin/bash
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
# start api servicecd $(dirname $(dirname $0))
if [ -f ./venv/bin/activate ]; then
source ./venv/bin/activate
fi
exec gunicorn -b 203.0.113.1:9001 -w 2 --threads 8 --access-logfile - spug.wsgi
```
