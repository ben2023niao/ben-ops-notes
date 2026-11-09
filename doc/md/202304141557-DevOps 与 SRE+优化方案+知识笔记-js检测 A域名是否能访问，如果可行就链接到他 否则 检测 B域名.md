---
id: "doc-3f85a391847f"
title: "js检测 A域名是否能访问，如果可行就链接到他 否则 检测 B域名"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/68653249.html"
---

# js检测 A域名是否能访问，如果可行就链接到他 否则 检测 B域名

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-js%E6%A3%80%E6%B5%8B%20A%E5%9F%9F%E5%90%8D%E6%98%AF%E5%90%A6%E8%83%BD%E8%AE%BF%E9%97%AE%EF%BC%8C%E5%A6%82%E6%9E%9C%E5%8F%AF%E8%A1%8C%E5%B0%B1%E9%93%BE%E6%8E%A5%E5%88%B0%E4%BB%96%20%E5%90%A6%E5%88%99%20%E6%A3%80%E6%B5%8B%20B%E5%9F%9F%E5%90%8D.md)

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
