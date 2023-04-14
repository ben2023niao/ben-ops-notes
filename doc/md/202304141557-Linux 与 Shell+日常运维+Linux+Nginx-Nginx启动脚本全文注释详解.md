---
id: "doc-f2eb13af6195"
title: "Nginx启动脚本全文注释详解"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "Linux", "Nginx", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/84417212.html"
---

# Nginx启动脚本全文注释详解

**nginx服务脚本 /etc/init.d/nginx** 展开源码

```bash
#!/bin/bash
#
# nginx - this script starts and stops the nginx daemon    # 脚本功能简介
#
# chkconfig:   - 85 15    # 开机自动启动设置
# description:  NGINX is an HTTP(S) server, HTTP(S) reverse \
#               proxy and IMAP/POP3 proxy server    # 脚本描述
# processname: nginx    # 进程名称及相关配置文件
# config:      /etc/nginx/nginx.conf
# config:      /etc/sysconfig/nginx
# pidfile:     /var/run/nginx.pid
# Source function library.    # 加载系统函数库 functions
. /etc/rc.d/init.d/functions

# Source networking configuration.    # 加载网络配置
. /etc/sysconfig/network

# Check that networking is up.
# 检测网络服务是否启动，为 no 则退出脚本
[ "$NETWORKING" = "no" ] && exit 0
# 启动命令赋值给变量nginx
nginx="/usr/local/nginx/sbin/nginx"
# 取变量中的名称，即进程名
prog=$(basename $nginx)
# nginx配置文件路径
NGINX_CONF_FILE="/usr/local/nginx/conf/nginx.conf"
# 如果存在sysconfig,则加载
[ -f /etc/sysconfig/nginx ] && . /etc/sysconfig/nginx

# 定义锁文件路径
lockfile=/var/lock/subsys/nginx

make_dirs() {
 # make required directories
 user=`$nginx -V 2>&1 | grep "configure arguments:.*--user=" | sed 's/[^*]*--user=\([^ ]*\).*/\1/g' -`
 if [ -n "$user" ]; then
 if [ -z "`grep $user /etc/passwd`" ]; then
 useradd -M -s /bin/nologin $user
 fi
 options=`$nginx -V 2>&1 | grep 'configure arguments:'`
 for opt in $options; do
 if [ `echo $opt | grep '.*-temp-path'` ]; then
 value=`echo $opt | cut -d "=" -f 2`
 if [ ! -d "$value" ]; then
 # echo "creating" $value
 mkdir -p $value && chown -R $user $value
 fi
 fi
 done
 fi
}

start() { # 定义start函数
 [ -x $nginx ] || exit 5 # nginx不可执行，则退出脚本
 [ -f $NGINX_CONF_FILE ] || exit 6 # 如果配置文件不存在，则退出脚本
 make_dirs # 创建必需目录
 echo -n $"Starting $prog: " # 打印开始启动提示
 daemon $nginx -c $NGINX_CONF_FILE # 调用系统daemon函数，指定配置文件启动nginx服务
 retval=$? # 将启动命令返回值赋值给retval，后面会进行判断
 echo # 打印空行
 [ $retval -eq 0 ] && touch $lockfile # 如果返回值为0，则创建锁文件，表示服务启动成功
 return $retval # 返回状态值
}

stop() { # 定义stop函数
 echo -n $"Stopping $prog: "
 killproc $prog -QUIT # 使用系统killproc函数指定参数停止nginx服务
 retval=$?
 echo
 [ $retval -eq 0 ] && rm -f $lockfile # 如果返回值为0，则删除锁文件，表示关闭服务成功
 return $retval
}

restart() { # 定义重启服务函数
 configtest || return $? # 如果检查语法不成功，则退出函数
 stop # 执行停止函数
 sleep 1 # 等待1s钟，确保服务正常退出
 start # 执行启动函数
}

reload() { # 定义重新加载配置函数
 configtest || return $?
 echo -n $"Reloading $prog: "
 killproc $nginx -HUP # -HUP优雅停止nginx服务
 RETVAL=$?
 echo
}

force_reload() {
 restart
}

configtest() { # 定义检查语法的函数
 $nginx -t -c $NGINX_CONF_FILE # -t 检查语法，-c 指定配置文件
}

rh_status() { # 状态函数
 status $prog # 打印nginx服务状态
}

rh_status_q() { # 静默状态检查函数
 rh_status >/dev/null 2>&1 # 输出和错误都定向到空
}
case "$1" in # 获取传参值
 start)
 rh_status_q && exit 0 # 如果状态检查成功，则退出脚本，不需要启动
 $1 # 获取 $1 值，执行start函数
 ;;
 stop)
 rh_status_q || exit 0 # 如果状态检查不成功，则退出脚本，不需要启动
 $1 # 获取 $1 值，执行stop函数
 ;;
 restart|configtest)
 $1
 ;;
 reload)
 rh_status_q || exit 7
 $1
 ;;
 force-reload)
 force_reload
 ;;
 status)
 rh_status
 ;;
 condrestart|try-restart)
 rh_status_q || exit 0
 ;;
 *) # 上述值都不匹配，则打印使用帮助提示，并退出脚本
 echo $"Usage: $0 {start|stop|status|restart|reload|configtest}"
 exit 2
esac
```

## CentOS7 Nginx启动脚本

Nginx的安装路径为`/usr/local/nginx`

```
# 脚本文件
/usr/lib/systemd/system/nginx.service

# 脚本内容
[Unit]
Description=nginx - high performance web server
Documentation=http://nginx.org/en/docs/
After=network.target

[Service]
Type=forking
PIDFile=/var/run/nginx.pid
ExecStartPost=/bin/sleep 0.1
ExecStartPre=/usr/local/nginx/sbin/nginx -t -c /usr/local/nginx/conf/nginx.conf
ExecStart=/usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID
LimitNOFILE=1000000
LimitNPROC=1000000
LimitCORE=1000000
[Install]
WantedBy=multi-user.target
```

## 相关命令

- 启动：`systemctl start nginx`
- 停止：`systemctl stop nginx`
- 重启：`systemctl restart nginx`

参考：

- [Shell学习宝典](https://chegva.com/2056.html)
- [Shell脚本示例](https://chegva.com/3632.html)
- [跟老男孩学Linux运维：Shell编程实](https://github.com/anzhihe/learning/tree/master/shell)
- [/etc/rc.d/rc.sysinit 全文注释详解](https://chegva.com/3637.html)
