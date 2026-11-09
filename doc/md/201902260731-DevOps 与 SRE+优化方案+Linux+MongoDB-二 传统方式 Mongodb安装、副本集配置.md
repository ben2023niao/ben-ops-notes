---
id: "doc-e88b92d65afc"
title: "二 传统方式 Mongodb安装、副本集配置"
date: "2019-02-26T07:31:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "MongoDB", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84414082.html"
---

# 二 传统方式 Mongodb安装、副本集配置

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/201902260731-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BLinux%2BMongoDB-%E4%BA%8C%20%E4%BC%A0%E7%BB%9F%E6%96%B9%E5%BC%8F%20Mongodb%E5%AE%89%E8%A3%85%E3%80%81%E5%89%AF%E6%9C%AC%E9%9B%86%E9%85%8D%E7%BD%AE.md)

```
1) 在三个节点机上建立mongodb副本集测试文件夹，用于存放整个副本集文件
[root@mongodb-master01 ~]# mkdir -p /data/mongodb/data/replset/

2）在三个节点机上安装mongodb
下载地址：https://www.mongodb.org/dl/linux/x86_64-rhel62

[root@mongodb-master01 ~]# wget http://downloads.mongodb.org/linux/mongodb-linux-x86_64-rhel62-v3.6-latest.tgz
[root@mongodb-master01 ~]# tar -zvxf mongodb-linux-x86_64-rhel62-v3.6-latest.tgz

3）分别在每个节点机上启动mongodb（启动时指明--bind_ip地址，默认是127.0.0.1，需要改成本机ip，否则远程连接时失败）
[root@mongodb-master01 ~]# mv mongodb-linux-x86_64-rhel62-3.6.11-rc0-2-g2151d1d219 /usr/local/mongodb
[root@mongodb-master01 ~]# nohup /usr/local/mongodb/bin/mongod -dbpath /data/mongodb/data/replset -replSet repset --bind_ip=203.0.113.1 --port=27017 &

[root@mongodb-master01 ~]# ps -ef|grep mongodb
root 7729 6977 1 15:10 pts/1 00:00:01 /usr/local/mongodb/bin/mongod -dbpath /data/mongodb/data/replset -replSet repset
root 7780 6977 0 15:11 pts/1 00:00:00 grep mongodb

[root@mongodb-master01 ~]# lsof -i:27017
COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
mongod 7729 root 10u IPv4 6554476 0t0 TCP localhost:27017 (LISTEN)
```

**4）初始化副本集 登陆mongodb操作记录** 展开源码

