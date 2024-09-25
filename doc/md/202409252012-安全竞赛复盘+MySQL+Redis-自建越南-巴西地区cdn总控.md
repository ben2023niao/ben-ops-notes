---
id: "doc-b36148a47c13"
title: "自建越南/巴西地区cdn总控"
date: "2024-09-25T20:12:27.347000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["技术履历与演练复盘", "安全竞赛复盘"]
tags: ["安全竞赛复盘", "MySQL", "Redis", "CDN", "安全运维", "故障排查"]
source: "https://ji-shu-jian-li.gitbook.io/ben_bird/zi-jian-yue-nan-ba-xi-di-qu-cdn-zong-kong.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "7eac65fa25e12ead83efcfe9328579784872823242ee4155ca2a6dd4a9c66a08"
---

# 自建越南/巴西地区cdn总控

> 原文：[自建越南/巴西地区cdn总控](https://ji-shu-jian-li.gitbook.io/ben_bird/zi-jian-yue-nan-ba-xi-di-qu-cdn-zong-kong.html)

> 来源：GitBook 网页 HTML｜页面时间：2024-09-25 20:12｜日期依据：GitBook 页面更新时间

![文档配图 1](../media/5d99fe9f5ea57a6fb9.png)

![文档配图 2](../media/3961a9fbb09c5133b4.jpg)

![文档配图 3](../media/d0a4ba36d05b22bc02.jpg)

![文档配图 4](../media/7e1c2b5f5cb426b746.jpg)

![文档配图 5](../media/8f3525f9b1cbe623d0.jpg)

![文档配图 6](../media/35b3c1ee9ecc84ba91.png)

1 <示例地址> 下载CDN主控

![文档配图 7](../media/cbfc490beb3d1cf172.png)

2 <示例地址> 下载

## Windows Server 2016

系统镜像

![文档配图 8](../media/396257b39df2536e39.png)

3 虚拟机安装

![文档配图 9](../media/dfe05857ef8e46d8cf.png)

**准备阶段**

a. 单核 CPU 即可，内存大于 **4GB** 即可。

b. Windows Server 2012/2016 操作系统 64 位版本。

c. 安装包已集成 Apache + PHP + mySQL 等服务，无需再额外安装。

d. 推荐使用Chrome谷歌浏览器进行登陆管理。

**特别注意**：默认情况下，新界面版与经典版主控都使用了相同的Apache 1280端口和mySQL 8816端口，须分开安装之。

**第一步：默认必须将 FikkerCDN-NewUI.rar 安装包解压到 D 盘根目录下面**

![文档配图 10](../media/cc91f47729dec77a14.png)

注：默认必须安装在 **D** 盘的根目录下，如上图所示。

注：最常见的错误为安装到 **D:\FikkerCDN-NewUI\FikkerCDN-NewUI** 目录下面了。

注：如需更改默认 **D:\FikkerCDN-NewUI** 安装目录，参看 <[有关 CDN 主控(新界面版)的几个常问问题](示例地址)> **★★★★★**

**第二步：安装 vcredist目录下的 vs10/vs15 微软运行库**

![文档配图 11](../media/4f937fc56991bc755b.png)

**第三步：注册服务/启动服务**

a. 运行【**注册服务.bat**】，将主控注册成系统服务。

b. 运行【**启动服务.bat**】，将系统服务立即启动起来。

c. 为了减少不必要的冲突，关闭Windows防火墙/xx盾/xx锁/xx狗等，阿里云服务器需设置安全组并开启端口1280等。

**第四步：登录后台 - 推荐Chrome谷歌浏览器**

管理员

登录地址: 示例地址 登录帐号：admin，初始密码：123qwe

用户端

登录地址：示例地址 说明: 用户端帐号由用户创建或管理员创建/删除/冻结。

注：默认为 **1280** 端口，主要是避免与 80 端口冲突和尽量避免备案。

注：如需更改默认 **1280** 端口，参看 <[有关 CDN 主控(新界面版)的几个常问问题](示例地址)> **★★★★★**

**截图示例：**

![文档配图 12](../media/a3fac6dfb602cdfde8.png)
