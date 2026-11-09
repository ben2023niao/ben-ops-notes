---
id: "doc-1d22fd81304e"
title: "Docker一键安装spug"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "MySQL", "Docker", "SQL注入", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68649901.html"
---

# Docker一键安装spug

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2BMySQL%2BDocker-Docker%E4%B8%80%E9%94%AE%E5%AE%89%E8%A3%85spug.md)

## 依赖环境

- Docker
- 现代浏览器

## 安装步骤

以下安装步骤使用 `Centos7.x` 操作系统。

阿里云的镜像与 [Docker hub](https://hub.docker.com/r/openspug/spug/tags) 同步更新，国内用户建议使用阿里云的镜像。

```bash
docker pull registry.aliyuncs.com/openspug/spug
```

### 1. 启动容器

如果需要持久化存储代码和数据，可以添加：-v 映射容器内/data路径。

根据需要，以下两种启动方式任选其一即可。官方镜像内置了 `Mysql` 数据库，如果需要使用外部已有数据库（Mysql 5.6+）参考 安装相关问题 里的 Docker 部署使用外部 Mysql

```bash
# 持久化存储启动命令：
# /spug 指的是映射本地的磁盘路径，也可以是其他目录，/data是容器内代码和数据初始化存储的路径
docker run -d --restart=always --name=spug -p 80:80 -v /spug:/data registry.aliyuncs.com/openspug/spug
# 如果你需要在spug内使用docker命令则需要添加额外的参数
docker run -d --restart=always --name=spug -p 80:80 -v /spug/:/data -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker registry.aliyuncs.com/openspug/spug
```

### 2. 初始化

以下操作会创建一个用户名为 `admin` 密码为 `spug.dev` 的管理员账户，可自行替换管理员账户。

```bash
docker exec spug init_spug admin spug.dev
```

### 3. 访问测试

在浏览器中输入 `<http://localhost:80>` 访问。

```
用户名： admin
密码：[已脱敏]
```
