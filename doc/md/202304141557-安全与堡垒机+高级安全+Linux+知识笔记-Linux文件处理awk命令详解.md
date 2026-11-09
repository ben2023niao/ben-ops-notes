---
id: "doc-52d6bdbc441f"
title: "Linux文件处理awk命令详解"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Linux", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68656958.html"
---

# Linux文件处理awk命令详解

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2BLinux%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-Linux%E6%96%87%E4%BB%B6%E5%A4%84%E7%90%86awk%E5%91%BD%E4%BB%A4%E8%AF%A6%E8%A7%A3.md)

## Linux文件处理awk命令详解教程

**[Linux](https://haicoder.net/linux/linux-tutorial.html)** 中的 awk 是一个强大的文本分析工具，简单来说 awk 就是把文件逐行读入，（空格，制表符）为默认分隔符将每行切片，切开的部分再进行各种分析处理。

## Linux awk命令说明

awk 是一个强大的文本分析工具，相对于 **[grep](https://haicoder.net/linux/linux-grep.html)** 的查找，**[sed](https://haicoder.net/linux/linux-sed.html)** 的编辑，awk 在其对数据分析并生成报告时，显得尤为强大。

awk 有 3 个不同版本: awk、nawk 和 gawk，未作特别说明，一般指 gawk，gawk 是 AWK 的 GNU 版本。

awk 其名称得自于它的创始人 Alfred Aho 、Peter Weinberger 和 Brian Kernighan 姓氏的首个字母。实际上 AWK 的确拥有自己的语言： AWK 程序设计语言 ， 三位创建者已将它正式定义为 “样式扫描和处理语言”。

它允许您创建简短的程序，这些程序读取输入文件、为数据排序、处理数据、对输入执行计算以及生成报表，还有无数其他的功能。

## Linux awk命令详解

### 功能

对文本进行分析与处理。

### 语法

`awk '{pattern + action}' input-file(s)`

### 参数

| 参数 | 描述 |

| --- | --- |

| field-separator | awk 命令分隔符。 |

| commands | 命令。 |

| input-file | 要处理的文件。 |

### 说明

尽管操作可能会很复杂，但语法总是这样，其中 pattern 表示 AWK 在数据中查找的内容，而 action 是在找到匹配内容时所执行的一系列命令。花括号（{}）不需要在程序中始终出现，但它们用于根据特定的模式对一系列指令进行分组。 pattern 就是要表示的正则表达式，用斜杠括起来。

awk 语言的最基本功能是在文件或者字符串中基于指定规则浏览和抽取信息，awk 抽取信息后，才能进行其他文本操作。完整的 awk 脚本通常用来格式化文本文件中的信息。

通常，awk 是以文件的一行为处理单位的。awk 每接收文件的一行，然后执行相应的命令，来处理文本。

## Linux awk命令功能详解

| 命令 | 描述 |

| --- | --- |

| $0 | 表示整个当前行。 |

| $1 | 每行第一个字段。 |

| NF | 字段数量变量。 |

| NR | 每行的记录号，多文件记录递增。 |

| FNR | 与 NR 类似，不过多文件记录不递增，每个文件都从 1 开始。 |

| \t | 制表符。 |

| \n | 换行符。 |

| FS | BEGIN 时定义分隔符。 |

| RS | 输入的记录分隔符， 默认为换行符(即文本是按一行一行输入)。 |

| ~ | 匹配，与 == 相比不是精确比较。 |

| !~ | 不匹配，不精确比较。 |

| == | 等于，必须全部相等，精确比较。 |

| != | 不等于，精确比较。 |

| && | 逻辑与。 |

| || | 逻辑或。 |

| + | 匹配时表示 1 个或 1 个以上。 |

| `/[0-9][0-9]+/` | 两个或两个以上数字。 |

| `/[0-9][0-9]*/` | 一个或一个以上数字。 |

| FILENAME | 文件名。 |

| OFS | 输出字段分隔符， 默认也是空格，可以改为制表符等。 |

| ORS | 输出的记录分隔符，默认为换行符,即处理结果也是一行一行输出到屏幕。 |

| -F’[:#/]’ | 定义三个分隔符。 |

## awk内建变量

| 变量 | 描述 |

| --- | --- |

| $n | 当前记录的第n个字段，字段间由FS分隔 |

| $0 | 完整的输入记录 |

| ARGC | 命令行参数的数目 |

| ARGIND | 命令行中当前文件的位置(从0开始算) |

| ARGV | 包含命令行参数的数组 |

| CONVFMT | 数字转换格式(默认值为%.6g)ENVIRON环境变量关联数组 |

| ERRNO | 最后一个系统错误的描述 |

| FIELDWIDTHS | 字段宽度列表(用空格键分隔) |

| FILENAME | 当前文件名 |

| FNR | 各文件分别计数的行号 |

| FS | 字段分隔符(默认是任何空格) |

| IGNORECASE | 如果为真，则进行忽略大小写的匹配 |

| NF | 一条记录的字段的数目 |

| NR | 已经读出的记录数，就是行号，从1开始 |

| OFMT | 数字的输出格式(默认值是%.6g) |

| OFS | 输出记录分隔符（输出换行符），输出时用指定的符号代替换行符 |

| ORS | 输出记录分隔符(默认值是一个换行符) |

| RLENGTH | 由match函数所匹配的字符串的长度 |

| RS | 记录分隔符(默认是一个换行符) |

| RSTART | 由match函数所匹配的字符串的第一个位置 |

| SUBSEP | 数组下标分隔符(默认值是/034) |

## 调用awk三种方式

### 命令行方式

`awk [-F field-separator] 'commands' input-file(s)`

其中，commands 是真正 awk 命令，[-F 域分隔符] 是可选的。 input-file(s) 是待处理的文件。

在 awk 中，文件的每一行中，由域分隔符分开的每一项称为一个域。通常，在不指名 -F 域分隔符的情况下，默认的域分隔符是空格。

### shell脚本方式

将所有的 awk 命令插入一个文件，并使 awk 程序可执行，然后 awk 命令解释器作为脚本的首行，一遍通过键入脚本名称来调用。相当于 shell 脚本首行的：

`#!/bin/sh`

可以换成：

`#!/bin/awk`

### awk文件

将所有的 awk 命令插入一个单独文件，然后调用：

`awk -f awk-script-file input-file(s)`

其中，-f 选项加载 awk-script-file 中的 awk 脚本，input-file(s) 跟上面的是一样的。

## Linux awk命令常用实例

### 实例

| 实例 | 描述 |

| --- | --- |

| awk ‘{print $1,$4}’ file | 以空格或者 tab 分隔显示第一列和第四列 |

| awk -F : ‘{ print $1,$2 }’ file | 以冒号分隔，显示第一列和第二列 |

| awk -va=1 ‘{print $1,$1+a}’ file | 通过 v 参数设置变量 |

| awk ‘$1>2’ file | 过滤出第一列大于 2 的列 |

| awk ‘$1==2 {print $1,$3}’ file | 过滤第一列等于 2 的列 |

| awk ‘$1>2 && $2==“Hello” {print $1,$2,$3}’ file | 过滤第一列大于 2 并且第二列等于 ‘Hello’ 的行 |

| awk ‘$2 ~ /th/ {print $2,$4}’ file | 输出第二列包含 “th”，并打印第二列与第四列 |

| awk '/haicoder/ ’ file | 输出包含 “haicoder” 的行 |

| awk ‘BEGIN{IGNORECASE=1} /haicoder/’ log.txt | 忽略大小写 |

| awk ‘length>80’ file | 从文件总取出长度大于 80 的行 |

| awk -F ‘:’ ‘BEGIN {print “start1,start7”} {print $1 “,” $7} END {print “end1,end7”}’ file | 显示文件的第 1 列和第 7 列，用逗号分隔显示，所有行开始前添加列名 start1，start7，最后一行添加，end1，end7 |

| awk -F : ‘{ print NR " " NF " " $0 }’ file | 统计文件中，每行的行号，每行的列数，对应的完整行内容 |

| awk ‘BEGIN { print length(“Hello HaiCoder”) }’ | 输出字符串长度 |

| awk -F ‘:’ ‘{ print toupper($1) }’ file | 第一列转成大写 |

| awk -F ‘:’ ‘{ if ($1 > “d”) { print $1 } else { print “-” } }’ file | 输出第一个字段的第一个字符大于 d 的行 |
