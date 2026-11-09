---
id: "doc-2cceaae4a53e"
title: "glances 监控安装"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "监控告警", "Glances", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84419123.html"
---

# glances 监控安装

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BLinux%2B%E7%9B%91%E6%8E%A7%E5%91%8A%E8%AD%A6-glances%20%E7%9B%91%E6%8E%A7%E5%AE%89%E8%A3%85.md)

**linux虚拟终端后台常驻启动 （防火墙开61208）**

```bash
yum -y install epel-release screen glances python2-bottle.noarch
使用-R 创建虚拟终端：
screen -R glances
创建好虚拟终端后运行程序
glances -w
这个时候，我们按Ctrl+a，再按d，即可保持glances后台常驻
```

****任意一台linux机器执行 bash glances.sh_34.96.164.233 就能看监控情况****

![文档配图](../media/ee9542e32aa6deab17.png)
