---
id: "doc-42e10021312d"
title: "Nginx 解析漏洞"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Docker", "Nginx", "PHP", "恶意代码", "漏洞", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/84422181.html"
---

# Nginx 解析漏洞

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4%2BDocker%2BNginx-Nginx%20%E8%A7%A3%E6%9E%90%E6%BC%8F%E6%B4%9E.md)

## 一、漏洞简介

## 二、漏洞影响

- Nginx 1.x 最新版
- PHP 7.x最新版

## 三、复现过程

直接执行`docker-compose up -d`启动容器，无需编译。

访问`<http://www.0-sec.org/uploadfiles/nginx.png>`和`<http://your-ip/uploadfiles/nginx.png/.php>`即可查看效果。

正常显示：
![文档配图](../media/1e3c1045d88b5caade.png)
增加`/.php`后缀，被解析成PHP文件：执行木马
![文档配图](../media/640e30d10bf35899e0.png)
