---
id: "doc-30c0a22a56d5"
title: "git checkout revert与reset"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Java", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68657525.html"
---

# git checkout revert与reset

```
git checkout
git checkout 使用于撤销未提交的修改，命令如下：

$ git checkout file-name
例如：

$ git checkout -- src/com/android/.../xxx.java
$ git checkout -- *.java #撤销所有java文件
$ git checkout . #撤销所有的修改
```

命令 git checkout –- readme.txt 意思就是，把 readme.txt 文件在工作区做的修改全部撤销，这里有 2 种情况，如下：

- readme.txt 自动修改后，还没有放到暂存区，使用撤销修改就回到和版本库一模一样的状态。
- 另外一种是 readme.txt 已经放入暂存区了，接着又作了修改，撤销修改就回到添加暂存区后的状态。

其实也就是撤销到最后一次没有放入暂存区的状态。注意：命令 git checkout —- readme.txt 中的 —- 很重要，如果没有 —- 的话，那么命令变成创建分支了。

## git revert

git revert 是用一次新的 commit 来回滚之前的 commit。

## git reset

| 选项 | 描述 |

| --- | --- |

| –hard | 暂存区，工作区全部用指定提交版本的目录树替换掉。 |

| –soft | 不进行暂存区和工作区的覆盖，只进行提交的版本的替换。 |

| –mixed（默认） | 覆盖暂存区，但不覆盖工作区。 |

git reset –-hard ** 版本回退是撤销某次提交，但是此次之后的修改都会被退回到暂存区。

## revert与reset的区别

在回滚操作上看，效果一样。但是在日后继续 merge 以前的老版本时有区别。revert 是用一次逆向的 commit “中和” 之前的提交，因此日后合并老的 branch 时，导致这部分改变不会再次出现，但是 reset 是之间把某些 commit 在某个 branch 上删除，因而和老的 branch 再次 merge 时，这些被回滚的 commit 应该还会被引入。

git reset 是把 HEAD 向后移动了一下，而 git revert 是 HEAD 继续前进，只是新的 commit 的内容和要 revert 的内容正好相反，能够抵消要被 revert 的内容。

这样在版本回退的时候就比较的好，比如本地 dev 分支，远程 master 分支，某一次的上线发现线上有重大的 bug，然后你 reset 本地代码到前一个版本，在你 git push 的时候 git 会报一个错误：“说你的本地分支版本低于远程 master 分支的版本，让你先去 pull 下来代码，再提交”，这就不行了，你 pull 下来的代码还是最新版有 bug 的代码，不进行 pull 代码，master 分支又不让你提交。

解决这个问题还得使用 revert 来进行 “回退” 操作，为什么加引号呢，是因为这种回退是向前提交一次中和了上次的修改，这就比较好了，这样你 revert 之后相当于指针向前移动一次，本地版本 dev 高于远程 master 版本，这时你就可以 git push 本地代码到远程了。也就是说，git reset 对未提交到（git push）远程的修改做回滚比较好，如果要回滚本地，同时想远程也回滚，就要用到 revert。

## git checkout revert与reset比较

| 命令 | 作用域 | 常用情景 |

| --- | --- | --- |

| git reset | 提交层面 | 在私有分支上舍弃一些没有提交的更改。 |

| git reset | 文件层面 | 将文件从缓存区中移除。 |

| git checkout | 提交层面 | 切换分支或查看旧版本。 |

| git checkout | 文件层面 | 舍弃工作目录中的更改。 |

| git revert | 提交层面 | 在公共分支上回滚更改。 |

| git revert | 文件层面 | （然而并没有）。 |
