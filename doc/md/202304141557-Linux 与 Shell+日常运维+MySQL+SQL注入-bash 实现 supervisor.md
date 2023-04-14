---
id: "doc-d1a7e99d6c6a"
title: "bash 实现 supervisor"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "MySQL", "SQL注入", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/66979847.html"
---

# bash 实现 supervisor

## 需求描述

1、实现一个脚本工具，该脚本提供类似 supervisor 功能，可以对进程进行管理

2、一键查看所有进程运行状态

3、单个或批量启动进程，单个或批量停止进程

4、提供进程分组功能，可以按组查看进行运行状态，可以按组启动或停止该组内所有进程

查看服务器所有进程脚本 app_status.sh

配置文件 process.cfg

扩展：

1、启动服务器进程脚本 app_start.sh

2、停止服务器进程脚本 app_stop.sh

## [#](https://www.wjsljc.com/document/shell/case/app/#拆分脚本功能，抽象函数)拆分脚本功能，抽象函数

1、function get_all_group 返回进程组列表字符串

2、function get_all_process 返回进程名称列表字符串

3、function get_process_info 返回进程详细信息列表字符串，详细信息包括：运行状态、PID、CPU、MEM、启动时间

```
注：该函数可以接收一个参数，参数为进程名称
```

4、function get_all_process_by_group 返回进程组内的所有进程名称列表字符串

例子：DB 组--> "mysql postgresql oracle"

## [#](https://www.wjsljc.com/document/shell/case/app/#功能函数)功能函数

### [#](https://www.wjsljc.com/document/shell/case/app/#get-all-group)get_all_group

返回进程组列表字符串

```bash
#!/bin/bash
#
# Func: Get Porcess Status In process.cfg
# Define Variables
HOME_DIR="/Users/lijinchao/mySelf/code/shell/case/app"
CONFIG_FILE="process.cfg"
this_pid=$$ # 表示脚本运行时本身会生成一个子进程，$$表示它的pid
function get_all_group() {
 G_LIST=$(sed -n "/^\[GROUP_LIST\]/,/^\[.*\]/p" process.cfg | egrep -v "(^$|\[.*\])")
 echo $G_LIST
 # 如不用egrep而使用grep等价如下写法
 # sed -n "/^\[GROUP_LIST\]/,/^\[.*\]/p" process.cfg | grep -v "^$" | grep -v "\[.*\]"
 # sed -n "/^\[GROUP_LIST\]/,/^\[.*\]/p" process.cfg | grep -vE "^$|\[.*\]"
}
#for g in $(get_all_group); do
 #echo $g
#done
```

### [#](https://www.wjsljc.com/document/shell/case/app/#get-all-process)get_all_process

返回进程名称列表字符串

```
function get_all_process() {
 for g in $(get_all_group); do
 P_LIST+=$(sed -n "/^\[$g\]/,/^\[.*\]/p" $HOME_DIR/$CONFIG_FILE | egrep -v "(^$|\[.*\])")
 P_LIST+=" " # ngin和macos可能不同，根据实际情况决定需不需要这行
 done
 echo $P_LIST
}
```

### [#](https://www.wjsljc.com/document/shell/case/app/#get-process-info)get_process_info

返回进程详细信息列表字符串，详细信息包括：运行状态、PID、CPU、MEM、启动时间

get_process_info 分为两个函数 get_process_pid_by_name（通过名称获取 pid）和 get_process_info_by_pid（通过 pid 获取信息）

```
function get_process_pid_by_name() {
 # $#表示参数个数
 if [ $# -ne 1 ]; then
 return 1
 else
 # $0代表脚本本身
 pids=$(ps -ef | grep $1 | grep -v grep | grep -v $0 | awk '{print $2}')
 echo $pids
 fi
}
# get_process_pid_by_name node
function get_process_info_by_pid() {
 # 使用awk而非grep是因为精准过滤$2(pid)相等的值,过滤其他位置可能出现相等的值的干扰
 # wc -l 表示统计返回信息的行数
 if [ $(ps -ef | awk -v pid=$1 '$2==pid{print }' | wc -l) -eq 1 ]; then
 pro_status="RUNNING"
 else
 pro_status="STOPED"
 fi
 pro_cpu=$(ps aux | awk -v pid=$1 '$2==pid{print $3}') # 第三列是CPU占用率
 pro_mem=$(ps aux | awk -v pid=$1 '$2==pid{print $4}') # 第四列是内存占用率
 pro_start_time=$(ps -p $1 -o lstart | grep -v STARTED) # ps -p $1 -o lstart 获取详细pid启动时间
}
# get_process_info_by_pid 8975
# echo "$pro_status $pro_cpu $pro_mem $pro_start_time"
```

### [#](https://www.wjsljc.com/document/shell/case/app/#get-all-process-by-group)get_all_process_by_group

返回进程组内的所有进程名称列表字符串

get_process_info 分为两个函数 is_group_in_config（判断 group 是否存在）和 get_all_process_by_group（通过 group 名称列表字符串）

```
function get_all_process_by_group() {
 is_group_in_config $1
 if [ $? -eq 0 ]; then
 p_list=$(sed -n "/\[$1\]/,/\[.*\]/p" $HOME_DIR/$CONFIG_FILE | egrep -v "(^$|^#|\[.*\])")
 echo $p_list
 else
 echo "GroupName $1 is not in process.cfg"
 fi
}
function is_group_in_config() {
 for gn in $(get_all_group); do
 if [ $gn == $1 ]; then
 return # 正常返回
 fi
 done
 return 1
}
# get_all_process_by_group WEB
```
