---
id: "doc-bf387621de72"
title: "nginx log 正则分析"
date: "2021-12-21T15:59:07.581000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Shell", "Nginx"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/nginx/nginx-log-zheng-ze-fen-xi.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "ad40734fbc2b85676b26635b92a62edf66f8e07d7210008837f1ec5ea3b98f35"
---

# nginx log 正则分析

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202112211559-%E6%9C%8D%E5%8A%A1%E9%83%A8%E7%BD%B2%2BShell%2BNginx-nginx%20log%20%E6%AD%A3%E5%88%99%E5%88%86%E6%9E%90.md)

> 原文：[nginx log 正则分析](https://xn--6o0a585a.gitbook.io/devops/fu-wu/nginx/nginx-log-zheng-ze-fen-xi.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-21 15:59｜日期依据：GitBook 页面更新时间

```
echo "完整请求链路统计"
awk -F ',' '{a["客户ip："$3" =>"$6" ["$4"] ""{"$7"}"" 耗时:"$10" <=upstream=> 后端响应:"$28"["$25"]"" {"$29"}"" 耗时:"$34" =>"$1 ]++}END{for(i in a)print a[i],i|"uniq|sort -k1 -nr|head -n10"}' lbhyapi.log

echo "后端响应次数统计"
awk -F ',' '{a[" =>"$6" ["$4"] ""{"$7"}"" <=upstream=> 后端响应:"$28"["$25"]"" {"$29"}" ]++}END{for(i in a)print a[i],i|"uniq|sort -k1 -nr|head -n10"}' lbhyapi.log

echo "接口耗时统计"
awk -F ',' '{a[" =>"$6" ["$4"] ""{"$7"}"" 耗时:"$10" <=upstream=> 后端响应:"$28"["$25"]"" {"$29"}"" 耗时:"$34 ]++}END{for(i in a)print a[i],i|"uniq|sort -k1 -nr|head -n10"}' lbhyapi.log
```
