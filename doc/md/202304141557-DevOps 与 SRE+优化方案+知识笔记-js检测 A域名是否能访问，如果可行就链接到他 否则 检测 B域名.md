---
id: "doc-3f85a391847f"
title: "js检测 A域名是否能访问，如果可行就链接到他 否则 检测 B域名"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/68653249.html"
---

# js检测 A域名是否能访问，如果可行就链接到他 否则 检测 B域名

如题，求一个思路，
场景使用在
判断：[img01.abc.com/a.jpg 和 img02.abc.com/a.jpg 哪个域名连得通就加载哪个域名图片~](http://img01.abc.com/a.jpg和img02.abc.com/a.jpg哪个域名连得通就加载哪个域名图片~)

```
// 检测图片是否能正常加载
var imgLoad = function(url) {
 var img = new Image();
 img.src = url;
 if(img.complete) {
 return true
 } else {
 return false
 }
};
// 题目没有指定如果两个都能正常访问，我这快就理解为如果前面的能访问就优先使用前面的url
var imgSrc = imgLoad('img01.abc.com/a.jpg') && 'img01.abc.com/a.jpg' || imgLoad('img02.abc.com/a.jpg') && 'img02.abc.com/a.jpg';
```
