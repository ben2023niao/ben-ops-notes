---
id: "doc-edd44167db27"
title: "域名检测告警功能方案-dig"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "DNS", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/66979515.html"
---

# 域名检测告警功能方案-dig

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BLinux%2BDNS-%E5%9F%9F%E5%90%8D%E6%A3%80%E6%B5%8B%E5%91%8A%E8%AD%A6%E5%8A%9F%E8%83%BD%E6%96%B9%E6%A1%88-dig.md)

```
使用 dig 命令可以很方便地解析域名
所以实现一个收集不同DNS服务器内实时更新的业务域名解析记录功能
因此写了一个定时解析的 Shell 脚本，配合 Linux 的计划任务去定时解析。

rpm -qa bind-utils 要使用 dig 命令，需要确认提供该命令的软件包是否安装。如果没有安装则使用 yum 安装即可。

加入计划任务
[root@ben]# tail -1 /etc/crontab
*/5 * * * * root /root/dig_dns_8.8.8.8.sh /root/nordstrom.list &>/dev/null
*/10 * * * * root /root/dig_dns_114.114.114.114.sh /root/nordstrom.list &>/dev/null
*/5 * * * * root /root/dig_dns_223.5.5.5.sh /root/nordstrom.list &>/dev/null

效果
[root@m1 ~]# cat nordstrom.list
www.nordstrom.com
m.shop.nordstrom.com
n.nordstrommedia.com
nordstrom.com
predictivesearch.nordstrom.com
recs.p13n.nordstrom.com
secure.nordstrom.com
secure.nordstromimage.com
shop.nordstrom.com
sid.nordstrom.com
tag.aws.nordstromdata.com
www.nordstromrack.com
www.hautelookcdn.com
[root@m1 ~]# chmod +x dig_dns_8.8.8.8.sh
[root@m1 ~]# ./dig_dns_8.8.8.8.sh nordstrom.list
[root@m1 ~]# ls
dig_dns_8.8.8.8.sh dig_dns_114.114.114.114.sh dig_dns_223.5.5.5.sh crondig.sh nordstrom.list nordstrom.res
[root@m1 ~]# cat nordstrom.res
203.0.113.1
203.0.113.1
203.0.113.1
203.0.113.1
203.0.113.1
203.0.113.1
203.0.113.1
203.0.113.1
203.0.113.1
203.0.113.1

dig_dns_8.8.8.8.sh 脚本
#!/bin/bashDNS_IP="203.0.113.1"
# 要请求哪个DNS服务器进行域名解析serverListfile=$1
# dig 命令有一个参数 -f 指定文件，这里定义传给 dig 的文件answerFile=""
# Answer_file="/tmp/baidu.res"
# 定义域名解析结果的输出文件路径
# 如果不指定，默认会输出到 /tmp/ 下的一个和脚本名一样且后缀为 .res 的文件IP_filter(){
/bin/egrep '^(\b([1-9][0-9]?|1[0-9]{2}|2[0-4][0-9]|25[0-5]))(\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\b){3}'
}
# 定义一个过滤IP的函数#------------------------------------------------scriptName=`/bin/basename $0`if /usr/bin/expr "${scriptName}" : ".*\.sh$" >/dev/null ;then
if [[ ! -f $1 ]]; then
echo -e "\n\tUsage : $(basename $0) filename\n"
echo -e "\n\t必须指定一个域名列表文件\n"
exit 3
fi
outFilename=$(basename ${serverListfile})
answerFile="/tmp/$(echo ${outFilename} | cut -d "." -f 1).res"
else
echo -e "\n\t脚本必须以 '.sh' 结尾 \n"
exit 3
fi/bin/gawk '!a[$0]++' < <(IP_filter < <(/usr/bin/dig @${DNS_IP} -f ${serverListfile} +short) ) | \
/bin/sort -t "." -k 1.1,1n -k 2,2.0n -k 3.1,3.0n -k 4,4n >> ${answerFile}
/bin/gawk '!a[$0]++' ${answerFile} | /bin/sort -t "." -k 1.1,1n -k 2,2.0n -k 3.1,3.0n -k 4,4n -o ${answerFile}
```
