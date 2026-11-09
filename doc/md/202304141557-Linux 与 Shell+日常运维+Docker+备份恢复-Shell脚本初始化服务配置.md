---
id: "doc-9feb5c97da40"
title: "Shell脚本初始化服务配置"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "Docker", "备份恢复", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/84417228.html"
---

# Shell脚本初始化服务配置

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-Linux%20%E4%B8%8E%20Shell%2B%E6%97%A5%E5%B8%B8%E8%BF%90%E7%BB%B4%2BDocker%2B%E5%A4%87%E4%BB%BD%E6%81%A2%E5%A4%8D-Shell%E8%84%9A%E6%9C%AC%E5%88%9D%E5%A7%8B%E5%8C%96%E6%9C%8D%E5%8A%A1%E9%85%8D%E7%BD%AE.md)

- **生产实践：**

    使用shell针对服务进行个性化配置

- **学习技巧：**

    [Shell](https://chegva.com/tag/shell/ "View all posts in Shell") 判断、循环、function，配置crontab、rsync、系统内核参数

- **脚本内容：**

使用shell脚本在业务初始化时执行服务个性化配置，提高机器快速扩容效率。

```bash
#!/bin/bash
set -x

hostname=`hostname`
baseurl=""
# select baseurl
function select_baseurl() {
 if [[ $hostname == *dictchunk* ]] ; then
 baseurl="https://git.chegva.com/anzhihe/rt-init/raw/master/dict-chunk"
 elif [[ $hostname == *public-rtchunk* ]] ; then
 baseurl="https://git.chegva.com/anzhihe/rt-init/raw/master/pub-rt-chunk"
 elif [[ $hostname == *gs-rtchunk* ]]; then
 baseurl="https://git.chegva.com/anzhihe/rt-init/raw/master/rt-chunk"
 else
 echo "无需baseurl配置，请忽略！"
 fi
}
# add network rto
function add_rto() {
 gateway=`ip r |grep default|awk '{print $3}'`
 if [ -z $gateway ];then
 echo "gateway is null"
 exit 1
 fi
 localIP=`hostname |xargs host |awk '{print $NF}'`
 if [[ $localIP == 100\.69* || $localIP == 100\.70* || $localIP == 100\.89* || $localIP == 100\.90* ]];then
 echo "gz ip: $localIP"
 ip r add 203.0.113.1/16 via $gateway rto_min 50ms
 ip r add 203.0.113.1/16 via $gateway rto_min 50ms
 ip r add 203.0.113.1/18 via $gateway rto_min 50ms
 ip r add 203.0.113.1/16 via $gateway rto_min 50ms
 if [[ $? -eq 0 ]];then
 echo "ip r add 203.0.113.1/16  via $gateway rto_min 50ms" >> /etc/rc.local
 echo "ip r add 203.0.113.1/16  via $gateway rto_min 50ms" >> /etc/rc.local
 echo "ip r add 203.0.113.1/18  via $gateway rto_min 50ms" >> /etc/rc.local
 echo "ip r add 203.0.113.1/16  via $gateway rto_min 50ms" >> /etc/rc.local
 fi
 elif [[ $localIP == 10\.88* || $localIP == 10\.89* || $localIP == 10\.90* ]];then
 echo "bj ip: $localIP"
 ip r add 203.0.113.1/16 via $gateway rto_min 50ms
 ip r add 203.0.113.1/16 via $gateway rto_min 50ms
 ip r add 203.0.113.1/16 via $gateway rto_min 50ms

 if [[ $? -eq 0 ]];then
 echo "ip r add 203.0.113.1/16  via $gateway rto_min 50ms" >> /etc/rc.local
 echo "ip r add 203.0.113.1/16  via $gateway rto_min 50ms" >> /etc/rc.local
 echo "ip r add 203.0.113.1/16  via $gateway rto_min 50ms" >> /etc/rc.local
 fi
 elif [[ $localIP == 10\.85* || $localIP == 10\.86* || $localIP == 10\.87* ]];then
 echo "sh ip: $localIP"
 ip r add 203.0.113.1/16 via $gateway rto_min 50ms
 ip r add 203.0.113.1/16 via $gateway rto_min 50ms
 ip r add 203.0.113.1/16 via $gateway rto_min 50ms

 if [[ $? -eq 0 ]];then
 echo "ip r add 203.0.113.1/16  via $gateway rto_min 50ms" >> /etc/rc.local
 echo "ip r add 203.0.113.1/16  via $gateway rto_min 50ms" >> /etc/rc.local
 echo "ip r add 203.0.113.1/16  via $gateway rto_min 50ms" >> /etc/rc.local
 fi
 else
 echo "not bj or gz sh ip, exit"
 exit 0
 fi
}
# add kernel para
function add_kernel_para() {
 ## 关闭coredump
 sysctl -w kernel.core_pattern="|/bin/false"
 echo "kernel.core_pattern = |/bin/false" >> /etc/sysctl.conf

 ## 备份sysctl.conf
 cp /etc/sysctl.conf /tmp/sysctl.conf.bak

 #hostname=`hostname`
 if [[ $hostname == *\.docker ]] ; then
 echo "docker机器跳过"
 exit 1
 fi
 # if [[ $hostname == *\.us01 ]] ; then
 # 	echo "美东机器跳过"
 # 	exit 1
 # fi
 ncs="net.core.somaxconn"
 sysctl -w ${ncs}=4096
 if grep -o "${ncs}" /etc/sysctl.conf > /dev/null
 then
 oldvalue=$(grep ${ncs} /etc/sysctl.conf|tail -1 | awk -F "=| " '{ print $NF }')
 if [ $oldvalue -ne 4096 ]
 then
 sed -i "s|\("${ncs}" *= *\).*|\14096|" /etc/sysctl.conf
 else
 echo "${ncs} 无需改动"
 fi
 else
 echo "新加vm配置"
 echo "${ncs} = 4096" >> /etc/sysctl.conf
 fi
 nitmsb="net.ipv4.tcp_max_syn_backlog"
 sysctl -w ${nitmsb}=4096
 if grep -o "$nitmsb" /etc/sysctl.conf > /dev/null
 then
 oldvalue=$(grep ${nitmsb} /etc/sysctl.conf|tail -1 | awk -F "=| " '{ print $NF }')
 if [ $oldvalue -ne 4096 ]
 then
 sed -i "s|\("${nitmsb}" *= *\).*|\14096|" /etc/sysctl.conf
 else
 echo "${nitmsb} 无需改动"
 fi
 else
 echo "新加vm配置"
 echo "${nitmsb} = 4096" >> /etc/sysctl.conf
 fi
}
# add system crontab
function add_cron() {
 if [[ $hostname == *dictchunk* ]] ; then
 if grep -q "archive_trp_clean.sh" /var/spool/cron/anzhihe; then
 echo "archive_trp_clean定时任务已经添加！"
 else
 echo "00 04 * * * cd /home/anzhihe/DDict/dict-chunk/ && bash archive_trp_clean.sh" >> /var/spool/cron/anzhihe
 echo "添加ddict crontab完成"
 fi

 elif [[ $hostname == *public-rtchunk* || $hostname == *gs-rtchunk* ]] ; then
 curl -sq $baseurl/clear_unitdb_log.sh -w "\n" > /home/anzhihe/opbin/clear_unitdb_log.sh
 chown anzhihe.anzhihe /home/anzhihe/opbin/clear_unitdb_log.sh
 chmod 744 /home/anzhihe/opbin/clear_unitdb_log.sh

 if grep -q "clear_unitdb_log.sh" /var/spool/cron/anzhihe; then
 echo "clear_unitdb_log定时任务已经添加！"
 else
 echo "*/5 * * * * cd /home/anzhihe/opbin;./clear_unitdb_log.sh >> clear_unitdb_log 2>&1" >> /var/spool/cron/anzhihe
 echo "添加rt crontab完成"
 fi
 else
 echo "no cron need to add "
 fi
}
# add rsyncd config
function add_rsyncd_config() {
 curl -sq $baseurl/rsyncd.password -w "\n" > /etc/rsyncd.password
 curl -sq $baseurl/rsync.password -w "\n" > /etc/rsync.password

 chmod 600 /etc/rsyncd.password /etc/rsync.password
 chown root.root /etc/rsyncd.password
 chown anzhihe.anzhihe /etc/rsync.password

 if [[ $hostname == *\.gz01 ]] ; then
 idc="gz"
 elif [[ $hostname == *\.ys || $hostname == *\.py02 ]] ; then
 idc="sh"
 elif [[ $hostname == *\.us01 || $hostname == *\.ru01 ]]; then
 idc="us01"
 # 配置us01 ntp
 #cp -f /etc/ntp.conf /etc/ntp.conf.bak-`date +%Y%m%d`
 #cp -f /usr/local/sys/configure/all_etc/ntp_md.conf /etc/ntp.conf
 #systemctl restart ntpd
 else
 echo "机器不在合理机房"
 exit 1
 fi
 if [ `ps -elf|grep -v grep |grep -c /usr/bin/rsync` -lt 1 ]; then
 curl -sq $baseurl/${idc}.rsyncd.conf -w "\n" > /etc/rsyncd.conf
 /usr/bin/rsync --daemon && echo "rsync已启动。"
 echo "/usr/bin/rsync --daemon" >> /etc/rc.d/rc.local
#    else
#    	curl -sq $baseurl/${idc}.rsyncd-append.conf -w "\n" >> /etc/rsyncd.conf
 fi
 echo "添加rsync配置完成..."
}
function main() {
 if [[ $hostname == *chunk* ]]; then
 select_baseurl
 add_kernel_para
 add_cron
 add_rsyncd_config
 else
 echo "非存储机器略过..."
 exit 0
 fi
}

main
```

参考：[Cobbler批量装机系统初始化脚本](https://chegva.com/2587.html)
