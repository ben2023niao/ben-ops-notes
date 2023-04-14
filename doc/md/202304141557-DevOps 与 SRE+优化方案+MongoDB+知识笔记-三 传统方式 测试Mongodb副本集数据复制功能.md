---
id: "doc-0f5ae3421beb"
title: "三 传统方式 测试Mongodb副本集数据复制功能"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "MongoDB", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84414086.html"
---

# 三 传统方式 测试Mongodb副本集数据复制功能

**<mongodb默认是从主节点读写数据的，副本节点上不允许读，需要设置副本节点可以读>**

```
1）在主节点172.16.60.205上连接到终端
[root@mongodb-master01 ~]# /usr/local/mongodb/bin/mongo 203.0.113.1:27017
................
#建立test 数据库
repset:PRIMARY> use test;
switched to db test
#往testdb表插入测试数据
repset:PRIMARY> db.testdb.insert({"test1":"testval1"})
WriteResult({ "nInserted" : 1 })

2）在副本节点172.16.60.206、172.16.60.207上连接到mongodb查看数据是否复制过来。
这里在172.16.60.206副本节点上进行查看
[root@mongodb-slave01 ~]# /usr/local/mongodb/bin/mongo 203.0.113.1:27017
................
repset:SECONDARY> use test;
switched to db test
repset:SECONDARY> show tables;
2019-02-26T15:37:46.446+0800 E QUERY [thread1] Error: listCollections failed: {
 "operationTime" : Timestamp(1551166663, 1),
 "ok" : 0,
 "errmsg" : "not master and slaveOk=false",
 "code" : 13435,
 "codeName" : "NotMasterNoSlaveOk",
 "$clusterTime" : {
 "clusterTime" : Timestamp(1551166663, 1),
 "signature" : {
 "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
 "keyId" : NumberLong(0)
 }
 }
} :
_getErrorWithCode@src/mongo/shell/utils.js:25:13
DB.prototype._getCollectionInfosCommand@src/mongo/shell/db.js:941:1
DB.prototype.getCollectionInfos@src/mongo/shell/db.js:953:19
DB.prototype.getCollectionNames@src/mongo/shell/db.js:964:16
shellHelper.show@src/mongo/shell/utils.js:853:9
shellHelper@src/mongo/shell/utils.js:750:15
@(shellhelp2):1:1
上面出现了报错！
这是因为mongodb默认是从主节点读写数据的，副本节点上不允许读，需要设置副本节点可以读
repset:SECONDARY> db.getMongo().setSlaveOk();
repset:SECONDARY> db.testdb.find();
{ "_id" : ObjectId("5c74ec9267d8c3d06506449b"), "test1" : "testval1" }
repset:SECONDARY> show tables;
testdb
如上发现已经在副本节点上发现了测试数据，即已经从主节点复制过来了。
（在另一个副本节点172.16.60.207也如上操作即可）
```
