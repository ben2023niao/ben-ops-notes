---
id: "doc-53cd79b1b467"
title: "2 Zabbix监控K8S 获取k8s的api地址"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "Kubernetes", "监控告警", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423006.html"
---

# 2 Zabbix监控K8S 获取k8s的api地址

```
查看K8S的api地址的命令如下，在k8s的master节点执行
注意获取到的地址确保外部可以访问
[root@k8s-master1 ~]# kubectl cluster-info
```

![文档配图](../media/5f0e95cab3464403c0.png)
