---
id: "doc-d3cebfacbaaf"
title: "PHP-laravel自动化构建发布"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "PHP", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68649784.html"
---

# PHP-laravel自动化构建发布

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2BPHP%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-PHP-laravel%E8%87%AA%E5%8A%A8%E5%8C%96%E6%9E%84%E5%BB%BA%E5%8F%91%E5%B8%83.md)

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
