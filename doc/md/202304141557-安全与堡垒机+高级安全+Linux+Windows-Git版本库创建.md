---
id: "doc-d10075217768"
title: "Git版本库创建"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Linux", "Windows", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68657428.html"
---

# Git版本库创建

版本库又名仓库，英文名 repository，你可以简单理解成一个目录，这个目录里面的所有文件都可以被 **[Git](https://haicoder.net/git/git-tutorial.html)** 管理起来，每个文件的修改、删除，Git 都能跟踪，以便任何时刻都可以追踪历史，或者在将来某个时刻可以 “还原”。

## Git创建版本库

```
选择一个合适的地方，创建一个空目录：
mkdir learngit
cd learngit
通过 git init 命令把这个目录变成 Git 可以管理的仓库：

git init
仓库建好了，当前目录下多了一个 .git 的目录，这个目录是 Git 来跟踪管理版本库的，没事千万不要手动修改这个目录里面的文件，不然改乱了，就把 Git 仓库给破坏了。

把文件添加到版本库

首先这里再明确一下，所有的版本控制系统，其实只能跟踪文本文件的改动，比如 TXT 文件，网页，所有的程序代码等等，Git 也不例外。

版本控制系统可以告诉你每次的改动，比如在第 5 行加了一个单词 “Linux”，在第 8 行删了一个 词 “Windows”。而图片、视频这些二进制文件，虽然也能由版本控制系统管理，但没法跟踪文件的变化，只能把二进制文件每次改动串起来，也就是只知道图片从 100KB 改成了 120KB，但到底改了啥，版本控制系统不知道，也没法知道。

不幸的是，Microsoft 的 Word 格式是二进制格式，因此，版本控制系统是没法跟踪 Word 文件的改动的，前面我们举的例子只是为了演示，如果要真正使用版本控制系统，就要以纯文本方式编写文件。

git add readme.txt
git commit -m "wrote a readme file"
为什么 Git 添加文件需要 add，commit 一共两步呢？因为 commit 可以一次提交很多文件，所以你可以多次 add 不同的文件，比如：

git add file1.txt
git add file2.txt file3.txt
git commit -m "add 3 files."
```
