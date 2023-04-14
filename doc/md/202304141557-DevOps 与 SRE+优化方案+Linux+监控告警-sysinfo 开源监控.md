---
id: "doc-ba9ebf2e0679"
title: "sysinfo 开源监控"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "监控告警", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/72066973.html"
---

# sysinfo 开源监控

sysinfo 使用 Python Flask 框架和 psutil 开发的一个中文版 Linux 服务器信息查看应用，可查看的信息包括系统、CPU、内存、硬盘、进程、网络、登录用户等，同时可查看并导出部分数据的图表。
<https://github.com/hypersport/sysinfo>

## 需要安装的 Python 包

- flask
- psutil
- netifaces

## 运行

1. 下载或使用 `git clone` 获取源代码
2. 进入目录执行 `python run.py` 启动应用
3. web 页面访问 [http://localhost:9468](http://localhost:9468/) ，修改 [auto-refresh.js](https://github.com/hypersport/sysinfo/blob/master/static/js/auto-refresh.js) 文件中的 `notRefresh` 可配置是否自动刷新。

## 运行截图

- 首页 / 系统信息
![文档配图](../media/fae6cbe0f5ce8724a2.png)
![文档配图](../media/a1d19304d1f34cb3f4.png)
![文档配图](../media/0f43c33883954a45f4.png)
![文档配图](../media/e1d42816e16699f122.png)

![文档配图](../media/95cb6ccc016e522562.png)
![文档配图](../media/39e759184a614390ba.png)

![文档配图](../media/9a284d4d046e28aa32.png)
![文档配图](../media/6913dc2ab4244a0e88.png)
![文档配图](../media/380be1b7a0378656e8.png)
![文档配图](../media/62e65eb7c5f30804af.png)
![文档配图](../media/12a61719f045f91b9c.png)
![文档配图](../media/8c14e9dc5eda49f857.png)
