---
id: "doc-7b11076aed00"
title: "域名检测告警功能方案-resolv.conf"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "DNS", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/66979517.html"
---

# 域名检测告警功能方案-resolv.conf

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
