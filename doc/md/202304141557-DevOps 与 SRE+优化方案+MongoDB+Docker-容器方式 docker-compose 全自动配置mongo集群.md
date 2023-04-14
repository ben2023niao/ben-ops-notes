---
id: "doc-7864c22f8647"
title: "容器方式 docker-compose 全自动配置mongo集群"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "MongoDB", "Docker", "日志分析", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84414117.html"
---

# 容器方式 docker-compose 全自动配置mongo集群

## 1. 创建工作目录

```
#ip地址 主机名 角色
#203.0.113.1 mongodb-master01 副本集主节点
#203.0.113.1 mongodb-slave01 副本集副本节点
#203.0.113.1 mongodb-slave02 副本集副本节点
mkdir -p /server/docker-compose/mongo-replica/{scripts,data} ; cd /server/docker-compose/mongo-replica
cat >> /etc/hosts << EOF
203.0.113.1 mongodb-master01
203.0.113.1 mongodb-slave01
203.0.113.1 mongodb-slave02
EOF
```

### 2. 生成 docker-compose.yml 文件

 展开源码

```bash
cat > docker-compose.yml <<EOF
version: '3'
services:
  mongo2:
    container_name: "mongo2"
    image: mongo:4.1.7
    ports:
      - "30012:27017"
    command: mongod --replSet vision-set  --bind_ip 203.0.113.1
    restart: always
  mongo3:
    container_name: "mongo3"
    image: mongo:4.1.7
    ports:
      - "30013:27017"
    command: mongod --replSet vision-set  --bind_ip 203.0.113.1
    restart: always
  mongo1:
    container_name: "mongo1"
    image: mongo:4.1.7
    ports:
      - "30011:27017"
    command: mongod --replSet vision-set --bind_ip 203.0.113.1
    links:
      - mongo2:mongo2
      - mongo3:mongo3
    restart: always
  mongo-vision-set-setup:
    container_name: "mongo-vision-set-setup"
    image: mongo:4.1.7
    depends_on:
      - "mongo1"
      - "mongo2"
      - "mongo3"
    links:
      - mongo1:mongo1
      - mongo2:mongo2
      - mongo3:mongo3
    volumes:
        - ./scripts:/scripts
    environment:
      - MONGO1=mongo1
      - MONGO2=mongo2
      - MONGO3=mongo3
      - RS=vision-set
    entrypoint: [ "/scripts/setup.sh" ]
EOF
docker-compose config # 检查配置
docker-compose up -d # 启动
docker-compose logs -f # 查看日志
```

### 3. 生成 setup.sh 自动配置脚本

 展开源码

```bash
cat > scripts/setup.sh <<EOF
#!/bin/bash
MONGO1=mongodb-master01 ; mongodb1=`cat /etc/hosts | grep ${MONGO1} | awk '{ print $1 }'`
MONGO2=mongodb-slave01  ; mongodb1=`cat /etc/hosts | grep ${MONGO2} | awk '{ print $1 }'`
MONGO3=mongodb-slave02  ; mongodb1=`cat /etc/hosts | grep ${MONGO3} | awk '{ print $1 }'`
port=${PORT:-27017}
until mongo --host ${mongodb1}:${port} --eval 'quit(db.runCommand({ ping: 1 }).ok ? 0 : 2)' &>/dev/null; do
  printf '.'
  sleep 1
done
echo "Started.."
echo setup.sh time now: `date +"%T" `
mongo --host ${mongodb1}:${port} <<EOF
 var cfg = {
 "_id": "${RS}",
 "protocolVersion": 1,
 "members": [
 {
 "_id": 0,
 "host": "${mongodb1}:${port}"
 },
 {
 "_id": 1,
 "host": "${mongodb2}:${port}"
 },
 {
 "_id": 2,
 "host": "${mongodb3}:${port}"
 }
 ]
 };
 rs.initiate(cfg, { force: true });
 rs.reconfig(cfg, { force: true });
EOF
```

### 4. 检查 mongo replica 配置是否成功

