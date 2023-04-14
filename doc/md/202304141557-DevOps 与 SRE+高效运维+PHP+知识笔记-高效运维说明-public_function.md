---
id: "doc-a88d3c2429ca"
title: "public_function"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "PHP", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/public_function_68649517.html"
---

# public_function

```bash
[tomcat@ph190svr002191 gitupdate]$ cat create_template_mode
#!/bin/bash
[ $(id -u) != "1000" ] && { echo "Error: You must be use tomcat to run this script!" && exit 1; }
## common var
production=A01
type='webphp'
ltype=`tr '[A-Z]' '[a-z]'<<< $type`
remote="$production"_"$type"
local="/web/$production/$type/WebRoot"
workdir=/web

## rsync argv
exfile=/bak/gitupdate/exclude_files/excludefile_${production}"_"${type}
passfile=/bak/gitupdate/rsync.password

. /bak/gitupdate/public_functions
[tomcat@ph190svr002191 gitupdate]$ cat public
Display all 172 possibilities? (y or n)
[tomcat@ph190svr002191 gitupdate]$ cat public_functions
#!/bin/bash
## common argv
GREEN_COLOR='\E[1;32m'
RED_COLOR='\E[1;31m'
RES='\E[0m'
comment="$production $type update use script on $(date +%Y%m%d_%H%M%S_%w)"
comment2="$production $type update WMS use script on $(date +%Y%m%d_%H%M%S_%w)"
comment3="$production $type git push file use script on $(date +%Y%m%d_%H%M%S_%w)"
## rsync argv
IP=203.0.113.1
rsync_home=/usr/bin/rsync
exfile2=/bak/gitupdate/exclude_files/includefile_${production}"_"${type}
if [ -n "$type" ];then
if [ ${type} = 'neptune-group-sports' ];then
vfile=$production"-"$type
else
vfile=$production"_"$type
fi
else
vfile=$production
fi
echo -ne "${GREEN_COLOR}===============即将开启新的人生,请享受!!!==============${RES}\n"
method="upgrade"
echo "升级请输入 :upgrade"
echo "版本回退请输入:rollback 请输入:"
read -p "(Please input u or r):" method

case "$method" in
upgrade|update|u|1)
echo "你将进行升级操作"
echo
method="upgrade"
;;

rolback|rollback|r|2)
echo "你将进行回退操作"
method="rollback"
;;

*)
echo "未选择或选择错误,程序退出"
exit 1
;;
esac
## head version numbers
VERNUMBER()
{
echo "==================$production $type:前10个版本号=================="
cd $workdir/$production/$type
git log --pretty=oneline -10 --pretty=format:"%h %s"
echo
}

wms_diff()
{
echo
echo -e "${GREEN_COLOR}=================${production} ${type} WMS 对比差异文件 112 and 204=================${RES}"

> /tmp/${production}_${type}_wms_diff.txt
${rsync_home} --no-motd -anrcL --out-format=%n%L --delete --files-from=${exfile2} --exclude "/*" --password-file=${passfile} files@${IP}::$remote $local | egrep -v '^./|/$|cannot delete non-empty' > /tmp/${production}_${type}_wms_diff.txt

NUM1=$(wc -l /tmp/${production}_${type}_wms_diff.txt | awk '{print $1}')
[ $NUM1 -eq 0 ] && { echo "NO find WMS different" && exit; } || cat /tmp/${production}_${type}_wms_diff.txt

echo
echo
echo -ne "${RED_COLOR}对比差异后,是否继续,please input (y|n): ${RES}"
read RR
[[ $RR != "y" ]] && exit
echo
}

wms_rsync()
{
echo -e "${GREEN_COLOR}================${production} ${type} WMS 正在获取代码 from 112 to 204================${RES}"
${rsync_home} --no-motd -arvczSH --out-format=%n%L --delete --files-from=${exfile2} --exclude "/*" --password-file=${passfile} files@${IP}::$remote $local | egrep -v '/$'
cd ${workdir}/${production}/${type} && git add . && git commit -am "$comment2" && git push
echo -e "${GREEN_COLOR}================${production} ${type} WMS 成功获取代码 from 112 to 204================${RES}"
echo
}
function diff()
{
echo
echo -ne "${GREEN_COLOR}====================${production} ${type} 对比差异文件 112 and 204====================${RES}\n"
#NUM1=$(${rsync_home} --no-motd -ancL --out-format=%n%L --delete --exclude-from=${exfile} --password-file=${passfile} files@${IP}::$remote $local | egrep -v '^./|/$' | wc -l)
#[ $NUM1 -eq 0 ] && echo "NO find different" && exit
#${rsync_home} --no-motd -ancL --out-format=%n%L --delete --exclude-from=${exfile} --password-file=${passfile} files@${IP}::$remote $local | egrep -v '^./|/$'

> /tmp/${production}_${type}_diff.txt

${rsync_home} --no-motd -ancL --out-format=%n%L --delete --exclude-from=${exfile} --password-file=${passfile} files@${IP}::$remote $local | egrep -v '^./|/$|cannot delete non-empty' > /tmp/${production}_${type}_diff.txt

NUM1=$(wc -l /tmp/${production}_${type}_diff.txt | awk '{print $1}')
[ $NUM1 -eq 0 ] && { echo "NO find different" && exit; } || cat /tmp/${production}_${type}_diff.txt

echo
echo -ne "${RED_COLOR}对比差异后,是否继续,please input (y|n): ${RES}"
read RR
#read -p "${RED_COLOR}对比差异后,是否继续,please input (y|n): " RR
[[ $RR != "y" ]] && exit
echo
}
function rsync()
{
echo -ne "${GREEN_COLOR}====================${production} ${type} 正在获取代码 from 112 to 204====================${RES}\n"
${rsync_home} --delete -avczSHL --exclude-from=${exfile} --password-file=${passfile} files@${IP}::$remote $local | grep -v /$
if [[ "${production}" == "A04" && "${type}" == "frontend_web" ]]; then
/bin/sh /bak/gitupdate/cdn_replace.sh
fi
# if [[ "${production}" == "A04" && "${type}" == "webapi" ]]; then
# /usr/local/php/bin/php /web/A04/webapi/WebRoot/artisan app:wsdl > /tmp/1.txt
# cat /tmp/1.txt
# echo "fcuk you"
# sleep 20
# fi
cd ${workdir}/${production}/${type} && git add . && git commit -am "$comment" && git push

echo -ne "${GREEN_COLOR}====================${production} ${type} 成功获取代码 from 112 to 204====================${RES}\n"
echo
}
function huanjing()
{
echo "请选择操作环境:"
echo -ne "\033[31;5m""1、生产环境\n""\033[0m"
echo "2、测试环境"
read -p "(请选择):" environment

case "$environment" in
1)
echo
echo
echo -ne "${RED_COLOR}========================你正在对""\033[31;5m""生产环境进行操作=====================${RES}\n"
environment="release"
verdir="/web/git_data/release"
;;
2)
echo -ne "${GREEN_COLOR}========================你正在对测试环境进行操作=====================${RES}\n"
environment="test"
verdir="/web/git_data/test"
;;

*)
echo -ne "${RED_COLOR}=======================未选择或选择错误,程序退出=====================${RES}\n"
exit 1
;;
esac
}
function ver()
{
newver=$(cd $workdir/$production/$type && git log -1 | head -1 | awk '{print $2}' | cut -c 1-7)
curver=$(cat $verdir/$vfile)
prever=$(cat $verdir/$vfile"_pre")
}
function upgrade()
{
if [[ "$curver" == "$newver" ]];then
echo -e "${GREEN_COLOR}当前版本与线上版本一致:$curver ${RES}"
else
echo -e "${GREEN_COLOR}即将从版本:$curver 更新到:$newver ${RES}"
echo -e "${GREEN_COLOR}异动文件列表: ${RES}"
cd $workdir/$production/$type && git --no-pager diff --name-only $curver $newver
echo -e "${RED_COLOR}以上文件将会被覆盖,请确认y/n: ${RES}"
read -p "(Please input y or n):" confirm
case "$confirm" in
y|Y|Yes|YES|yes|yES|yEs|YeS|yeS)
echo $curver > $verdir/$vfile"_pre"
echo $newver > $verdir/$vfile
echo -e "${GREEN_COLOR}已成功更新至版本:$newver ${RES}"
;;

n|N|No|NO|no|nO)
echo -e "${GREEN_COLOR}未对线上版本作出改动,目前线上版本为:$curver ${RES}"
;;

*)
echo -e "${GREEN_COLOR}未对线上版本作出改动,目前线上版本为:$curver ${RES}"
;;
esac
fi
}
#SHAW
function rollback()
{
if [ $curver = $prever ];then
echo -ne "${GREEN_COLOR}当前版本与线上版本一致:$curver ${RES}\n"
else
#echo "即将从版本:$curver 回退到:$prever ${RES}\n"
#echo "请确认y/n:"
echo -ne "${RED_COLOR}即将进行版本回退,请确认: ${RES}\n"
#read -p "(Please input y or n):" confirm
echo -ne "${RED_COLOR}(Please input y or n): ${RES}"
read confirm
case "$confirm" in
y|Y|Yes|YES|yes|yES|yEs|YeS|yeS)
#read -p "(Please 输入想回滚的版本号,默认是上一个版本号):" VERSION
echo -ne "${RED_COLOR}(Please 输入想回滚的版本号,默认是上一个版本号):${RES}"
read VERSION

if [ -z "$VERSION" ];then
VERSION=$prever
else
if [ $(echo ${#VERSION}) -lt 7 ];then
echo -ne "${RED_COLOR}输入的版本号长度至少为7位${RES}\n"
exit
else
VERSION=$(echo "$VERSION" | cut -c 1-7)
fi
fi
echo $VERSION
cd $workdir/$production/$type
dangqian=$(git log --oneline -1 | awk '{print $1}')
git reset --hard $VERSION
git reset $newver
git add .
git commit -am "from $dangqian rollback to $VERSION"
git push

rollbackver=$(git log -1 --pretty=oneline | awk '{print $1}' | cut -c 1-7)
if [ $(git --no-pager diff --name-only $rollbackver $VERSION | wc -l) -eq 0 ];then
echo "$VERSION" > $verdir/$vfile"_pre"
echo "$rollbackver" > $verdir/$vfile
echo
echo
echo -e "${GREEN_COLOR}from $dangqian rollback to $VERSION ${RES}"
echo -ne "${GREEN_COLOR}已成功回退至版本:${VERSION}${RES}\n"
else
echo -ne "${RED_COLOR}回退至版本:${VERSION}失败${RES}\n"
git --no-pager diff --name-only $rollbackver $VERSION
exit
fi
;;

n|N|No|NO|no|nO)
echo -ne "${GREEN_COLOR}未对线上版本作出改动,目前线上版本为:$curver ${RES}\n"
exit
;;

*)
echo -ne "${GREEN_COLOR}未对线上版本作出改动,目前线上版本为:$curver ${RES}\n"
exit
esac
fi
}
echo $verdir
if [ $method = "upgrade" ];then
echo -ne "${GREEN_COLOR}====================================================================${RES}\n"
echo "是否从远程服务器获取最新代码:"
echo "1、获取"
echo "2、不获取"
read -p "请选择1/2:" confirm
case "$confirm" in
y|Y|Yes|YES|yes|yES|yEs|YeS|yeS|1)
echo
# if [[ "${type}" == "webphp" || "${type}" == "webmobile" || "${type}" == "slot" || "${type}" == "webphp_new" || "${type}" == "webmobile_slot" || "${type}" == "webmobile_new" ]];then
if [[ "${type}" =~ "webphp"* || "${type}" =~ "webmobile"* || "${type}" == "slot" || "${type}" == "frontend_mobile" || "${type}" =~ "frontend_web"* ||"${type}" =~ "frontend_mobile"* ||"${type}" = "agent" ]];then
echo -ne "${GREEN_COLOR}是否升级WMS代码,please input (y|n):${RES}"
read UU
if [[ $UU == "y" ]];then
wms_diff
wms_rsync
else
diff
rsync
fi
else
diff
rsync
fi
;;

*)
echo
echo -ne "${GREEN_COLOR}=====================跳过从远程获取代码==============================${RES}\n"
cd $workdir/$production/$type && git add . && git commit -am "${comment3}" && git push
echo
;;
esac

huanjing
ver
upgrade

elif [ $method = "rollback" ];then
echo -ne "${GREEN_COLOR}====================================================================${RES}\n"
huanjing
ver
rollback

else
echo -ne "${RED_COLOR}=====================================================================${RES}\n"
fi
[tomcat@ph190svr002191 gitupdate]$
```
