---
id: "doc-df4a50c7b4bc"
title: "docker 部署mongo分片集群"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "MongoDB", "Docker", "Nginx", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84415156.html"
---

# docker 部署mongo分片集群

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BLinux%2BMongoDB-docker%20%E9%83%A8%E7%BD%B2mongo%E5%88%86%E7%89%87%E9%9B%86%E7%BE%A4.md)

**初始化脚本 init_linux_docker.sh** 展开源码

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
systemctl start docker;systemctl enable docker;systemctl is-enabled docker;docker ps ;echo "[start docker]                     ==> OK"
fi
```

```bash
服务器ip 203.0.113.1
参考来源 https://gitee.com/VinceHsu/docker-mongo.git
root@public-zaneperfor-mongo:~# wget https://raw.githubusercontent.com/ben2023niao/img/main/docker-mongo.zip-aa
root@public-zaneperfor-mongo:~# wget https://raw.githubusercontent.com/ben2023niao/img/main/docker-mongo.zip-ab
root@public-zaneperfor-mongo:~# wget https://raw.githubusercontent.com/ben2023niao/img/main/docker-mongo.zip-ac
root@public-zaneperfor-mongo:~# wget https://raw.githubusercontent.com/ben2023niao/img/main/docker-mongo.zip-ad
root@public-zaneperfor-mongo:~# cat docker-mongo.zip-a* > docker-mongo.zip
root@public-zaneperfor-mongo:~# rm -f docker-mongo.zip-a*
root@public-zaneperfor-mongo:~# unzip docker-mongo.zip
Archive: docker-mongo.zip
 creating: mongo/
 inflating: mongo/Dockerfile
 inflating: mongo/mongodb-4.0.2.tgz
 creating: mongos/
 inflating: mongos/Dockerfile
root@public-zaneperfor-mongo:~# ls
docker-mongo.zip mongo mongos
root@public-zaneperfor-mongo:~# tree .
.
├── docker-mongo.zip
├── mongo
│   ├── Dockerfile
│   └── mongodb-4.0.2.tgz
└── mongos
 └── Dockerfile

出镜像
cd mongo
docker build -t cfg_mongo:v1 .
cd ../mongos
docker build -t cfg_route_mongos:v1 .

查看镜像
docker images
REPOSITORY TAG IMAGE ID CREATED SIZE
cfg_route_mongo v1 2e1d837e3e51 3 hours ago 546MB
cfg_mongo v1 928d0e141ff4 3 hours ago 546MB
centos 7 eeb6ee3f44bd 17 months ago 204MB

运行容器
#创建1个configsvr，其中1个主节点，1个从节点
docker run -d -p 27012:27012 --name mongo_config_1 cfg_mongo:v1 --configsvr --dbpath /data/db --port 27012 --replSet crs --bind_ip_all
docker run -d -p 27013:27013 --name mongo_config_2 cfg_mongo:v1 --configsvr --dbpath /data/db --port 27013 --replSet crs --bind_ip_all

启动1个路由服务（mongos）
docker run -d -p 27011:27011 --name mongo_route_1 cfg_route_mongos:v1 --configdb crs/203.0.113.1:27012,203.0.113.1:27013 --port 27011 --bind_ip_all

创建2个分片服务（shardsvr），每个shardsvr包含2个副本，其中1个主节点，1个从节点
docker run -d -p 27017:27017 --name mongo_rs1_1 cfg_mongo:v1 --shardsvr --dbpath /data/db --port 27017 --replSet rs1 --bind_ip_all
docker run -d -p 27016:27016 --name mongo_rs1_2 cfg_mongo:v1 --shardsvr --dbpath /data/db --port 27016 --replSet rs1 --bind_ip_all
docker run -d -p 27015:27015 --name mongo_rs2_1 cfg_mongo:v1 --shardsvr --dbpath /data/db --port 27015 --replSet rs2 --bind_ip_all
docker run -d -p 27014:27014 --name mongo_rs2_2 cfg_mongo:v1 --shardsvr --dbpath /data/db --port 27014 --replSet rs2 --bind_ip_all

将这些mongo服务串联起来
初始化分片rs1副本集
docker exec -it mongo_rs1_1 bash
mongo --port 27017
use admin
config = {_id:"rs1",members:[ {_id:0,host:"203.0.113.1:27017"}, {_id:1,host:"203.0.113.1:27016"}] }
rs.initiate(config)
rs.status()
exit
echo 'rs.slaveOK();' > ~/.mongorc.js #设置mongo副本可读

