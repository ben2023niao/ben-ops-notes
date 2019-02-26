---
id: "doc-6b5e1e806fc2"
title: "四 传统方式 测试副本集故障转移功能"
date: "2019-02-26T08:06:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "MongoDB", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84414093.html"
---

# 四 传统方式 测试副本集故障转移功能

先停掉主节点172.16.60.205，查看mongodb副本集状态，可以看到经过一系列的投票选择操作，172.16.60.206当选主节点，172.16.60.207从172.16.60.206同步数据过来。

```
1）停掉原来的主节点172.16.60.205的mongodb，模拟故障
[root@mongodb-master01 ~]# ps -ef|grep mongodb|grep -v grep|awk '{print $2}'|xargs kill -9
[root@mongodb-master01 ~]# lsof -i:27017
[root@mongodb-master01 ~]#
```

**接着登录到另外两个正常的从节点172.16.60.206、172.16.60.207中的任意一个节点的mongodb，查看副本集状态** 展开源码

```
2）接着登录到另外两个正常的从节点172.16.60.206、172.16.60.207中的任意一个节点的mongodb，查看副本集状态
[root@mongodb-slave01 ~]# /usr/local/mongodb/bin/mongo 203.0.113.1:27017
.................
repset:PRIMARY> rs.status();
{
 "set" : "repset",
 "date" : ISODate("2019-02-26T08:06:02.996Z"),
 "myState" : 1,
 "term" : NumberLong(2),
 "syncingTo" : "",
 "syncSourceHost" : "",
 "syncSourceId" : -1,
 "heartbeatIntervalMillis" : NumberLong(2000),
 "optimes" : {
 "lastCommittedOpTime" : {
 "ts" : Timestamp(1551168359, 1),
 "t" : NumberLong(2)
 },
 "readConcernMajorityOpTime" : {
 "ts" : Timestamp(1551168359, 1),
 "t" : NumberLong(2)
 },
 "appliedOpTime" : {
 "ts" : Timestamp(1551168359, 1),
 "t" : NumberLong(2)
 },
 "durableOpTime" : {
 "ts" : Timestamp(1551168359, 1),
 "t" : NumberLong(2)
 }
 },
 "members" : [
 {
 "_id" : 0,
 "name" : "203.0.113.1:27017",
 "health" : 0,
 "state" : 8,
 "stateStr" : "(not reachable/healthy)",
 "uptime" : 0,
 "optime" : {
 "ts" : Timestamp(0, 0),
 "t" : NumberLong(-1)
 },
 "optimeDurable" : {
 "ts" : Timestamp(0, 0),
 "t" : NumberLong(-1)
 },
 "optimeDate" : ISODate("1970-01-01T00:00:00Z"),
 "optimeDurableDate" : ISODate("1970-01-01T00:00:00Z"),
 "lastHeartbeat" : ISODate("2019-02-26T08:06:02.917Z"),
 "lastHeartbeatRecv" : ISODate("2019-02-26T08:03:37.492Z"),
 "pingMs" : NumberLong(0),
 "lastHeartbeatMessage" : "Connection refused",
 "syncingTo" : "",
 "syncSourceHost" : "",
 "syncSourceId" : -1,
 "infoMessage" : "",
 "configVersion" : -1
 },
 {
 "_id" : 1,
 "name" : "203.0.113.1:27017",
 "health" : 1,
 "state" : 1,
 "stateStr" : "PRIMARY",
 "uptime" : 2246,
 "optime" : {
 "ts" : Timestamp(1551168359, 1),
 "t" : NumberLong(2)
 },
 "optimeDate" : ISODate("2019-02-26T08:05:59Z"),
 "syncingTo" : "",
 "syncSourceHost" : "",
 "syncSourceId" : -1,
 "infoMessage" : "",
 "electionTime" : Timestamp(1551168228, 1),
 "electionDate" : ISODate("2019-02-26T08:03:48Z"),
 "configVersion" : 1,
 "self" : true,
 "lastHeartbeatMessage" : ""
 },
 {
 "_id" : 2,
 "name" : "203.0.113.1:27017",
 "health" : 1,
 "state" : 2,
 "stateStr" : "SECONDARY",
 "uptime" : 2169,
 "optime" : {
 "ts" : Timestamp(1551168359, 1),
 "t" : NumberLong(2)
 },
 "optimeDurable" : {
 "ts" : Timestamp(1551168359, 1),
 "t" : NumberLong(2)
 },
 "optimeDate" : ISODate("2019-02-26T08:05:59Z"),
 "optimeDurableDate" : ISODate("2019-02-26T08:05:59Z"),
 "lastHeartbeat" : ISODate("2019-02-26T08:06:02.861Z"),
 "lastHeartbeatRecv" : ISODate("2019-02-26T08:06:02.991Z"),
 "pingMs" : NumberLong(0),
 "lastHeartbeatMessage" : "",
 "syncingTo" : "203.0.113.1:27017",
 "syncSourceHost" : "203.0.113.1:27017",
 "syncSourceId" : 1,
 "infoMessage" : "",
 "configVersion" : 1
 }
 ],
 "ok" : 1,
 "operationTime" : Timestamp(1551168359, 1),
 "$clusterTime" : {
 "clusterTime" : Timestamp(1551168359, 1),
 "signature" : {
 "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
 "keyId" : NumberLong(0)
 }
 }
}
```

