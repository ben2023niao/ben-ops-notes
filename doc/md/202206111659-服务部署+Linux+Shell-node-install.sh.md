---
id: "doc-a3ad21baacae"
title: "node-install.sh"
date: "2022-06-11T16:59:41.868000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Linux", "Shell", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/node-install.sh.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "822c3343268fe25bba7c97baa6d4f5cbe635e6fdbfb33109bbe5eaecf5e74dcd"
---

# node-install.sh

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202206111659-%E6%9C%8D%E5%8A%A1%E9%83%A8%E7%BD%B2%2BLinux%2BShell-node-install.sh.md)

> 原文：[node-install.sh](https://xn--6o0a585a.gitbook.io/devops/fu-wu/node-install.sh.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:59｜日期依据：GitBook 页面更新时间

```
#最新下载地址 https://nodejs.org/en/download/
#部署nodejs和npm
wget https://nodejs.org/dist/v12.14.1/node-v12.14.1-linux-x64.tar.xz
tar xf node-v10.16.0-linux-x64.tar.xz
cd node-v10.16.0-linux-x64
export PATH=$PATH:/root/node-v12.14.1-linux-x64/bin
source /etc/profile
node -v
npm -v

#部署yarn
curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | sudo tee /etc/yum.repos.d/yarn.repo
#如果没有nodejs,这个方法网速很慢
# curl -sL https://rpm.nodesource.com/setup_13.x | bash -
# yum -y install nodejs

#安装yarn
sudo yum install yarn
#export PATH=$PATH:/usr/share/yarn/bin
```
