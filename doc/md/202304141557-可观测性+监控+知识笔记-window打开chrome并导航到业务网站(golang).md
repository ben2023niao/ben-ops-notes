---
id: "doc-9837ec83d1ab"
title: "window打开chrome并导航到业务网站(golang)"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/66979898.html"
---

# window打开chrome并导航到业务网站(golang)

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7%2B%E7%9B%91%E6%8E%A7%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-window%E6%89%93%E5%BC%80chrome%E5%B9%B6%E5%AF%BC%E8%88%AA%E5%88%B0%E4%B8%9A%E5%8A%A1%E7%BD%91%E7%AB%99%28golang%29.md)

```
```

![文档配图](../media/74db43770458664053.png)

```
C:\Program Files\Google\Chrome\Application 路径下打开 git-bash
./chrome.exe https://confluence.bssrv.com/
如果浏览器的安装路径中有空格，可以用“ ”代替，如下：

C:\Program Files\Mozilla Firefox\firefox.exe

可以替换为C:\Program" "Files\Mozilla" "Firefox\firefox.exe

1、用IE浏览器打开网页的批处理代码：start c:\progra~1\Intern~1\iexplore.exe 网址

例子：

@echo off
title 打开网页
start c:\progra~1\Intern~1\iexplore.exe "http://www.baidu.com"
2、用谷歌浏览器打开网页的批处理代码：安装路径 网址

例子：

@echo off
title 打开网页
start C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe http://www.google.com.hk
3、用火狐浏览器打开网页的批处理代码：安装路径 网址

例子：

@echo off
title 打开网页
start C:\Program" "Files\Mozilla" "Firefox\firefox.exe "http://www.163.com"
4、批量打开网页的代码(转载)：

@echo off
mode con lines=16
title 批量打开网页
color 2f
cls
echo.
echo 现在是 %date% %time%echo
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
start www.baidu.com
start www.jb51.net
echo 开启完成，正在返回！
5、关闭浏览器的批处理代码：

@echo off
title 结束进程
taskkill /f /t /im iexplore.exe
taskkill /f /t /im chrome.exe
taskkill /f /t /im firefox.exe
```
