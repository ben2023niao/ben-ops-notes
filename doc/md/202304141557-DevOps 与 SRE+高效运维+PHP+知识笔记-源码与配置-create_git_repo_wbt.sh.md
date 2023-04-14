---
id: "doc-8cbbd98a39f1"
title: "create_git_repo_wbt.sh"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "PHP", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/create_git_repo_wbt.sh_68649428.html"
---

# create_git_repo_wbt.sh

```bash
#!/bin/bash
[ $(id -u) != "1000" ] && { echo "Error: You must be use tomcat to run this script!" && exit 1; }
[ $# -ne 2 ] && { echo "Usage:$0 \$1=product \$2=role" && exit; }
## def var
CP=$1
ROLE=$2
TIME2=$(date +%Y%m%d_%H%M%S)
## init repo
echo "==========init repo=========="
read -p "Please sure rm -rf /web/${CP}/${ROLE} (n/y)": DEL
[[ "$DEL" == "y" || -z "$DEL" ]] && {
[ -d /web/${CP}/${ROLE} ] && mv /web/${CP}/${ROLE} /web/${CP}/${ROLE}-$TIME2
#rm -rf /web/${CP}/${ROLE}
mkdir -p /web/${CP}/${ROLE}/WebRoot
cd /web/${CP}/${ROLE} && git init
echo '.svn' > .gitignore
echo '.htaccess' >> .gitignore
git add .
git commit -am "${CP} ${ROLE} repo shaw"
echo
echo
}
## chou luo repo
echo "==========chou luo repo=========="
read -p "Please sure rm -rf /web/git_data/repo/${CP}_${ROLE}.git (n/y)": DEL
[[ "$DEL" == "y" || -z "$DEL" ]] && {
cd /web/git_data/repo/
mv ${CP}_${ROLE}.git ${CP}_${ROLE}.git-$TIME2
#rm -rf ${CP}_${ROLE}.git
git clone --bare /web/${CP}/${ROLE} ${CP}_${ROLE}.git
cd ${CP}_${ROLE}.git/hooks
\cp post-update.sample post-update
git update-server-info
echo
echo
}
## init reop and luo reop establish relations
echo "==========init repo and luo repo establish relations=========="
cd /web/${CP}/${ROLE}/
git remote add origin /web/git_data/repo/${CP}_${ROLE}.git
git push --set-upstream origin master
git remote -v
echo
echo
## version numbers write to file
echo "==========version numbers write to file=========="
cd /web/git_data/repo/${CP}_${ROLE}.git
V=$(git log | grep 'commit' | awk '{print $2}' | cut -c '1-7')
echo "$V" > /web/git_data/release/${CP}_${ROLE}
echo "$V" > /web/git_data/release/${CP}_${ROLE}_pre
echo "$V" > /web/git_data/test/${CP}_${ROLE}
echo "$V" > /web/git_data/test/${CP}_${ROLE}_pre
echo $V
echo
echo
## create update scripts and filter file
echo "==========create update scripts and filter file=========="
cd /bak/gitupdate/
\cp create_template_mode ${CP}_${ROLE}.sh
sed -i "s@production=A01@production=${CP}@g" ${CP}_${ROLE}.sh
sed -i "s@type='webphp'@type=\'${ROLE}\'@g" ${CP}_${ROLE}.sh
chmod +x ${CP}_${ROLE}.sh

cat > /bak/gitupdate/exclude_files/excludefile_${CP}_${ROLE} << EOF
*.svn*
*.git*
EOF
echo "/bak/gitupdate/${CP}_${ROLE}.sh"
echo "/bak/gitupdate/exclude_files/excludefile_${CP}_${ROLE}"
cat /bak/gitupdate/exclude_files/excludefile_${CP}_${ROLE}
echo
echo
## pull code
echo "==========pull code=========="
/bin/bash ${CP}_${ROLE}.sh
```
