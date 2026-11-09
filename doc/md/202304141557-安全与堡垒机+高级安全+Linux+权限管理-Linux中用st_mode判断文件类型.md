---
id: "doc-f993c587cbe6"
title: "Linux中用st_mode判断文件类型"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Linux", "权限管理", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68654648.html"
---

# Linux中用st_mode判断文件类型

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2BLinux%2B%E6%9D%83%E9%99%90%E7%AE%A1%E7%90%86-Linux%E4%B8%AD%E7%94%A8st_mode%E5%88%A4%E6%96%AD%E6%96%87%E4%BB%B6%E7%B1%BB%E5%9E%8B.md)

```c
在Linux中，可以利用stat()函数来获取一个文件的状态
#include <sys/stat.h>
#include <unistd.h>
int stat(const char *file_name, struct stat *buf);
这个函数执行成功返回0，失败返回-1。取得的文件状态存放在buf指针指向的struct stat结构提中， struct stat的定义如下：
struct stat
{
dev_t st_dev; /* ID of device containing file -文件所在设备的ID*/
ino_t st_ino; /* inode number -inode节点号*/
mode_t st_mode; /* 文件的类型和存取的权限*/
nlink_t st_nlink; /* number of hard links -链向此文件的连接数(硬连接)*/
uid_t st_uid; /* user ID of owner -user id*/
gid_t st_gid; /* group ID of owner - group id*/
dev_t st_rdev; /* device ID (if special file) -设备号，针对设备文件*/
off_t st_size; /* total size, in bytes -文件大小，字节为单位*/
blksize_t st_blksize; /* blocksize for filesystem I/O -系统块的大小*/
blkcnt_t st_blocks; /* number of blocks allocated -文件所占块数*/
time_t st_atime; /* time of last access -最近存取时间*/
time_t st_mtime; /* time of last modification -最近修改时间*/
time_t st_ctime; /* time of last status change - */
};
其中， st_mode这个变量用来判断文件类型。
st_mode是用特征位来表示文件类型的，特征位的定义如下：
S_IFMT 0170000 文件类型的位遮罩
S_IFSOCK 0140000 socket
S_IFLNK 0120000 符号链接(symbolic link)
S_IFREG 0100000 一般文件
S_IFBLK 0060000 区块装置(block device)
S_IFDIR 0040000 目录
S_IFCHR 0020000 字符装置(character device)
S_IFIFO 0010000 先进先出(fifo)
S_ISUID 0004000 文件的(set user-id on execution)位
S_ISGID 0002000 文件的(set group-id on execution)位
S_ISVTX 0001000 文件的sticky位
S_IRWXU 00700 文件所有者的遮罩值(即所有权限值)
S_IRUSR 00400 文件所有者具可读取权限
S_IWUSR 00200 文件所有者具可写入权限
S_IXUSR 00100 文件所有者具可执行权限
S_IRWXG 00070 用户组的遮罩值(即所有权限值)
S_IRGRP 00040 用户组具可读取权限
S_IWGRP 00020 用户组具可写入权限
S_IXGRP 00010 用户组具可执行权限
S_IRWXO 00007 其他用户的遮罩值(即所有权限值)
S_IROTH 00004 其他用户具可读取权限
S_IWOTH 00002 其他用户具可写入权限
S_IXOTH 00001 其他用户具可执行权限
摘自《Linux C 函数库参考手册》
判断文件类型时，用对文件的st_mode的值与上面给出的值相与，再比较。比如：
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
int main()
{
int abc;
struct stat buf;
stat("/home", &buf);
abc = buf.st_mode & S_IFDIR;//与对应的标志位相与
if(abc == S_IFDIR) //结果与标志位比较
printf("It's a directory.\n");
return 0;
}
运行结果：
It's a directory.
其实还有一个简单的方法，文件类型在POSIX中定义了检查这些类型的宏定义：
S_ISLINGK(st_mode) 判断是否位符号链接
S_ISREG(st_mode) 是否为一般文件
S_ISDIR(st_mode) 是否为目录
S_ISCHR(st_mode) 是否位字符装置文件
S_ISBLK(s3e) 是否先进先出
S_ISSOCK(st_mode) 是否为socket
可以根据这些函数的返回值判断，如果是，则返回1。（我试了一下，好像是这样的)
```
