---
id: "doc-a7b6813a4da2"
title: "mysql 提权"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "MySQL", "SQL注入", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68652368.html"
---

# mysql 提权

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4%2BMySQL%2BSQL%E6%B3%A8%E5%85%A5-mysql%20%E6%8F%90%E6%9D%83.md)

A valid MySQL server must be available.

## Shell

It can be used to break out from restricted environments by spawning an interactive system shell.

- ```
mysql -e '\! /bin/sh'

```
## Library load

It loads shared libraries that may be used to run code in the binary execution context.

- A MySQL server must accept connections in order for this to work.

The following loads the `/path/to/[lib.so](http://lib.so)` shared object.
```

mysql --default-auth ../../../../../path/to/lib

```
## Sudo

If the binary is allowed to run as superuser by `sudo`, it does not drop the elevated privileges and may be used to access the file system, escalate or maintain privileged access.

- ```
sudo mysql -e '\! /bin/sh'
```

## Limited SUID

If the binary has the SUID bit set, it may be abused to access the file system, escalate or maintain access with elevated privileges working as a SUID backdoor. If it is used to run commands (e.g., via `system()`-like invocations) it only works on systems like Debian (<= Stretch) that allow the default `sh` shell to run with SUID privileges.

This example creates a local SUID copy of the binary and runs it to maintain elevated privileges. To interact with an existing SUID binary skip the first command and run the program using its original path.

- ```
sudo install -m =xs $(which mysql) .

./mysql -e '\! /bin/sh'

```
```
