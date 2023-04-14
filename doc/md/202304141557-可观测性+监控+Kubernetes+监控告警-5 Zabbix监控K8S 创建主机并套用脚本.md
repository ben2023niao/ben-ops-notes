---
id: "doc-2df081998562"
title: "5 Zabbix监控K8S 创建主机并套用脚本"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "Kubernetes", "监控告警", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423047.html"
---

# 5 Zabbix监控K8S 创建主机并套用脚本

- 注意：主机名称必须与上面采集数据py脚本中定义的`clientname`的值保持一致

## 1、上传模板

- 将K8S监控的zabbix模板文件上传至zabbix服务端，通过web界面导入即可
![文档配图](../media/d74e148fe92b90ce73.png)
![文档配图](../media/0987cceb244ea0a9ca.png)

## 2、创建主机![文档配图](../media/93e8ad1e83c8b2e9ed.png)

## 3、绑定模板

## ![文档配图](../media/cd350dae9105b521b0.png)
