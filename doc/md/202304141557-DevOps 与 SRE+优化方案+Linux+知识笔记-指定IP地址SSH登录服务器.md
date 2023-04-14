---
id: "doc-80ac6fa541f3"
title: "指定IP地址SSH登录服务器"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/72069789.html"
---

# 指定IP地址SSH登录服务器

在Linux实例中分别通过配置`/etc/hosts.allow`和`/etc/hosts.deny`这两个文件，拒绝或者允许指定的IP及IP地址段通过SSH远程登录服务器。分别介绍如下。

- **/etc/hosts.allow**

```
#编辑/etc/hosts.allow文件，添加类似如下的内容，只允许指定IP地址通过SSH登录。
sshd:203.0.113.1:allow #允许192.168.1.1这个IP地址通过SSH登录。
sshd:203.0.113.1/24:allow #允许192.168.2.1/24这个IP地址段通过SSH登录。
```

- **/etc/hosts.deny**

```
#编辑/etc/hosts.deny文件，添加类似如下的内容，拒绝所有IP地址通过SSH登录。
sshd:ALL # 拒绝全部的SSH登录
```

同时设置上述两个文件时，hosts.allow文件中规则的优先级更高，参考上述两个文件进行设置时，服务器只允许192.168.1.1这个IP地址以及192.168.2.1/24这个IP地址段通过SSH进行登录，其他的IP都会被拒绝SSH登录。
