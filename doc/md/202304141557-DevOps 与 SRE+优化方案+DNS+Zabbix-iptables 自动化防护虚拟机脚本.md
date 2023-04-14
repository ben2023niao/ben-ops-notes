---
id: "doc-1befac248f30"
title: "iptables 自动化防护虚拟机脚本"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "DNS", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/72069646.html"
---

# iptables 自动化防护虚拟机脚本

**iptables.sh** 展开源码

```bash
#!/bin/bash
IPT="/sbin/iptables"
iptables_init(){
echo '#iptables 初始化配置'
echo '#删除已有规则'
echo "$IPT --delete-chain"
echo "$IPT --flush"

echo '#不允许进和转发，只允许出/回环网卡。最安全的'
echo "$IPT -P INPUT DROP"
echo "$IPT -P FORWARD DROP"
echo "$IPT -P OUTPUT ACCEPT"
echo "$IPT -A INPUT -i lo -j ACCEPT"

echo '#允许所有人ping'
echo "$IPT -A INPUT -p icmp -m icmp --icmp-type any -j ACCEPT"

echo '#允许关联的状态包已建立的或相关连接的通行'
echo "$IPT -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT"
echo "$IPT -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT"
echo '#想要进入的封包是否为刚刚我发出去的回应?如果是刚刚我发出去的回应,那麼就可以予以接受放行.'
echo '#ESTABLISHED：已建立的链接状态. RELATED：该封包为本机发出的封包有关.'
}
iptables_ssh(){
echo '#获取SSH端口'
if grep "^Port" /etc/ssh/sshd_config>/dev/null;then
sshdport=`grep "^Port" /etc/ssh/sshd_config | sed "s/Port\s//g" `
else
sshdport=22
echo '#允许SSH端口的连接,脚本自动侦测目前的SSH端口,否则默认为22端口'
fi
echo '#获取SSH端口 $sshdport'

#INPUT
echo "$IPT -A INPUT -p tcp -m tcp --dport $sshdport -j ACCEPT"
echo '# 限制 ssh 端口单个IP的最大连接数为 3'
echo "$IPT -I INPUT -p tcp --dport $sshdport -m connlimit --connlimit-above 3 -j DROP"

#OUTPUT
}
iptables_dns_udp_53(){
if [ -s /etc/resolv.conf ];then
nameserver1=`cat /etc/resolv.conf |grep nameserver |awk 'NR==1{print $2 }'`
nameserver2=`cat /etc/resolv.conf |grep nameserver |awk 'NR==2{print $2 }'`
fi
echo '#允许DNS'
echo '#获取DNS-1服务器 $nameserver1'
local comment='dns-name-server-1'
[ ! -z "$nameserver1" ] && echo "$IPT -A OUTPUT -p udp -m udp -d $nameserver1 --dport 53 -m comment --comment $comment -j ACCEPT"
echo '#获取DNS-2服务器 $nameserver2'
local comment='dns-name-server-2'
[ ! -z "$nameserver2" ] && echo "$IPT -A OUTPUT -p udp -m udp -d $nameserver2 --dport 53 -m comment --comment $comment -j ACCEPT"
}
tcp_10050(){
echo "#tcp_10050"
#INPUT
local comment='zabbix-agent'
local state='ZABBIX'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport 10050 -m comment --comment $comment -j $state"
#OUTPUT
}
tcp_10051(){
echo "#tcp_10051"
#INPUT

#OUTPUT
cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='zabbix-proxy'
echo "$IPT -A OUTPUT -d $tcp -p tcp -m tcp --dport 10051 -m comment --comment $comment -j ACCEPT"
done
}
tcp_2631(){
echo "#tcp_2631"
#INPUT
local comment='sshd-service'
local state='SSHD'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport $sshdport -m comment --comment $comment -j $state"

local comment='netscaler'
local state='NETSCALER'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport $sshdport -m comment --comment $comment -j $state"

#OUTPUT
cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='ssh'

if [ "$tcp" = '203.0.113.1/32' ];then local comment='squid-proxy';fi

if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='rsync' ;fi

echo "$IPT -A OUTPUT -d $tcp -p tcp -m tcp --dport $sshdport -m comment --comment $comment -j ACCEPT"
done
}
tcp_3128(){
echo "#tcp_3128"
#INPUT
local comment='squid'
local state='SQUID'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport 3128 -m comment --comment $comment -j $state"

#OUTPUT
echo "$IPT -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 3128 -m comment --comment $comment -j ACCEPT"
}
tcp_443(){
echo "#tcp_443"
#INPUT

#OUTPUT
cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='wms'
if [ "$tcp" = '203.0.113.1/32' ];then local comment='BS_OPTP' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='BS_git' ;fi
echo "$IPT -A OUTPUT -d $tcp -p tcp -m tcp --dport 443 -m comment --comment $comment -j ACCEPT"
done
}
tcp_4315(){
echo "#tcp_4315"
#INPUT

#OUTPUT
cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='WMS-DB'
echo "$IPT -A OUTPUT -d $tcp -p tcp -m tcp --dport 4315 -m comment --comment $comment -j ACCEPT"
done
}
tcp_4316(){
echo "#tcp_4316"
#INPUT

#OUTPUT
local comment='INTER-WMS-DB'
echo "$IPT -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 4316 -m comment --comment $comment -j ACCEPT"
}
tcp_4505(){
echo "#tcp_4505"
#INPUT

#OUTPUT
local comment='salt-mom'
echo "$IPT -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 4505:4506 -m comment --comment $comment -j ACCEPT"
}
tcp_4506(){
echo "#tcp_4506"
#INPUT

#OUTPUT
local comment='salt-mom'
echo "$IPT -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 4505:4506 -m comment --comment $comment -j ACCEPT"
}
tcp_5044(){
echo "#tcp_5044"
#INPUT

#OUTPUT
cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='RSYNC'
if [ "$tcp" = '203.0.113.1/32' ];then local comment='logship' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='logship' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='logship' ;fi
echo "$IPT -A OUTPUT -d $tcp -p tcp -m tcp --dport 5044 -m comment --comment $comment -j ACCEPT"
done
}
tcp_80(){
echo "#tcp_80"
#INPUT
local comment='netscaler'
local state='NETSCALER'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -m comment --comment 'netscaler' -j $state"

#OUTPUT

cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='CMDB'
if [ "$tcp" = '203.0.113.1/32' ];then local comment='yum-repo' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='wms' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='wms' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='gcp-proxy' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='SSHD' ;fi
echo "$IPT -A OUTPUT -d $tcp -p tcp -m tcp --dport 80 -m comment --comment $comment -j ACCEPT"
done
}
tcp_8080(){
echo "#tcp_8080"
#INPUT
local comment='netscaler'
local state='NETSCALER'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport 8080 -m comment --comment $comment -j $state"
#OUTPUT
local comment='CMDB'
echo "$IPT -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 8080 -m comment --comment $comment -j ACCEPT"
}
tcp_8086(){
echo "#tcp_8086"
#INPUT

#OUTPUT
local comment='telegraf-influxdb'
echo "$IPT -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 8086 -m comment --comment $comment -j ACCEPT"
}
tcp_87(){
echo "#tcp_87"
#INPUT
local comment='netscaler'
local state='NETSCALER'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport 87 -m comment --comment $comment -j $state"
#OUTPUT
}
tcp_873(){
echo "#tcp_873"
#INPUT
local comment='rsync'
local state='RSYNC'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport 873 -m comment --comment $comment -j $state"

#OUTPUT
cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='RSYNC'
if [ "$tcp" = '203.0.113.1/32' ];then local comment='SSHD' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='SSHD' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='DT-SSHD' ;fi
echo "$IPT -A OUTPUT -d $tcp -p tcp -m tcp --dport 873 -m comment --comment $comment -j ACCEPT"
done
}
tcp_8888(){
echo "#tcp_8888"
#INPUT
local comment='netscaler'
local state='NETSCALER'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport 8888 -m comment --comment $comment -j $state"
#OUTPUT
}
tcp_999(){
echo "#tcp_999"
#INPUT
local comment='netscaler'
local state='NETSCALER'
echo "$IPT -A INPUT -p tcp -m state --state NEW -m tcp --dport 9999 -m comment --comment $comment -j $state"
#OUTPUT
}
tcp_NETSCALER(){
echo "#tcp_NETSCALER"
#INPUT
local comment='netscaler'
local state='NETSCALER'
cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
203.0.113.1/24
203.0.113.1/24
203.0.113.1/24
203.0.113.1/24
203.0.113.1/24
203.0.113.1/32
203.0.113.1/24
203.0.113.1/24
203.0.113.1/24
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='NETSCALER'
if [ "$tcp" = '203.0.113.1/32' ];then local comment='public_software_management' ;fi
echo "$IPT -A $state -s $tcp -m comment --comment $comment -j ACCEPT"
done
}
tcp_RSYNC(){
echo "#tcp_RSYNC"
#INPUT
local comment='rsync'
local state='RSYNC'
echo "$IPT -A $state -s 203.0.113.1/32 -m comment --comment $comment -j ACCEPT"
echo "$IPT -A $state -s 203.0.113.1/32 -m comment --comment $comment -j ACCEPT"
}
tcp_SQUID(){
echo "#tcp_SQUID"
#INPUT
local state='SQUID'
local comment='squid-proxy'
echo "$IPT -A $state -s 203.0.113.1/32 -m comment --comment $comment -j ACCEPT"
echo "$IPT -A $state -j RETURN"
}
tcp_SSHD(){
echo "#tcp_SSHD"
#INPUT
local comment='sshd-service'
local state='SSHD'
cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='jenkins'
if [ "$tcp" = '203.0.113.1/32' ];then local comment='RSYNC' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='SHTerm' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='SHTerm' ;fi
echo "$IPT -A $state -s $tcp -m comment --comment $comment -j ACCEPT"
done
echo "$IPT -A $state -j RETURN"
}
tcp_ZABBIX(){
echo "#tcp_ZABBIX"
#INPUT
local state='ZABBIX'
local comment='PH190-zabbix-proxy'
echo "$IPT -A $state -s 203.0.113.1/32 -m comment --comment $comment -j ACCEPT"
echo "$IPT -A $state -j RETURN"
}
#备份之前 iptables
mkdir back
iptables-save > back/iptables_back_$(date +%Y:%m:%d-%H:%M:%S).txt
#生成当前 iptables
echo > iptables_new.sh
iptables_init >> iptables_new.sh
iptables_ssh >> iptables_new.sh
iptables_dns_udp_53 >> iptables_new.sh
tcp_10050 >> iptables_new.sh
tcp_10051 >> iptables_new.sh
tcp_2631 >> iptables_new.sh
tcp_3128 >> iptables_new.sh
tcp_443 >> iptables_new.sh
tcp_4315 >> iptables_new.sh
tcp_4316 >> iptables_new.sh
tcp_4505 >> iptables_new.sh
tcp_4506 >> iptables_new.sh
tcp_5044 >> iptables_new.sh
tcp_80 >> iptables_new.sh
tcp_8080 >> iptables_new.sh
tcp_8086 >> iptables_new.sh
tcp_87 >> iptables_new.sh
tcp_873 >> iptables_new.sh
tcp_8888 >> iptables_new.sh
tcp_999 >> iptables_new.sh
tcp_NETSCALER >> iptables_new.sh
tcp_RSYNC >> iptables_new.sh
tcp_SQUID >> iptables_new.sh
tcp_SSHD >> iptables_new.sh
tcp_ZABBIX >> iptables_new.sh
# 保存规则并重启IPTABLES
#bash iptables_new.sh && iptables save && service iptables restart
#清理临时文件
rm -f tcp.txt
```

