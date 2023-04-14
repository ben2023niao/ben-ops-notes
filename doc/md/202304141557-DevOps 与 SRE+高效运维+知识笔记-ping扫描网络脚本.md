---
id: "doc-c0b3d14ab60c"
title: "ping扫描网络脚本"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/72056996.html"
---

# ping扫描网络脚本

```bash
#!/bin/bash
echo 'inputip:' #提示输入要扫描的ip地址
read inputip #获取终端输入给变量inputip
tip=$inputip #将获取到的inputip 给变量 tip 这里是多余的赋值 只是不想修改下面的代码而已
echo -n '1: ' #输出行号
#使用ping方法查看 注意等好后面的是 反单引号 结尾处也是 反单引号
res=`ping $tip -c 1 | grep ttl | awk '{print $4}' | awk -F: '{print $1}'`
#判断
if [ $res > 0 ]
then
 echo "$tip.$n on"
else
 echo "$tip.$n off"
echo ''
fi
```
