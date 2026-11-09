---
id: "doc-479fcaf1704c"
title: "mongodb容器化单机部署"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "MongoDB", "Docker", "Nginx", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84414429.html"
---

# mongodb容器化单机部署

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BMongoDB%2BDocker-mongodb%E5%AE%B9%E5%99%A8%E5%8C%96%E5%8D%95%E6%9C%BA%E9%83%A8%E7%BD%B2.md)

MMP读写集群部署还要改项目代码
![文档配图](../media/7b7f6603557bc21fe8.png)

所以用最简单的方式来部署 mongodb

```bash
docker run -d \
-p 27017:27017 \
-v /etc/localtime:/etc/localtime \
-v /opt/mongodb/mongo_configdb:/data/configdb \
-v /opt/mongodb/mongo_db:/data/db \
--name docker_mongodb mongo:3.2

# 交互界面进入 mongo
docker exec -it docker_mongodb mongo admin
# 创建一个 admin 管理员账号
db.createUser({
user: "root",
pwd: "[已脱敏]",
roles: [ { role: "root", db: "admin" } ]
})
# 创建一个 performance 项目库账号
use performance
db.createUser({
user: "user-xxx",
pwd: "[已脱敏]",
roles: [ { role: "dbOwner", db: "performance" } ]
})

url: 'mongodb://203.0.113.1:27017/performance', # 配置文件内未开启认证时:
url: 'mongodb://user-xxx:[密码已脱敏]@203.0.113.1:27017/performance’,  # 开启认证后:
```

**docker-install-mongo.sh** 展开源码

