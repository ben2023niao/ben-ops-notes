---
id: "doc-c8ebefb97961"
title: "利用国外主机使用国内主机 达到免备案"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Docker", "Nginx", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/68649306.html"
---

# 利用国外主机使用国内主机 达到免备案

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BDocker%2BNginx-%E5%88%A9%E7%94%A8%E5%9B%BD%E5%A4%96%E4%B8%BB%E6%9C%BA%E4%BD%BF%E7%94%A8%E5%9B%BD%E5%86%85%E4%B8%BB%E6%9C%BA%20%E8%BE%BE%E5%88%B0%E5%85%8D%E5%A4%87%E6%A1%88.md)

```nginx
条件
需要：国外主机 + 国内主机 + 无备案域名适用：不想备案又想使用国内主机配置以我例子说明
1. 一个腾讯云深圳的主机 2h 4g 5Mbps,2. 一个阿里云香港 1h 1g 30Mbps3. 未备案域名 bughello.cn如果想使用国内主机就必须要备案.这时可以通过海外 反代 国内。nginx 配置
server
{
server_name bughello.cn;
set $proxy_host_ http://203.0.113.1:9091;# 静态资走国内
# 尽管海外主机带宽很大,但是延迟高,国内更快。
rewrite ^/(.*)\.jpg$ $proxy_host_/$1.jpg permanent;
rewrite ^/(.*)\.gif$ $proxy_host_/$1.gif permanent;
rewrite ^/(.*)\.png$ $proxy_host_/$1.png permanent;
rewrite ^/(.*)\.js$ $proxy_host_/$1.js permanent;
rewrite ^/(.*)\.css$ $proxy_host_/$1.css permanent;location / {
proxy_pass $proxy_host_;
}
}

完事
尽量少用阿里云主机作为过墙工具，易封 ip。对于我被封了也无所谓，再买个就好了，docker 运行下镜像，完事。
```
