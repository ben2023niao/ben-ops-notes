---
id: "doc-6f2379853fc4"
title: "node远程执行shell命令"
date: "2021-12-27T17:23:07.286000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["通知与集成", "Telegram"]
tags: ["Telegram", "Linux", "Shell"]
source: "https://xn--6o0a585a.gitbook.io/devops/telegram-ji-qi-ren/node-yuan-cheng-zhi-xing-shell-ming-ling.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "74bd1f2a68697a5c9d7aa8a982d31285d3086ed46b0446e18066f03c50b9c584"
---

# node远程执行shell命令

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202112271723-%E9%80%9A%E7%9F%A5%E4%B8%8E%E9%9B%86%E6%88%90%2BTelegram%2BLinux-node%E8%BF%9C%E7%A8%8B%E6%89%A7%E8%A1%8Cshell%E5%91%BD%E4%BB%A4.md)

> 原文：[node远程执行shell命令](https://xn--6o0a585a.gitbook.io/devops/telegram-ji-qi-ren/node-yuan-cheng-zhi-xing-shell-ming-ling.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-27 17:23｜日期依据：GitBook 页面更新时间

### 教程

**Github地址：**<https://github.com/marknote/TeleShellBot>

**1、安装**

```
git clone https://github.com/marknote/TeleShellBot.git
cd TeleShellBot
npm install
```

`git`和`npm`安装请参考：[Debian/Ubuntu/CentOS安装最新版的Node.js和NPM教程](https://www.moerats.com/archives/328/)，[Debian/Ubuntu/CentOS安装Git教程](https://www.moerats.com/archives/216/)。

**2、配置**
根据[Telegram instructions](https://telegram.org/blog/bot-revolution)去创建一个机器人的`UserID`，然后将`UserID`和`BOT token`放到`config.js`里面。

```
module.exports = {
    config:function(){
        return (
            {
                adminUsers:[ADMIN_ID], //admin users' telegram id, should be numbers
                botToken: 'YOUR_BOT_TOEKN', // bot token

            }
        );
    }
};
```

**3、运行**

or

**原文地址：**<https://www.v2ex.com/t/394208>
