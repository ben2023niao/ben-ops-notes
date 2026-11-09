---
id: "doc-873cb8ea3866"
title: "Git中的origin和master"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68657480.html"
---

# Git中的origin和master

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-Git%E4%B8%AD%E7%9A%84origin%E5%92%8Cmaster.md)

```
首先要明确一点，对 Git 的操作是围绕 3 个大的步骤来展开的 ：

从 git 拉取数据（git clone）
改动代码
将改动传回 git（git push）
这 3 个步骤又涉及到两个 repository，一个是 remote repository，在远程服务器上，一个是 local repository，在自己工作区上。

1, 3 两个步骤涉及到 remote server/remote repository/remote branch
2 涉及到 local repository/local branch
git clone 会根据你指定的 remote server/repository/branch，拷贝一个副本到你本地，在 git push 之前，你对所有文件的改动都是在你自己本地的 local repository 来做的，你的改动(local branch)和 remote branch 是独立（并行）的。Git 显示的就是 local repository。

在 clone 完成之后，Git 会自动为你将此远程仓库命名为 origin（origin 只相当于一个别名，运行 git remote –v 或者查看 .git/config 可以看到 origin 的含义），并下载其中所有的数据，建立一个指向它的 master 分支的指针，我们用(远程仓库名)/(分支名)这样的形式表示远程分支，所以 origin/master 指向的是一个 remote branch（从那个 branch 我们 clone 数据到本地），但你无法在本地更改其数据。

同时，Git 会建立一个属于你自己的本地 master 分支，它指向的是你刚刚从 remote server 传到你本地的副本。随着你不断的改动文件，git add, git commit，master 的指向会自动移动，你也可以通过 merge（fast forward）来移动 master 的指向。

$git branch -a (to show all the branches git knows about)
运行后，输出如下：

* master
remotes/origin/HEAD -> origin/master
remotes/origin/master
接着，我们再次查看分支：

$git branch -r (to show remote branches git knows about)
运行后，输出如下：

origin/HEAD -> origin/master
origin/master
可以发现，master 就是 local branch，origin/master 是 remote branch（master is a branch in the local repository. remotes/origin/master is a branch named master on the remote named origin）

$git diff origin/master master （show me the changes between the remote master branch and my master branch).
需要注意的是，remotes/origin/master 和 origin/master 的指向是相同的：

$git diff origin/master remotes/origin/master
```

## 总结

- 在 git clone 完成之后，Git 会自动为你将此远程仓库命名为 origin。
- 在 git clone 完成之后，Git 会建立一个属于你自己的本地 master 分支，它指向的是你刚刚从 remote server 传到你本地的副本。
- master 就是本地 master 分支。
- origin/master 是远程仓库 origin 下的 master 分支。
- remotes/origin/master 等同于 origin/master。
