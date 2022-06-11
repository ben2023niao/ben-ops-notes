---
id: "doc-d2572e1ad26e"
title: "nginx-install.sh"
date: "2022-06-11T17:03:02.188000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Shell", "Nginx", "区块链", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/nginx-install.sh.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "ac50ada402e23d8b88ce0451ac39cff2813604dff0947003afceb0861ae4da70"
---

# nginx-install.sh

> 原文：[nginx-install.sh](https://xn--6o0a585a.gitbook.io/devops/fu-wu/nginx-install.sh.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 17:03｜日期依据：GitBook 页面更新时间

```bash
#!/bin/bash

dir=/home/data
nginx_download_path="http://nginx.org/download/nginx-1.15.7.tar.gz"
nginx_install_dir="/usr/local/nginx"
nginx_name="nginx-1.15.7.tar.gz"

[ -f /etc/init.d/functions ] && . /etc/init.d/functions || exit 1

# create file download dir
create_dir(){
  if [ ! -e $dir ]
    then
      mkdir $dir
  else
    echo "file download dir is exit!"
  fi
}

# install nginx-1.15.7
install_nginx(){
  # yum install something
  yum install -y wget
  wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-6.repo
  yum install -y pcre pcre-devel openssl openssl-devel gcc make gcc-c++
  # download nginx
  [ -e $dir ] && cd $dir
  wget $nginx_download_path
  if [ -f $nginx_name ]
    then
      echo 'nginx download success'
      # tar nginx
      tar zxf $nginx_name && cd nginx-1.15.7
      # add user nginx
      useradd nginx -s /sbin/nologin -M
      # install nginx
      ./configure --user=nginx --group=nginx --prefix=/usr/local/nginx --with-http_stub_status_module --with-http_ssl_module --with-stream --with-stream_ssl_module --with-http_v2_module --with-threads
      [ $(echo $?) -eq 0 ] && make && make install
      [ $(echo $?) -eq 0 ] && echo "nginx install success"
  fi
}
# start nginx
start_nginx(){
 # check syntax
 $nginx_install_dir/sbin/nginx -t
 # start
 if [ $(echo $?) -eq 0 ]
   then
     $nginx_install_dir/sbin/nginx
     if [ $(netstat -lutnp|grep 80|wc -l) -eq 1 ]
       then
         action "nginx starting success..."  /bin/true
     else
         echo "nginx starting fail,plaese check the service!"
     fi
 fi
}

# main function
main(){
   #create dir
   create_dir
   # install
   install_nginx
   sleep 3
   # start
   start_nginx
   sleep 2
}
main
```