发现当原来的主节点172.16.60.205宕掉后，经过选举，原来的从节点172.16.60.206被推举为新的主节点。

```
3）现在在172.16.60.206新主节点上创建测试数据
repset:PRIMARY> use kevin;
switched to db kevin
repset:PRIMARY> db.kevin.insert({"shibo":"hahaha"})
WriteResult({ "nInserted" : 1 })

4）另一个从节点172.16.60.207上登录mongodb查看
[root@mongodb-slave02 ~]# /usr/local/mongodb/bin/mongo 203.0.113.1:27017
................
repset:SECONDARY> use kevin;
switched to db kevin
repset:SECONDARY> db.getMongo().setSlaveOk();
repset:SECONDARY> show tables;
kevin
repset:SECONDARY> db.kevin.find();
{ "_id" : ObjectId("5c74f42bb0b339ed6eb68e9c"), "shibo" : "hahaha" }

发现从节点172.16.60.207可以同步新的主节点172.16.60.206的数据

5）再重新启动原来的主节点172.16.60.205的mongodb
[root@mongodb-master01 ~]# nohup /usr/local/mongodb/bin/mongod -dbpath /data/mongodb/data/replset -replSet repset --bind_ip=203.0.113.1 --port=27017 &

mongod 9162 root 49u IPv4 6561201 0t0 TCP mongodb-master01:55236->mongodb-slave01:27017 (ESTABLISHED)
[root@mongodb-master01 ~]# ps -ef|grep mongodb
root 9162 6977 4 16:14 pts/1 00:00:01 /usr/local/mongodb/bin/mongod -dbpath /data/mongodb/data/replset -replSet repset --bind_ip=203.0.113.1 --port=27017
root 9244 6977 0 16:14 pts/1 00:00:00 grep mongodb
```

**再次登录到三个节点中的任意一个的mongodb，查看副本集状态** 展开源码

