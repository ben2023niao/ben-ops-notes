---
id: "doc-f2b353d9c6ed"
title: "docker_hub.sh 私有容器镜像仓库管理脚本"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "Docker", "Nginx", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/79927206.html"
---

# docker_hub.sh 私有容器镜像仓库管理脚本

将脚本内容的HUB=203.0.113.1:5000 修改为你的docker镜像仓库的IP

```
#将脚本内容的HUB=203.0.113.1:5000 修改为你的docker镜像仓库的IP
示例：

sh docker_hub.sh -push nginx #推nginx镜像到私有仓库
sh docker_hub.sh -pull nginx #从私有仓库拉nginx镜像
sh docker_hub.sh nginx #从私有仓库查nginx镜像
sh docker_hub.sh -dd nginx #从私有仓库删nginx镜像
```

**docker_hub.sh** 展开源码

```bash
#!/bin/bash
#cnetos7,docker-ce v17.12.0,registry v2.6.2
#Docker registry 私有仓库镜像查询、删除、上传、下载
#root
[[ $UID -ne 0 ]] && { echo "Run in root user !";exit; }
#need jq ,get json data
[[ -f /usr/bin/jq ]] || { echo 'install jq';yum install -y jq &>/dev/null; }
#参数 variable
#registry容器名称,默认registry
RN=${RN:-registry}
#访问网址,默认localhost:5000  请修改HUB信息为私有残仓库IP
HUB=${HUB:-localhost:5000}
HUB=203.0.113.1:5000

#检测 check
function Check_hub() {
[[ `curl -s $HUB/v2/_catalog` == "Failed connect" ]] && { echo -e "\033[31m$HUB 访问失败\033[0m";exit; }
}
#查询images
function Select_img() {
IMG=$(curl -s $HUB/v2/_catalog |jq .repositories |awk -F'"' '{for(i=1;i<=NF;i+=2)$i=""}{print $0}')
[[ $IMG = "" ]] && { echo -e "\033[31m$HUB 没有docker镜像\033[0m";exit; }
#echo "$HUB Docker镜像："
for n in $IMG;
 do
 TAG=$(curl -s http://$HUB/v2/$n/tags/list |jq .tags |awk -F'"' '{for(i=1;i<=NF;i+=2)$i=""}{print $0}')
 for t in $TAG;
 do
 echo "$n:$t";
 done
done
}
#删除images
function Delete_img() {
for n in $IMGS;
do
 IMG=${n%%:*}
 TAG=${n##*:}
 i=1
 [[ "$IMG" == "$TAG" ]] && { TAG=latest; n="$n:latest"; }
 Digest=`curl --header "Accept: application/vnd.docker.distribution.manifest.v2+json" -Is ${HUB}/v2/${IMG}/manifests/${TAG} |awk '/Digest/ {print $NF}'`
 [[ -z "$Digest" ]] && { echo -e "\033[31m$IMG:$TAG  镜像不存在\033[0m";} || {
 URL="${HUB}/v2/${IMG}/manifests/${Digest}"
 Rs=$(curl -Is -X DELETE ${URL%?}|awk '/HTTP/ {print $2}')
 [[ $Rs -eq 202 ]] && { let i++;echo "$n  删除成功"; } || { echo -e "\033[31m$n  删除失败\033[0m"; } }
done
#registry垃圾回收 RN=registry
[[ "$i" -gt 1 ]] && { echo "Clean...";docker exec ${RN} /bin/registry garbage-collect /etc/docker/registry/config.yml &>/dev/null;docker restart ${RN} &>/dev/null; }
}
#删除镜像所在目录(清除所有 -dd .* )
#简单高效,删库跑路，必备技能
function Delete_img_a() {
[[ -f /usr/bin/docker ]] || echo 'No docker !'
[[ -z $(docker ps |awk '/'$RN'/ {print $NF}') ]] && { echo "$RN容器不存在!";exit; }
for n in $IMGS;
do
 IMG="${n%%:*}"
 docker exec $RN rm -rf /var/lib/registry/docker/registry/v2/repositories/$IMG
done
echo '清理 Clean ...'
docker exec $RN bin/registry garbage-collect /etc/docker/registry/config.yml &>/dev/null
docker restart $RN &>/dev/null
}
#上传 push
function Push() {
for IMG in $IMGS;
do
 echo -e "\033[33m docker push $IMG to $HUB \033[0m"
 docker tag $IMG $HUB/$IMG
 docker push $HUB/$IMG
 docker rmi $HUB/$IMG &>/dev/null
done
}
#下载 pull
function Pull() {
for IMG in $IMGS;
do
 echo -e "\033[33m dokcer pull $IMG from $HUB \033[0m"
 docker pull $HUB/$IMG
 docker tag $HUB/$IMG $IMG
 docker rmi $HUB/$IMG &>/dev/null
done
}
case "$1" in
 "-h")
 echo
 echo "#默认查询images"
 echo "sh $0 -h #帮助 -d #删除 -dd #清理空间"
 echo "    -pull img1 img2 #下载 -push #上传"
 echo
 echo "#示例：删除 nginx:1.1 nginx:1.2 (镜像名:版本)"
 echo "sh $0 -d nginx:1.1 nginx:1.2 "
 echo "sh $0 -dd nginx #删除nginx所有版本"
 echo
 echo "#定义仓库url地址hub.test.com:5000(默认 localhost:5000)"
 echo "env HUB=hub.test.com:5000 /bin/sh $0 -d nginx:1.1 "
 echo
;;
 "-d")
 Check_hub
 IMGS=${*/-dd/}
 IMGS=${IMGS/-d/}
 Delete_img
;;
 "-dd")
 Check_hub
 IMGS=${*/-dd/}
 IMGS=${IMGS/-d/}
 Delete_img_a
;;
 "-pull")
 IMGS=${*/-pull/}
 Pull
;;
 "-push")
 IMGS=${*/-push/}
 Push
;;
 *)
 Check_hub
 Select_img
;;
esac
```