**使用案例 新IP 203.0.113.1 添加TCP 443端口OUTPUT规则**

```
tcp_443(){  #找到 iptables.sh 的对应函数端口
echo "#tcp_443"
#INPUT
#OUTPUT 添加 443 端口OUTPUT 规则的新IP 203.0.113.1
cat > tcp.txt << EOF
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
203.0.113.1/32
EOF
for tcp in `cat tcp.txt`
do
local comment='wms'
if [ "$tcp" = '203.0.113.1/32' ];then local comment='new-443-output';fi #添加 新IP 203.0.113.1 备注
if [ "$tcp" = '203.0.113.1/32' ];then local comment='BS_OPTP' ;fi
if [ "$tcp" = '203.0.113.1/32' ];then local comment='BS_git' ;fi
echo "$IPT -A OUTPUT -d $tcp -p tcp -m tcp --dport 443 -m comment --comment $comment -j ACCEPT"
done
}
```

**运行脚本生成 iptalbes 规则**

```
[root@ph190svr002184 iptables]# ls
iptables.sh
[root@ph190svr002184 iptables]# bash iptables.sh
[root@ph190svr002184 iptables]# ls
back iptables_new.sh iptables.sh
[root@ph190svr002184 iptables]# tree .
.
├── back
│   └── iptables_back_2022:11:15-10:44:23.txt
├── iptables_new.sh
└── iptables.sh

1 directory, 3 files
[root@ph190svr002184 iptables]# tail -10 iptables_new.sh
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -j RETURN
#tcp_ZABBIX
/sbin/iptables -A ZABBIX -s 203.0.113.1/32 -m comment --comment PH190-zabbix-proxy -j ACCEPT
/sbin/iptables -A ZABBIX -j RETURN
```

