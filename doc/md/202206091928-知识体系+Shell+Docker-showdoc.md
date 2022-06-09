---
id: "doc-4737afa22d5e"
title: "showdoc"
date: "2022-06-09T19:28:41.127000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "知识体系"]
tags: ["知识体系", "Shell", "Docker", "数据库恢复", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/showdoc.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "2b7c7937b9c301ed5cb5f5feea41d714b1f23f7c6b4bb44e3769ea98aaf9511c"
---

# showdoc

> 原文：[showdoc](https://xn--6o0a585a.gitbook.io/devops/showdoc.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-09 19:28｜日期依据：GitBook 页面更新时间

### Docker方式安装

#### 基础安装

安装前请确保你的环境已经装好了docker服务 。docker的安装教程在网上比较多，可以搜索了解下。这里重点介绍showdoc.

```bash
# 原版官方镜像安装命令(中国大陆用户不建议直接使用原版镜像，可以用后面的加速镜像)
docker pull star7th/showdoc

# 中国大陆镜像安装命令（安装后记得执行docker tag命令以进行重命名）
docker pull registry.cn-shenzhen.aliyuncs.com/star7th/showdoc
docker tag registry.cn-shenzhen.aliyuncs.com/star7th/showdoc:latest star7th/showdoc:latest

##后续命令无论使用官方镜像还是加速镜像都需要执行

#新建存放showdoc数据的目录
mkdir -p /showdoc_data/html
chmod  -R 777 /showdoc_data
# 如果你是想把数据挂载到其他目录，比如说/data1，那么，可以在/data1目录下新建一个showdoc_data/目录，
# 然后在根目录的新建一个软链接/showdoc_data到/data1/showdoc_data
# 这样既能保持跟官方教程推荐的路径一致，又能达到自定义存储的目的.

#启动showdoc容器
docker run -d --name showdoc --user=root --privileged=true -p 4999:80 \
-v /showdoc_data/html:/var/www/html/ star7th/showdoc
```

根据以上命令操作的话，往后showdoc的数据都会存放在 /showdoc_data/html 目录下。
你可以打开 [http://localhost:4999](http://localhost:4999/) 来访问showdoc (localhost可改为你的服务器域名或者IP)。账户密码是showdoc/123456，登录后你便可以看到右上方的管理后台入口。建议登录后修改密码。
对showdoc的问题或建议请至<https://github.com/star7th/showdoc> 出提issue。若觉得showdoc好用，不妨点个star。

#### 如何升级

这里的升级是针对上面docker安装方式的升级。如果你原来是采用非docker安装方式（如php安装方式）的话，请跳过本部分文字，直接去看下部分。

#### 非docker安装方式如何升级到docker安装方式

先参考前文，用docker方式全新安装一个showdoc，并且做好数据持久化。
接下来，假设你原来安装的旧showdoc已上传到服务器的 /tmp/showdoc 目录，那么

#### 数据备份

备份/showdoc_data/html 目录即可。比如执行下面命令压缩存放

#### 其他参考命令

#### 其他支持

- 常见问题：<http://www.showdoc.cc/help?page_id=16118>
- 如果你没有自己的服务器，但又想使用ShowDoc作为分档分享工具，你可以使用在线的ShowDoc [http://www.showdoc.com.cn](http://www.showdoc.com.cn/)
- ShowDoc使用交流qq群

<https://www.showdoc.com.cn/help?page_id=6912631551342243>
