---
id: "doc-2aa805050ec6"
title: "shell脚本缺陷案例"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "Linux", "漏洞", "权限管理", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/84417174.html"
---

# shell脚本缺陷案例

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-Linux%20%E4%B8%8E%20Shell%2B%E6%97%A5%E5%B8%B8%E8%BF%90%E7%BB%B4%2BLinux%2B%E6%BC%8F%E6%B4%9E-shell%E8%84%9A%E6%9C%AC%E7%BC%BA%E9%99%B7%E6%A1%88%E4%BE%8B.md)

```bash
◇ 将保留字或特殊字符声明为变量名.

case=value0 # 引发错误.
23skidoo=value1 # 也会引发错误.
# 以数字开头的变量名是被shell保留使用的.
# 试试_23skidoo=value1. 以下划线开头的变量就没问题.
# 然而 . . .   如果只用一个下划线作为变量名就不行.
_=25
echo $_ # $_是一个特殊变量, 代表最后一个命令的最后一个参数.

xyz((!*=value2 # 引起严重的错误.
# Bash3.0之后, 标点不能出现在变量名中.

◇ 使用连字符或其他保留字符来做变量名(或函数名).

var-1=23
# Use 'var_1' instead.
function-whatever () # 错误
# 使用'function_whatever ()'来代替.

# Bash3.0之后, 标点不能出现在函数名中.
function.whatever () # 错误
# 使用'functionWhatever ()'来代替.

◇ 让变量名与函数名相同. 这会使得脚本的可读性变得很差.

do_something ()
{
 echo "This function does s
}
do_something=do_something
do_something do_something
# 这么做是合法的, 但是会让人混淆.
◇ 不合时宜的使用空白字符. 与其它编程语言相比, Bash非常讲究空白字符的使用.
var1 = 23   # 'var1=23'才是正确的.
# 对于上边这一行来说, Bash会把"var1"当作命令来执行,
# "="和"23"会被看作"命令""var1"的参数.

let c = $a - $b   # 'let c=$a-$b'或'let "c = $a - $b"'才是正确的.

if [ $a -le 5]    # if [ $a -le 5 ]   是正确的.
# if [ "$a" -le 5 ]   这么写更好.
# [[ $a -le 5 ]] 也行.
◇ 在大括号包含的代码块中, 最后一条命令没有以分号结尾.
{ ls -l; df; echo "Done." }
# bash: syntax error: unexpected end of file
{ ls -l; df; echo "Done."; }
#                        ^
### 最后的这条命令必须以分号结尾.
◇ 假定未初始化的变量(赋值前的变量)被"清0". 事实上, 未初始化的变量值为"null", 而不是0.
#!/bin/bash
echo "uninitialized_var = $uninitialized_var"
# uninitialized_var =
◇ 混淆测试符号=和-eq. 请记住, =用于比较字符变量, 而-eq用来比较整数.
if [ "$a" = 273 ]      # $a是整数还是字符串?
if [ "$a" -eq 273 ]    # $a为整数.
# 有些情况下, 即使你混用-eq和=, 也不会产生错误的结果.
# 然而 . . .
a=273.0   # 不是一个整数.

if [ "$a" = 273 ]
then
  echo "Comparison works."
else
  echo "Comparison does not work."
fi    # Comparison does not work.
# 与a=" 273"和a="0273"相同.
# 类似的, 如果对非整数值使用"-eq"的话, 就会产生问题.

if [ "$a" -eq 273.0 ]
then
  echo "a = $a"
fi  # 因为产生了错误消息, 所以退出.
# test.sh: [: 273.0: integer expression expected
◇ 误用了字符串比较操作符.
例子 31-1. 数字比较与字符串比较并不相同
#!/bin/bash
# bad-op.sh: 尝试一下对整数使用字符串比较.
echo
number=1
# 下面的"while循环"有两个错误:
#+ 一个比较明显, 而另一个比较隐蔽.
while [ "$number" < 5 ]    # 错! 应该是:  while [ "$number" -lt 5 ]
do
  echo -n "$number "
  let "number += 1"
done
#  如果你企图运行这个错误的脚本, 那么就会得到一个错误消息:
#+ bad-op.sh: line 10: 5: No such file or directory
#  在单中括号结构([ ])中, "<"必须被转义.
#+ 即便如此, 比较两个整数还是错误的.
echo "---------------------"
while [ "$number" \< 5 ]    #  1 2 3 4
do                          #
  echo -n "$number "        #  看起来*好像可以工作, 但是 . . .
  let "number += 1"         #+ 事实上是比较ASCII码,
done                        #+ 而不是整数比较.
echo; echo "---------------------"
# 这么做会产生问题. 比如:
lesser=5
greater=105
if [ "$greater" \< "$lesser" ]
then
  echo "$greater is less than $lesser"
fi                          # 105 is less than 5
#  事实上, 在字符串比较中(按照ASCII码的顺序)
#+ "105"小于"5".
echo
exit 0
有时候在"test"中括号([ ])结构里的变量需要被引用起来(双引号). 如果不这么做的话, 可能会引起不可预料的结果.
脚本中的命令可能会因为脚本宿主不具备相应的运行权限而导致运行失败, 如果用户在命令行中就不能调用这个命令的话, 那么即使把它放到脚本中来运行, 也还是会失败. 这时可以通过修改命令的属性来解决这个问题, 有时候甚至要给它设置suid位(当然, 要以root身份来设置).
试图使用-作为重定向操作符(事实上它不是), 通常都会导致令人不快的结果.
command1 2> - | command2  # 试图将command1的错误输出重定向到一个管道中...
#    ...不会工作.
command1 2>& - | command2  # 也没效果.
◇ 使用Bash 2.0或更高版本的功能, 可以在产生错误信息的时候, 引发修复动作. 但是比较老的Linux机器默认安装的可能是Bash 1.XX.
#!/bin/bash
minimum_version=2
# 因为Chet Ramey经常给Bash添加一些新的特征,
# 所以你最好将$minimum_version设置为2.XX, 3.XX, 或是其他你认为比较合适的值.
E_BAD_VERSION=80
if [ "$BASH_VERSION" \< "$minimum_version" ]
then
  echo "This script works only with Bash, version $minimum or greater."
  echo "Upgrade strongly recommended."
  exit $E_BAD_VERSION
fi
...
在非Linux机器上的Bourne shell脚本(#!/bin/sh)中使用Bash特有的功能, 可能会引起不可预料的行为. Linux系统通常都会把bash别名化为sh, 但是在一般的UNIX机器上却不一定会这么做.
使用Bash未文档化的特征, 将是一种危险的举动. 本书之前的几个版本就依赖一个这种"特征", 下面说明一下这个"特征", 虽然exit或return所能返回的最大正值为255, 但是并没有限制我们使用负整数. 不幸的是, Bash 2.05b之后的版本, 这个漏洞消失了.
一个带有DOS风格换行符(\r\n)的脚本将会运行失败, 因为#!/bin/bash\r\n是不合法的, 与我们所期望的#!/bin/bash\n不同. 解决办法就是将这个脚本转换为UNIX风格的换行符.
#!/bin/bash
echo "Here"
unix2dos $0    # 脚本先将自己改为DOS格式.
chmod 755 $0   # 更改可执行权限.
               # 'unix2dos'会删除可执行权限.

./$0           # 脚本尝试再次运行自己.
               # 但它作为一个DOS文件, 已经不能运行了.

echo "There"
exit 0
以#!/bin/sh开头的Bash脚本, 不能在完整的Bash兼容模式下运行. 某些Bash特定的功能可能会被禁用. 如果脚本需要完整的访问所有Bash专有扩展, 那么它需要使用#!/bin/bash作为开头.
如果在here document中, 结尾的limit string之前加上空白字符的话, 将会导致脚本的异常行为.
脚本不能将变量export到它的父进程(即调用这个脚本的shell), 或父进程的环境中. 就好比我们在生物学中所学到的那样, 子进程只会继承父进程, 反过来则不行.
WHATEVER=/home/bozo
export WHATEVER
exit 0
bash $ echo $WHATEVERbash$

可以确定的是, 即使回到命令行提示符, 变量$WHATEVER仍然没有被设置.
◇ 在子shell中设置和操作变量之后, 如果尝试在子shell作用域之外使用同名变量的话, 将会产生令人不快的结果.
例子 31-2. 子shell缺陷
#!/bin/bash
# 子shell中的变量缺陷.
outer_variable=outer
echo
echo "outer_variable = $outer_variable"
echo
(
# 开始子shell
echo "outer_variable inside subshell = $outer_variable"
inner_variable=inner  # Set
echo "inner_variable inside subshell = $inner_variable"
outer_variable=inner  # 会修改全局变量么?
echo "outer_variable inside subshell = $outer_variable"
# 如果将变量'导出'会产生不同的结果么?
#    export inner_variable
#    export outer_variable
# 试试看.
# 结束子shell
)
echo
echo "inner_variable outside subshell = $inner_variable"  # 未设置.
echo "outer_variable outside subshell = $outer_variable"  # 未修改.
echo
exit 0
# 如果你打开第19和第20行的注释会怎样?
# 会产生不同的结果么? (译者注: 小提示, 第18行的'导出'都加上引号了.)
◇ 将echo的输出通过管道传递给read命令可能会产生不可预料的结果. 在这种情况下, read命令的行为就好像它在子shell中运行一样. 可以使用set命令来代替(就好像例子 11-17一样).
例子 31-3. 将echo的输出通过管道传递给read命令
#!/bin/bash
#  badread.sh:
#  尝试使用'echo'和'read'命令
#+ 非交互的给变量赋值.

a=aaa
b=bbb
c=ccc
echo "one two three" | read a b c
# 尝试重新给变量a, b, 和c赋值.
echo
echo "a = $a"  # a = aaa
echo "b = $b"  # b = bbb
echo "c = $c"  # c = ccc
# 重新赋值失败.
# ------------------------------
# 试试下边这种方法.
var=`echo "one two three"`
set -- $var
a=$1; b=$2; c=$3
echo "-------"
echo "a = $a"  # a = one
echo "b = $b"  # b = two
echo "c = $c"  # c = three
# 重新赋值成功.
# ------------------------------
#  也请注意, echo到'read'的值只会在子shell中起作用.
#  所以, 变量的值*只*会在子shell中被修改.
a=aaa          # 重新开始.
b=bbb
c=ccc
echo; echo
echo "one two three" | ( read a b c;
echo "Inside subshell: "; echo "a = $a"; echo "b = $b"; echo "c = $c" )
# a = one
# b = two
# c = three
echo "-----------------"
echo "Outside subshell: "
echo "a = $a"  # a = aaa
echo "b = $b"  # b = bbb
echo "c = $c"  # c = ccc
echo
exit 0
事实上, 也正如Anthony Richardson指出的那样, 通过管道将输出传递到任何循环中, 都会引起类似的问题.
# 循环的管道问题.
#  这个例子由Anthony Richardson编写,
#+ 由Wilbert Berendsen补遗.
foundone=false
find $HOME -type f -atime +30 -size 100k |
while true
do
   read f
   echo "$f is over 100KB and has not been accessed in over 30 days"
   echo "Consider moving the file to archives."
   foundone=true
   # ------------------------------------
   echo "Subshell level = $BASH_SUBSHELL"
   # Subshell level = 1
   # 没错, 现在是在子shell中运行.
   # ------------------------------------
done

#  变量foundone在这里肯定是false,
#+ 因为它是在子shell中被设置为true的.
if [ $foundone = false ]
then
   echo "No files need archiving."
fi
# =====================现在, 下边是正确的方法:=================
foundone=false
for f in $(find $HOME -type f -atime +30 -size 100k)  # 这里没使用管道.
do
   echo "$f is over 100KB and has not been accessed in over 30 days"
   echo "Consider moving the file to archives."
   foundone=true
done

if [ $foundone = false ]
then
   echo "No files need archiving."
fi
# ==================这里是另一种方法==================
#  将脚本中读取变量的部分放到一个代码块中,
#+ 这样一来, 它们就能在相同的子shell中共享了.
#  感谢, W.B.
find $HOME -type f -atime +30 -size 100k | {
     foundone=false
     while read f
     do
       echo "$f is over 100KB and has not been accessed in over 30 days"
       echo "Consider moving the file to archives."
       foundone=true
     done

     if ! $foundone
     then
       echo "No files need archiving."
     fi
}
一个相关的问题: 当你尝试将tail -f的stdout通过管道传递给grep时, 会产生问题.
tail -f /var/log/messages | grep "$ERROR_MSG" >> error.log
# "error.log"文件将不会写入任何东西.
```

- 在脚本中使用"suid"命令是非常危险的, 因为这会危及系统安全. [1]
- 使用shell脚本来编写CGI程序是值得商榷的. 因为[Shell](https://chegva.com/tag/shell/ "View all posts in Shell")脚本的变量不是"类型安全"的, 当CGI被关联的时候, 可能会产生令人不快的行为. 此外, 它还很难抵挡住"破解的考验".
- Bash不能正确的处理双斜线(//)字符串.
- 在Linux或BSD上编写的Bash脚本, 可能需要修改一下, 才能使它们运行在商业的UNIX(或Apple OSX)机器上. 这些脚本通常都使用GNU命令和过滤工具, GNU工具通常都比一般的UNIX上的同类工具更加强大. 这方面的一个非常明显的例子就是, 文本处理工具tr.

## 注意事项

| [1] | 给脚本设置*suid*权限是没用的. |

| --- | --- |

摘自：高级Bash脚本编程指南: 一本深入学习shell脚本艺术的书籍

**参考：**

- [Shell调试技巧](https://chegva.com/3776.html)
- [Shell学习宝典](https://chegva.com/2056.html)
