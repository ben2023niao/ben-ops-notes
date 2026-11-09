---
id: "doc-015522b44242"
title: "日常命令"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "Linux", "DNS", "Redis", "权限管理", "监控告警", "日志分析"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68653708.html"
---

# 日常命令

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2BLinux%2BDNS-%E6%97%A5%E5%B8%B8%E5%91%BD%E4%BB%A4.md)

```bash
ps -aux : 显示当前所有的进程及其详细信息
kill 进程号: 杀死进程,如果杀不掉,可以用kill -9 进程号
pkill: 批量杀进程
上下方向键,选择上一条命令或者下一条命令.
killall 进程号: 杀死此进程和它所有的子进程
top: 动态监控进程状态
top -d 10: 10秒更新一次状态
top -p pid0[, pid1]..[, pidn] : 查看单个进程或某些进程
cal 02 2015: 查看2015年2月的月历
netstat -anp: 查看网络连接,带进程号
netstat -anp | grep :445 : 在当前监听的端口中查找是否有445端口。
sudo -s : ubuntu切换到root用户 su : centos临时切换到root用户
su username : 从root用户切换回普通用户
export PATH="$PATH:/home/heluan123132/" : 加入环境变量
ifconfig 网卡名 203.0.113.1 netmask 203.0.113.1 : 设置IP地址和子网掩码
route -n : 查看默认网关
tar -xzvf filename.tar.bz2 : tar解压缩，v-详细显示处理的文件，z-用gzip压缩或解压
tar -xzvf filename.tar.gz -C dirname : 解压到指定目录
apt install gdb : 下载并安装程序 apt search bind : 查找是否有这个包
yum install cmake : 下载并安装程序
wget http://download.redis.io/releases/redis-3.2.3.tar.gz : 下载文件，linux版的迅雷。
curl 网址 : 访问网页
git clone git网址 : git克隆网上目录到本地
netstat -anp : 列出所有监听端口
cat -n input : 带行号查看内容
cat filename | tail -n +3000 | head -n 1000 ：从第3000行开始，显示1000行。即显示3000~3999行
`pwd` : 返回此命令结果的字符串
fdisk -l : 查看磁盘分区 mkfs -t ext4 /dev/sda3 : 格式化分区
df -lh : 查看各磁盘占用情况 free -m : 查看内存使用情况
mount /dev/sda3 /mnt/sda3 : 挂载分区 df -Th : 查看分区文件格式
dpkg -l : 查看所有的已安装包
tail -f /var/log/syslog : 跟踪系统日志
tcpdump -i : linux抓包工具
tcpdump -i eno16777984 : 抓包时指定网卡
tcpdump -A udp port 6161 : 监听该端口的数据包并以ASC码方式打印出来。
iptables -A INPUT -p tcp --dport 8080 //统计该端口的输入流量(dport destination port的缩写)
iptables -A OUTPUT -p tcp --sport 8080 //统计该商品的输出流量(sport source port的缩写)
iptables -L -v -n -x //查看统计报告
/etc/apparmor.d/ : 此目录下放置了各程序的权限配置文件
dig baidu.com A/MX/CNAME/URL/NS : 询问域名服务器的IP指向/邮件路由/别名/网址转发/DNS记录
dpkg-reconfigure tzdata : 修改系统时区
scp Bin/xCloudClient root@203.0.113.1:/usr/local/xcloud/bin : 远程上传文件
history|tail -n 10 >> git_cmd ：追加到文件末尾
history 10 : 显示linux最近10条命令
traceroute: 追踪路由
route: 查看本机路由表
uname: 查看操作系统名字
rm -f : 删除时不做错误提示
cent os 7 查看系统语言：locale 更改系统语言: vi /etc/locale.conf
cent os 设置DHCP : 打开/etc/sysconfig/network-scripts/ifcfg-ens33，设置：BOOTPROTO=DHCP ONBOOT=yes
unzip test.zip -d test : unzip解压到指定目录
wc -l `find . -name *.c -o -name *.h` 统计代码行数
rm `find . -name *.swp` 删除所有以swp为后缀的文件
rm \&\&qall : 删除&&qall文件。文件名中有特殊符号的，需要带转义字符。
rpm -qa|grep mariadb : centos查看软件的安装包
man、info、--help : Linux下查看帮助的三个命令
nload: 查看实时网络流量
stat filename: 统计文件信息，精确到秒的更新时间。
strace ./test : 追踪该程序运行后产生的系统调用。
gstack 10086 : 查看10086号进程的堆栈信息。
./qps_server & : 以后台方式启动程序
pidof qps_server : 查看进程的进程ID

-------------------------------------------------------------------------------------
useradd/usermod/userdel : 添加/修改/删除用户
useradd username -g groupname : 添加用户时指定用户组
usermod -g root heluan : 将用户设置到root用户组
passwd username : 给用户设置密码
tail -l /etc/passwd : [已脱敏]
tail -l /etc/shadow : 查看各用户密码
groupadd/groupmod/groupdel : 添加/修改/删除用户组
tail -l /etc/group : 查看用户组信息
-------------------------------------------------------------------------------------
ls -al /home : 显示/home目录下所有的文件（包括隐藏文件）的详细信息。
touch file1.txt : 创建一个名为file1.txt的空文件。
cp -r dirsrc dirdst : 将dirsrc目录及其中所有内容复制到dirdst文件夹中。
cp * /mnt/heluan/etc/bind : 复制当前目录下所有文件到指定目录中
cp ddns.key named.conf rndc.conf -t /mnt/heluan : 将这三个文件复制到指定目录下
mv file1.txt file2.txt : 将file1.txt复制到file2.txt(也可用于重命名)。
mv a.dir b.dir c.dir 1.txt 2.txt -t des.dir : 可以一次将这些文件移动到des.dir下。
rm -rf files : 删除files文件夹及其子目录。
-------------------------------------------------------------------------------------
mkdir -m 777 dirname : 创建文件夹，并指定权限。
mkdir -p dir/files : 如父目录不存在，连同父目录一起创建。
rmdir -p dirname : 只能删除空目录
pwd : [已脱敏]
cd ~ : 返回登录目录 cd / : 返回根目录 cd .. : 返回上级目录 cd - : 返回上个目录
rm -r ~/Documents/* : 删除目录下所有文件及文件夹
-------------------------------------------------------------------------------------
chmod 764 file1.txt : 设置文件的权限。
chmod 764 -R dirname : 设置文件夹的权限，递归应用到里面所有的文件和文件夹。
chown yaozishu myheart : 将myheart文件的所有者改为用户yaozishu。
find . -name filename/dirname : 在当前目录下按照目录名或者文件名查找
find . -mtime -30 : 查找最近30天内修改过的文件。
-------------------------------------------------------------------------------------
grep&sed命令：
grep hello *.txt : 在所有后缀为txt的文件中搜索含有hello单词的行。
grep -c ^$ test.sh : 从test.sh文件中搜索空行，打印出行数。
grep -n enum *.h : 在所有后缀为.h的文件中搜索含有enum单词的行，并带行号输出。
sed -i "s/garden/mirGarden/g" 1.txt ：将文件1.txt内的文字“garden”替换成“mirGarden”
sed -i "s/garden/mirGarden/g" `ls` ：将当前目录下的所有文件内的“garden”替换成“mirGarden”，其实也就是ls出多个文件名而已
sed -i "s/g_client_/g_user_/g" `find . -name *.h -o -name *.c` : 将当前目录下代码中所有的"g_client_"替换成“g_user_”
sed '1,$d' file1.txt : 删除该文件中第一行到最后一行。
sed -n 's/hello/[&]/p' hello.c ：将hello.c文件中hello单词加上[]
sed -n '/hello/w output' input : 将与hello匹配的行写入output文件
sed -i '/}/a\ ' hello.c : 在hello.c文件中所有匹配‘}’的行后面插入空行，并保存到原文件。
sed -i '/printf/c\new line' hello.c : 将带printf的行替换为新行。
sed -i '$r add.c' hello.c : 把add.c的内容添加到hello.c的最后一行后面。
sed 'y/abc/ABC/' input : 将所有的a,b,c分别替换成大写字母
sed -n '/printf/{p;=}' hello.c : 打印包括printf的行内容和行号
sed -i '6,7d' hello.c : 删除第6-7行
sed -i '/printf/{y/32/75/; s/add/Add/g}' hello.c : 将printf匹配的行中3、2分别替换为7、5，将add替换为Add
sed -n '/include/p; /main/p' hello.c ：分别打印出包含include和main的行。
sed -i "s/\r//g" `find . -name *.h` : 当前目录下所有的.h文件中去掉\r符号
--------------------------------------------------------------------------------------
awk命令：
awk '/^$/{print "this is a blank line"}' input : 遇到空行打印字符串。
awk -f cmd.awk input : 调用文件中的命令。
awk '{print $2,$1,$4,$3}' student.txt : 按域操作符打印
awk '{print $0}' student.txt : 打印所有域
awk 'BEGIN{x = 1; y = 1} {print $(x + y)}' student.txt : 利用表达式打印域
awk -F"\t" '{print $3}' student.txt : 设置域分隔符
awk 'BEGIN{FS = "\t+"} {print $1, $3}' student.txt : 环境变量中设置域分隔符
awk 'BEGIN{FS = ":"} $0~/root/' /etc/passwd : [已脱敏]
$0!~/root/ : 所有域中不匹配root的行
awk -F":" '{if($3~10 || $4==20) print $0}' /etc/passwd : [已脱敏]
awk 'BEGIN{FS=","} {print NR, $0} END{print FILENAME}' student.txt ：打印系统变量
printf修饰符一般格式：%-width.prec 格式控制符 例：%-10.3f
FS: 域分隔符 OFS: 列输出分隔符 ENVIRON["AWKPATH"]=/bin/gawk : 设定环境变量名
当awk过程中BEGIN完成，正式执行的时候，参数数组中只应该有awk和输入文件名两个参数。
--------------------------------------------------------------------------------------
正则表达式：
^d : 以d开头的行 . : 一个任意字符 $ : 最后一个
x* : 匹配前面字符0-N次 + : 匹配前面字符1-N次 ? : 匹配前面字符0|1次
--------------------------------------------------------------------------------------
通配符：
* : 0~n个字符 % : 1~n个字符 ? : 单个字符
[a,b,c] : 范围
--------------------------------------------------------------------------------------
sort排序工具：
sort -t: -k3nr input.txt; //以冒号为分隔符，根据第三域的数字大小从大到小排序
```
