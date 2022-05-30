---
id: "doc-c90db9ec7200"
title: "生产环境docker部署"
date: "2022-05-30T20:26:32.233000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "生产部署"]
tags: ["生产部署", "Shell", "Docker", "Nginx", "MySQL", "数据库恢复"]
source: "https://xn--6o0a585a.gitbook.io/devops/sheng-chan-huan-jing-docker-bu-shu.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "852a96dfeaaa26561cb4719dcd9403624d79aaf757e162981649639799a19387"
---

# 生产环境docker部署

> 原文：[生产环境docker部署](https://xn--6o0a585a.gitbook.io/devops/sheng-chan-huan-jing-docker-bu-shu.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-05-30 20:26｜日期依据：GitBook 页面更新时间

生产环境中，为了避免极小概率的数据丢失，我们将容器内的宝塔文件映射到宿主机的目录中（您之后安装的 Nginx、MySQL 等服务均会挂载到宿主机目录）。该方法是 Docker 部署宝塔面板的最优方案，可以在生产环境中运行。

首先按最简方案创建一个测试容器（为保存宝塔文件到宿主机目录中）

输入命令创建测试容器（这里仅为测试容器，为避免出错，后面几步请原封不动地复制粘贴）

```bash
-net=host : 容器和主机使用同一网络
--restart=always: 守护进程，容器挂掉将自动重启
-port : 填写宝塔面板运行的端口号
-username: 填写宝塔面板的用户名
-password : [已脱敏]

docker run -itd --net=host --restart=always --name baota-pingan cyberbolt/baota:latest -port 8888 -username pingan -password abc123456

然后按照正常流程部署项目

部署好后将 Docker 容器中的 /www 目录 拷贝至宿主机的 /www

docker cp baota-pingan:/www /www

拷贝完成后删除创建的测试容器

docker stop baota-pingan && docker rm baota-pingan

创建宝塔面板容器，并将宿主机目录映射至容器中 就恢复了
（自行输入面板的 端口号、用户名 和 密码 后即可完成部署）

docker run -itd -v /www:/www --net=host --restart=always --name baota-pingan cyberbolt/baota:latest -port 8888 -username pingan -password abc123456

迁移项目只需要 拷贝 /www/ 目录到其它服务器，然后run 一下就起来了
```