初始化分片rs2副本集
docker exec -it mongo_rs2_1 bash
mongo --port 27015
use admin
config = {_id:"rs2",members:[ {_id:0,host:"203.0.113.1:27015"}, {_id:1,host:"203.0.113.1:27014"}] }
rs.initiate(config)
rs.status()
exit
echo 'rs.slaveOK();' > ~/.mongorc.js #设置mongo副本可读

初始化配置服务副本集
docker exec -it mongo_config_1 bash
mongo --port 27012
use admin
config = {_id:"crs", configsvr:true, members:[ {_id:0,host:"203.0.113.1:27012"}, {_id:1,host:"203.0.113.1:27013"} ] }
rs.initiate(config)
rs.status()
exit
echo 'rs.slaveOK();' > ~/.mongorc.js #设置mongo副本可读

通过mongos添加分片关系到configsvr
docker exec -it mongo_route_1 bash
mongo --port 27011
use admin
db.runCommand({addshard:"rs1/203.0.113.1:27017,203.0.113.1:27016"})
db.runCommand({addshard:"rs2/203.0.113.1:27015,203.0.113.1:27014"})
db.runCommand({listshards:1})
db.runCommand({enablesharding:"louder"})
sh.shardCollection("louder.test",{feedId:"hashed"})
use louder
for (i =0; i<10000;i++){db.test.save({feedId:i})}
db.stats()
查看分片结果

重启全部容器
root@public-zaneperfor-mongo:~# for i in `docker ps | awk '{print $13}'`;do docker restart $i;done
mongo_rs2_2
mongo_rs2_1
mongo_rs1_2
mongo_rs1_1
mongo_route_1
mongo_config_2
mongo_config_1
root@public-zaneperfor-mongo:~# docker ps
CONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMES
d253abd9530d cfg_mongo:v1 "mongod --shardsvr -…" 3 hours ago Up 18 seconds 203.0.113.1:27014->27014/tcp mongo_rs2_2
3ef5d592dd4c cfg_mongo:v1 "mongod --shardsvr -…" 3 hours ago Up 17 seconds 203.0.113.1:27015->27015/tcp mongo_rs2_1
7372725db518 cfg_mongo:v1 "mongod --shardsvr -…" 3 hours ago Up 15 seconds 203.0.113.1:27016->27016/tcp mongo_rs1_2
e2c42f9228fa cfg_mongo:v1 "mongod --shardsvr -…" 3 hours ago Up 14 seconds 203.0.113.1:27017->27017/tcp mongo_rs1_1
ab4324f58605 cfg_route_mongo:v1 "mongos --configdb c…" 3 hours ago Up 9 seconds 203.0.113.1:27011->27011/tcp mongo_route_1
1c2ae0edce72 cfg_mongo:v1 "mongod --configsvr …" 3 hours ago Up 6 seconds 203.0.113.1:27013->27013/tcp mongo_config_2
3f4099094f1d cfg_mongo:v1 "mongod --configsvr …" 3 hours ago Up 3 seconds 203.0.113.1:27012->27012/tcp mongo_config_1
```

**zaneperfor 项目内配置上集群 config.prod.js config.default.js** 展开源码

```
#zaneperfor 项目内配置上集群 config.prod.js config.default.js
 // mongodb 服务
 const dbclients = {
 db3: {
 //单路由方式
 url: 'mongodb://203.0.113.1:27011/performance',
 options: {
 poolSize: 100,
 keepAlive: 10000,
 connectTimeoutMS: 10000,
 autoReconnect: true,
 reconnectTries: 100,
 reconnectInterval: 1000,
 useUnifiedTopology: true,
 },
 },
 };
 if (config.report_data_type === 'mongodb') {
 dbclients.db1 = {
 url: 'mongodb://203.0.113.1:27011/performance',
 options: {
 poolSize: 100,
 keepAlive: 10000,
 connectTimeoutMS: 10000,
 autoReconnect: true,
 reconnectTries: 100,
 reconnectInterval: 1000,
 useUnifiedTopology: true,
 },
 };
 }
 // mongoose配置
 config.mongoose = {
 clients: dbclients,
 };
```
