---
id: "doc-7ce75d9d392b"
title: "create_git_repo_wbt_v2.sh"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "CVE", "漏洞", "备份恢复", "CVE-2014-6271", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/create_git_repo_wbt_v2.sh_68649431.html"
---

# create_git_repo_wbt_v2.sh

```
# -gt：大于，greater than。-eq：等于，equal。-lt：小于，less than。-ge：大于等于，greater than or equal。-le：小于等于，less than or equal。-ne：不等于，not equal。
#全局变量
TIME2=$(date +%Y%m%d_%H%M%S)
function check_bash() {#判断系统bash是否安全
env bash
if  test "$?" -eq "0"
then
    echo "system have bash"
    env x='() { :;}; echo "CVE-2014-6271 系统存在bash破壳漏洞 !!!"' bash -c "echo 系统bash无破壳漏洞 "
    if test "$SHELL" -ne '/bin/bash' ; then echo "请切换到 bash 解释器来执行 $0 " ; exit ; fi #不是 bash 就退出
else
    echo "system no bash"
    exit 1
fi
}
unset -f check_bash

fucntion check_user_tomcat() { #判断tomcat用户
# if [ ! $1 ]; then $1='tomcat' fi    #没有$1传入就设置默认用户为tomcat
# local u=$1                                 #全局外部变量转换为函数内部变量隔离开更安全
if test "$USER" -eq "tomcat"
then
    echo "当前用户是 $u"
else
    echo "当前用户不是 $u"
    exit 1
fi
# unset -v u                                    #释放函数内部函数
}
unset -f check_user_tomcat

function init_work() { #一次性创建好工作目录
local CP=$1
local ROLE=$2
if test "$#" -ne "2"
then
    echo "Usage:$0 \$1=product \$2=role" #判断脚本参数
    exit 1
fi

cat << EOF > "$init_dir_conf"
/web/${CP}/${ROLE}/WebRoot
/web/git_data/repo/
/web/git_data/release/
/web/git_data/test/
/bak/gitupdate/
/bak/gitupdate/exclude_files/
EOF
local d
for d in `cat $init_dir_conf`; do mkdir -p $d ; done
unset -v d

#备份
[ -d /web/${CP}/${ROLE} ] && mv /web/${CP}/${ROLE} /web/${CP}/${ROLE}-$TIME2
[ -d /web/git_data/repo/${CP}/${ROLE} ] && mv /web/git_data/repo/${CP}_${ROLE}.git /web/git_data/repo/${CP}_${ROLE}.git-$TIME2
#初始化
cd /web/${CP}/${ROLE}
env git || echo "请安装 git"
git init
cat << EOF > .gitignore
.svn
.htaccess
EOF
git add . && git commit -am "${CP} ${ROLE} repo shaw"
#写入隔离文件
cat > /bak/gitupdate/exclude_files/excludefile_${CP}_${ROLE} << EOF
*.svn*
*.git*
EOF
cd /web/git_data/repo/
git clone --bare /web/${CP}/${ROLE} ${CP}_${ROLE}.git
cd ${CP}_${ROLE}.git/hooks
cp post-update.sample post-update
git update-server-info

#打版本标签
cd /web/git_data/repo/${CP}_${ROLE}.git
local V=$(git log | grep 'commit' | awk '{print $2}' | cut -c '1-7')
echo "$V" > /web/git_data/release/${CP}_${ROLE}
echo "$V" > /web/git_data/release/${CP}_${ROLE}_pre
echo "$V" > /web/git_data/test/${CP}_${ROLE}
echo "$V" > /web/git_data/test/${CP}_${ROLE}_pre
echo "$V 版本已刷新"
unset -v V

#生成项目脚本
cd /bak/gitupdate/
cat << EOF > "/bak/gitupdate/${CP}_${ROLE}.sh"
ltype=`tr '[A-Z]' '[a-z]'<<< ${ROLE}`
remote="${CP}"_"${ROLE}"
local="/web/${CP}/${ROLE}/WebRoot"
workdir=/web
## rsync argv
exfile=/bak/gitupdate/exclude_files/excludefile_${CP}"_"${ROLE}
passfile=/bak/gitupdate/rsync.password
. /bak/gitupdate/public_functions
EOF
#检查生成的脚本 语法
bash -n /bak/gitupdate/${CP}_${ROLE}.sh
#chmod +x /bak/gitupdate/${CP}_${ROLE}.sh
#显示生成的文件
echo "/bak/gitupdate/${CP}_${ROLE}.sh"
cat /bak/gitupdate/${CP}_${ROLE}.sh
echo "/bak/gitupdate/exclude_files/excludefile_${CP}_${ROLE}"
cat /bak/gitupdate/exclude_files/excludefile_${CP}_${ROLE}
}
unset -f init_work

####

. /bak/gitupdate/public_functions  改造中...
```
