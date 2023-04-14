---
id: "doc-c45fa6bd3c55"
title: "Zabbix监控K8S"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "Kubernetes", "监控告警", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84422993.html"
---

# Zabbix监控K8S

![文档配图](../media/f3666e336cdc5d5ea3.png)

一、环境准备和说明
1、下载python3安装包
2、安装依赖包文件
3、创建目录并安装
4、建立执行文件软链
5、zabbix-sender安装

二、获取k8s的api地址

三、Master节点获取token

四、创建脚本并修改脚本
1、创建目录和脚本
2、创建外部采集脚本

五、创建主机并套用脚本
1、上传模板
2、创建主机
3、绑定模板

六、查看获取到的数据

七、查看监控告警信息
