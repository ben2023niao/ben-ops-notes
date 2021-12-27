---
id: "doc-334721512c5a"
title: "Laravel 部署：环境一键安装"
date: "2021-12-27T13:28:32.753000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Linux", "Nginx", "MySQL", "Redis", "故障排查", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/laravel-bu-shu/laravel-bu-shu-huan-jing-yi-jian-an-zhuang.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "a79d3247b48e7393b637ef9ee63fc05925f78434cc1ef61b5d487cc7c9eb455b"
---

# Laravel 部署：环境一键安装

> 原文：[Laravel 部署：环境一键安装](https://xn--6o0a585a.gitbook.io/devops/fu-wu/laravel-bu-shu/laravel-bu-shu-huan-jing-yi-jian-an-zhuang.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-27 13:28｜日期依据：GitBook 页面更新时间

### 简介

适用于 Ubuntu 16.04 / 18.04 / 20.04 的 LNMP 安装脚本，并设置了国内镜像加速。

请确保所有命令都以 root 账户执行，如果登录账户不是 root，则需要执行 `sudo -H -s` 切换为 root 账户后再下载安装。

> 注：下文将使用 `{version}` 来替代你选中的系统，如 16.04 / 18.04 / 20.04。

### 软件列表

- Git
- PHP 7.4
- Nginx
- MySQL
- Sqlite3
- Composer
- Nodejs 10
- Yarn
- Redis
- Beanstalkd
- Memcached

### 可选软件列表

以下软件需手动执行安装脚本：

- Elasticsearch：`./{version}/install_elasticsearch.sh`，默认为 6.x，如果要安装 7.x 则执行 `./{version}/install_elasticsearch.sh 7`

### 安装

#### Ubuntu 16.04

#### Ubuntu 18.04

#### Ubuntu 20.04

#### 特别说明

此脚本会将安装脚本下载到当前用户的 Home 目录下的 `laravel-ubuntu-init` 目录并自动执行安装脚本。

**安装结束之后会在屏幕上输出 Mysql root 账号的密码，请妥善保存。**

如果当前不是 root 账户则不会自动安装，需要切换到 root 账户后执行 `./{version}/install.sh`。

### 日常使用

#### 1. 新增 Nginx 站点

会提示输入站点名称（只能是英文、数字、`-` 和 `_`）、域名（多个域名用空格隔开），确认无误后会创建对应的 Nginx 配置并重启 Nginx。

#### 2. 新增 Mysql 用户、数据库

会提示输入 root 密码，如果错误将无法继续。输入需要创建的 Mysql 用户名，以及确认是否需要创建对应用户名的数据库。

创建完毕之后会将新用户的密码输出到屏幕上，请妥善保存。

#### 3. 以 www-data 身份执行命令

本项目提供了一个 `sudowww` 的 `alias`，当需要以 `www-data` 用户身份执行命令时（如 `git clone 项目`、`php artisan config:cache` 等），可以直接在命令前加上 `sudowww`，同时在原命令两端加上单引号，如：