```bash
#!/bin/bash
if [[ $EUID -ne 0 ]]; then
 echo "This script must be run as root"
 exit 1
fi
function init_ulimits(){ #[ulimits 配置]
cat > /etc/security/limits.conf <<EOF
* soft noproc 20480
* hard noproc 20480
root soft nofile 65535
root hard nofile 65535
* soft nofile 65535
* hard nofile 65535
EOF
ulimit -n 65535
ulimit -u 20480
echo "[ulimits 配置] ==> OK"
}
function init_tomcat() { #[tomcat 用户ssh密钥配置]
useradd tomcat
usermod -aG sudo tomcat
mkdir -p /home/tomcat/.ssh
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAxV6WVONrWBPUNIhw4IrtZSF8F7gUrRlXgZ0CXeAQIFSFXve8qAQ86lIWWDSKjygGfl6FKUoxYzhRzxfhRiKjAwi3BH7d1lKlFwzOBvOPeS57K5znWXPz+E09/Vj1xJ9MHqzl3/Ece0M/2srPtVTgB1Ico8AFi9pPaYZSy3bue36OKVFnC9kVvkriiIe/k/vux5KF/TcXCkc91IVMGCqp8H8NqaJnQWmFB1RYMz9JUe6G9V400iTn9cJmcfS7r5jfT+ZI3K0s6FiCDvQ5LsRNcZhD4uy6YdkG3QBOPOuSwR1sHOcfADyMkWPAXezasI7nfAj7VuuMiqvVt2Ju5A1low== tomcat@jump' > /home/tomcat/.ssh/authorized_keys
chown -R tomcat.tomcat /home/tomcat/
echo "[tomcat 用户ssh密钥配置] ==> OK"
}
function init_kernel(){ #[内核 优化]
cat > /etc/sysctl.conf <<EOF
fs.file-max = 65535
net.ipv4.tcp_max_tw_buckets = 5000
#表示系统同时保持TIME_WAIT套接字的最大数量，如果超过这个数字，TIME_WAIT套接字将立刻被清除并打印警告信息。减少它的最大数量，避免Squid服务器被大量的TIME_WAIT套接字拖死。
net.ipv4.tcp_max_orphans = 3276800
#系统中最多有多少个TCP套接字不被关联到任何一个用户文件句柄上。
net.ipv4.tcp_fin_timeout = 30
#表示如果套接字由本端要求关闭，这个参数决定了它保持在FIN-WAIT-2状态的时间。
net.ipv4.tcp_keepalive_time = 1200
#表示当keepalive起用的时候，TCP发送keepalive消息的频度。缺省是2小时，改为20分钟。
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_tw_reuse = 1
#表示开启重用，允许将TIME-WAIT sockets重新用于新的TCP连接。
net.ipv4.tcp_timestamps = 0
#时间戳可以避免序列号的卷绕。一个1Gbps的链路肯定会遇到以前用过的序列号，时间戳能够让内核接受这种“异常”的数据包，这里需要将其关掉。
net.ipv4.tcp_tw_recycle = 1
#表示开启TCP连接中TIME-WAIT sockets的快速回收。
net.ipv4.ip_local_port_range = 1024 65000
#表示用于向外连接的端口范围。缺省情况下很小：32768到61000，改为1024到65000。
net.ipv4.tcp_mem = 786432 1048576 1572864
#同样有3个值
#net.ipv4.tcp_mem[0]:低于此值，TCP没有内存压力
#net.ipv4.tcp_mem[1]:在此值下，进入内存压力阶段
#net.ipv4.tcp_mem[2]:高于此值，TCP拒绝分配socket。
#可根据物理内存大小进行调整，如果内存足够大的话，可适当往上调。建议94500000 915000000 927000000。
net.core.wmem_default = 8388608
#发送套接字缓冲区大小的缺省值（以字节为单位）
net.core.rmem_default = 8388608
#接收套接字缓冲区大小的缺省值（以字节为单位）
net.core.rmem_max = 16777216
#接收套接字缓冲区大小的最大值（以字节为单位）
net.core.wmem_max = 16777216
#发送套接字缓冲区大小的最大值（以字节为单位）
net.ipv4.tcp_wmem = 8192 436600 873200
#TCP写buffer,可参考的优化值: 8192 436600 873200
net.ipv4.tcp_rmem = 32768 436600 873200
#TCP读buffer,可参考的优化值: 32768 436600 873200
net.core.somaxconn = 65408
#web应用中listen函数的backlog默认会给我们内核参数的net.core.somaxconn限制到128，而nginx定义的NGX_LISTEN_BACKLOG默认为511，所以有必要调整这个值。
net.core.netdev_max_backlog = 262144
#每个网络接口接收数据包的速率比内核处理这些包的速率快时，允许送到队列的数据包的最大数目。
net.ipv4.tcp_max_syn_backlog = 8192
#表示SYN队列的长度，默认为1024，加大队列长度为8192，可以容纳更多等待连接的网络连接数。
net.ipv4.tcp_retries2 = 5
net.ipv4.conf.lo.arp_ignore = 0
net.ipv4.conf.lo.arp_announce = 0
net.ipv4.conf.all.arp_ignore = 0
EOF
sysctl -p >/dev/null 2>&1
echo "[内核 优化] ==> OK"
}
check_yum=`whereis yum | sed "s/yum://g" | md5sum | awk '{print $1}'`
check_apt=`whereis apt | sed "s/apt://g" | md5sum | awk '{print $1}'`
if [[ "$check_yum" != '68b329da9893e34099c7d8ad5cb9c940' ]];then install=yum ;fi
if [[ "$check_apt" != '68b329da9893e34099c7d8ad5cb9c940' ]];then install=apt ;fi ;echo "[服务器包管理器]                       ==> $install"
if [[ "$install" == 'apt' ]];then #全自动配置mongo集群
apt-get update >> /dev/null ;echo "[apt update]                                 ==> OK"
timedatectl set-timezone Asia/Shanghai ;echo "[设置上海时区Asia/Shanghai]                  ==> OK"
apt-get install -y net-tools vim wget curl zip unzip
apt-get install -y docker* >> /dev/null ;echo "[net-tools vim wget curl zip unzip docker* ] ==> OK"
systemctl start docker;systemctl enable docker;systemctl is-enabled docker;docker ps ;echo "[start docker]                               ==> OK"
docker run -d \
-p 27017:27017 \
-v /etc/localtime:/etc/localtime \
-v /opt/mongodb/mongo_configdb:/data/configdb \
-v /opt/mongodb/mongo_db:/data/db \
--name docker_mongodb mongo:3.2

docker ps
cat > echo.txt << EOF
# 交互界面进入 mongo
docker exec -it docker_mongodb mongo admin
# 创建一个 admin 管理员账号
db.createUser({
user: "root",
pwd: "[已脱敏]",
roles: [ { role: "root", db: "admin" } ]
})

# 创建一个 performance 项目库账号
use performance
db.createUser({
user: "user-xxx",
pwd: "[已脱敏]",
roles: [ { role: "dbOwner", db: "performance" } ]
})

# 配置文件内未开启认证时:
url: 'mongodb://203.0.113.1:27017/performance',
# 开启认证后:
url: 'mongodb://user-xxx:[密码已脱敏]@203.0.113.1:27017/performance’,
EOF
cat echo.txt
fi
```
