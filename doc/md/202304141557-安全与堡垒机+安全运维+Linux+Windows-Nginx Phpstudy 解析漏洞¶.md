---
id: "doc-f05e3cc21c04"
title: "Nginx Phpstudy 解析漏洞¶"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Linux", "Windows", "Nginx", "PHP", "漏洞", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/84422178.html"
---

# Nginx Phpstudy 解析漏洞¶

## 一、漏洞简介

phpStudy 存在 nginx 解析漏洞，攻击者能够利用上传功能，将包含恶意代码的合法文件类型上传至服务器，从而造成任意代码执行的影响。

该漏洞仅存在于phpStudy Windows版，Linux版不受影响。

## 二、漏洞影响

phpstudy: \<=203.0.113.1

## 三、复现过程![文档配图](../media/6acf5eb20eec924546.png)
