---
id: "doc-5c1acd58f3ff"
title: "Git工具"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Linux", "Windows", "日志分析", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68657421.html"
---

# Git工具

```
Git支持的协议
本地传输
SSH 协议
Git 协议
HTTP 协议
本地协议
远程仓库在该协议中就是硬盘上的另一个目录。这常见于团队每一个成员都对一个共享的文件系统(例如 NFS )拥有访问权。

$ git clone /opt/git/project.git
$ git clone file:///opt/git/project.git
$ git remote add local_proj /opt/git/project.git
SSH协议
$ git clone ssh://user@server:project.git
Git工具
Git补丁
如果收到的补丁文件是用 git diff 或由其它 Unix 的 diff 命令生成，就该用 git apply 命令来应用补丁。

$ git apply /tmp/patch-ruby-client.patch
如果贡献者提供的是 format-patch 补丁：

$ git am 0001-limit-log-function.patch
引用日志
在你工作的同时，Git 在后台的工作之一就是保存一份引用日志——一份记录最近几个月你的 HEAD 和分支引用的日志。

$ git reflog
每次你的分支顶端因为某些原因被修改时，Git 就会为你将信息保存在这个临时历史记录里面。你也可以使用这份数据来指明更早的分支。如果你想查看仓库中 HEAD 在五次前的值，你可以使用引用日志的输出中的
@n 引用：

$ git show HEAD@{5}
祖先引用
另一种指明某次提交的常用方法是通过它的祖先。如果你在引用最后加上一个 ˆ，Git 将其理解为此次提交的父提交。那么，想看上一次提交，你可以使用 HEADˆ，意思是 “HEAD 的父提交”：

$ git show HEAD^
你也可以在 ˆ 后添加一个数字——例如， d921970ˆ2 意思是 “d921970 的第二父提交”

$ git show d921970^2
双点
你想要查看你的试验分支上哪些没有被提交到主分支，那么你就可以使用 master…experiment 来让 Git 显示这些提交的日志——这句话的意思是 “所有可从 experiment 分支中获得而不能从 master 分支中获得的提交”。

$ git log master..experiemnt
另一方面，如果你想看相同的——所有在 master 而不在 experiment 中的分支——你可以交换分支的名字。experiment…master 显示所有可在 master 获得而在 experiment 中不能的提交：

$ git log experiment..master
这在你想保持 experiment 分支最新和预览你将合并的提交的时候特别有用。这个语法的另一种常见用途是查看你将把什么推送到远程：

$ git log origin/master..HEAD
这条命令显示任何在你当前分支上而不在远程 origin 上的提交。

多点
多点语法就像速记一样有用；但是你也许会想针对两个以上的分支来指明修订版本，比如查看哪些提交被包含在某些分支中的一个，但是不在你当前的分支上。Git 允许你在引用前使用ˆ字符或者–not 指明你不希望提交被包含其中的分支。因此下面三个命令是等同的：

$ git log refA..refB
$ git log ^refA refB
$ git log refB --not refA
这样很好，因为它允许你在查询中指定多于两个的引用，而这是点语法所做不到的。例如，如果你想查找所有从 refA 或 refB 包含的但是不被 refC 包含的提交，你可以输入下面中的一个：

$ git log refA refB ^refC
$ git log refA refB --not refC
三点
这个可以指定被两个引用中的一个包含但不被两者同时包含的分支。如果你想查看 master 或者 experiment 中包含的但不是两者共有的引用，你可以运行：

$ git log master...experiment
这个再次给出你普通的 log 输出但是只显示那四次提交的信息，按照传统的提交日期排列。这种情形下， log 命令的一个常用参数是 --left-right，它会显示每个提交到底处于哪一侧的分支。这使得数据更加有用。

$ git log --left-right master...experiment
交互式暂存
如果你运行 git add 时加上-i或者 --interactive 选项，Git 就进入了一个交互式的 shell 模式。

$ git add -i
储藏
经常有这样的事情发生，当你正在进行项目中某一部分的工作，里面的东西处于一个比较杂乱的状态，而你想转到其他分支上进行一些工作。问题是，你不想提交进行了一半的工作，否则以后你无法回到这个工作点。

解决这个问题的办法就是 git stash 命令。“储藏“ 可以获取你工作目录的中间状态——也就是你修改过的被追踪的文件和暂存的变更——并将它保存到一个未完结变更的堆栈中，随时可以重新应用。

储藏：

git stash
查看储藏：

git stash list
应用储藏

git stash apply stash@2
移除储藏：

git stash drop stash@2
引用储藏并移除：

git stash pop
从储藏中创建分支：

git stash branch， branchname
重写历史
改变最近一次提交：

$ git commit --amend
修改多个提交说明：

$ git rebase -i HEAD~3
$ git commit --amend
$ git rebase --continue
再次提醒这是一个衍合命令—— HEAD~3…HEAD 范围内的每一次提交都会被重写，无论你是否修改说明。不要涵盖你已经推送到中心服务器的提交——这么做会使其他开发者产生混乱。

核弹级选项：filter-branch，如果你想用脚本的方式修改大量的提交，还有一个重写历史的选项可以用——例如，全局性地修改电子邮件地址或者将一个文件从所有提交中删除。这个命令是 filter-branch，这个会大面积地修改你的历史，所以你很有可能不该去用它，除非你的项目尚未公开，没有其他人在你准备修改的提交的基础上工作。

$ git filter-branch --tree-filter 'rm -f passwords.txt' HEAD
自定义Git
设置编辑器
$ git config --global core.editor emacs
修改 core.editor 即可。

提交模板
如果把此项指定为你系统上的一个文件，当你提交的时候， Git 会默认使用该文件定义的内容。 例如：你创建了一个模板文件 $HOME/.gitmessage.txt

$ git config --global commit.template $HOME/.gitmessage.txt
颜色
Git 会按照你需要自动为大部分的输出加上颜色，你能明确地规定哪些需要着色以怎样着色，设置 color.ui 为 true 来打开所有的默认终端着色：

$ git config --global color.ui true
格式化与空白
格式化与空白是许多开发人员在协作时，特别是在跨平台情况下，遇到的令人头疼的小问题。 由于编辑器的不同或者 Windows 程序员在跨平台项目中的文件行尾加入了回车换行符， 一些细微的空格变化会不经意地进入大家合作的工作或提交的补丁中。不用怕，Git 的一些配置选项会帮助你解决这些问题。

假如你正在 Windows 上写程序，或者你正在和其他人合作，他们在 Windows 上编程，而你却在其他系统上，在这些情况下，你可能会遇到行尾结束符问题。 这是因为 Windows 使用回车和换行两个字符来结束一行，而 Mac 和 Linux 只使用换行一个字符。 虽然这是小问题，但它会极大地扰乱跨平台协作。Git 可以在你提交时自动地把行结束符 CRLF 转换成 LF，而在签出代码时把 LF 转换成 CRLF。用 core.autocrlf 来打开此项功能， 如果是在 Windows 系统上，把它设置成 true，这样当签出代码时，LF 会被转换成 CRLF：

$ git config --global core.autocrlf true
Linux 或 Mac 系统使用 LF 作为行结束符，因此你不想 Git 在签出文件时进行自动的转换；当一个以 CRLF 为行结束符的文件不小心被引入时你肯定想进行修正， 把 core.autocrlf 设置成 input 来告诉 Git 在提交时把 CRLF 转换成 LF，签出时不转换：

$ git config --global core.autocrlf input
这样会在 Windows 系统上的签出文件中保留 CRLF，会在 Mac 和 Linux 系统上，包括仓库中保留 LF。如果你是 Windows 程序员，且正在开发仅运行在 Windows 上的项目，可以设置 false 取消此功能，把回车符记录在库中：

$ git config --global core.autocrlf false
```
