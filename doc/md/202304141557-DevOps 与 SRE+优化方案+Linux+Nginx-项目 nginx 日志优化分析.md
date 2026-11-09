---
id: "doc-7c39eeba9a04"
title: "项目 nginx 日志优化分析"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "Nginx", "恶意代码", "日志分析", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/72057043.html"
---

# 项目 nginx 日志优化分析

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BLinux%2BNginx-%E9%A1%B9%E7%9B%AE%20nginx%20%E6%97%A5%E5%BF%97%E4%BC%98%E5%8C%96%E5%88%86%E6%9E%90.md)

```
[root@hk210svr008026 logs]# tail -1 A04_agent_three_mobile.log | awk -F'の' '{print "+客户ip->CDN->源服务器->内网ip= "$3" -> "$29" -> "$4" +用户访问= " $8" 请求 "$5$6" +状态= "$9" +服务器返回= "$11$23" +返回内容格式= "$26" +耗时秒= "$12" +产品信息= "$41" +客户端UA=  "$10}' | awk -F "+" '{for(i=1;i<=NF;i++) a[i,NR]=$i}END{for(i=1;i<=NF;i++) {for(j=1;j<=NR;j++) printf a[i,j] " ";print ""}}'

客户ip->CDN->源服务器->内网ip= 203.0.113.1, 203.0.113.1 -> hk210svr008026 -> 203.0.113.1
用户访问= POST 请求 d88web.com/_glaxy_a04_/agent/proxy
状态= 200
服务器返回= https://d88web.com//web/A04/agent_three_web/WebRoot/_glaxy_a04_/agent/proxy
返回内容格式= application/json
耗时秒= 0.261
产品信息= -{\x22productId\x22:\x22A04\x22,\x22deviceId\x22:\x22efdf9b490ca24c8c9cf54e26ff27928b\x22,\x22uri\x22:\x22/customer/findCustomersByLoginNames.do\x22,\x22para\x22:\x22msss020117\x22,\x22userId\x22:1011361484,\x22requestSource\x22:\x222\x22,\x22userName\x22:\x22msss020117\x22,\x22loginName\x22:\x22msss020117\x22,\x22language\x22:\x22zh\x22}
客户端UA= Mozilla/5.0 (Linux; U; Android 12; zh-cn; M2102J2SC Build/SKQ1.211006.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.116 Mobile Safari/537.36 XiaoMi/MiuiBrowser/16.8.58 swan-mibrowser
```

```bash
#!/bin/bash
sleep_time=3
now=`date +"%Y:%H:%M"`
dir='/usr/local/nginx/logs/'

mkdir -p $dir && cd $dir
#1分钟内变动文件
change_logs=`find $dir -mmin -1`
#安全检查 防止日志被木马感染改动后缀
for check_log in $change_logs;do
 echo "$check_log" | grep -v '.log' && echo "1分钟内变动文件 $check_log 不是日志文件请注意!!!"
 echo "$check_log" | grep -E "error|ERROR|err|ERR" && echo "1分钟内变动文件 $check_log 是错误日志请注意!!!"
done
logs=`ls $dir | grep ".log" | grep -v '.gz' | grep -v '.backup' | grep -v '.txt' | grep -v '.sh'`
echo > befor.txt
echo > now.txt

for befor in $logs ;do wc -l $befor >> befor.txt ;done
sleep $sleep_time
for now in $logs ;do wc -l $now >> now.txt ;done

diff befor.txt now.txt | grep '< ' | awk '{print $3}' > diffent_log.txt
diff befor.txt now.txt | grep '< ' | awk '{print "befor_"$2"_"$3}' > diffent_log_befor.txt
diff befor.txt now.txt | grep '> ' | awk '{print "now_"$2"_"$3}' > diffent_log_now.txt

for log_txt in `cat diffent_log.txt`;do
 grep $log_txt diffent_log_befor.txt | awk -F'_' '{print $2}' > befor_nu.txt
 grep $log_txt diffent_log_now.txt | awk -F'_' '{print $2}' > now_nu.txt
 sed -n "`cat befor_nu.txt`,`cat now_nu.txt`p" $log_txt > $log_txt.txt
done
for log in `cat diffent_log.txt`;do
 cat $log | while read line;do
 echo"File:${line}" | awk -F'の' '{print $9}' > status_code.txt
 if [[ "`cat status_code.txt`" != "200" ]];then
 echo "状态码非 200 File:${line}"
 echo "File:${line}" | awk -F'の' '{print "+客户ip->CDN->源服务器->内网ip= "$3" -> "$29" -> "$4" +用户访问= " $8" 请求 "$5$6" +状态= "$9" +服务器返回= "$11$23" +返回内容格式= "$26" +耗时秒= "$12" +产品信息= "$41" +客户端UA=  "$10}' | awk -F "+" '{for(i=1;i<=NF;i++) a[i,NR]=$i}END{for(i=1;i<=NF;i++) {for(j=1;j<=NR;j++) printf a[i,j] " ";print ""}}'
 fi
```
