---
id: "doc-184dcb79a068"
title: "start-ws.sh"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/start-ws.sh_68650286.html"
---

# start-ws.sh

```bash
#!/bin/bash
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
# start websocket servicecd $(dirname $(dirname $0))
if [ -f ./venv/bin/activate ]; then
source ./venv/bin/activate
fi
exec daphne -p 9002 spug.asgi:application
```
