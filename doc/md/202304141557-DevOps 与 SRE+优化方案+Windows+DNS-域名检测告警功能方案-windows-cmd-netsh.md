---
id: "doc-c66368d0184d"
title: "域名检测告警功能方案-windows-cmd-netsh"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Windows", "DNS", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/66979519.html"
---

# 域名检测告警功能方案-windows-cmd-netsh

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BWindows%2BDNS-%E5%9F%9F%E5%90%8D%E6%A3%80%E6%B5%8B%E5%91%8A%E8%AD%A6%E5%8A%9F%E8%83%BD%E6%96%B9%E6%A1%88-windows-cmd-netsh.md)

Windows 下切换 DNS 的批处理脚本

贡献两个批处理脚本，双击切换DNS服务器：

切换成静态DNS服务器，其中第一行是primary，第二行是secondary

```
netsh interface ip set dns local static 203.0.113.1
netsh interface ip add dns local 203.0.113.1
```

使用dhcp自动获取dns服务器

```
netsh interface ip set dns local dhcp
```

```bash
注意这两个脚本里的local需要换成你自己的网络连接的名字，你可以通过netsh interface ip show dns来查看你当前的网络连接的名字以及DNS服务器列表

然后windows电脑安装 git
打开git-bash
编写脚本
for www in baidu.com xxx.com ; do
for dns_ip in 203.0.113.1 203.0.113.1 203.0.113.1 ; do
netsh interface ip add dns local $dns_ip
#更换dns后请求域名
curl $www
done
done
```
