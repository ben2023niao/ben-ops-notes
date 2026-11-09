---
id: "doc-f87d61bbda5f"
title: "init_spug"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/init_spug_68650142.html"
---

# init_spug

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%E8%AF%B4%E6%98%8E-init_spug.md)

```bash
#!/bin/bash
#
set -e
set -upython3 /data/spug/spug_api/manage.py updatedb
python3 /data/spug/spug_api/manage.py user add -u $1 -p $2 -n 管理员 -s
```
