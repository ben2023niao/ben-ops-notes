---
id: "doc-50c4294d23ff"
title: "Shell脚本示例"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "Linux", "日志分析", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/84417209.html"
---

# Shell脚本示例

**/etc/init.d/rpcbind** 展开源码

```bash
#! /bin/sh
#
# rpcbind       Start/Stop RPCbind
#
# chkconfig: 2345 13 87
# description: The rpcbind utility is a server that converts RPC program \
#              numbers into universal addresses. It must be running on the \
#              host to be able to make RPC calls on a server on that machine.
#
# processname: rpcbind
# probe: true
# config: /etc/sysconfig/rpcbind
# This is an interactive program, we need the current locale
[ -f /etc/profile.d/lang.sh ] && . /etc/profile.d/lang.sh
# We can't Japanese on normal console at boot time, so force.
if [ "$LANG" = "ja" -o "$LANG" = "ja_JP.eucJP" ]; then
 if [ "$TERM" = "linux" ] ; then

 fi
fi
# Source function library.
. /etc/init.d/functions

# Source networking configuration.
[ -f /etc/sysconfig/network ] && . /etc/sysconfig/network

prog="rpcbind"
[ -f /etc/sysconfig/$prog ] && . /etc/sysconfig/$prog
RETVAL=0
uid=`id | cut -d\( -f1 | cut -d= -f2`

start() {
 # Check that networking is up.
 [ "$NETWORKING" = "yes" ] || exit 6
 [ -f /sbin/$prog ] || exit 5
 # Make sure the rpcbind is not already running.
 if status $prog > /dev/null ; then
 exit 0
 fi
 # Only root can start the service
 [ $uid -ne 0 ] && exit 4
 echo -n $"Starting $prog: "
 daemon $prog $1 "$RPCBIND_ARGS"
 RETVAL=$?
 echo
 if [ $RETVAL -eq 0 ] ; then
 touch /var/lock/subsys/$prog
 [ ! -f /var/run/rpcbind.pid ] &&
 /sbin/pidof $prog > /var/run/rpcbind.pid
 fi
 return $RETVAL
}

stop() {
 echo -n $"Stopping $prog: "
 killproc $prog
 RETVAL=$?
 echo
 [ $RETVAL -eq 0 ] && {
 rm -f /var/lock/subsys/$prog
 rm -f /var/run/rpcbind*
 }
 return $RETVAL
}
# See how we were called.
case "$1" in
 start)
 start
 RETVAL=$?
 ;;
 stop)
 stop
 RETVAL=$?
 ;;
 status)
 status $prog
 RETVAL=$?
 ;;
 restart | reload| force-reload)
 stop
 start
 RETVAL=$?
 ;;
 condrestart | try-restart)
 if [ -f /var/lock/subsys/$prog ]; then
 stop
 start -w
 RETVAL=$?
 fi
 ;;
 *)
 echo $"Usage: $0 {start|stop|status|restart|reload|force-reload|condrestart|try-restart}"
 RETVAL=2
 ;;
esac
exit $RETVAL
```

**/etc/init.d/functions** 展开源码

```
#  -*-Shell-script-*-
#
# functions	This file contains functions to be used by most or all
#		shell scripts in the /etc/init.d directory.
#
# 该脚本几乎被 /etc/init.d/ 下的所有脚本所调用，因为它包含了大量的的基础函数。同时也被 /etc/rc.d/rc.sysinit引用 ，例如 success、action、failure 等函数
################################################################################
# functions这个脚本是给/etc/init.d里边的文件使用的。提供了一些基础的功能，看看里边究竟有些什么。首先会设置umask，path，还有语言环境，然后会设置success,failure,warning,normal几种情况下的字体颜色。下面再看看提供的重要方法：
# checkpid: 检查是否已存在pid，如果有一个存在，返回0（通过查看/proc目录）
# daemon: 启动某个服务。/etc/init.d目录部分脚本的start使用到这个
# killproc: 杀死某个进程。/etc/init.d目录部分脚本的stop使用到这个
# pidfileofproc: 寻找某个进程的pid
# pidofproc: 类似上面的，只是还查找了pidof命令
# status: 返回一个服务的状态
# echo_success,echo_failure,echo_passed,echo_warning分别输出各类信息
# success,failure,passed,warning分别记录日志并调用相应的方法
# action:打印某个信息并执行给定的命令，它会根据命令执行的结果来调用 success,failure方法
# strstr:判断$1是否含有$2
# confirm:显示 "Start service $1 (Y)es/(N)o/(C)ontinue? [Y]"的提示信息，并返回选择结果
TEXTDOMAIN=initscripts # 设置 TEXTDOMAIN 变量
# 某些系统使用LC_MESSAGES shell变量所指定的消息类型. 其他一些系统根据shell变量TEXTDOMAIN的值来创建消息类型的名称, 可能还会加上后缀'.mo'. 如果你使用TEXTDOMAIN变量, 你可能需要设置变量TEXTDOMAINDIR指向消息类型文件所在的位置. 还有某些系统以这种形式两个变量都使用: TEXTDOMAINDIR/LC_MESSAGES/Lc_Messages/TEXTDOMAIN.mo.
# Make sure umask is sane    # 确保 root 用户的 umask 是正确的 022 （也就是 rwxr-xr-x）
umask 022
# Set up a default search path.   # 设置默认的 PATH 变量
PATH="/sbin:/usr/sbin:/bin:/usr/bin"
export PATH # 导出为环境变量
# Get a sane screen width         # 设置正确的屏幕宽度
[ -z "${COLUMNS:-}" ] && COLUMNS=80 # 如果 COLUMNS 变量的值为空，则设置为 80 （列）
# 如果 CONSOLETYPE 为空则设置 CONSOLETYPE 为 /sbin/consoletype 命令返回的值
# 一般是 vt 或者 pty 、serial
[ -z "${CONSOLETYPE:-}" ] && CONSOLETYPE="$(/sbin/consoletype)"
################################################################################
# 如果存在 /etc/sysconfig/i18n 且 NOLOCALE 变量的值为空，则执行 /etc/sysconfig/i18n 文件，取得 LANG 变量的值，根据 LANG 的值作出选择
if [ -f /etc/sysconfig/i18n -a -z "${NOLOCALE:-}" -a -z "${LANGSH_SOURCED:-}" ] ; then
 . /etc/profile.d/lang.sh 2>/dev/null
 # avoid propagating LANGSH_SOURCED any further
 unset LANGSH_SOURCED
fi
# Read in our configuration
# 首先如果 BOOTUP 变量为空，则
if [ -z "${BOOTUP:-}" ]; then
 # 如果存在 /etc/sysconfig/init 文件，执行 /etc/sysconfig/init 文件
 if [ -f /etc/sysconfig/init ]; then
 . /etc/sysconfig/init
 else # 否则我们就手工设置
 # This all seem confusing? Look in /etc/sysconfig/init,
 # or in /usr/doc/initscripts-*/sysconfig.txt
 BOOTUP=color # 第一设置 BOOTUP 变量，默认就是 color
 RES_COL=60 # 设置在屏幕的第几列输出后面的 "[ xxx ]" ，默认是第60列
 # MOVE_TO_COL 是用于打印 "OK" 或者 "FAILED" ,或者 "PASSED" ,或者 "WARNING" 之前的部分，不含 "["
 MOVE_TO_COL="echo -en \\033[${RES_COL}G"
 SETCOLOR_SUCCESS="echo -en \\033[1;32m" # 设置后面的字体都为绿色
 SETCOLOR_FAILURE="echo -en \\033[1;31m" # 设置后面的字体都为红色
 SETCOLOR_WARNING="echo -en \\033[1;33m" # 设置后面的字体都为黄色
 SETCOLOR_NORMAL="echo -en \\033[0;39m" # 设置后面输出的字体都为白色（默认
 LOGLEVEL=1
 fi
 if [ "$CONSOLETYPE" = "serial" ]; then # 如果是通过串口登录的，则全部取消彩色输出
 BOOTUP=serial
 MOVE_TO_COL=
 SETCOLOR_SUCCESS=
 SETCOLOR_FAILURE=
 SETCOLOR_WARNING=
 SETCOLOR_NORMAL=
 fi
fi
################################################################################
# Interpret escape sequences in an fstab entry
fstab_decode_str() {
 fstab-decode echo "$1"
}
# Check if any of $pid (could be plural) are running
# 下面定义一个函数 checkpid （），目的是检查 /proc 下是否存在指定的目录（例如 /proc/1/）
checkpid() {
 local i

 for i in $* ; do
 [ -d "/proc/$i" ] && return 0 # 如果有任意一个存在，则返回0；
 done
 return 1 # 如果给出的参数全部不存在对应的目录，则返回1
}

__readlink() {
 ls -bl "$@" 2>/dev/null| awk '{ print $NF }'
}

__fgrep() {
 s=$1
 f=$2
 while read line; do
 if strstr "$line" "$s"; then
 echo $line
 return 0
 fi
 done < $f
 return 1
}
# __umount_loop awk_program fstab_file first_msg retry_msg retry_umount_args
# awk_program should process fstab_file and return a list of fstab-encoded
# paths; it doesn't have to handle comments in fstab_file.
__umount_loop() {
 local remaining sig=
 local retry=3 count

 remaining=$(LC_ALL=C awk "/^#/ {next} $1" "$2" | sort -r)
 while [ -n "$remaining" -a "$retry" -gt 0 ]; do
 if [ "$retry" -eq 3 ]; then
 action "$3" fstab-decode umount $remaining
 else
 action "$4" fstab-decode umount $5 $remaining
 fi
 count=4
 remaining=$(LC_ALL=C awk "/^#/ {next} $1" "$2" | sort -r)
 while [ "$count" -gt 0 ]; do
 [ -z "$remaining" ] && break
 count=$(($count-1))
 usleep 500000
 remaining=$(LC_ALL=C awk "/^#/ {next} $1" "$2" | sort -r)
 done
 [ -z "$remaining" ] && break
 kill $sig $(fstab-decode /sbin/fuser -m $remaining 2>/dev/null | sed -e "s/\b$$\b//g") > /dev/null
 sleep 3
 retry=$(($retry -1))
 sig=-9
 done
}
# Similar to __umount loop above, specialized for loopback devices
__umount_loopback_loop() {
 local remaining devremaining sig=
 local retry=3
 remaining=$(awk '$1 ~ /^\/dev\/loop/ && $2 != "/" {print $2}' /proc/mounts)
 devremaining=$(awk '$1 ~ /^\/dev\/loop/ && $2 != "/" {print $1}' /proc/mounts)
 while [ -n "$remaining" -a "$retry" -gt 0 ]; do
 if [ "$retry" -eq 3 ]; then
 action $"Unmounting loopback filesystems: " \
 fstab-decode umount $remaining
 else
 action $"Unmounting loopback filesystems (retry):" \
 fstab-decode umount $remaining
 fi
 for dev in $devremaining ; do
 losetup $dev > /dev/null 2>&1 && \
 action $"Detaching loopback device $dev: " \
 losetup -d $dev
 done
 remaining=$(awk '$1 ~ /^\/dev\/loop/ && $2 != "/" {print $2}' /proc/mounts)
 devremaining=$(awk '$1 ~ /^\/dev\/loop/ && $2 != "/" {print $1}' /proc/mounts)
 [ -z "$remaining" ] && break
 fstab-decode /sbin/fuser -k -m $sig $remaining >/dev/null
 sleep 3
 retry=$(($retry -1))
 sig=-9
 done
}
# __proc_pids {program} [pidfile]
# Set $pid to pids from /var/run* for {program}.  $pid should be declared
# local in the caller.
# Returns LSB exit code for the 'status' action.
# 检察pid文件
__pids_var_run() {
 local base=${1##*/}
 local pid_file=${2:-/var/run/$base.pid}
 local pid_dir=$(/usr/bin/dirname $pid_file)
 local binary=$3
 [ -d "$pid_dir" -a ! -r "$pid_dir" ] && return 4
 pid=
 if [ -f "$pid_file" ] ; then # 如果 /var/run 下存在该服务的 pid 文件，则
 local line p

 [ ! -r "$pid_file" ] && return 4 # "user had insufficient privilege"
 while : ; do # 对于 line 变量的每个 word 进行检查
 read line
 [ -z "$line" ] && break
 for p in $line ; do
# 如果 p 全部是数字，且存在 /proc/$p/ 目录，则认为该数字是一个 pid ，把它加入到 pid 变量
 if [ -z "${p//[0-9]/}" -a -d "/proc/$p" ] ; then
 if [ -n "$binary" ] ; then
 local b=$(readlink /proc/$p/exe | sed -e 's/\s*(deleted)$//')
 [ "$b" != "$binary" ] && continue
 fi
 pid="$pid $p" # 到最后 pid 变量的值可能是有多个由空格分隔的数字组成
 fi
 done
 done < "$pid_file" # 从该 pid 文件每次读取一行，送给变量 line 。注意 pid 文件可能有多行，且不一定都是数字
 if [ -n "$pid" ]; then
 return 0
 fi
 return 1 # "Program is dead and /var/run pid file exists"
 fi
 return 3 # "Program is not running"
}
# Output PIDs of matching processes, found using pidof
__pids_pidof() {
 pidof -c -m -o $$ -o $PPID -o %PPID -x "$1" || \
 pidof -c -m -o $$ -o $PPID -o %PPID -x "${1##*/}"
}
################################################################################
# A function to start a program.
# daemon 函数，它的作用是启动某项服务。/etc/init.d/ 下的脚本的 start 部分都会用到它
daemon() {
 # Test syntax.
 local gotbase= force= nicelevel corelimit
 local pid base= user= nice= bg= pid_file=
 local cgroup=
 nicelevel=0
 # daemon 函数本身可以指定多个选项，例如 --check <value> ，--check=<value>
 while [ "$1" != "${1##[-+]}" ]; do
 case $1 in
 '') echo $"$0: Usage: daemon [+/-nicelevel] {program}"
 # 也可以指定 nice 值
 return 1;;
 --check)
 base=$2
 gotbase="yes"
 shift 2
 ;;
 --check=?*)
 base=${1#--check=}
 gotbase="yes"
 shift
 ;;
 --user) # 也可以指定要以什么用户身份运行（--user <usr> , --user=<usr>)
 user=$2
 shift 2
 ;;
 --user=?*)
 user=${1#--user=}
 shift
 ;;
 --pidfile)
 pid_file=$2
 shift 2
 ;;
 --pidfile=?*)
 pid_file=${1#--pidfile=}
 shift
 ;;
 --force) # --force 表示强制运行
 force="force"
 shift
 ;;
 [-+][0-9]*)
 nice="nice -n $1" # 如果 daemon 的第一个参数是数字，则认为是 nice 值
 shift
 ;;
 *) echo $"$0: Usage: daemon [+/-nicelevel] {program}"
 return 1;;
 esac
 done
 # Save basename.
 # basename 就是从服务器的二进制程序的 full path 中取出最后的部分
 [ -z "$gotbase" ] && base=${1##*/}
 # See if it's already running. Look *only* at the pid file.
 # 检查该服务是否已经在运行。不过 daemon 函数只查看 pid 文件而已
 __pids_var_run "$base" "$pid_file"

 # 如果 pid 变量最终为空，且 force 变量为空（不强制启动），则返回
 [ -n "$pid" -a -z "$force" ] && return
 # make sure it doesn't core dump anywhere unless requested
 # ulimit 是控制由该 shell 启动的进程能够使用的资源，-S 是 soft control 的意思，-c 是指最大的 core
 # dump 文件大小，如果 DEAMON_COREFILE_LIMIT 为空，则默认为 0
 corelimit="ulimit -S -c ${DAEMON_COREFILE_LIMIT:-0}"
 # if they set NICELEVEL in /etc/sysconfig/foo, honor it
 # 如果存在 /etc/sysconfi/foo 文件，且其中有 NICELEVEL 变量则用它代替  daemon 后面的那个 nice 值
 # 注意，这里的 nice 赋值是用 nice -n <value> 的格式，因为 nice 本身可以启动命令，用这个格式较方便
 [ -n "${NICELEVEL:-}" ] && nice="nice -n $NICELEVEL"
 # if they set CGROUP_DAEMON in /etc/sysconfig/foo, honor it
 # cgroup进程设置
 if [ -n "${CGROUP_DAEMON}" ]; then
 if [ ! -x /bin/cgexec ]; then
 echo -n "Cgroups not installed"; warning
 echo
 else
 cgroup="/bin/cgexec";
 for i in $CGROUP_DAEMON; do
 cgroup="$cgroup -g $i";
 done
 fi
 fi
 # Echo daemon
 # 如果 BOOTUP 的值为 verbose ，则打印一个服务名
 [ "${BOOTUP:-}" = "verbose" -a -z "${LSB:-}" ] && echo -n " $base"
 # And start it up.
 # 如果 user 变量为空，则默认使用 root 启动它
 if [ -z "$user" ]; then
 $cgroup $nice /bin/bash -c "$corelimit >/dev/null 2>&1 ; $*"
 else
 $cgroup $nice runuser -s /bin/bash $user -c "$corelimit >/dev/null 2>&1 ; $*"
 fi
 # 如果上面的命令成功，则显示一个绿色的 [ OK ] ，否则显示 [ FAILURE ]
 [ "$?" -eq 0 ] && success $"$base startup" || failure $"$base startup"
}
################################################################################
# A function to stop a program.
# /etc/init.d/ 下面的脚本的 stop 部分都会用到它
killproc() {
 local RC killlevel= base pid pid_file= delay try binary=
 RC=0; delay=3; try=0 # RC 是最终返回的值，初始化为 0
 # Test syntax.
 # killproc 函数的语法格式是 killproc <service> [<signal>] ，例如 killproc nginx 9
 if [ "$#" -eq 0 ]; then
 echo $"Usage: killproc [-p pidfile] [ -d delay] {program} [-signal]"
 return 1
 fi
 if [ "$1" = "-p" ]; then
 pid_file=$2
 shift 2
 fi
 if [ "$1" = "-b" ]; then
 if [ -z $pid_file ]; then
 echo $"-b option can be used only with -p"
 echo $"Usage: killproc -p pidfile -b binary program"
 return 1
 fi
 binary=$2
 shift 2
 fi
 if [ "$1" = "-d" ]; then
 delay=$(echo $2 | awk -v RS=' ' -v IGNORECASE=1 '{if($1!~/^[0-9.]+[smhd]?$/) exit 1;d=$1~/s$|^[0-9.]*$/?1:$1~/m$/?60:$1~/h$/?60*60:$1~/d$/?24*60*60:-1;if(d==-1) exit 1;delay+=d*$1} END {printf("%d",delay+0.5)}')
 if [ "$?" -eq 1 ]; then
 echo $"Usage: killproc [-p pidfile] [ -d delay] {program} [-signal]"
 return 1
 fi
 shift 2
 fi
 # check for second arg to be kill level
 # 如果 $2 不为空，则表示用户有设定信号，则把 $2 的值赋予 killlevel 变量
 [ -n "${2:-}" ] && killlevel=$2
 # Save basename.
 # basename 得出服务的名称
 base=${1##*/}
 # Find pid.
 # 找出pid
 __pids_var_run "$1" "$pid_file" "$binary"
 RC=$?
 if [ -z "$pid" ]; then
 if [ -z "$pid_file" ]; then
 pid="$(__pids_pidof "$1")"
 else
 [ "$RC" = "4" ] && { failure $"$base shutdown" ; return $RC ;}
 fi
 fi
 # Kill it.
 if [ -n "$pid" ] ; then # 如果 pid 的值最终不为空
 # 且 BOOTUP 的值为 verbose ，且 LSB 变量不为空，则打印一个服务名
 [ "$BOOTUP" = "verbose" -a -z "${LSB:-}" ] && echo -n "$base "
 if [ -z "$killlevel" ] ; then # 用户没有指定信号
 # 调用 checkpid  $pid 检查是否在 /proc/ 下存在进程目录
 if checkpid $pid 2>&1; then
 # TERM first, then KILL if not dead
 # 如果有，先尝试用 TERM 信息，不行再用 KILL 信号
 kill -TERM $pid >/dev/null 2>&1
 # usleep 和 sleep 一样，不过单位是百万分之1秒。这里休眠1秒
 usleep 100000
 if checkpid $pid ; then
 # 如果 checkpid $pid 还是查到有 /proc/<pid>/ 目录存在，则表示还没有杀死，继续等待1秒
 try=0
 # 如果1秒后用 checkpid 检查还是有，则再等待3秒；
 while [ $try -lt $delay ] ; do
 checkpid $pid || break
 sleep 1
 let try+=1
 done
 # 如果还是没有杀死，则用 KILL 信号
 if checkpid $pid ; then
 # 执行 kill -KILL 杀死它
 kill -KILL $pid >/dev/null 2>&1
 # 等待1秒种
 usleep 100000
 fi
 fi
 fi
 checkpid $pid # 再次检查 pid 目录
 RC=$? # 并把结果返回给 RC ，这就算是 killproc 的最后状态了
 # 如果 RC 的值为0，则表示kill -9 没有杀死了进程，则调用 failure 函数，否则调用 success
 [ "$RC" -eq 0 ] && failure $"$base shutdown" || success $"$base shutdown"
 RC=$((! $RC))
 # use specified level only
 # 上面都是在没有指定信号的情况的，下面是用户指定了信号的。例如 restart）或者 reload）部分
 else
 if checkpid $pid; then # 如果检查到进程存在，则
 # 执行kill命令，但使用指定的信号 $killlevel
 kill $killlevel $pid >/dev/null 2>&1
 RC=$? # 并把状态值返回给变量 RC
 # 如果 RC 为0则表示成功，调用 success；否则调用 failure 函数
 [ "$RC" -eq 0 ] && success $"$base $killlevel" || failure $"$base $killlevel"
 elif [ -n "${LSB:-}" ]; then
 RC=7 # Program is not running
 fi
 fi
 else
 if [ -n "${LSB:-}" -a -n "$killlevel" ]; then
 RC=7 # Program is not running
 else # 这个 else 是针对 if [ -n "${pid:-}" ]  的，也就是说没有 pid 文件，pidof 命令也没有找到 pid ，则调用 failure 函数，表示停止服务失败
 failure $"$base shutdown"
 RC=0
 fi
 fi
 # Remove pid file if any.
 # 根据具体情况可能需要删除 pid 文件
 if [ -z "$killlevel" ]; then
 # 如果pid_file文件不存在，则删除 /var/run 下的 pid 文件
 rm -f "${pid_file:-/var/run/$base.pid}"
 fi
 # 并把 RC 作为 exit status 返回
 return $RC
}
################################################################################
# A function to find the pid of a program. Looks *only* at the pidfile
# pidfileofproc 和 checkpid 类似，但不执行 pidof 命令，只查询 pid 文件
pidfileofproc() {
 local pid

 # Test syntax.
 if [ "$#" = 0 ] ; then
 echo $"Usage: pidfileofproc {program}"
 return 1
 fi
 __pids_var_run "$1"
 [ -n "$pid" ] && echo $pid
 return 0
}
################################################################################
# A function to find the pid of a program.
# pidofproc 函数和上面的 pidfileofproc 函数类似，但多了一步 pidof 命令
pidofproc() {
 local RC pid pid_file=
 # Test syntax.
 if [ "$#" = 0 ]; then
 echo $"Usage: pidofproc [-p pidfile] {program}"
 return 1
 fi
 if [ "$1" = "-p" ]; then
 pid_file=$2
 shift 2
 fi
 fail_code=3 # "Program is not running"
 # First try "/var/run/*.pid" files
 __pids_var_run "$1" "$pid_file"
 RC=$?
 if [ -n "$pid" ]; then
 echo $pid
 return 0
 fi
 [ -n "$pid_file" ] && return $RC
 __pids_pidof "$1" || return $RC
}
################################################################################
# status 函数是判断服务的状态，总共有4种
status() {
 local base pid lock_file= pid_file= binary=
 # Test syntax.
 if [ "$#" = 0 ] ; then
 echo $"Usage: status [-p pidfile] {program}"
 return 1
 fi
 if [ "$1" = "-p" ]; then
 pid_file=$2
 shift 2
 fi
 if [ "$1" = "-l" ]; then
 lock_file=$2
 shift 2
 fi
 if [ "$1" = "-b" ]; then
 if [ -z $pid_file ]; then
 echo $"-b option can be used only with -p"
 echo $"Usage: status -p pidfile -b binary program"
 return 1
 fi
 binary=$2
 shift 2
 fi
 base=${1##*/}
 # First try "pidof"
 # 同样是查找 pid 先，调用__pids_var_run
 __pids_var_run "$1" "$pid_file" "$binary"
 RC=$?
 if [ -z "$pid_file" -a -z "$pid" ]; then
 # 如果没有pidfile文件和pid，则直接使用 pidof 命令
 pid="$(__pids_pidof "$1")"
 fi
 if [ -n "$pid" ]; then # 如果 pid 变量的值不为空，则表示找到进程
 # 则打印 "xxx (pid nnn) is running "，并返回0
 echo $"${base} (pid $pid) is running..."
 return 0
 fi
 case "$RC" in
 0)
 echo $"${base} (pid $pid) is running..."
 return 0
 ;;
 1)
 # 如果 pidof 命令找不到，但从 pid 文件找到了 pid ，则打印如下信息，并返回1
 echo $"${base} dead but pid file exists"
 return 1
 ;;
 4)
 echo $"${base} status unknown due to insufficient privileges."
 return 4
 ;;
 esac
 if [ -z "${lock_file}" ]; then
 lock_file=${base}
 fi
 # See if /var/lock/subsys/${lock_file} exists
 # 如果 pidof 命令和 pid 文件都没有找到 pid，但在 /var/lock/subsys 下存在对应的文件，则打如下信息并返回2
 if [ -f /var/lock/subsys/${lock_file} ]; then
 echo $"${base} dead but subsys locked"
 return 2
 fi
 # 如果 pidof 命令、pidf 文件都没有找到pid ，且没有别锁，则打印 “xxx is stopped”，并返回3
 echo $"${base} is stopped"
 return 3
}
################################################################################
# 下面的 echo_xxx 函数就是真正在屏幕上打印 [ OK ] 、[ PASSED ]、[ FAILURE ]、[ WARNING ] 的部分了
echo_success() { # 以echo_success 部分为例
 [ "$BOOTUP" = "color" ] && $MOVE_TO_COL # 首先是打印 “[” 之前的空格
 echo -n "[" # 然后打印 "["
 [ "$BOOTUP" = "color" ] && $SETCOLOR_SUCCESS # 设置字体为红色
 echo -n $"  OK  " # 打印 OK
 [ "$BOOTUP" = "color" ] && $SETCOLOR_NORMAL # 返回字体为白色
 echo -n "]" # 打印 "]"
 echo -ne "\r" # 换行
 return 0 # 返回 0，其他一律返回 1
}

echo_failure() {
 [ "$BOOTUP" = "color" ] && $MOVE_TO_COL
 echo -n "["
 [ "$BOOTUP" = "color" ] && $SETCOLOR_FAILURE
 echo -n $"FAILED"
 [ "$BOOTUP" = "color" ] && $SETCOLOR_NORMAL
 echo -n "]"
 echo -ne "\r"
 return 1
}

echo_passed() {
 [ "$BOOTUP" = "color" ] && $MOVE_TO_COL
 echo -n "["
 [ "$BOOTUP" = "color" ] && $SETCOLOR_WARNING
 echo -n $"PASSED"
 [ "$BOOTUP" = "color" ] && $SETCOLOR_NORMAL
 echo -n "]"
 echo -ne "\r"
 return 1
}

echo_warning() {
 [ "$BOOTUP" = "color" ] && $MOVE_TO_COL
 echo -n "["
 [ "$BOOTUP" = "color" ] && $SETCOLOR_WARNING
 echo -n $"WARNING"
 [ "$BOOTUP" = "color" ] && $SETCOLOR_NORMAL
 echo -n "]"
 echo -ne "\r"
 return 1
}
################################################################################
# Inform the graphical boot of our current state
update_boot_stage() {
 if [ -x /bin/plymouth ]; then
 /bin/plymouth --update="$1"
 fi
 return 0
}
################################################################################
# Log that something succeeded
# success 函数除了打印 [ xxx ] 之外，还会使用 initlog 记录信息
success() {
 [ "$BOOTUP" != "verbose" -a -z "${LSB:-}" ] && echo_success
 return 0
}
# Log that something failed
failure() {
 local rc=$?
 [ "$BOOTUP" != "verbose" -a -z "${LSB:-}" ] && echo_failure
 [ -x /bin/plymouth ] && /bin/plymouth --details
 return $rc
}
# Log that something passed, but may have had errors. Useful for fsck
passed() {
 local rc=$?
 [ "$BOOTUP" != "verbose" -a -z "${LSB:-}" ] && echo_passed
 return $rc
}
# Log a warning
warning() {
 local rc=$?
 [ "$BOOTUP" != "verbose" -a -z "${LSB:-}" ] && echo_warning
 return $rc
}
################################################################################
# Run some action. Log its output.
# action 函数是另外一个最重要的函数，它的作用是打印某个提示信息并执行给定命令
action() {
 local STRING rc

 STRING=$1
 echo -n "$STRING "
 shift
 "$@" && success $"$STRING" || failure $"$STRING"
 rc=$?
 echo
 return $rc
}
# Run some action. Silently.
action_silent() {
 local STRING rc

 STRING=$1
 echo -n "$STRING "
 shift
 "$@" >/dev/null && success $"$STRING" || failure $"$STRING"
 rc=$?
 echo
 return $rc
}
################################################################################
# returns OK if $1 contains $2
# strstr 函数是判断 $1 字符串是否含有 $2 字符串，是则返回0，否则返回1
strstr() {
 [ "${1#*$2*}" = "$1" ] && return 1
 return 0
}
################################################################################
# Confirm whether we really want to run this service
# confirm 函数是用于交互式的启动服务
confirm() {
 [ -x /bin/plymouth ] && /bin/plymouth --hide-splash
 while : ; do
 echo -n $"Start service $1 (Y)es/(N)o/(C)ontinue? [Y] " # 打印一个提示信息
 read answer
 # 如果 answer 变量是 y 或者 Y 则返回 0（但未真正启动）
 if strstr $"yY" "$answer" || [ "$answer" = "" ] ; then
 return 0
 elif strstr $"cC" "$answer" ; then
 rm -f /var/run/confirm
 [ -x /bin/plymouth ] && /bin/plymouth --show-splash
 return 2
 elif strstr $"nN" "$answer" ; then
 return 1
 fi
 done
}
# resolve a device node to its major:minor numbers in decimal or hex
get_numeric_dev() {
(
 fmt="%d:%d"
 if [ "$1" == "hex" ]; then
 fmt="%x:%x"
 fi
 ls -lH "$2" | awk '{ sub(/,/, "", $5); printf("'"$fmt"'", $5, $6); }'
) 2>/dev/null
}
# Check whether file $1 is a backup or rpm-generated file and should be ignored
is_ignored_file() {
 case "$1" in
 *~ | *.bak | *.orig | *.rpmnew | *.rpmorig | *.rpmsave)
 return 0
 ;;
 esac
 return 1
}
# Evaluate shvar-style booleans
is_true() {
 case "$1" in
 [tT] | [yY] | [yY][eE][sS] | [tT][rR][uU][eE])
 return 0
 ;;
 esac
 return 1
}
# Evaluate shvar-style booleans
is_false() {
 case "$1" in
 [fF] | [nN] | [nN][oO] | [fF][aA][lL][sS][eE])
 return 0
 ;;
 esac
 return 1
}
# Apply sysctl settings, including files in /etc/sysctl.d
apply_sysctl() {
 sysctl -e -p /etc/sysctl.conf >/dev/null 2>&1
 for file in /etc/sysctl.d/* ; do
 is_ignored_file "$file" && continue
 test -f "$file" && sysctl -e -p "$file" >/dev/null 2>&1
 done
}

key_is_random() {
 [ "$1" = "/dev/urandom" -o "$1" = "/dev/hw_random" \
 -o "$1" = "/dev/random" ]
}

find_crypto_mount_point() {
 local fs_spec fs_file fs_vfstype remaining_fields
 local fs
 while read fs_spec fs_file remaining_fields; do
 if [ "$fs_spec" = "/dev/mapper/$1" ]; then
 echo $fs_file
 break;
 fi
 done < /etc/fstab
}
# Because of a chicken/egg problem, init_crypto must be run twice.  /var may be
# encrypted but /var/lib/random-seed is needed to initialize swap.
init_crypto() {
 local have_random dst src key opt mode owner params makeswap skip arg opt
 local param value rc ret mke2fs mdir prompt mount_point

 ret=0
 have_random=$1
 while read dst src key opt; do
 [ -z "$dst" -o "${dst#\#}" != "$dst" ] && continue
 [ -b "/dev/mapper/$dst" ] && continue;
 if [ "$have_random" = 0 ] && key_is_random "$key"; then
 continue
 fi
 if [ -n "$key" -a "x$key" != "xnone" ]; then
 if test -e "$key" ; then
 owner=$(ls -l $key | (read a b owner rest; echo $owner))
 if ! key_is_random "$key"; then
 mode=$(ls -l "$key" | cut -c 5-10)
 if [ "$mode" != "------" ]; then
 echo $"INSECURE MODE FOR $key"
 fi
 fi
 if [ "$owner" != root ]; then
 echo $"INSECURE OWNER FOR $key"
 fi
 else
 echo $"Key file for $dst not found, skipping"
 ret=1
 continue
 fi
 else
 key=""
 fi
 params=""
 makeswap=""
 mke2fs=""
 skip=""
 # Parse the src field for UUID= and convert to real device names
 if [ "${src%%=*}" == "UUID" ]; then
 src=$(/sbin/blkid -t "$src" -l -o device)
 elif [ "${src/^\/dev\/disk\/by-uuid\/}" != "$src" ]; then
 src=$(__readlink $src)
 fi
 # Is it a block device?
 [ -b "$src" ] || continue
 # Is it already a device mapper slave? (this is gross)
 devesc=${src##/dev/}
 devesc=${devesc//\//!}
 for d in /sys/block/dm-*/slaves ; do
 [ -e $d/$devesc ] && continue 2
 done
 # Parse the options field, convert to cryptsetup parameters and
 # contruct the command line
 while [ -n "$opt" ]; do
 arg=${opt%%,*}
 opt=${opt##$arg}
 opt=${opt##,}
 param=${arg%%=*}
 value=${arg##$param=}
 case "$param" in
 cipher)
 params="$params -c $value"
 if [ -z "$value" ]; then
 echo $"$dst: no value for cipher option, skipping"
 skip="yes"
 fi
 ;;
 size)
 params="$params -s $value"
 if [ -z "$value" ]; then
 echo $"$dst: no value for size option, skipping"
 skip="yes"
 fi
 ;;
 hash)
 params="$params -h $value"
 if [ -z "$value" ]; then
 echo $"$dst: no value for hash option, skipping"
 skip="yes"
 fi
 ;;
 verify)
 params="$params -y"
 ;;
 swap)
 makeswap=yes
 ;;
 tmp)
 mke2fs=yes
 esac
 done
 if [ "$skip" = "yes" ]; then
 ret=1
 continue
 fi
 if [ -z "$makeswap" ] && cryptsetup isLuks "$src" 2>/dev/null ; then
 if key_is_random "$key"; then
 echo $"$dst: LUKS requires non-random key, skipping"
 ret=1
 continue
 fi
 if [ -n "$params" ]; then
 echo "$dst: options are invalid for LUKS partitions," \
 "ignoring them"
 fi
 if [ -n "$key" ]; then
 /sbin/cryptsetup -d $key luksOpen "$src" "$dst" <&1 2>/dev/null && success || failure
 rc=$?
 else
 mount_point="$(find_crypto_mount_point $dst)"
 [ -n "$mount_point" ] || mount_point=${src##*/}
 prompt=$(printf $"%s is password protected" "$mount_point")
 plymouth ask-for-password --prompt "$prompt" --command="/sbin/cryptsetup luksOpen -T1 $src $dst" <&1
 rc=$?
 fi
 else
 [ -z "$key" ] && plymouth --hide-splash
 /sbin/cryptsetup $params ${key:+-d $key} create "$dst" "$src" <&1 2>/dev/null && success || failure
 rc=$?
 [ -z "$key" ] && plymouth --show-splash
 fi
 if [ $rc -ne 0 ]; then
 ret=1
 continue
 fi
 if [ -b "/dev/mapper/$dst" ]; then
 if [ "$makeswap" = "yes" ]; then
 mkswap "/dev/mapper/$dst" 2>/dev/null >/dev/null
 fi
 if [ "$mke2fs" = "yes" ]; then
 if mke2fs "/dev/mapper/$dst" 2>/dev/null >/dev/null \
 && mdir=$(mktemp -d /tmp/mountXXXXXX); then
 mount "/dev/mapper/$dst" "$mdir" && chmod 1777 "$mdir"
 umount "$mdir"
 rmdir "$mdir"
 fi
 fi
 fi
 done < /etc/crypttab
 return $ret
}
# A sed expression to filter out the files that is_ignored_file recognizes
__sed_discard_ignored_files='/\(~\|\.bak\|\.orig\|\.rpmnew\|\.rpmorig\|\.rpmsave\)$/d'
#if we have privileges lets log to kmsg, otherwise to stderr
if strstr "$(cat /proc/cmdline)" "rc.debug"; then
 [ -w /dev/kmsg ] && exec 30>/dev/kmsg && BASH_XTRACEFD=30
 set -x
fi
```

**参考：**

- [Shell学习宝典](https://chegva.com/2056.html)
- [如何写SysV服务管理脚本](https://www.cnblogs.com/f-ck-need-u/p/7524401.html)
- [functions文件详细分析和说明](https://www.cnblogs.com/f-ck-need-u/p/7518142.html)
- [/etc/init.d/functions详解](https://www.cnblogs.com/image-eye/archive/2011/10/26/2220405.html)
- [/etc/rc.d/rc.sysinit 全文注释详解](https://chegva.com/3638.html)
