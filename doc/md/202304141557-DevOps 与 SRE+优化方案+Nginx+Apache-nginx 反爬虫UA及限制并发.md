---
id: "doc-1da036fb9f84"
title: "nginx 反爬虫UA及限制并发"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Nginx", "Apache", "Java", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/72057038.html"
---

# nginx 反爬虫UA及限制并发

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BNginx%2BApache-nginx%20%E5%8F%8D%E7%88%AC%E8%99%ABUA%E5%8F%8A%E9%99%90%E5%88%B6%E5%B9%B6%E5%8F%91.md)

处理请求头文件agent-deny.conf

 展开源码

```c
#禁止境内常见爬虫(根据需求自行控制是否禁止)
if ($http_user_agent ~* "qihoobot|Yahoo! Slurp China|Baiduspider|Baiduspider-image|spider|Sogou spider|Sogou web spider|Sogou inst spider|Sogou spider2|Sogou blog|Sogou News Spider|Sogou Orion spider|ChinasoSpider|Sosospider|YoudaoBot|yisouspider|EasouSpider|Tomato Bot|Scooter") {
return 403;
}
#禁止境外常见爬虫(根据需求自行控制是否禁止)
if ($http_user_agent ~* "Googlebot|Googlebot-Mobile|AdsBot-Google|Googlebot-Image|Mediapartners-Google|Adsbot-Google|Feedfetcher-Google|Yahoo! Slurp|MSNBot|Catall Spider|ArchitextSpider|AcoiRobot|Applebot|Bingbot|Discordbot|Twitterbot|facebookexternalhit|ia_archiver|LinkedInBot|Naverbot|Pinterestbot|seznambot|Slurp|teoma|TelegramBot|Yandex|Yeti|Infoseek|Lycos|Gulliver|Fast|Grabber") {
return 403;
}
#禁止指定 UA 及 UA 为空的访问
if ($http_user_agent ~ "WinHttp|WebZIP|FetchURL|node-superagent|java/|Bytespider|FeedDemon|Jullo|JikeSpider|Indy Library|Alexa Toolbar|AskTbFXTV|AhrefsBot|CrawlDaddy|CoolpadWebkit|Java|Feedly|Apache-HttpAsyncClient|UniversalFeedParser|ApacheBench|Microsoft URL Control|Swiftbot|ZmEu|oBot|jaunty|Python-urllib|lightDeckReports Bot|YYSpider|DigExt|HttpClient|MJ12bot|heritrix|Ezooms|BOT/0.1|YandexBot|FlightDeckReports|Linguee Bot|iaskspider|^$") {
return 403;
}
#禁止非 GET|HEAD|POST 方式的抓取
if ($request_method !~ ^(GET|HEAD|POST)$) {
return 403;
}
#禁止 Scrapy 等工具的抓取
#if ($http_user_agent ~* (Python|Java|Wget|Scrapy|Curl|HttpClient|Spider|PostmanRuntime)) {
if ($http_user_agent ~* (Scrapy|HttpClient)) {
return 403;
}
#屏蔽IP地址
#deny 203.0.113.1
#慎用-封IP段(203.0.113.1-203.0.113.1)
#deny 203.0.113.1/8
#慎用-封IP段(203.0.113.1-203.0.113.1)
#deny 203.0.113.1/16
#慎用-封IP段(203.0.113.1-203.0.113.1)
#deny 203.0.113.1/24
#使用说明：在网站 xxx.conf 相关配置中的 server 段插入如下代码：
#include agent_deny.conf;
```

nginx.conf引入agent_deny.conf

 展开源码

```nginx
http {
#....
#引入限制爬虫UA配置文件
include agent_deny.conf;
#....
location =/robots.txt {# 爬虫规则说明，没有啥实际作用
default_type text/html;
add_header Content-Type "text/plain; charset=UTF-8";
return 200 "User-agent: *\nDisallow: /";
 }
}
```

nginx.conf添加限制并发控制

 展开源码

```nginx
http {
#....
#漏桶算法
#客户端IP限制并发连接数
limit_conn_zone $binary_remote_addr zone=conip:10m;
#客户端IP限制请求频率，每秒10次
limit_req_zone $binary_remote_addr zone=reqip:10m rate=10r/s;
location / {
limit_conn conip 2;
limit_req zone=reqip burst=20 nodelay;
#        limit_rate 512k;# 限制客户端下载速率
#        ...
#        #allow 203.0.113.1/24; #仅允许局域网IP段访问
#        #deny all; # 拒绝所有IP
#        proxy_set_header Host $host;
#        proxy_set_header X-Real-IP $remote_addr;
#        proxy_set_header REMOTE-HOST $remote_addr;
#        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 }
#....
}
```

重启nginx服务后，校验是否拦截爬虫UA

```bash
curl -I -A '' www.test.com
curl -X GET -I -A 'YYSpider' www.test.com
curl -X GET -I -A 'Baiduspider' www.test.com
```
