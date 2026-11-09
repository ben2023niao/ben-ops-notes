---
id: "doc-3bbc0d2badef"
title: "域名检测告警功能方案-目前最完美方案"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Docker", "监控告警", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/66979525.html"
---

# 域名检测告警功能方案-目前最完美方案

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BDocker%2B%E7%9B%91%E6%8E%A7%E5%91%8A%E8%AD%A6-%E5%9F%9F%E5%90%8D%E6%A3%80%E6%B5%8B%E5%91%8A%E8%AD%A6%E5%8A%9F%E8%83%BD%E6%96%B9%E6%A1%88-%E7%9B%AE%E5%89%8D%E6%9C%80%E5%AE%8C%E7%BE%8E%E6%96%B9%E6%A1%88.md)

利用百度统计 在前台代码加 js 方式自动化收集域名方式

服务端部署
docker run -it --rm -d --name webfunny -p 8011:8011 -p 8010:8010 -v 映射目录:/app/config_variable/ webfunny/webfunny_monitor:版本号
心跳检测地址： 域名 + /server/health

监控项目端
进入项目设置页（projectSetting.html），复制探针代码，安插到域名项目的html中 （类似加百度统计）

参考项目详细官方文档
<https://www.webfunny.cn/des.html>

效果图

![文档配图](../media/d52754d64d5e2a7722.png)

![文档配图](../media/86dde2f0ad971cfcc6.png)

![文档配图](../media/f56a4351cd21575c77.png)
![文档配图](../media/b57b6b51f9d8ec3a94.png)
![文档配图](../media/01ad2f4f594927fdc8.png)
![文档配图](../media/f132929931691ec2da.png)

![文档配图](../media/0eab3f4c82c3010077.png)
![文档配图](../media/6a1d4d23af9c5dca3c.png)
![文档配图](../media/f4b753d9c240e118be.png)
![文档配图](../media/16d45671c0a62f2d41.png)
![文档配图](../media/914c5c16da9dad3f45.png)
![文档配图](../media/2dace2c70aa59870af.png)
![文档配图](../media/1c1650edb7b77ce49c.png)
![文档配图](../media/c78860aecdeb611079.png)
![文档配图](../media/c288d943970ecbd350.png)
