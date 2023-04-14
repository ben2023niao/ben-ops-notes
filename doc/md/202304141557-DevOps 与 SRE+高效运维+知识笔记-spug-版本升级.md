---
id: "doc-b85b03b643fe"
title: "spug-版本升级"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650057.html"
---

# spug-版本升级

## 版本升级

### 注意

版本升级可能涉及数据库表结构的更新，表结构的更新依赖 Django 提供的 migrate 工具， 该工具的正常运行依赖安装时初始化生成的 migrations 目录和数据库的 django_migrations 表，

请不要删除或改动这些目录或表，否则当涉及表结构更新的版本升级后可能造成缺少表字段等问题。

#### 警告

如果你现在部署的 `v2.x.x` 的版本（系统设置/关于），请不要通过该升级工具升级 `v3` 版本，否则会造成运行异常！。[#419](https://github.com/openspug/spug/issues/419)

```
```
