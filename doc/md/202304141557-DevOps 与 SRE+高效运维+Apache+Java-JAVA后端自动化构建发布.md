---
id: "doc-39ae718b0833"
title: "JAVA后端自动化构建发布"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "Apache", "Java", "备份恢复", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68649782.html"
---

# JAVA后端自动化构建发布

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2BApache%2BJava-JAVA%E5%90%8E%E7%AB%AF%E8%87%AA%E5%8A%A8%E5%8C%96%E6%9E%84%E5%BB%BA%E5%8F%91%E5%B8%83.md)

```bash
#!/bin/bash
# 自动化发布脚本
##### 备份 开始 #####
echo "–备份开始–";
datename=$(date +%Y%m%d-%H%M%S);
mkdir -m 700 /usr/local/war/$datename;
cp -a -R /usr/local/apache-tomcat-9.0.17/webapps/FireFighting.war /usr/local/war/$datename;
echo "–备份成功–"##### 停止服务 #####
echo "–开始停止服务–";
ps -ef|grep 'apache-tomcat-9.0.17'|grep -v grep|awk '{print $2}'|xargs kill -9;
echo "–停止服务成功—";##### 删除原始文件 #####
echo "–删除原war包–";
rm -rf /usr/local/apache-tomcat-9.0.17/webapps/FireFighting*;
echo "–删除原war包成功–";##### 复制新war包 #####
echo "–开始复制新war包–";
cp -a -R /usr/local/warNew/FireFighting.war /usr/local/apache-tomcat-9.0.17/webapps/;
echo "-复制新war包成功-";##### 启动服务 #####
echo "–启动服务–";
echo "–启动server服务–";
sh /usr/local/apache-tomcat-9.0.17/bin/startup.sh;
echo "–启动server服务成功–";
##### 成功结束 #####
```
