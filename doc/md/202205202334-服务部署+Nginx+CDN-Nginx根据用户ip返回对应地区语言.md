---
id: "doc-3291c1c52d55"
title: "Nginx根据用户ip返回对应地区语言"
date: "2022-05-20T23:34:09.522000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Nginx", "CDN"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/nginx/nginx-gen-ju-yong-hu-ip-fan-hui-dui-ying-di-qu-yu-yan.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "bf49cbeb18b331c3ac2ca20823f5f22e6cffa5e966b3a11239b733b4db21e25a"
---

# Nginx根据用户ip返回对应地区语言

> 原文：[Nginx根据用户ip返回对应地区语言](https://xn--6o0a585a.gitbook.io/devops/fu-wu/nginx/nginx-gen-ju-yong-hu-ip-fan-hui-dui-ying-di-qu-yu-yan.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-05-20 23:34｜日期依据：GitBook 页面更新时间

1 Nginx 编译进 geoip2 模块后更改主配置 http 部分 （geoip2 比geoip 更优秀）

```
    #Nginx 编译进geoip模块后在主配置http内添加
    #开启CDN后获取访客真实IP地址
    set_real_ip_from 203.0.113.1/0;
    real_ip_header X-Forwarded-For;
    ## GEOIP2 国家
    geoip2 /usr/share/GeoIP/GeoLite2-Country.mmdb {
          $geoip2_Country_code country iso_code;
    }
    ## GEOIP2 城市
    geoip2 /usr/share/GeoIP/GeoLite2-City.mmdb {
          $geoip2_City_code country iso_code;
    }
    # 好单独为 城市级别 单独设置
```

2 域名的nginx 配置内添加负载均衡配置

```
upstream ben {
    ip_hash;
    server 203.0.113.1 weight=1 max_fails=2 fail_timeout=2s;
    server 203.0.113.1 weight=2 max_fails=2 fail_timeout=2s;
    server 203.0.113.1 weight=2 max_fails=2 fail_timeout=2s;
}
```

3 伪静态内写 ip 地区转化对应语言逻辑

4 然后前端就能感觉到用户语言 lang 了
