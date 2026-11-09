---
id: "doc-cc16ddd19fc3"
title: "Cymothoa 后门"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "MySQL", "Apache", "SQL注入", "恶意代码", "权限管理", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68652731.html"
---

# Cymothoa 后门

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4%2BMySQL%2BApache-Cymothoa%20%E5%90%8E%E9%97%A8.md)

## 【false】Cymothoa

cymothoa 是一个后门工具，利用代码 shellcode 会被注入到进程中，只要进程存在，后门就会有效，所以一般选择一些自启服务的进程来注入，例如 web 服务 mysql，apache 等。其后门所拥有的权限和注入的进程权限是相同的。当拿下目标 shell 后就可以使用 cymothoa 添加后门了。

**使用：**

下载，进入Cymothoa，运行

```
./cymothoa -S  #列出可用的shellcode
```

`![文档配图](../media/8faf746c3a1b8ef4c9.png)`

这里我们就用序号 1 这个 payload，通过端口来反向 shell。使用**-p**参数，用来指定需要注入的进程的 pid， **- s**，用来指定使用 shellcode 的序号，**-y**用来指定反向 shell 的端口，即别人连接自己时需要连接的端口。运行后当出现 infected 即感染的意思则代表后门注入成功。

 `![文档配图](../media/5548b27376bcf8a757.png)`

没成功，先没管了。。。