```
4）初始化副本集
在三个节点中的任意一个节点机上操作（比如在172.16.60.205节点机）

登陆mongodb
[root@mongodb-master01 ~]# /usr/local/mongodb/bin/mongo 203.0.113.1:27017
.........
#使用admin数据库
> use admin
switched to db admin

#定义副本集配置变量，这里的 _id:”repset” 和上面命令参数“ –replSet repset” 要保持一样。
> config = { _id:"repset", members:[{_id:0,host:"203.0.113.1:27017"},{_id:1,host:"203.0.113.1:27017"},{_id:2,host:"203.0.113.1:27017"}]}
{
 "_id" : "repset",
 "members" : [
 {
 "_id" : 0,
 "host" : "203.0.113.1:27017"
 },
 {
 "_id" : 1,
 "host" : "203.0.113.1:27017"
 },
 {
 "_id" : 2,
 "host" : "203.0.113.1:27017"
 }
 ]
}

#初始化副本集配置
> rs.initiate(config);
{
 "ok" : 1,
 "operationTime" : Timestamp(1551166191, 1),
 "$clusterTime" : {
 "clusterTime" : Timestamp(1551166191, 1),
 "signature" : {
 "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
 "keyId" : NumberLong(0)
 }
 }
}

#查看集群节点的状态
repset:SECONDARY> rs.status();
{
 "set" : "repset",
 "date" : ISODate("2019-02-26T07:31:07.766Z"),
 "myState" : 1,
 "term" : NumberLong(1),
 "syncingTo" : "",
 "syncSourceHost" : "",
 "syncSourceId" : -1,
 "heartbeatIntervalMillis" : NumberLong(2000),
 "optimes" : {
 "lastCommittedOpTime" : {
 "ts" : Timestamp(1551166263, 1),
 "t" : NumberLong(1)
 },
 "readConcernMajorityOpTime" : {
 "ts" : Timestamp(1551166263, 1),
 "t" : NumberLong(1)
 },
 "appliedOpTime" : {
 "ts" : Timestamp(1551166263, 1),
 "t" : NumberLong(1)
 },
 "durableOpTime" : {
 "ts" : Timestamp(1551166263, 1),
 "t" : NumberLong(1)
 }
 },
 "members" : [
 {
 "_id" : 0,
 "name" : "203.0.113.1:27017",
 "health" : 1,
 "state" : 1,
 "stateStr" : "PRIMARY",
 "uptime" : 270,
 "optime" : {
 "ts" : Timestamp(1551166263, 1),
 "t" : NumberLong(1)
 },
 "optimeDate" : ISODate("2019-02-26T07:31:03Z"),
 "syncingTo" : "",
 "syncSourceHost" : "",
 "syncSourceId" : -1,
 "infoMessage" : "could not find member to sync from",
 "electionTime" : Timestamp(1551166202, 1),
 "electionDate" : ISODate("2019-02-26T07:30:02Z"),
 "configVersion" : 1,
 "self" : true,
 "lastHeartbeatMessage" : ""
 },
 {
 "_id" : 1,
 "name" : "203.0.113.1:27017",
 "health" : 1,
 "state" : 2,
 "stateStr" : "SECONDARY",
 "uptime" : 76,
 "optime" : {
 "ts" : Timestamp(1551166263, 1),
 "t" : NumberLong(1)
 },
 "optimeDurable" : {
 "ts" : Timestamp(1551166263, 1),
 "t" : NumberLong(1)
 },
 "optimeDate" : ISODate("2019-02-26T07:31:03Z"),
 "optimeDurableDate" : ISODate("2019-02-26T07:31:03Z"),
 "lastHeartbeat" : ISODate("2019-02-26T07:31:06.590Z"),
 "lastHeartbeatRecv" : ISODate("2019-02-26T07:31:06.852Z"),
 "pingMs" : NumberLong(0),
 "lastHeartbeatMessage" : "",
 "syncingTo" : "203.0.113.1:27017",
 "syncSourceHost" : "203.0.113.1:27017",
 "syncSourceId" : 0,
 "infoMessage" : "",
 "configVersion" : 1
 },
 {
 "_id" : 2,
 "name" : "203.0.113.1:27017",
 "health" : 1,
 "state" : 2,
 "stateStr" : "SECONDARY",
 "uptime" : 76,
 "optime" : {
 "ts" : Timestamp(1551166263, 1),
 "t" : NumberLong(1)
 },
 "optimeDurable" : {
 "ts" : Timestamp(1551166263, 1),
 "t" : NumberLong(1)
 },
 "optimeDate" : ISODate("2019-02-26T07:31:03Z"),
 "optimeDurableDate" : ISODate("2019-02-26T07:31:03Z"),
 "lastHeartbeat" : ISODate("2019-02-26T07:31:06.589Z"),
 "lastHeartbeatRecv" : ISODate("2019-02-26T07:31:06.958Z"),
 "pingMs" : NumberLong(0),
 "lastHeartbeatMessage" : "",
 "syncingTo" : "203.0.113.1:27017",
 "syncSourceHost" : "203.0.113.1:27017",
 "syncSourceId" : 0,
 "infoMessage" : "",
 "configVersion" : 1
 }
 ],
 "ok" : 1,
 "operationTime" : Timestamp(1551166263, 1),
 "$clusterTime" : {
 "clusterTime" : Timestamp(1551166263, 1),
 "signature" : {
 "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
 "keyId" : NumberLong(0)
 }
 }
}
```

如上信息表明：
副本集配置成功后，172.16.60.205为主节点PRIMARY，203.0.113.1/207为副本节点SECONDARY。
health：1 1表明状态是正常，0表明异常
state:1 值小的是primary节点、值大的是secondary节点