**生成的 iptables 防护规则**

```
#iptables 初始化配置
#删除已有规则
/sbin/iptables --delete-chain
/sbin/iptables --flush
#不允许进和转发，只允许出/回环网卡。最安全的
/sbin/iptables -P INPUT DROP
/sbin/iptables -P FORWARD DROP
/sbin/iptables -P OUTPUT ACCEPT
/sbin/iptables -A INPUT -i lo -j ACCEPT
#允许所有人ping
/sbin/iptables -A INPUT -p icmp -m icmp --icmp-type any -j ACCEPT
#允许关联的状态包已建立的或相关连接的通行
/sbin/iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
/sbin/iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
#想要进入的封包是否为刚刚我发出去的回应?如果是刚刚我发出去的回应,那麼就可以予以接受放行.
#ESTABLISHED：已建立的链接状态. RELATED：该封包为本机发出的封包有关.
#获取SSH端口
#允许SSH端口的连接,脚本自动侦测目前的SSH端口,否则默认为22端口
#获取SSH端口 $sshdport
/sbin/iptables -A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
# 限制 ssh 端口单个IP的最大连接数为 3
/sbin/iptables -I INPUT -p tcp --dport 22 -m connlimit --connlimit-above 3 -j DROP
#允许DNS
#获取DNS-1服务器 $nameserver1
#获取DNS-2服务器 $nameserver2
#tcp_10050
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 10050 -m comment --comment zabbix-agent -j ZABBIX
#tcp_10051
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 10051 -m comment --comment zabbix-proxy -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 10051 -m comment --comment zabbix-proxy -j ACCEPT
#tcp_2631
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -m comment --comment sshd-service -j SSHD
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -m comment --comment netscaler -j NETSCALER
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 22 -m comment --comment ssh -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 22 -m comment --comment ssh -j ACCEPT
#tcp_3128
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 3128 -m comment --comment squid -j SQUID
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 3128 -m comment --comment squid -j ACCEPT
#tcp_443
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 443 -m comment --comment wms -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 443 -m comment --comment wms -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 443 -m comment --comment BS_OPTP -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 443 -m comment --comment BS_git -j ACCEPT
#tcp_4315
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 4315 -m comment --comment WMS-DB -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 4315 -m comment --comment WMS-DB -j ACCEPT
#tcp_4316
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 4316 -m comment --comment INTER-WMS-DB -j ACCEPT
#tcp_4505
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 4505:4506 -m comment --comment salt-mom -j ACCEPT
#tcp_4506
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 4505:4506 -m comment --comment salt-mom -j ACCEPT
#tcp_5044
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 5044 -m comment --comment logship -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 5044 -m comment --comment logship -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 5044 -m comment --comment logship -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 5044 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 5044 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 5044 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 5044 -m comment --comment RSYNC -j ACCEPT
#tcp_80
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -m comment --comment 'netscaler' -j NETSCALER
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 80 -m comment --comment yum-repo -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 80 -m comment --comment wms -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 80 -m comment --comment gcp-proxy -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 80 -m comment --comment wms -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 80 -m comment --comment SSHD -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 80 -m comment --comment CMDB -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 80 -m comment --comment CMDB -j ACCEPT
#tcp_8080
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 8080 -m comment --comment netscaler -j NETSCALER
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 8080 -m comment --comment CMDB -j ACCEPT
#tcp_8086
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 8086 -m comment --comment telegraf-influxdb -j ACCEPT
#tcp_87
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 87 -m comment --comment netscaler -j NETSCALER
#tcp_873
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 873 -m comment --comment rsync -j RSYNC
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment SSHD -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment DT-SSHD -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment SSHD -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A OUTPUT -d 203.0.113.1/32 -p tcp -m tcp --dport 873 -m comment --comment RSYNC -j ACCEPT
#tcp_8888
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 8888 -m comment --comment netscaler -j NETSCALER
#tcp_999
/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 9999 -m comment --comment netscaler -j NETSCALER
#tcp_NETSCALER
/sbin/iptables -A NETSCALER -s 203.0.113.1/32 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/32 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/24 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/24 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/24 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/24 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/24 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/32 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/24 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/24 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/24 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/32 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/32 -m comment --comment NETSCALER -j ACCEPT
/sbin/iptables -A NETSCALER -s 203.0.113.1/32 -m comment --comment public_software_management -j ACCEPT
#tcp_RSYNC
/sbin/iptables -A RSYNC -s 203.0.113.1/32 -m comment --comment rsync -j ACCEPT
/sbin/iptables -A RSYNC -s 203.0.113.1/32 -m comment --comment rsync -j ACCEPT
#tcp_SQUID
/sbin/iptables -A SQUID -s 203.0.113.1/32 -m comment --comment squid-proxy -j ACCEPT
/sbin/iptables -A SQUID -j RETURN
#tcp_SSHD
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment RSYNC -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment SHTerm -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment SHTerm -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -s 203.0.113.1/32 -m comment --comment jenkins -j ACCEPT
/sbin/iptables -A SSHD -j RETURN
#tcp_ZABBIX
/sbin/iptables -A ZABBIX -s 203.0.113.1/32 -m comment --comment PH190-zabbix-proxy -j ACCEPT
/sbin/iptables -A ZABBIX -j RETURN
```
