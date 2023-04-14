---
id: "doc-2cceaae4a53e"
title: "glances 监控安装"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "监控告警", "Glances", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84419123.html"
---

# glances 监控安装

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
