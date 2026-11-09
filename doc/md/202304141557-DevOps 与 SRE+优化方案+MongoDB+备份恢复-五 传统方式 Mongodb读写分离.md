---
id: "doc-429e9fbeb1d9"
title: "五 传统方式 Mongodb读写分离"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "MongoDB", "备份恢复", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84414106.html"
---

# 五 传统方式 Mongodb读写分离

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BMongoDB%2B%E5%A4%87%E4%BB%BD%E6%81%A2%E5%A4%8D-%E4%BA%94%20%E4%BC%A0%E7%BB%9F%E6%96%B9%E5%BC%8F%20Mongodb%E8%AF%BB%E5%86%99%E5%88%86%E7%A6%BB.md)

目前来看。Mongodb副本集可以完美支持故障转移。至于主节点的读写压力过大如何解决？常见的解决方案是读写分离。

```python
一般情况下，常规写操作来说并没有读操作多，所以在Mongodb副本集中，一台主节点负责写操作，两台副本节点负责读操作。
1）设置读写分离需要先在副本节点SECONDARY 设置 setSlaveOk。
2）在程序中设置副本节点负责读操作，如下代码：<br>
public class TestMongoDBReplSetReadSplit {
public static void main(String[] args) {
try {
List<ServerAddress> addresses = new ArrayList<ServerAddress>();
ServerAddress address1 = new ServerAddress("203.0.113.1" , 27017);
ServerAddress address2 = new ServerAddress("203.0.113.1" , 27017);
ServerAddress address3 = new ServerAddress("203.0.113.1" , 27017);
addresses.add(address1);
addresses.add(address2);
addresses.add(address3);
MongoClient client = new MongoClient(addresses);
DB db = client.getDB( "test" );
DBCollection coll = db.getCollection( "testdb" );
BasicDBObject object = new BasicDBObject();
object.append( "test2" , "testval2" );

//读操作从副本节点读取
ReadPreference preference = ReadPreference. secondary();
DBObject dbObject = coll.findOne(object, null , preference);
System. out .println(dbObject);
} catch (Exception e) {
e.printStackTrace();
}
}
}
```

读参数除了secondary一共还有五个参数：primary、primaryPreferred、secondary、secondaryPreferred、nearest。
**primary**：默认参数，只从主节点上进行读取操作；
**primaryPreferred**：大部分从主节点上读取数据,只有主节点不可用时从secondary节点读取数据。
**secondary**：只从secondary节点上进行读取操作，存在的问题是secondary节点的数据会比primary节点数据“旧”。
**secondaryPreferred**：优先从secondary节点进行读取操作，secondary节点不可用时从主节点读取数据；
**nearest**：不管是主节点、secondary节点，从网络延迟最低的节点上读取数据。

读写分离做好后，就可以进行数据分流，减轻压力，解决了"主节点的读写压力过大如何解决？"这个问题。不过当副本节点增多时，主节点的复制压力会加大有什么办法解决吗？基于这个问题，Mongodb已有了相应的解决方案 - 引用仲裁节点：
在Mongodb副本集中，仲裁节点不存储数据，只是负责故障转移的群体投票，这样就少了数据复制的压力。看起来想的很周到啊，其实不只是主节点、副本节点、仲裁节点，还有Secondary-Only、Hidden、Delayed、Non-Voting，其中：
**Secondary-Only**：不能成为primary节点，只能作为secondary副本节点，防止一些性能不高的节点成为主节点。
**Hidden**：这类节点是不能够被客户端制定IP引用，也不能被设置为主节点，但是可以投票，一般用于备份数据。
**Delayed**：可以指定一个时间延迟从primary节点同步数据。主要用于备份数据，如果实时同步，误删除数据马上同步到从节点，恢复又恢复不了。
**Non-Voting**：没有选举权的secondary节点，纯粹的备份数据节点。
