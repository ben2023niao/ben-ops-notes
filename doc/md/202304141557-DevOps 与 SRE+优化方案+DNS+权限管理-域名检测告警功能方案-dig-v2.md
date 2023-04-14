---
id: "doc-12abc4dab443"
title: "域名检测告警功能方案-dig-v2"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "DNS", "权限管理", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/66979542.html"
---

# 域名检测告警功能方案-dig-v2

## 轮询指定 DNS 服务器解析域名并更新 hosts 绑定脚本流程：指定 DNS 服务器解析目标域名，将结果储存到临时文件 -> 判断解析是否成功再继续 -> 当解析成功，将最新解析 IP 替换之前 hosts 里绑定的 IP -> 当解析失败，删除临时文件。

```bash
# RHEL & CentOS
yum -y install bind-utils

# Debian & Ubuntu
apt-get -y install dnsutils
```

[www.txt](http://www.txt) 内写域名

脚本代码：

```bash
#!/usr/bin/env bash
```

cat [www.txt](http://www.txt)
for www in `cat www.txt` ; do

for dns_ip in 203.0.113.1 114.114.114 203.0.113.1 ;do

```
if dig @$dns_ip $www +short > /tmp/digout 2>&1
then
    now_ip=$(awk "/\$www/ {print $1}" /etc/hosts)
    new_ip=$(cat /tmp/digout | tail -n1)
    sed -i "s/$now_ip/$new_ip/" /etc/hosts
else
    rm -f /tmp/digout
fi
```

#换好DNS后获取了新DNS 解析ip 然后绑定到本地 curl 测试域名访问
curl $www
#然后判断域名访问情况

done
done

使用方法：

```
# 新建脚本文件
vi /root/dig_hosts.sh

# 赋予运行权限
chmod +x /root/dig_hosts.sh

# 使用 crontab -e 命令添加定时任务。例如设置每天上午 9 点 30 运行 30 9 * * * /root/dig_hosts.sh > /dev/null 2>&1
```

注：在使用脚本前，需要先手动在 hosts 里绑定好域名，不然运行脚本将找不到替换目标。
