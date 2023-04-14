---
id: "doc-d3cebfacbaaf"
title: "PHP-laravel自动化构建发布"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "PHP", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68649784.html"
---

# PHP-laravel自动化构建发布

![文档配图](../media/16c4c85080739ad8b6.png)![文档配图](../media/52172fde953545391a.png)

```bash
#!/bin/bash
cd /www/wwwroot/zn-admin/stock/
bash git-pull.sh
cd /www/wwwroot/en-admin/stock/
bash git-pull.sh
cd /www/wwwroot/vn-admin/stock/
bash git-pull.sh
cd /www/wwwroot/zh-admin/stock/
bash git-pull.sh
```

## git-pull.sh 脚本内容

## git fetch --all ; git reset --hard origin/pingan_zk ; git pull ; git log -1
