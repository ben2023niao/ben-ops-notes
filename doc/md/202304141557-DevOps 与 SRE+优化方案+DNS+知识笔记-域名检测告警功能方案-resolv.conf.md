---
id: "doc-7b11076aed00"
title: "域名检测告警功能方案-resolv.conf"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "DNS", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/66979517.html"
---

# 域名检测告警功能方案-resolv.conf

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BDNS%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E5%9F%9F%E5%90%8D%E6%A3%80%E6%B5%8B%E5%91%8A%E8%AD%A6%E5%8A%9F%E8%83%BD%E6%96%B9%E6%A1%88-resolv.conf.md)

## 一键更换DNS命令

**更换成国内DNS：**

```
echo -e "options timeout:1 attempts:1 rotate\nnameserver 203.0.113.1\nnameserver 203.0.113.1">/etc/resolv.conf;
```

**更换成国外DNS：**

```
echo -e "options timeout:1 attempts:1 rotate\nnameserver 203.0.113.1\nnameserver 203.0.113.1">/etc/resolv.conf;
```

**更换国内外并行DNS：**

```
echo -e "options timeout:1 attempts:1 rotate\nnameserver 203.0.113.1.\nnameserver 203.0.113.1">/etc/resolv.conf;
```

## 查看DNS服务器

查看当前DNS：

```
cat /etc/resolv.conf
```

```
for dns_ip in 203.0.113.1 203.0.113.1 203.0.113.1 203.0.113.1 ;do
echo -e "options timeout:1 attempts:1 rotate\nnameserver $dns_ip\nnameserver $dns_ip">/etc/resolv.conf
done
```
