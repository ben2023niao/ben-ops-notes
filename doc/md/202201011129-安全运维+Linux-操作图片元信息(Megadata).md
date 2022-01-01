---
id: "doc-76a1bb9c467e"
title: "操作图片元信息(Megadata)"
date: "2022-01-01T11:29:54.606000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全运维", "Linux"]
source: "https://xn--6o0a585a.gitbook.io/devops/an-quan/cao-zuo-tu-pian-yuan-xin-xi-megadata.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "953c78e703e041e2e7d5c5a1d6c01fffa96d2a7f7c16dc26e8b74124e94812cc"
---

# 操作图片元信息(Megadata)

> 原文：[操作图片元信息(Megadata)](https://xn--6o0a585a.gitbook.io/devops/an-quan/cao-zuo-tu-pian-yuan-xin-xi-megadata.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-01-01 11:29｜日期依据：GitBook 页面更新时间

安装：

```
# Mac上安装
$ brew install exiftool

# 或Linux上安装
$ sudo apt-get install exiftool

# 查看图片全部exif信息
$ exiftool 图片位置

# 查看图片某个tag信息
$ exiftool -tag
```

### 语法

每种格式的图片都有自己不同的一堆Tags，比如时间、日期、地理位置等，jpg和png都很不一样。
所以到官网参考每种图片的不同tags，才能确定自己要怎么改这个信息。

[ExifTool Tag Names](https://link.segmentfault.com/?enc=phbR2RL5ngaKkZMSf%2BttQA%3D%3D.Piix4LnnvYisydyI5f9TP%2FDnnJUDYFalkh2myIfbQazuELi8DVG6bAj6N7ALiDjolYTMQmduLPPSJAjgmqH5LvCHcJlMTSEyqddgb41zvzU%3D)

注意，引用tag时，要用小写。

基本语法是一样的：

- 设置某tag的值：`-tag=VALUE`
- 增减某tag值(如果是数字的话)：`-tag+=VALUE` 或`-tag-=VALUE`
- 清空: `-tag=`

但是有一点一定要注意：每种tag所接受的值的格式是很严格的：

- 日期
- 时长

### 常用操作

更改创建和修改时间：

写入标签：

转移标签「<」（将某一个标签值赋予另一个标签）：

其它：

### 常用标签名(Tags)

> 因为编辑exif信息需要知道图片里内置的各种标签名才能修改，所以下面为标签名参考。

#### JPEG

- `Comment`: 描述，无字数限制。

#### PNG

- `Comment`: 描述，无字数限制。
- `Description`：描述，无字数限制。
