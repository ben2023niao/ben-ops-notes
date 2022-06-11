---
id: "doc-4fcb1d76b398"
title: "部署ES"
date: "2022-06-11T16:26:08.818000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/bu-shu-es.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "30566755270b2621dac32d560ec5d038c9f77da2268e27746fe9a60f8f8a5097"
---

# 部署ES

> 原文：[部署ES](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/bu-shu-es.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:26｜日期依据：GitBook 页面更新时间

**1、安装docker-compose**

```
sudo curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

```
sudo chmod +x /usr/local/bin/docker-compose
```

```
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

```
docker-compose --version
```

**2、elasticsearch**

```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:6.4.0
```

```
vim /etc/sysctl.conf

vm.max_map_count=262144

vim /etc/security/limits.conf

soft nofile 65536
hard nofile 65536
```

**3、创建文件和目录**

```
mkdir /home/docker/elasticsearch -p

cd /home/docker/elasticsearch

mkdir config

vim elasticsearch.yml

cd /home/docker/elasticsearch

vim docker-compose.yml

mkdir data
```

**4、elasticsearch.yml**

**5、docker-compose.yml**

**6、在每个服务器的docker-compose.yml 同级目录下同时执行 docker-compose up –d 命令，根据服务器性能，大概等待1分钟左右，两个节点的集群就创建成功了，当然可以通过执行以下命令查看启动状态：**

**7、查看集群的所有节点：**
