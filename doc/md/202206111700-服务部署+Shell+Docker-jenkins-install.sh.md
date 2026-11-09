---
id: "doc-b39a190e846a"
title: "jenkins-install.sh"
date: "2022-06-11T17:00:32.045000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Shell", "Docker", "自动化", "安全运维", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/jenkins-install.sh.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "6f6f53710ee615b57593101cc26f0b4ac85154922f540574f4dabb0e6644d538"
---

# jenkins-install.sh

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202206111700-%E6%9C%8D%E5%8A%A1%E9%83%A8%E7%BD%B2%2BShell%2BDocker-jenkins-install.sh.md)

> 原文：[jenkins-install.sh](https://xn--6o0a585a.gitbook.io/devops/fu-wu/jenkins-install.sh.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 17:00｜日期依据：GitBook 页面更新时间

```bash
#拉取最新镜像并启动容器
docker pull jenkins/jenkins:lts
#查看镜像
docker images
#查看镜像jenkins版本
docker inspect 【镜像ID】 |grep VERSION
#创建Jenkins工程目录
mkdir -p /home/jenkins_home
#给目录修改权限，否则送气权限不足会报错
chown -R 1000:1000 jenkins_home
#挂载工程目录并制定端口启动容器，8080可以根据自己想要的宿主机容器变更，使用前查看端口是否占用如果是云服务器器注意开启安全组和防火墙开发此端口
docker run -d --name jenkins -p 7070:8080 -v /home/jenkins_home:/var/jenkins_home jenkins/jenkins:lts
docker ps | grep jenkins
#查看启动日志，记录安全立牌
docker logs -f jenkins
#记录安全令牌，访问客户端 localhost:8080
#初始插件安装
```
