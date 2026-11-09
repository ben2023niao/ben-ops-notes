---
id: "doc-4c908cad71d4"
title: "漏洞扫描-AWVS-Nessus-Docker版"
date: "2021-12-31T14:11:44.274000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全运维", "Shell", "Docker"]
source: "https://xn--6o0a585a.gitbook.io/devops/an-quan/lou-dong-sao-miao-awvsnessusdocker-ban.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "e9f7727c2e4e67da222dcbbf99fb50389837ca9db15091656e38c7d30728e483"
---

# 漏洞扫描-AWVS-Nessus-Docker版

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202112311411-%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4%2BShell%2BDocker-%E6%BC%8F%E6%B4%9E%E6%89%AB%E6%8F%8F-AWVS-Nessus-Docker%E7%89%88.md)

> 原文：[漏洞扫描-AWVS-Nessus-Docker版](https://xn--6o0a585a.gitbook.io/devops/an-quan/lou-dong-sao-miao-awvsnessusdocker-ban.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-31 14:11｜日期依据：GitBook 页面更新时间

Docker源长期及时更新，感谢雷石安全实验室。

在docker仓库已经打包好2个扫描器，分别是awvs13和nessus，供广大兄弟们使用。

```bash
# 拉取镜像
docker pull leishianquan/awvs-nessus:v2
# 启动
docker run --name awvs-nessus -it -d -p 13443:3443 -p 8834:8834 leishianquan/awvs-nessus:v2
# 查看容器
docker ps –a
# 启动容器
docker start container-id
# 进入容器
docker exec –it container-id /bin/bash

# 进入容器后，启动nessus
/etc/init.d/nessusd start

# 访问扫描器地址和账号密码
Nessus:
https://203.0.113.1:8834/#/
account:leishi/leishianquan

Awvs13:
https://203.0.113.1:13443/
account:[邮箱已脱敏]/Admin123
```
