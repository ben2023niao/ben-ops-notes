---
id: "doc-162345613615"
title: "glances.sh"
date: "2021-12-21T15:32:57.899000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["可观测性", "监控"]
tags: ["监控", "Shell", "Python", "Docker", "Nginx", "MySQL", "Redis", "Zabbix", "监控告警", "DNS", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/jian-kong/glances-jian-kong-bu-shu/glances.sh.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "99d5bcb0886292e808de3fe65d94b9c1826e6b61b5fafec8bc2d8d0ee9c579b3"
---

# glances.sh

> 原文：[glances.sh](https://xn--6o0a585a.gitbook.io/devops/jian-kong/glances-jian-kong-bu-shu/glances.sh.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-21 15:32｜日期依据：GitBook 页面更新时间

```bash
#!/bin/bash
#服务端
#服务器运行 glances 容器
#docker run -d --restart="always" --name glances -p 61208-61209:61208-61209 -e GLANCES_OPT="-w" -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host docker.io/nicolargo/glances

#agent端
#获取全部json 数据
curl -s http://203.0.113.1:61208/api/3/all > all

function system(){
echo "主机名        : `hostname`"
echo "系统          : `cat all | jq ".system.hr_name"`" | sed "s/\"//g"
echo "内核版本      : `cat all | jq ".system.os_version"`" | sed "s/\"//g"
echo "CPU 总使用率  : `cat all | jq '.cpu.total'` %"
echo "内存使用率    : `cat all | jq ".quicklook.mem"` %"
echo "交换分区使用率: `cat all | jq ".quicklook.swap"` %"
echo "服务器ip"
ip a |\
grep "global" |\
awk '{print $2}' |\
awk -F/ '{print $1}'

if [ ! -d "/www/server/panel/vhost/nginx/" ];then
    echo "宝塔 nginx 未配置域名"
else
    echo "宝塔 nginx 配置域名"
    find /www/server/panel/vhost/nginx/ -name "*.conf" |\
    grep -Ev "*default.conf" |\
    xargs cat |\
    grep server_name |\
    grep -Ev "#" |\
    grep -Ev "203.0.113.1" |\
    sed 's/server_name/ /g' |\
    sed 's/;/ /g'
fi

if [ ! -d "/www/server/panel/vhost/apache/" ];then
    echo "宝塔 apache 未配置域名"
else
    echo "宝塔 apache 配置域名"
    find /www/server/panel/vhost/apache/ -name "*.conf" |\
    grep -Ev "*default.conf" |\
    xargs cat |\
    grep ServerAlias |\
    awk '{print $2}'
fi

}

function alert(){
echo 报警信息
cat all | jq '.alert'
}

function amps(){
echo 服务组件统计信息
cat all | jq '.amps'
}

function tcp_ip(){
echo "TCP/IP协议链接环境过程监控"
echo "LISTEN                          : `cat all | jq '.connections.LISTEN'`"
echo "ESTABLISHED                     : `cat all | jq '.connections.ESTABLISHED'`"
echo "SYN_SENT                        : `cat all | jq '.connections.SYN_SENT'`"
echo "SYN_RECV                        : `cat all | jq '.connections.SYN_RECV'`"
echo "initiated                       : `cat all | jq '.connections.initiated'`"
echo "terminated                      : `cat all | jq '.connections.terminated'`"
echo "Iptables之nf_conntrack模块监控"
echo "nf_conntrack_count              : `cat all | jq '.connections.nf_conntrack_count'`"
echo "nf_conntrack_max                : `cat all | jq '.connections.nf_conntrack_max'`"
echo "nf_conntrack_percent            : `cat all | jq '.connections.nf_conntrack_percent'`"
}

function cpu(){
echo "CPU 监控"
echo "CPU 型号                        : `cat all | jq ".quicklook.cpu_name"`" | sed "s/\"//g"
echo "CPU 主频                        : `cat all | jq ".quicklook.cpu_hz"` 次/s"
echo "CPU 超频                        : `cat all | jq ".quicklook.cpu_hz_current"` 次/s"
echo "CPU 物理核心                    : `cat all | jq '.core.phys'` 核"
echo "CPU 逻辑核心                    : `cat all | jq '.core.log'` 核"
echo "CPU 总使用率                    : `cat all | jq '.cpu.total'` %"
echo "CPU 空闲率                      : `cat all | jq '.cpu.idle'` %"
echo "CPU user使用率                  : `cat all | jq '.cpu.user'` %"
echo "CPU nice使用率                  : `cat all | jq '.cpu.nice'` %"
echo "CPU system使用率                : `cat all | jq '.cpu.system'` %"
echo "CPU iowait                      : `cat all | jq '.cpu.iowait'` %"
echo "CPU irq处理硬中断时间           : `cat all | jq '.cpu.irq'`"
echo "CPU softirq处理软中断时间       : `cat all | jq '.cpu.softirq'`"
echo "CPU guest处理虚拟机时间         : `cat all | jq '.cpu.guest'`"
echo "CPU guest_nice处理虚拟机时间    : `cat all | jq '.cpu.guest_nice'`"
echo "CPU cpucore                     : `cat all | jq '.cpu.cpucore'`"
echo "CPU ctx_switches                : `cat all | jq '.cpu.ctx_switches'`"
echo "CPU interrupts                  : `cat all | jq '.cpu.interrupts'`"
echo "CPU soft_interrupts             : `cat all | jq '.cpu.soft_interrupts'`"
echo "CPU syscalls                    : `cat all | jq '.cpu.syscalls'`"

cat > CPU_参数扫盲.txt << EOF
user       （通常缩写为us），   代表用户态CPU时间。注意，它不包括下面的nice时间，但包括了guest时间。
nice       （通常缩写为ni），   代表低优先级用户态CPU时间，也就是进程nice值被调整为1-19之间的CPU时间。这里注意，nice可取值范围是-20到19，数值越大，优先级反而越低。
system     （通常缩写为sys），  代表内核态CPU时间。
idle       （通常缩写为id），   代表空闲时间，注意，它不包括等待I/O的时间（iowait）。
iowait     （通常缩写为wa），   代表等待I/O的CPU时间。
irq        （通常缩写为hi），   代表处理硬中断的CPU时间。
softirq    （通常缩写为si），   代表处理软中断的CPU时间。
steal      （通常缩写为st），   代表当系统运行在虚拟机中的时候，被其他虚拟机占用的CPU时间。
guest      （通常缩写为guest），代表通过虚拟化运行其他操作系统的时间，也就是运行虚拟机的CPU时间。
guest_nice （通常缩写为gnice），代表以低优先级运行虚拟机的时间。
Idel表示：CPU处于空闲状态时间比例。一般而言，idel + user + nice 约等于100%"
User表示：CPU一共花了多少比例的时间运行在用户态空间或者说是用户进程(running user space processes)。典型的用户态空间程序有：Shells、数据库、web服务器……"
Nice表示：可理解为，用户空间进程的CPU的调度优先级，范围为[-20,19]"
Syst表示：CPU花了多少比例的时间在内核空间运行。分配内存、IO操作、创建子进程……都是内核操作。这也表明，当IO操作频繁时，System参数会很高。"
Wait表示：在计算机中，读写磁盘的操作远比CPU运行的速度要慢，CPU负载处理数据，而数据一般在磁盘上需要读到内存中才能处理。当CPU发起读写操作后，需要等着磁盘驱动器将数据读入内存(可参考：JAVA IO 以及 NIO 理解)，从而导致CPU 在等待的这一段时间内无事可做。CPU处于这种等待状态的时间由Wait参数来衡量"
EOF
}

function percpu(){
cat all |\
jq ".percpu" |\
sed "s/\[//g"|\
sed "s/\]//g"|\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\"//g" |\
sed "s/\,//g" |\
grep -v '^\s*$' |\
grep -E "cpu_number:|total:|user:|system:|idle:|iowait:" > percpu.txt

cat percpu.txt | grep cpu_number: | sed "s/cpu_number/CPU/g" > percpu_cpu.txt
cat percpu.txt | grep total:      | sed "s/total/总/g"       > percpu_total.txt
cat percpu.txt | grep user:       | sed "s/user/用户/g"      > percpu_user.txt
cat percpu.txt | grep system:     | sed "s/system/系统/g"    > percpu_system.txt
cat percpu.txt | grep idle:       | sed "s/idle/空闲/g"      > percpu_idle.txt
cat percpu.txt | grep iowait:     | sed "s/iowait/IO/g"      > percpu_iowait.txt

paste \
precpu_cpu.txt \
precpu_total.txt \
precpu_user.txt \
precpu_system.txt \
precpu_iowait.txt

}

function cpu_list(){
awk '$0 ~/cpu[0-9]/' /proc/stat |\
while read line ; do
echo "$line" |\
awk '{total=$2+$3+$4+$5+$6+$7+$8;free=$5;print$1" 空闲 "free/total*100"%"," 使用 " (total-free)/total*100"%"}' |\
sed 's/%/ %/g'|sed 's/\./ ./g';
done |\
awk '{print $1" "$2" "$3" "$5" "$6" "$7" "$9}'
}

function diskio(){
echo "磁盘信息监控"
cat all |\
jq '.diskio' |\
sed "s/\[//g" |\
sed "s/\]//g" |\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\,//g" |\
sed "s/\"//g" |\
sed "s/disk_name:/磁盘名:/g" |\
sed "s/read_count/读IO数/g" |\
sed "s/write_count/写IO数/g" |\
sed "s/read_bytes/IO读字节数/g" |\
sed "s/write_bytes/IO写字节数/g" |\
sed "s/key: disk_name//g" |\
grep -v '^\s*$' |\
grep -v time_since_update > diskio.txt

cat diskio.txt | grep 磁盘名 > diskio_name.txt
cat diskio.txt | grep 读IO数 > diskio_read.txt
cat diskio.txt | grep IO读字节数 > diskio_read_bytes.txt
cat diskio.txt | grep 写IO数 > diskio_write.txt
cat diskio.txt | grep IO写字节数 > diskio_write_bytes.txt

paste \
diskio_name.txt \
diskio_read.txt \
diskio_read_bytes.txt \
diskio_write.txt \
diskio_write_bytes.txt
}

function disk_list(){
df -P -h |\
sed 's/%/ %/g' |\
awk 'NR == 1 {next} {print $1" 容量"$2" 已用"$5" "$6" 挂载点"$7}'
}

function dockerinfo(){
echo "运行容器信息"
cat all |\
jq  ".docker.containers" |\
sed "s/\[//g" |\
sed "s/\]//g" |\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\"//g" |\
sed "s/\,//g" |\
grep -v '^\s*$' |\
grep -v 'name' |\
grep -v 'time_since_update' |\
sed "s/Names/容器名/g" |\
sed "s/Id/容器ID/g" |\
sed "s/Image/Image镜像/g" |\
sed "s/Status/容器状态/g" |\
sed "s/Command/容器运行命令/g" |\
sed "s/cpu/容器CPU/g" |\
sed "s/memory/容器内存/g" |\
sed "s/io/容器io/g" |\
sed "s/network/容器网络/g"

echo "docker服务信息"
cat all |\
jq  ".docker.version.Components" |\
sed "s/\[//g" |\
sed "s/\]//g" |\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\"//g" |\
sed "s/\,//g" |\
grep -v '^\s*$' |\
sed "s/Name/组件服务名/g" |\
sed "s/Version/版本/g" |\
sed "s/Details/详细信息/g" |\
sed "s/Arch/系统架构/g" |\
sed "s/BuildTime/构建时间/g" |\
sed "s/Experimental/测试(实验)模式/g" |\
sed "s/GitCommit/Git提交记录/g" |\
sed "s/Os/操作系统/g"

#cat all | jq  ".docker.version.Version"
#cat all | jq  ".docker.version.ApiVersion"
#cat all | jq  ".docker.version.MinAPIVersion"
#cat all | jq  ".docker.version.GitCommit"
#cat all | jq  ".docker.version.GoVersion"
#cat all | jq  ".docker.version.Os"
#cat all | jq  ".docker.version.Arch"
#cat all | jq  ".docker.version.KernelVersion"
#cat all | jq  ".docker.version.BuildTime"
}

function file_system(){
cat all |\
jq ".fs" |\
sed "s/\[//g" |\
sed "s/\]//g" |\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\"//g" |\
sed "s/\,//g" |\
grep -v '^\s*$' |\
sed "s/device_name/挂载设备名/g" |\
sed "s/fs_type/文件系统类型/g" |\
sed "s/size/大小/g" |\
sed "s/used/已使用/g" |\
sed "s/free/未使用/g" |\
sed "s/percent/百分比/g" |grep -v key
}

function public_address(){
ip a |\
grep "global" |\
awk '{print $2}' |\
awk -F/ '{print $1}' |\
grep -v 192.168 |\
grep -v 203.0.113.1 |\
grep -v 172.17
}

function public_address_get_domain(){
#公网ip获取域名解析
export -f public_address

for pub_ip in `public_address`;do
echo $pub_ip
curl -s "https://dnsdblookup.com/$pub_ip" |\
grep 'span class="date"' |\
sed "s/<//g" |\
sed "s/>//g" |\
sed "s/lispan//g" |\
sed "s/class=\"date\"//g" |\
sed "s/\/spana href=\"\// /g" |\
sed "s/\/\" target=/ /g" |\
awk '{print $1" "$2}'
done
}

function irq(){
#上下文切换
cat all |\
jq ".irq" |\
sed "s/\[//g" |\
sed "s/\]//g" |\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\"//g" |\
sed "s/\,//g" |\
grep -v time_since_update |\
grep -v key |\
grep -v '^\s*$' |\
sed "s/irq_line/设备/g" |\
sed "s/irq_rate/每秒内设备中断数/g"
}

function load(){
cat all |\
jq ".load" |\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\"//g" |\
sed "s/\,//g" |\
sed "s/min1/1分钟内负载/g" |\
sed "s/min5/5分钟内负载/g" |\
sed "s/min10/10分钟内负载/g" |\
sed "s/cpucore/cpu核心/g"
}

function mem(){
echo "  内存使用率: `cat all | jq ".quicklook.mem"` %"
cat all |\
jq ".mem" |\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\"//g" |\
sed "s/\,//g"
}

function memswap(){
echo "  交换分区使用率: `cat all | jq ".quicklook.swap"` %"
cat all |\
jq ".mem" |\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\"//g" |\
sed "s/\,//g"
}

function network(){
cat all |\
jq ".network" |\
sed "s/\[//g"|\
sed "s/\]//g"|\
sed "s/{//g" |\
sed "s/}//g" |\
sed "s/\"//g" |\
sed "s/\,//g" |\
grep -v '^\s*$' |\
grep -v key |\
grep -v cumulative |\
grep -v time_since_update |\
grep -v alias |\
sed "s/interface_name/网卡/g" |\
sed "s/is_up/状态/g"
}

function processcount(){
echo "当前系统默认支持的最大线程数 `cat /proc/sys/kernel/pid_max`"
echo "全部进程数量 : `cat all | jq ".processcount.total"`"
echo "运行进程数量 : `cat all | jq ".processcount.running"`"
echo "睡眠进程数量 : `cat all | jq ".processcount.sleeping"`"
echo "运行线程数量 : `cat all | jq ".processcount.thread"`"
echo "僵尸进程数量 : `ps -ef | grep defunct | grep -v grep | wc -l`"
echo "如果运行线程接近最大线程服务器会宕机！！！"
echo "如果运行线程接近最大线程服务器会宕机！！！"
echo "如果运行线程接近最大线程服务器会宕机！！！"
}

function processlist(){
cat all |\
jq ".processlist" |\
grep '"name"' |\
grep -E "BT|zabbix_agent|nginx|php|docker|http|mysql|redis|ftp|python|firewalld|ip" |\
sed "s/\"//g" |\
sed "s/\,//g" |\
sed "s/name//g" |\
uniq -c |\
awk '{print "核心进程数量 :"$0}'
}

function ssh_history(){
tail /var/log/check_user_history.log | sed "s/#//g"
}

function now(){
cat all |\
jq ".now" |\
sed "s/\"//g"
}

function folders(){
cat all | jq ".folders"
}

function gpu(){
cat all | jq ".gpu"
}

#依次导入函数
export -f system
export -f alert
export -f amps
export -f tcp_ip
export -f cpu
export -f cpu_list
export -f diskio
export -f disk_list
export -f dockerinfo
export -f file_system
export -f public_address
export -f public_address_get_domain
export -f irq
export -f load
export -f mem
export -f memswap
export -f network
export -f now
export -f percpu
export -f processcount
export -f processlist
export -f ssh_history

#依次执行函数
system
alert
amps
tcp_ip
cpu
cpu_list
percpu
diskio
disk_list
dockerinfo
file_system
public_address
public_address_get_domain
irq
load
mem
memswap
network
now
processcount
processlist
ssh_history
```