```bash
# 进入 mongo1 如果提示符变为 primary，则初始化基本成功
docker exec -it mongo1 mongo
vision-set:PRIMARY>
# 先在 primary 数据库中插入数据：
vision-set:PRIMARY> db.mycollection.insert({name : 'sample'})
WriteResult({ "nInserted" : 1 })
vision-set:PRIMARY> db.mycollection.find()
{ "_id" : ObjectId("57761827767433de37ff95ee"), "name" : "sample" }
# 然后新建一个与 secondary 数据库的连接，并测试文档是否在那里复制：
vision-set:PRIMARY> db2 = (new Mongo('mongo2:27017')).getDB('test')
test
vision-set:PRIMARY> db2.setSlaveOk()
vision-set:PRIMARY> db2.mycollection.find())
{ "_id" : ObjectId("57761827767433de37ff95ee"), "name" : "sample" }
#执行 db2.setSlaveOk() 命令来让 shell 知道我们故意在查询非 primary 的数据库。
```

## 补充：mongodb mongod 启动参数参考

 展开源码

```
我们可以通过 mongod –help 查看 mongod 的所有参数说明，以下是各参数的中文解释。
基本配置
–quiet # 安静输出
–port arg # 指定服务端口号，默认端口27017
–bind_ip arg # 绑定服务IP，若绑定127.0.0.1，则只能本机访问，不指定默认本地所有IP
–logpath arg # 指定MongoDB日志文件，注意是指定文件不是目录
–logappend # 使用追加的方式写日志
–pidfilepath arg # PID File 的完整路径，如果没有设置，则没有PID文件
–keyFile arg # 集群的私钥的完整路径，只对于Replica Set 架构有效
–unixSocketPrefix arg # UNIX域套接字替代目录,(默认为 /tmp)
–fork # 以守护进程的方式运行MongoDB，创建服务器进程
–auth # 启用验证
–cpu # 定期显示CPU的CPU利用率和iowait
–dbpath arg # 指定数据库路径
–diaglog arg # diaglog选项 0=off 1=W 2=R 3=both 7=W+some reads
–directoryperdb # 设置每个数据库将被保存在一个单独的目录
–journal # 启用日志选项，MongoDB的数据操作将会写入到journal文件夹的文件里
–journalOptions arg # 启用日志诊断选项
–ipv6 # 启用IPv6选项
–jsonp # 允许JSONP形式通过HTTP访问（有安全影响）
–maxConns arg # 最大同时连接数 默认2000
–noauth # 不启用验证
–nohttpinterface # 关闭http接口，默认关闭27018端口访问
–noprealloc # 禁用数据文件预分配(往往影响性能)
–noscripting # 禁用脚本引擎
–notablescan # 不允许表扫描
–nounixsocket # 禁用Unix套接字监听
–nssize arg (=16) # 设置信数据库.ns文件大小(MB)
–objcheck # 在收到客户数据,检查的有效性，
–profile arg # 档案参数 0=off 1=slow, 2=all
–quota # 限制每个数据库的文件数，设置默认为8
–quotaFiles arg # number of files allower per db, requires –quota
–rest # 开启简单的rest API
–repair # 修复所有数据库run repair on all dbs
–repairpath arg # 修复库生成的文件的目录,默认为目录名称dbpath
–slowms arg (=100) # value of slow for profile and console log
–smallfiles # 使用较小的默认文件
–syncdelay arg (=60) # 数据写入磁盘的时间秒数(0=never,不推荐)
–sysinfo # 打印一些诊断系统信息
–upgrade # 如果需要升级数据库

Replicaton 参数
–fastsync # 从一个dbpath里启用从库复制服务，该dbpath的数据库是主库的快照，可用于快速启用同步
–autoresync # 如果从库与主库同步数据差得多，自动重新同步，
–oplogSize arg # 设置oplog的大小(MB)

主/从参数
–master # 主库模式
–slave # 从库模式
–source arg # 从库 端口号
–only arg # 指定单一的数据库复制
–slavedelay arg # 设置从库同步主库的延迟时间

Replica set(副本集)选项
–replSet arg # 设置副本集名称

Sharding(分片)选项
–configsvr # 声明这是一个集群的config服务,默认端口27019，默认目录/data/configdb
–shardsvr # 声明这是一个集群的分片,默认端口27018
–noMoveParanoia # 关闭偏执为moveChunk数据保存?
```

## 案列

```
示例：
./mongod -shardsvr -replSet shard1 -port 16161 -dbpath /data/mongodb/data/shard1a -oplogSize 100 -logpath /data/mongodb/logs/shard1a.log -logappend -fork -rest
# 上述参数都可以写入 mongod.conf 配置文档里例如：
dbpath = /data/mongodb
logpath = /data/mongodb/mongodb.log
logappend = true
port = 27017
fork = true
auth = true
```
