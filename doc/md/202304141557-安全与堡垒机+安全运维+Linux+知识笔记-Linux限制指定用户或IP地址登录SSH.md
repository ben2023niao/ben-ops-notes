---
id: "doc-a9c8c0170b35"
title: "Linux限制指定用户或IP地址登录SSH"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Linux", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68649555.html"
---

# Linux限制指定用户或IP地址登录SSH

## 限制用户通过SSH登录

编辑/etc/ssh/sshd_config配置文件，增加类似如下的Deny Users选项，拒绝指定用户通过SSH登录。然后重启SSH服务即可。

```
# 允许aliyun和从192.168.1.1登录的test帐户通过SSH登录系统。
AllowUsers aliyun test@203.0.113.1
# 拒绝zhangsan、aliyun帐户通过SSH登录系统。
DenyUsers zhangsan aliyun
```

## 限制IP地址通过SSH登录

除了限制某个指定用户通过SSH登录外，还可以针对指定的IP地址进行限制。在Linux实例中分别通过配置/etc/hosts.allow和/etc/hosts.deny这两个文件，拒绝或者允许指定的IP及IP地址段通过SSH远程登录服务器。分别介绍如下。

- 编辑/etc/hosts.allow文件，添加类似如下的内容，只允许指定IP地址通过SSH登录。

```
sshd:203.0.113.1:allow #允许192.168.1.1这个IP地址通过SSH登录。
sshd:203.0.113.1/24:allow #允许192.168.2.1/24这个IP地址段通过SSH登录。
```

- 编辑/etc/hosts.deny文件，添加类似如下的内容，拒绝所有IP地址通过SSH登录。

```
sshd:ALL # 拒绝全部的SSH登录
sshd:203.0.113.1:deny
```

同时设置上述两个文件时，hosts.allow文件中规则的优先级更高，参考上述两个文件进行设置时，服务器只允许192.168.1.1这个IP地址以及192.168.2.1/24这个IP地址段通过SSH进行登录，其他的IP都会被拒绝SSH登录。

配置完成后，需要重启SSH服务。
