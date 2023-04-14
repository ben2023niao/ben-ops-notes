---
id: "doc-04819add8f8b"
title: "mongodb备份与恢复"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "MySQL", "MongoDB", "SQL注入", "备份恢复", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84414422.html"
---

# mongodb备份与恢复

## JSON格式工具

 展开源码

```python
A 导出工具mongoexport
Mongodb中的mongoexport工具可以把一个collection导出成JSON格式或CSV格式的文件。
可以通过参数指定导出的数据项，也可以根据指定的条件导出数据。

mongoexport参数说明

$ mongoexport --help
-h:指明数据库宿主机的IP
-u:指明数据库的用户名
-p:指明数据库的密码
-d:指明数据库的名字
-c:指明collection的名字
-f:指明要导出那些列
-o:指明到要导出的文件名
-q:指明导出数据的过滤条件
--authenticationDatabase admin
单表备份至json格式

mongoexport -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d noah -c log \
 -o /tmp/log.json
单表备份至csv格式
如果我们需要导出CSV格式的数据，则需要使用----type=csv参数：需要制定导出的列名

mongoexport -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d noah -c log \
 --type=csv -f uid,name,age,date \
 -o /tmp/log.csv
B 导入工具mongoimport
Mongodb中的mongoimport工具可以把一个特定格式文件中的内容导入到指定的collection中。
该工具可以导入JSON格式数据，也可以导入CSV格式数据。具体使用如下所示：
mongoimport 参数说明

$ mongoimport --help
参数说明：
-h:指明数据库宿主机的IP
-u:指明数据库的用户名
-p:指明数据库的密码
-d:指明数据库的名字
-c:指明collection的名字
-f:指明要导入那些列
-j, --numInsertionWorkers=<number> (defaults to 1) //并行备份
恢复json格式表数据到log1

mongoimport -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d noah \
 -c log1 /tmp/log.json
恢复csv格式的文件到log2
如果要导入CSV格式文件中的内容，则需要通过--type参数指定导入格式，具体如下所示：

#csv格式的文件头行，有列名字
mongoimport -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d noah \
 -c log2 --type=csv --headerline --file /tmp/log.csv
##--headerline:指明第一行是列名，不需要导入。
#csv格式的文件头行，没有列名字
mongoimport -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d oldboy \
 -c log3 --type=csv -f id,name,age,date --file /tmp/log1.csv
C 异构平台迁移案例
mysql -----> mongodb
world数据库下city表进行导出，导入到mongodb

mysql开启安全路径
添加以下配置
vim /etc/my.cnf
secure-file-priv=/tmp
#重启数据库生效
/etc/init.d/mysqld restart
导出mysql的city表数据
source /root/world.sql
select * from world.city into outfile '/tmp/city1.csv' fields terminated by ',';
处理备份文件
desc world.city
 ID | int(11) | NO | PRI | NULL | auto_increment |
| Name | char(35) | NO | | | |
| CountryCode | char(3) | NO | MUL | | |
| District | char(20) | NO | | | |
| Population

#添加第一行列名信息
vim /tmp/city.csv
ID,Name,CountryCode,District,Population
在mongodb中导入备份
mongoimport -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d world \
 -c city --type=csv ID,Name,CountryCode,District,Population --file /tmp/city1.csv

use world
db.city.find({CountryCode:"CHN"});
```

## BSON格式工具

```html
$ mongodump --help
-h:指明数据库宿主机的IP
-u:指明数据库的用户名
-p:指明数据库的密码
-d:指明数据库的名字
-c:指明collection的名字
-o:指明到要导出的文件名
-q:指明导出数据的过滤条件
-j, --numParallelCollections=<number> (defaults to 4) //并行备份

# 1全库备份
mongodump -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -o /tmp/backup

# 2备份world库
mongodump -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d world -o /tmp/backup/

# 3备份noah库下的log集合
mongodump -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d noah -c log -o /tmp/backup/

# 4压缩备份
mongodump -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d noah -o /tmp/backup/ --gzip
mongodump -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d app -c vast -o /tmp/backup/ --gzip

mongorestore恢复工具
# 1恢复world库
mongorestore -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d world1 /tmp/backup/world

# 2恢复oldguo库下的t1集合
mongorestore -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d noah -c log1 --gzip /tmp/backup/noah/log.bson

# 3drop表示恢复的时候把之前的集合drop掉
mongorestore -uroot -proot123 --port 27017 \
 --authenticationDatabase admin -d noah --drop /tmp/backup/noah
```
