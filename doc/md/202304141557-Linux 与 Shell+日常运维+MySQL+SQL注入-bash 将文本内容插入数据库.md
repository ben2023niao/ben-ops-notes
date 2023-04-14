---
id: "doc-539332ae5e53"
title: "bash 将文本内容插入数据库"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "MySQL", "SQL注入", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/66979850.html"
---

# bash 将文本内容插入数据库

一般来说可以通过 sql 语句执行插入，但如果要插入一个文本特定的内容或者需要过滤等处理的内容就需要通过 shell 来操作了

例如：将 id 大于 1014 的数据插入特定表中

```
1010	jerry	1991-12-13	male
1011	mike	1991-12-13	female
1012	tracy	1991-12-13	male
1013	kobe	1991-12-13	male
1014	allen	1991-12-13	female
1015	curry	1991-12-13	male
1016	tom	1991-12-13	female
```

- while read使用

```
user=root
pwd=[已脱敏]
mysql_connect="mysql -u"$user" -p"$pwd""

cat data.txt | while read id name birth sex
do
 if [ $id -gt 1014 ];then
 # 注意这里面的变量要使用单引号，否则会被解析成id的数值
 $mysql_conn -e "INSERT INTO school.student values('$id','$name','$birth','$sex')"
 fi
done
```

当处理文本分隔符不同的时候

```
2025:hao:1989-12-21:male
2026:zhang:1989-12-21:male
2027:ouyang:1989-12-21:male
2028:li:1989-12-21:female
```

- IFS 为管道符号的时候不能直接使用 mysql_conn 变量，要将 sql 语句直接写在里面

```
user="dbuser"
password="[已脱敏]"
host="203.0.113.1"
mysql_conn="mysql -u'$user' -p'$password' -h'$host'"
IFS="|" # 根据文本变换

cat data-2.txt | while read id name birth sex
do
 mysql -u"$user" -p"$password" -h"$host" -e "INSERT INTO school.student2 values('$id','$name','$birth','$sex')"
done
```