```json
[root@mongodb-master01 ~]# /usr/local/mongodb/bin/mongo 203.0.113.1:27017
....................
repset:SECONDARY> rs.status();
{
 "set" : "repset",
 "date" : ISODate("2019-02-26T08:16:11.741Z"),
 "myState" : 2,
 "term" : NumberLong(2),
 "syncingTo" : "203.0.113.1:27017",
 "syncSourceHost" : "203.0.113.1:27017",
 "syncSourceId" : 1,
 "heartbeatIntervalMillis" : NumberLong(2000),
 "optimes" : {
 "lastCommittedOpTime" : {
 "ts" : Timestamp(1551168969, 1),
 "t" : NumberLong(2)
 },
 "readConcernMajorityOpTime" : {
 "ts" : Timestamp(1551168969, 1),
 "t" : NumberLong(2)
 },
 "appliedOpTime" : {
 "ts" : Timestamp(1551168969, 1),
 "t" : NumberLong(2)
 },
 "durableOpTime" : {
 "ts" : Timestamp(1551168969, 1),
 "t" : NumberLong(2)
 }
 },
 "members" : [
 {
 "_id" : 0,
 "name" : "203.0.113.1:27017",
 "health" : 1,
 "state" : 2,
 "stateStr" : "SECONDARY",
 "uptime" : 129,
 "optime" : {
 "ts" : Timestamp(1551168969, 1),
 "t" : NumberLong(2)
 },
 "optimeDate" : ISODate("2019-02-26T08:16:09Z"),
 "syncingTo" : "203.0.113.1:27017",
 "syncSourceHost" : "203.0.113.1:27017",
 "syncSourceId" : 1,
 "infoMessage" : "",
 "configVersion" : 1,
 "self" : true,
 "lastHeartbeatMessage" : ""
 },
 {
 "_id" : 1,
 "name" : "203.0.113.1:27017",
 "health" : 1,
 "state" : 1,
 "stateStr" : "PRIMARY",
 "uptime" : 127,
 "optime" : {
 "ts" : Timestamp(1551168969, 1),
 "t" : NumberLong(2)
 },
 "optimeDurable" : {
 "ts" : Timestamp(1551168969, 1),
 "t" : NumberLong(2)
 },
 "optimeDate" : ISODate("2019-02-26T08:16:09Z"),
 "optimeDurableDate" : ISODate("2019-02-26T08:16:09Z"),
 "lastHeartbeat" : ISODate("2019-02-26T08:16:10.990Z"),
 "lastHeartbeatRecv" : ISODate("2019-02-26T08:16:11.518Z"),
 "pingMs" : NumberLong(0),
 "lastHeartbeatMessage" : "",
 "syncingTo" : "",
 "syncSourceHost" : "",
 "syncSourceId" : -1,
 "infoMessage" : "",
 "electionTime" : Timestamp(1551168228, 1),
 "electionDate" : ISODate("2019-02-26T08:03:48Z"),
 "configVersion" : 1
 },
 {
 "_id" : 2,
 "name" : "203.0.113.1:27017",
 "health" : 1,
 "state" : 2,
 "stateStr" : "SECONDARY",
 "uptime" : 127,
 "optime" : {
 "ts" : Timestamp(1551168969, 1),
 "t" : NumberLong(2)
 },
 "optimeDurable" : {
 "ts" : Timestamp(1551168969, 1),
 "t" : NumberLong(2)
 },
 "optimeDate" : ISODate("2019-02-26T08:16:09Z"),
 "optimeDurableDate" : ISODate("2019-02-26T08:16:09Z"),
 "lastHeartbeat" : ISODate("2019-02-26T08:16:10.990Z"),
 "lastHeartbeatRecv" : ISODate("2019-02-26T08:16:11.655Z"),
 "pingMs" : NumberLong(0),
 "lastHeartbeatMessage" : "",
 "syncingTo" : "203.0.113.1:27017",
 "syncSourceHost" : "203.0.113.1:27017",
 "syncSourceId" : 1,
 "infoMessage" : "",
 "configVersion" : 1
 }
 ],
 "ok" : 1,
 "operationTime" : Timestamp(1551168969, 1),
 "$clusterTime" : {
 "clusterTime" : Timestamp(1551168969, 1),
 "signature" : {
 "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
 "keyId" : NumberLong(0)
 }
 }
}
```

发现原来的主节点172.16.60.205在故障恢复后，变成了新的主节点172.16.60.206的从节点
