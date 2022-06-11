---
id: "doc-f5f5f1d47c13"
title: "go-install.sh"
date: "2022-06-11T17:00:52.744000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Linux", "Go", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/go-install.sh.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "0af4f44535129cb7cb27c6f4ed61d0d1be658907997da1a435cfb04c54a06a4c"
---

# go-install.sh

> 原文：[go-install.sh](https://xn--6o0a585a.gitbook.io/devops/fu-wu/go-install.sh.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 17:00｜日期依据：GitBook 页面更新时间

```
mkdir -p $HOME/golang && curl https://dl.google.com/go/go1.12.12.linux-amd64.tar.gz | tar -C $HOME/golang -xz
export PATH=$HOME/golang/go/bin:$PATH
go version
export GOPATH=$HOME/go
#设置 GOPROXY 环境变量，将 Go Module 的镜像库切换到阿里云以优化下载速度
export GOPROXY=https://mirrors.aliyun.com/goproxy/
```
