---
id: "doc-2c2411baafc6"
title: "Shell脚本eval使用方法"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/84417217.html"
---

# Shell脚本eval使用方法

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-Linux%20%E4%B8%8E%20Shell%2B%E6%97%A5%E5%B8%B8%E8%BF%90%E7%BB%B4%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-Shell%E8%84%9A%E6%9C%ACeval%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95.md)

**eval**用来在执行命令时作二次解析：主要是每次执行一个shell命令它会先检察一次，看到有$标志就会把值替换一次，然后再执行一遍。eval不会唤起起另一个shell来执行，而是在本身这个shell内多解析一次，所以替换的结果可以保留下来使用。

使用示例：

```bash
#!/bin/bash
# eval.sh：example for eval

pages=4
#for ((i=1; i<=${pages}; i++))
for i in $(eval echo {1..${pages}})
do
echo $i
done

printf "%0.s-" {1..20}
#printf '%0.s-' $(seq 1 $variable)
echo

count=1
var1=I
var2=am
var3=a
var4=script
while [ $count -lt 5 ]; do
 eval "echo \$var$count"
 let 'count=count + 1'
done

# 输出结果：
1
2
3
4
--------------------
I
am
a
script
```

count会一直变化1 2 3...，同时替换var1 var2 var3，然后再对var1 var2 var3...取值。其中因为第一个var不想被运算，所以先用\构造一个变量， 然后第二次运算时才会被替换解析。当然如果要三次以上变量替换在一行内解析也是可行的。

$ eval ". foo.sh"，eval还可以用来调用执行另一个shell脚本，脚本在同一个shell下执行，因此变量在此shell内都是有效的。

**参考：**

- [What is the “eval” command in bash?](https://unix.stackexchange.com/questions/23111/what-is-the-eval-command-in-bash)
- [shell 中的eval 如何使用](https://jingyan.baidu.com/article/9faa7231ee8d82473c28cbb0.html)
- <http://www.study-area.org/cyril/scripts/scripts/node18.html>
