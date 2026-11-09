---
id: "doc-ba63e4b5c0b6"
title: "ajax判断用户是否可以访问某个网页"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/68653247.html"
---

# ajax判断用户是否可以访问某个网页

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-ajax%E5%88%A4%E6%96%AD%E7%94%A8%E6%88%B7%E6%98%AF%E5%90%A6%E5%8F%AF%E4%BB%A5%E8%AE%BF%E9%97%AE%E6%9F%90%E4%B8%AA%E7%BD%91%E9%A1%B5.md)

## 需求

这阵子接到个任务：如果用户没有连接vpn，那么他无法正常访问需要连接vpn的网站。需求是在访问该网站之前判断用户是否连接了vpn，如果没有，就给一个友好的提示。

## 思考

如何判断用户是否连接了vpn？我最初的想法是：先获取用户的ip，然后判断ip和该网站的ip是否在同一个网络下，但是由于鄙人对计算机网络的认知仅停留在会背七层协议的阶段上，加之万能的百度谷歌都没有搜到满意的解决思路。所以必须另辟蹊径。

## 思路

我们是否能够请求该网站，然后判断请求的状态码，以判断用户是否连接vpn？于是，在访问该网站之前，我异步请求了该网站，然后设置超时，最后在请求完成事件中做逻辑判断，成功的解决了该任务，走向了人生的巅峰。

## 参考代码

```
var url = 'http://www.baidu.com'
$.ajax({
 url: url,
 timeout: 3000,
 dataType: 'jsonp',
 async: true, // 使用timeout时，请求必须是同步的
 complete: function (xhr) {
 if (xhr.readyState === 4 && xhr.status === 200) {
 window.open(url)
 } else {
 alert('网络请求失败，请检查您的网络或使用vpn连接!')
 }
 }
})
```

```
```

1. ajax的complete回调还有一个参数status，可以获取请求的最终状态。我做项目的时候发现个问题，一个网址在我本机打开状态是timeout，在另一台机器打开状态时error，然后我的代码逻辑是判断状态是否是timeout，没有考虑到error的情况，所以最好通过状态码去判断是否请求成功。
2. 一个问题有多种解法，当你一个方向走不通时，可以考虑从另外的角度看问题。
