---
id: "doc-c702afac560b"
title: "程序漏洞导致Docker逃逸 （Shocker 攻击）"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Linux", "Docker", "漏洞", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68652200.html"
---

# 程序漏洞导致Docker逃逸 （Shocker 攻击）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4%2BLinux%2BDocker-%E7%A8%8B%E5%BA%8F%E6%BC%8F%E6%B4%9E%E5%AF%BC%E8%87%B4Docker%E9%80%83%E9%80%B8%20%EF%BC%88Shocker%20%E6%94%BB%E5%87%BB%EF%BC%89.md)

## **Shocker 攻击**

漏洞描述：从Docker容器逃逸并读取到主机某个目录的文件内容。Shocker攻击的关键是执行了系统调用open_by_handle_at函数，Linux手册中特别提到调用open_by_handle_at函数需要具备CAP_DAC_READ_SEARCH能力，而Docker1.0版本对Capability使用黑名单管理策略，并且没有限制CAP_DAC_READ_SEARCH能力，因而引发了容器逃逸的风险。

漏洞影响版本： Docker版本< 1.0， 存在于 Docker 1.0 之前的绝大多数版本

（真实环境基本不会存在了）

github项目地址：[gabrtv/shocker: Shocker / Docker Breakout PoC (github.com)](https://github.com/gabrtv/shocker)
![文档配图](../media/e0733be4232494b9f8.png)
