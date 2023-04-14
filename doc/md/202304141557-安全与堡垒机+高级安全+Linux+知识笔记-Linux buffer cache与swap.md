---
id: "doc-bd81544e9b52"
title: "Linux buffer cache与swap"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Linux", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68656954.html"
---

# Linux buffer cache与swap

## Linux缓存机制介绍

在 **[Linux](https://haicoder.net/linux/linux-tutorial.html)** 系统中，为了提高文件系统性能，内核利用一部分物理内存分配出缓冲区，用于缓存系统操作和数据文件，当内核收到读写的请求时，内核先去缓存区找是否有请求的数据，有就直接返回，如果没有则通过驱动程序直接操作磁盘。

缓存机制优点：减少系统调用次数，降低 CPU 上下文切换和磁盘访问频率。

### CPU上下文切换

CPU 上下文切换是指 CPU 给每个进程一定的服务时间，当时间片用完后，内核从正在运行的进程中收回处理器，同时把进程当前运行状态保存下来，然后加载下一个任务，这个过程叫做上下文切换。

实质上就是被终止运行进程与待运行进程的进程切换。

## Linux swap

### 用途

Swap 意思是交换分区，通常我们说的虚拟内存，是从硬盘中划分出的一个分区。

当物理内存不够用的时候，内核就会释放缓存区（buffers/cache）里一些长时间不用的程序，然后将这些程序临时放到 Swap 中，也就是说如果物理内存和缓存区内存不够用的时候，才会用到 Swap。

### swap清理

我们要清理 swap，可以使用如下命令：

`swapoff -a && swapon -a`

注意：这样清理有个前提条件，空闲的内存必须比已经使用的 swap 空间大。

## 查看缓存区及内存使用情况

在 Linux 中，我们要查看缓存以及内存使用情况，可以使用 free 命令，free 命令用于检测物理内存和交换内存已使用量和可用量（默认单位为 KB）

`[root@backup ~]# free -m # 使用-m参数表示以兆字节为单位显示内存

 total used free shared buffers cached

Mem: 64181 44372 19809 3 12 216

-/+ buffers/cache: 44143 20038

Swap: 32767 0 32767`

第一部分 Mem 行解释：

| 字段 | 描述 |

| --- | --- |

| *total* | 内存总数 |

| *used* | 已经使用的内存数 |

| *free* | 空闲的内存数 |

| *shared* | 当前已经废弃不用 |

| *buffers* | 缓存内存数 |

| *cached* | 缓存内存数 |

第二部分 (-/+ buffers/cache) 解释：

| 字段 | 描述 |

| --- | --- |

| (-buffers/cache) used内存数 | 第一部分 Mem 行中的 used – buffers – cached |

| (+buffers/cache) free内存数 | 第一部分 Mem 行中的 free + buffers + cached |

可见 -buffers/cache 反映的是被程序实实在在吃掉的内存，而 +buffers/cache 反映的是可以挪用的内存总数。

第三部分是指交换分区。

## 定期时间间隔更新内存状态

如果我们要定时刷新查看内存使用状态，我们可以使用 free -s 选项加上一个整数，用来在定期时间间隔内更新free 命令。比如，下面的命令将会在每 5 秒更新一个 free 命令：

`free -s 5`

## buffer与cached

### 定义

缓存（cached）是把读取过的数据保存起来，重新读取时若命中（找到需要的数据）就不要去读硬盘了，若没有命中就读硬盘。其中的数据会根据读取频率进行组织，把最频繁读取的内容放在最容易找到的位置，把不再读的内容不断往后排，直至从中删除。

缓冲（buffers）是根据磁盘的读写设计的，把分散的写操作集中进行，减少磁盘碎片和硬盘的反复寻道，从而提高系统性能。

Linux 有一个守护进程定期清空缓冲内容（即写入磁盘），也可以通过 sync 命令手动清空缓冲。举个例子吧：我这里有一个 ext2 的U盘，我往里面 cp 一个 3M 的 MP3，但 U 盘的灯没有跳动，过了一会儿（或者手动输入 sync）U 盘的灯就跳动起来了。卸载设备时会清空缓冲，所以有些时候卸载一个设备时要等上几秒钟。

修改 /etc/sysctl.conf 中的 vm.swappiness 右边的数字可以在下次开机时调节 swap 使用策略。该数字范围是 0～100，数字越大越倾向于使用 swap。默认为 60，可以改一下试试。

两者都是 RAM 中的数据，简单来说，buffer 是即将要被写入磁盘的，而 cache 是被从磁盘中读出来的。

buffer 是由各种进程分配的，被用在如输入队列等方面。一个简单的例子如某个进程要求有多个字段读入，在所有字段被读入完整之前，进程把先前读入的字段放在 buffer 中保存。

cache 经常被用在磁盘的 I/O 请求上，如果有多个进程都要访问某个文件，于是该文件便被做成 cache 以方便下次被访问，这样可提高系统性能。

### buffer与cached详解

#### Cache

缓冲区，高速缓存，是位于 CPU 与主内存间的一种容量较小但速度很高的存储器。

由于 CPU 的速度远高于主内存，CPU 直接从内存中存取数据要等待一定时间周期，Cache 中保存着 CPU 刚用过或循环使用的一部分数据，当 CPU 再次使用该部分数据时可从 Cache 中直接调用，这样就减少了 CPU 的等待时间，提高了系统的效率。

Cache 又分为一级 Cache(L1 Cache)和二级 Cache(L2 Cache)，L1 Cache 集成在 CPU 内部，L2 * Cache 早期一般是焊在主板上,现在也都集成在 CPU 内部，常见的容量有 256KB 或 512KB L2 Cache。

它是根据程序的局部性原理而设计的，就是 cpu 执行的指令和访问的数据往往在集中的某一块，所以把这块内容放入 cache 后，cpu 就不用在访问内存了，这就提高了访问速度。当然若 cache 中没有 cpu 所需要的内容，还是要访问内存的。从内存读取与磁盘读取角度考虑，cache 可以理解为操作系统为了更高的读取效率，更多的使用内存来缓存可能被再次访问的数据。

Cache 并不是缓存文件的，而是缓存块的(块是 I/O 读写最小的单元)；Cache 一般会用在 I/O 请求上，如果多个进程要访问某个文件，可以把此文件读入 Cache 中，这样下一个进程获取 CPU 控制权并访问此文件直接从 Cache 读取，提高系统性能。

#### Buffer

缓冲区，一个用于存储速度不同步的设备或优先级不同的设备之间传输数据的区域。通过 buffer 可以减少进程间通信需要等待的时间，当存储速度快的设备与存储速度慢的设备进行通信时，存储慢的数据先把数据存放到 buffer，达到一定程度存储快的设备再读取 buffer 的数据，在此期间存储快的设备 CPU 可以干其他的事情。

Buffer：一般是用在写入磁盘的，例如：某个进程要求多个字段被读入，当所有要求的字段被读入之前已经读入的字段会先放到 buffer 中。Buffer 是根据磁盘的读写设计的，把分散的写操作集中进行，减少磁盘碎片和硬盘的反复寻道，从而提高系统性能。Linux 有一个守护进程定期清空缓冲内容（即写入磁盘），也可以通过 sync 命令手动清空缓冲。

#### 总结

- cache 是高速缓存，用于 CPU 和内存之间的缓冲；
- buffer 是 I/O 缓存，用于内存和硬盘的缓冲；
- cache 最初用于 cpu cache，主要原因是 cpu 与 memory，由于 cpu 快，memory 跟不上，且有些值使用次数多，所以放入 cache 中，主要目的是，重复使用，并且一级/二级物理 cache 速度快。
- buffer 主要用于 disk 与 memory，主要是保护硬盘或减少网络传输的次数（内存数据表现 dataSet）。当然也可以提高速度（不会立即写入硬盘或直接从硬盘中读出的数据马上显示），重复使用，最初最主要的目的是保护 disk。

## free

- Free 中的 buffer 和 cache：（它们都是占用内存）
- buffer : 作为 buffer cache 的内存，是块设备的读写缓冲区
- cache: 作为 page cache 的内存, 文件系统的 cache
- 如果 cache 的值很大，说明 cache 住的文件数很多。如果频繁访问到的文件都能被 cache 住，那么磁盘的读IO bi 会非常小。

## 手动清理缓存

清理 pagecache（页面缓存）

`[root@backup ~]# echo 1 > /proc/sys/vm/drop_caches 或者 # sysctl -w vm.drop_caches=1`

清理 dentries（目录缓存）和 inodes

`[root@backup ~]# echo 2 > /proc/sys/vm/drop_caches 或者 # sysctl -w vm.drop_caches=2`

清理 pagecache、dentries 和 inodes

`[root@backup ~]# echo 3 > /proc/sys/vm/drop_caches 或者 # sysctl -w vm.drop_caches=3`

上面三种方式都是临时释放缓存的方法，要想永久释放缓存，需要在 /etc/sysctl.conf 文件中配置：vm.drop_caches=1/2/3，然后 sysctl -p 生效即可！

另外，可以使用 sync 命令来清理文件系统缓存，还会清理僵尸(zombie)对象和它们占用的内存。

### 清理步骤总结

```
echo 1 > /proc/sys/vm/drop_caches

echo 2 > /proc/sys/vm/drop_caches

echo 3 > /proc/sys/vm/drop_caches
sync
```
