---
id: "doc-340402b96881"
title: "Nginx应对网站扫描/攻击/采集方法"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "DNS", "Nginx", "Apache", "PHP", "Java", "SQL注入"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68656872.html"
---

# Nginx应对网站扫描/攻击/采集方法

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2BDNS%2BNginx-Nginx%E5%BA%94%E5%AF%B9%E7%BD%91%E7%AB%99%E6%89%AB%E6%8F%8F-%E6%94%BB%E5%87%BB-%E9%87%87%E9%9B%86%E6%96%B9%E6%B3%95.md)

```nginx
#禁垃圾蜘蛛
if ($http_user_agent ~* "CheckMarkNetwork|Synapse|Bingbot|Googlebot|Nimbostratus-Bot|Dark|scraper|LMAO|Hakai|Gemini|Wappalyzer|masscan|crawler4j|Mappy|Center|eright|aiohttp|MauiBot|Crawler|researchscan|Dispatch|AlphaBot|Census|ips-agent|NetcraftSurveyAgent|ToutiaoSpider|EasyHttp|Iframely|sysscan|fasthttp|muhstik|DeuSu|mstshash|HTTP_Request|ExtLinksBot|package|SafeDNSBot|CPython|SiteExplorer|SSH|MegaIndex|BUbiNG|CCBot|NetTrack|Digincore|aiHitBot|SurdotlyBot|null|SemrushBot|Test|Copied|ltx71|Nmap|DotBot|AdsBot|InetURL|Pcore-HTTP|PocketParser|Wotbox|newspaper|DnyzBot|redback|PiplBot|SMTBot|WinHTTP|Auto Spider 1.0|GrabNet|TurnitinBot|Go-Ahead-Got-It|Download Demon|Go!Zilla|GetWeb!|GetRight|libwww-perl|Cliqzbot|MailChimp|SMTBot|Dataprovider|XoviBot|linkdexbot|SeznamBot|Qwantify|spbot|evc-batch|zgrab|Go-http-client|FeedDemon|JikeSpider|Indy Library|Alexa Toolbar|AskTbFXTV|AhrefsBot|CrawlDaddy|CoolpadWebkit|Java|UniversalFeedParser|ApacheBench|Microsoft URL Control|Swiftbot|ZmEu|jaunty|Python-urllib|lightDeckReports Bot|YYSpider|DigExt|HttpClient|MJ12bot|EasouSpider|LinkpadBot|Ezooms|YoudaoBot|YandexBot|Rogerbot|exabot|ia_archiver|Teoma|gigabot|DOCOMO Sprider|AhrefsBot|SemrushBot|Sosospider|Yahoo! Slurp China|Yahoo! Slurp|MSNBot|MSNot-media|FlightDeckReports Bot|Bytespider|Mail.RU_Bot") {
return 403;
break;
}#禁攻击采集
if ($http_user_agent ~* "FeedDemon|BOT/0.1 (BOT for JCE)|CrawlDaddy|Java|Jullo|Feedly|UniversalFeedParser|ApacheBench") {
return 403;
break;
}
#UA 不全，十有八九不是正常访问，禁
if ($http_user_agent = "Mozilla") {
return 403;
break;
}
#UA 不全，十有八九不是正常访问，禁
if ($http_user_agent = "Mozilla/5\.0") {
return 403;
break;
}
#UA 不全，十有八九不是正常访问，禁
if ($http_user_agent = "Mozilla/4\.0") {
return 403;
break;
}
#禁空 UA
if (http_user_agent ~* ^http_user_agent ~* ^http_user_agent ~* ^) {
return 403;
  break;
}
#过滤url参数
set $URL $request_uri;
if ($URL ~* "member|plus|base|data|dede|public|plug|Vote|tool|feed|components|skin|tinyMCE|version|sysimage|wp-content|wp-admin|static|common|face|shell|swfupload|utility|convert|sitemap|siteserver|BackupDB|file|user|system|upimg|install|wap|multiupload|ewebeditor|office|wallet|backup|bitcoin|maccms|vendor|apply|bjebhgm|photo|module|external|Analytics|tools|subdomains|notes|md5|ckeditor|bbs|ajax|zhuitanyun|logbaak|help|weki|dxyylc|Somnus|manage|J4H7eFjWoBa3bO6U|SiteFiles|dowds|source|ucenter|phpcms|language|TeatchClass|taglib|sql|allowurl|shitan|root|wp-login|houtai|admin001|htadmin|clock2|webadmin"){
return 403;
break;
}
#禁特殊后缀
location ~* \.(asp|xml|jsp|aspx|dev|aspx|ewebeditor|sql|xsl|asmx|htaccess|ini|env|git|project|cgi|md5|ajax.js|swf|tpl.php)$ {
return 403;
break;
}
#禁止非GET方式的抓取
if ($request_method !~ ^(GET)$) {
return 403;
}
#禁止特殊请求方式
if ($request_method ~* "HEAD|DELETE|OPTIONS|POST" ) {
return 403;
break;
}
#禁特殊请求工具
if ($http_user_agent ~* "Wget|Curl" ) {
return 403;
break;
}
#禁部分爬取工具
if ($http_user_agent ~* "crawl|curb|git|Wtrace|Scrapy|python|http://www.snsbianpofanghu.com/" ) {
return 403;
break;
}
#禁压缩包
location ~* \.(tgz|bak|zip|rar|tar|gz|bz2|xz|tar.gz)$ {
return 403;
break;
}
#屏蔽ip
deny 203.0.113.1/24;
deny 203.0.113.1/16;
deny 203.0.113.1;
#限制指定蜘蛛访问频次
limit_req_zone $anti_spider zone=one:100m rate=30r/m;
limit_req zone=one burst=5 nodelay;

server
{
if ($http_user_agent ~* "Sogou web spider|YisouSpider") {
set $anti_spider $http_user_agent;
}
#限制所有ip访问频次

limit_req_zone $binary_remote_addr zone=allips:100m rate=30r/m;
limit_req zone=allips burst=5 nodelay;
```
