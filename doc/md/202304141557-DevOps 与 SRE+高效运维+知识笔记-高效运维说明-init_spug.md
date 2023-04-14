---
id: "doc-f87d61bbda5f"
title: "init_spug"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/init_spug_68650142.html"
---

# init_spug

```bash
#!/bin/bash
#
set -e
set -upython3 /data/spug/spug_api/manage.py updatedb
python3 /data/spug/spug_api/manage.py user add -u $1 -p $2 -n 管理员 -s
```
