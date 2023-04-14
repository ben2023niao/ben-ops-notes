---
id: "doc-4d42e4b27aaa"
title: "账户管理"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "Docker", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650040.html"
---

# 账户管理

## 介绍

除了页面上对普通用的管理，`Spug` 还提供了 `manage.py user` 命令可用于管理员账户的管理操作。

## 创建账户

创建账户使用 `manage.py user add` 命令，用法示例如下

```
cd spug/spug_api
source venv/bin/activate
python manage.py user add -u admin -p 123 -n 张三丰 -s
```

Docker 安装的可以执行如下命令

```bash
docker exec spug python3 /data/spug/spug_api/manage.py user add -u admin -p 123 -n 张三丰 -s
```

以上命令会创建个登录名为 `admin` 密码为 `123` 昵称为 `张三丰` 的管理员账户，注意最后的 `-s` 参数，如果携带了这个参数意味着该账户为管理员账户， 管理员账户可以不受任何限制的访问所有功能模块。

## 重置密码

使用 `manage.py user reset` 命令来重置账户密码，用法示例如下

```
cd spug/spug_api
source venv/bin/activate
python manage.py user reset -u admin -p abc
```

Docker 安装的可以执行如下命令

```bash
docker exec spug python3 /data/spug/spug_api/manage.py user reset -u admin -p abc
```

上述操作会重置登录名为 `admin` 的账户的密码为 `abc`。

## 启用账户

当页面上登录连续错误数次超过3次后账户自动转为禁用状态，普通用户可以通过 `系统管理 / 账户管理` 在页面是启用账户即可，但管理员账户需要使用如下命令来启用

```
cd spug/spug_api
source venv/bin/activate
python manage.py user enable -u admin
```

Docker 安装的可以执行如下命令

```bash
docker exec spug python3 /data/spug/spug_api/manage.py user enable -u admin
```
