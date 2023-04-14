---
id: "doc-0ea210be06c3"
title: "Nginx解决跨域方案一"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Nginx", "CORS", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/68656782.html"
---

# Nginx解决跨域方案一

## 什么是跨域

跨域是前端开发中经常会遇到的问题，前端调用后台服务时，通常会遇到 No ‘Access-Control-Allow-Origin’ header is present on the requested resource 的错误，这是因为浏览器的同源策略拒绝了我们的请求。

所谓同源是指，域名，协议，端口相同，浏览器执行一个脚本时同源的脚本才会被执行。如果非同源，那么在请求数据时，浏览器会在控制台中报一个异常，提示拒绝访问。这个问题我们通常会使用 CORS(跨源资源共享)或者 JSONP 去解决，这两种方法也是使用较多的方法。

### 解决跨域

这个使用**[Nginx](https://haicoder.net/nginx/nginx-tutorial.html)**的代理功能即可，在 a 服务器的 Nginx 添加如下示例配置：

```nginx
location ~ /xxx/ {
 proxy_pass http://b.com;
}
```

这样就把路径中带有 /xxx/ 的请求都转到了 [b.com](http://b.com)。如果不需要保存 cookie，保持 session 这样的功能，这样就可以了。

然而，本项目就是要用到 cookie，所以就有了下边的内容。

### 设置domain

因为 cookie 当中是有 domain 的，两个服务器的一般不同，比如 a 服务器返回的 Response Headers 中是

`Set-Cookie:JSESSIONID=_3y4u02v4cbpBw10DoCrMSnjg7m34xuum1XRWBF1Uno; path=/; domain=a.com`

而 b 服务器返回的是

`Set-Cookie:JSESSIONID=_3y4u02v4cbpBw10DoCrMSnjg7m34xuum1XRWBF1Uno; path=/; domain=b.com`

这时候如果 a 项目的页面调用了 b 的接口，浏览器发现接口返回的 domain 不是 [a.com](http://a.com)，就不会把 cookie 保存起来，session 也就失效了。Nginx 引入了 proxy_cookie_domain 来解决这个问题。示例：

```nginx
location ~ /xxx/ {
 proxy_cookie_domain b.com a.com;
 proxy_pass http://b.com;
}
```

这样就可以在 Nginx 转接请求的时候自动把 domain 中的 [b.com](http://b.com) 转换成 [a.com](http://a.com)，这样 cookie 就可以设置成功了。

但是，对于有些情况这样转换不灵光。比如，b 项目的 domain 是 .[b.com](http://b.com)，前边多了一个小点，那对应的改为 proxy_cookie_domain .[b.com](http://b.com) [a.com](http://a.com); 可以不？通过实践，不行！！！

通过查看 Nginx 文档，找到了解决办法。其实，除了上边那种配置方式外，Nginx 还支持正则配置：

```nginx
location ~ /xxx/ {
 proxy_cookie_domain ~\.?b.com a.com;
 proxy_pass http://b.com;
}
```

这样就可以把 domain 中的 .[b.com](http://b.com) 转换成 [a.com](http://a.com) 啦。

### 设置path

正常情况下完成以上两步就可以了，因为 cookie 中的 path 一般默认的是 path=/，也就是所有请求都可以访问本 cookie。但有些服务器会指定，只允许某个层级下的请求可以访问 cookie，比如：

`Set-Cookie:JSESSIONID=_3y4u02v4cbpBw10DoCrMSnjg7m34xuum1XRWBF1Uno; path=/sub/; domain=b.com`

这样就只允许相对根路径，以 /sub/ 开头的请求路径才能访问 cookie。这时候就又可能出现 cookie 无效的问题了，为了解决这个问题，可以使用 proxy_cookie_path。示例：

```nginx
location ~ /xxx/ {
 proxy_cookie_domain ~\.?b.com a.com;
 proxy_cookie_path /sub/ /;
 proxy_pass http://b.com;
}
```

这样就把只允许 /sub/ 层级下的请求访问 cookie，改为允许所有请求访问 cookie 了。
