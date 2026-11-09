---
id: "doc-39ac7d2c3a11"
title: "Shell脚本重复调用命令行"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "日志分析", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/84417230.html"
---

# Shell脚本重复调用命令行

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-Linux%20%E4%B8%8E%20Shell%2B%E6%97%A5%E5%B8%B8%E8%BF%90%E7%BB%B4%2B%E6%97%A5%E5%BF%97%E5%88%86%E6%9E%90%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-Shell%E8%84%9A%E6%9C%AC%E9%87%8D%E5%A4%8D%E8%B0%83%E7%94%A8%E5%91%BD%E4%BB%A4%E8%A1%8C.md)

- **生产实践：**

    使用shell重复调用命令行

- **学习技巧：**

    [Shell](https://chegva.com/tag/shell/ "View all posts in Shell") 判断、循环、function & polysh工具使用

- **脚本内容：**

使用shell脚本一键迁移存储机器上的分片，使用polysh在中控机上执行，避免登陆集群机器手动执行命令，提高效率

mig_rt_out.sh：将分片迁出

**mig_rt_out.sh** 展开源码

```bash
#!/bin/bash
dirname="/home/anzhihe/opdir/"
logfile="/home/anzhihe/opdir/mig_rt.log"
show_copy_tasks="/home/anzhihe/rt-table/rt-dashboard/MasterCmd show_copy_tasks"
force_balance="/home/anzhihe/rt-table/rt-dashboard/MasterCmd force_balance offset=0 limit=1"
date_now=$(date +"%Y-%m-%d %H:%M:%S")

get_time() {
 echo -e "\n++++++++++++ $date_now ++++++++++++" | tee -a $logfile
}
# 获取迁移分片任务总数
get_tasksum() {
 sum=`/home/anzhihe/rt-table/rt-dashboard/MasterCmd show_copy_tasks |wc -l`
 task_sum=`expr $sum - 3`
}
# 将迁移任务信息记录日志
set_logfile() {
 echo "++++++++++++ $1 分片迁移任务开始 ++++++++++++" | tee -a $logfile
 echo $date_now >> $logfile && echo "$($show_copy_tasks)" | tee -a $logfile
}
# 配置分片迁移信息
set_copy_tasks_info() {
 if [ $# -lt 1 ]; then
 echo "Usage: `basename $0` host_ip1 host_ip2..."
 exit;
 elif [ $# -eq 1 ]; then
 json_file=`echo $1".json"`
 chunk_file=`echo "$dirname""$json_file"`
 #echo $chunk_file
 if [ ! -f "$chunk_file" ]; then
 get_time
 echo "/home/anzhihe/rt-table/rt-dashboard/trp_distribute --output_check_res 0 rm_chunks --chunks $1:9090 > $chunk_file" | tee -a $logfile
 /home/anzhihe/rt-table/rt-dashboard/trp_distribute --output_check_res 0 rm_chunks --chunks $1:9090 > $chunk_file | tee -a $logfile
 echo "/home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file" | tee -a $logfile
 /home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file | tee -a $logfile
 set_logfile "$1"
 else
 echo "$chunk_file文件已存在，请检查！" | tee -a $logfile
 exit 1
 fi
 else
 port=":9090"
 host=("$*")
 allhost=`echo $host | sed "s/\s\+/_/g"`
 hostinfo=`echo $host | sed "s/\s\+/${port}#/g"`${port}
 #echo $hostinfo
 json_file=`echo $allhost".json"`
 chunk_file=`echo "$dirname""$json_file"`
 #echo $chunk_file
 if [ ! -f "$chunk_file" ]; then
 get_time
 echo "/home/anzhihe/rt-table/rt-dashboard/trp_distribute --output_check_res 0 rm_chunks --chunks ${hostinfo} > $chunk_file" | tee -a $logfile
 /home/anzhihe/rt-table/rt-dashboard/trp_distribute --output_check_res 0 rm_chunks --chunks ${hostinfo} > $chunk_file | tee -a $logfile
 echo "/home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file" | tee -a $logfile
 /home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file | tee -a $logfile
 set_logfile "${allhost}"
 else
 echo "$chunk_file文件已存在，请检查！" | tee -a $logfile
 exit 1
 fi
 fi
}
# 执行分片迁移任务
run_copy_tasks() {
 while true
 do
 get_tasksum
 if [ $task_sum -ge 1 ]; then
 if echo $($show_copy_tasks) | grep -q "Copying" ; then
 sleep 30
 else
 $($force_balance)
 fi
 else
 date_now=$(date +"%Y-%m-%d %H:%M:%S")
 #cd $dirname && cp -f $json_file $json_file.bak-`date +%Y%m%d`
 echo "++++++++++++ ${date_now} 分片迁移任务已完成！++++++++++++" | tee -a $logfile
 break
 fi
 done
}

main() {
 get_tasksum
 if [ $task_sum -lt 1 ]; then
 set_copy_tasks_info "$@"
 sleep 10
 if [ -f "$chunk_file" ]; then
 run_copy_tasks
 else
 get_time
 echo "$json_file文件没有创建成功，请检察！" | tee -a $logfile
 exit 1
 fi
 else
 echo "已经存在迁移任务，请检查！"
 fi
}

main "$@"
```

mig_rt_in.sh：将分片迁回

**mig_rt_in.sh** 展开源码

```bash
#!/bin/bash
dirname="/home/anzhihe/opdir/"
logfile="/home/anzhihe/opdir/mig_rt.log"
show_copy_tasks="/home/anzhihe/rt-table/rt-dashboard/MasterCmd show_copy_tasks"
force_balance="/home/anzhihe/rt-table/rt-dashboard/MasterCmd force_balance offset=0 limit=1"
date_now=$(date +"%Y-%m-%d %H:%M:%S")

get_time() {
 echo -e "\n============ $date_now ============" | tee -a $logfile
}
# 获取迁移分片任务总数
get_tasksum() {
 sum=`/home/anzhihe/rt-table/rt-dashboard/MasterCmd show_copy_tasks |wc -l`
 task_sum=`expr $sum - 3`
}
# 将迁移任务信息记录日志
set_logfile() {
 echo "============ $1 分片迁回任务开始 ============" | tee -a $logfile
 echo $date_now >> $logfile && echo "$($show_copy_tasks)" | tee -a $logfile
}
# 配置分片迁移信息
set_copy_tasks_info() {
 if [ $# -ne 1 ]; then
 echo "Usage: `basename $0` chunk_file"
 exit
 fi
 if [ ! -f "$dirname$@" ]; then
 echo "$@文件不存在请检查！"
 exit
 fi
 host=`basename $1 .json`
 json_file_b=`echo $host"-b.json"`
 chunk_file=`echo "$dirname""$json_file_b"`
 echo $chunk_file
 if [[ "$@" == *_* ]]; then
 host1=`echo $host |awk -F"_" '{ print $1}'`
 host2=`echo $host |awk -F"_" '{ print $2}'`
 if [ ! -f "$chunk_file" ]; then
 get_time
 sed -n '/"ChunkAddr": "'$host1':9090"/{h;n;/"ChunkAddr":/!{:a;N;/"PartitionId"/!ba;x;H;n};x;H;x};p' $dirname$@ | sed -n '/"ChunkAddr": "'$host2':9090"/{h;n;/"ChunkAddr":/!{:a;N;/"PartitionId"/!ba;x;H;n};x;H;x};p' | tee -a $chunk_file
 echo "/home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file" | tee -a $logfile
 /home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file
 set_logfile $host
 else
 echo "$chunk_file文件已存在，请检察！" | tee -a $logfile
 exit 1
 fi
 else
 if [ ! -f "$chunk_file" ]; then
 get_time
 sed -n '/"ChunkAddr": "'$host':9090"/{h;n;/"ChunkAddr":/!{:a;N;/"PartitionId"/!ba;x;H;n};x;H;x};p' $dirname$@ | tee -a $chunk_file
 echo "/home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file" | tee -a $logfile
 /home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file
 set_logfile $host
 else
 echo "$chunk_file文件已存在，请检察！" | tee -a $logfile
 exit 1
 fi
 fi
}
# 执行分片迁移任务
run_copy_tasks() {
 while true
 do
 get_tasksum;
 if [ $task_sum -ge 1 ]; then
 if echo $($show_copy_tasks) | grep -q "Copying" ; then
 sleep 30
 else
 $($force_balance)
 fi
 else
 date_now=$(date +"%Y-%m-%d %H:%M:%S")
 cd $dirname && mv ${json_file} ${json_file}-`date +%Y%m%d` && mv ${json_file_b} ${json_file_b}-`date +%Y%m%d`
 echo "============ ${date_now} 分片迁回任务已完成！============" | tee -a $logfile
 break
 fi
 done
}

main() {
 get_tasksum
 if [ $task_sum -lt 1 ]; then
 set_copy_tasks_info "$@"
 sleep 10
 if [ -f "$chunk_file" ]; then
 json_file="$@"
 run_copy_tasks
 else
 get_time
 echo "$json_file文件没有创建成功，请检察！" | tee -a $logfile
 exit 1
 fi
 else
 echo "已经存在迁移任务，请检查！"
 fi
}

main "$@"
```

run_copy_tasks.sh：执行分片迁移

**run_copy_tasks.sh** 展开源码

```bash
#!/bin/bash
dirname="/home/anzhihe/opdir/"
logfile="/home/anzhihe/opdir/mig_rt.log"
show_copy_tasks="/home/anzhihe/rt-table/rt-dashboard/MasterCmd show_copy_tasks"
force_balance="/home/anzhihe/rt-table/rt-dashboard/MasterCmd force_balance offset=0 limit=1"
date_now=$(date +"%Y-%m-%d %H:%M:%S")

get_time() {
 echo -e "\n============ $date_now ============" | tee -a $logfile
}
# 获取迁移分片任务总数
get_tasksum() {
 sum=`/home/anzhihe/rt-table/rt-dashboard/MasterCmd show_copy_tasks |wc -l`
 task_sum=`expr $sum - 3`
}
# 将迁移任务信息记录日志
set_logfile() {
 echo "============ 重启分片迁移任务开始 ============" | tee -a $logfile
 echo $date_now >> $logfile && echo "$($show_copy_tasks)" | tee -a $logfile
}
# 配置分片迁移信息
set_copy_tasks_info() {
 if [ $# -ne 1 ]; then
 echo "Usage: `basename $0` chunk_file"
 exit
 fi
 if [ ! -f "$dirname$@" ]; then
 echo "$@文件不存在请检查！"
 exit
 fi
 host=`basename $1 .json`
 json_file_b=`echo $host"-b.json"`
 chunk_file=`echo "$dirname""$json_file_b"`
 echo $chunk_file
 if [[ "$@" == *_* ]]; then
 host1=`echo $host |awk -F"_" '{ print $1}'`
 host2=`echo $host |awk -F"_" '{ print $2}'`
 if [ ! -f "$chunk_file" ]; then
 get_time
 sed -n '/"ChunkAddr": "'$host1':9090"/{h;n;/"ChunkAddr":/!{:a;N;/"PartitionId"/!ba;x;H;n};x;H;x};p' $dirname$@ | sed -n '/"ChunkAddr": "'$host2':9090"/{h;n;/"ChunkAddr":/!{:a;N;/"PartitionId"/!ba;x;H;n};x;H;x};p' | tee -a $chunk_file
 echo "/home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file" | tee -a $logfile
 #/home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file
 set_logfile $host
 else
 echo "$chunk_file文件已存在，请检察！" | tee -a $logfile
 exit 1
 fi
 else
 if [ ! -f "$chunk_file" ]; then
 get_time
 sed -n '/"ChunkAddr": "'$host':9090"/{h;n;/"ChunkAddr":/!{:a;N;/"PartitionId"/!ba;x;H;n};x;H;x};p' $dirname$@ | tee -a $chunk_file
 echo "/home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file" | tee -a $logfile
 #/home/anzhihe/rt-table/rt-dashboard/trp_distribute set_copy_tasks_info --data-file $chunk_file
 set_logfile $host
 else
 echo "$chunk_file文件已存在，请检察！" | tee -a $logfile
 exit 1
 fi
 fi
}
# 执行分片迁移任务
run_copy_tasks() {
 set_logfile
 while true
 do
 get_tasksum;
 if [ $task_sum -ge 1 ]; then
 if echo $($show_copy_tasks) | grep -q "Copying" ; then
 sleep 30
 else
 $($force_balance)
 fi
 else
 date_now=$(date +"%Y-%m-%d %H:%M:%S")
 #cd $dirname && mv ${json_file} ${json_file}-`date +%Y%m%d` && mv ${json_file_b} ${json_file_b}-`date +%Y%m%d`
 echo "============ ${date_now} 分片迁移任务已完成！============" | tee -a $logfile
 break
 fi
 done
}

main() {
 run_copy_tasks
}

main
```

.bash_profile：polysh调用配置

**bash_profile** 展开源码

```
# ~/.bash_profile
# Get the aliases and functions
if [ -f ~/.bashrc ]; then
 . ~/.bashrc
fi
# User specific environment and startup programs
# User specific environment and startup programs
alias rp='polysh xxx --command="sh /home/anzhihe/opdir/cmdb.sh"'

rt-bj-pub() {
 local host_master=`polysh chegva-rtmaster01.bj01 --command='/home/anzhihe/rt-table/rt-dashboard/MasterCmd host_master | grep -E -o "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}" | grep -v 203.0.113.1'|awk '{ print $3 }'`
 case "$@" in
 "status")
 polysh $host_master --command="/home/anzhihe/rt-table/rt-dashboard/MasterCmd show_copy_tasks"
 ;;
 "stop")
 polysh $host_master --command="/home/anzhihe/rt-table/rt-dashboard/MasterCmd stop_copying_tasks"
 ;;
 "master")
 echo $host_master
 ;;
 *)
 if [[ "$1" == cmd ]]; then
 polysh $2 --user=anzhihe --command="$3"
 elif [[ "$1" == file ]]; then
 polysh $host_master --command="find /home/anzhihe/opdir -name "*.json*" |xargs -n1 basename"
 elif [[ "$1" == run ]]; then
 polysh $host_master --user=root --command="sh /home/anzhihe/opdir/run_copy_tasks.sh"
 elif [[ "$1" == out ]]; then
 host=`echo ${@:2}`
 polysh $host_master --user=root --command="sh /home/anzhihe/opdir/mig_rt_out.sh $host"
 elif [[ "$1" == back ]]; then
 host=`echo ${@:2}`
 polysh $host_master --user=root --command="sh /home/anzhihe/opdir/mig_rt_in.sh $host"
 else
 echo "输入参数有误，请检查后执行！"
 fi
 esac
}

rt-gz-gs() {
 local host_master=`polysh chegva-rtmaster00.gz01 --command='/home/anzhihe/rt-table/rt-dashboard/MasterCmd host_master | grep -E -o "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}" | grep -v 203.0.113.1'|awk '{ print $3 }'`
 case "$@" in
 "status")
 polysh $host_master --command="/home/anzhihe/rt-table/rt-dashboard/MasterCmd show_copy_tasks"
 ;;
 "stop")
 polysh $host_master --command="/home/anzhihe/rt-table/rt-dashboard/MasterCmd stop_copying_tasks"
 ;;
 "master")
 echo $host_master
 ;;
 *)
 if [[ "$1" == cmd ]]; then
 polysh $2 --user=anzhihe --command="$3"
 elif [[ "$1" == file ]]; then
 polysh $host_master --command="find /home/anzhihe/opdir -name "*.json*" |xargs -n1 basename"
 elif [[ "$1" == run ]]; then
 polysh $host_master --user=root --command="sh /home/anzhihe/opdir/run_copy_tasks.sh"
 elif [[ "$1" == out ]]; then
 host=`echo ${@:2}`
 polysh $host_master --user=root --command="sh /home/anzhihe/opdir/mig_rt_out.sh $host"
 elif [[ "$1" == back ]]; then
 host=`echo ${@:2}`
 polysh $host_master --user=root --command="sh /home/anzhihe/opdir/mig_rt_in.sh $host"
 else
 echo "输入参数有误，请检查后执行！"
 fi
 esac
}
#删除所有任务：
#./MasterCmd del_all_copy_tasks
#./MasterCmd stop_copying_tasks
PATH=$PATH:$HOME/bin
export PATH
```

参考：[批量命令工具Polysh推荐](https://chegva.com/3752.html)
