---
id: "doc-44eb77f6ac7e"
title: "以太坊公链私链geth同步"
date: "2022-06-11T16:05:43.869000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "区块链"]
tags: ["区块链", "Linux", "Shell", "Go", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/qu-kuai-lian/yi-tai-fang-gong-lian-si-lian-geth-tong-bu.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "71ef09204059ff76c97507df29a629499d21c6b7db871bc9f7b24f1f5eff8a00"
---

# 以太坊公链私链geth同步

> 原文：[以太坊公链私链geth同步](https://xn--6o0a585a.gitbook.io/devops/qu-kuai-lian/yi-tai-fang-gong-lian-si-lian-geth-tong-bu.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:05｜日期依据：GitBook 页面更新时间

1、安装必备环境插件 #1-5 公有链 +6-10 私有链

```
yum update -y && yum install git wget bzip2 vim gcc-c++ ntp epel-release nodejs cmake -y
yum install -y curl git golang nodejs gcc-c++
```

2、安装go语言

```
wget https://dl.google.com/go/go1.10.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.10.linux-amd64.tar.gz
echo 'export GOROOT=/usr/local/go' >> /etc/bashrc
echo 'export PATH=$PATH:$GOROOT/bin' >> /etc/bashrc
echo 'export GOPATH=/root/go' >> /etc/bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> /etc/bashrc
source /etc/bashrc
```

3、验证go语言安装成功

```
[root@jubeiTest root]# go version
go version go1.10 linux/amd64
```

4、安装geth客户端 '我的路径'=/mnt/

```
git clone https://github.com/ethereum/go-ethereum.git
cd go-ethereum
make all
echo 'export PATH=$PATH:/’你的路径’/go-ethereum/build/bin' >> /etc/bashrc
source /etc/bashrc
```

5、验证geth

6、智能合约

同步节点

7、创建创世文件（genesis.json）

8、初始化创世文件

9、创建start.sh脚本

10、进入控制台

history命令
