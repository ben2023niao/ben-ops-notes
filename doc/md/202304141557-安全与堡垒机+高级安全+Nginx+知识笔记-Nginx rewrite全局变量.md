---
id: "doc-c5fb46330e2e"
title: "Nginx rewrite全局变量"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Nginx", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68656864.html"
---

# Nginx rewrite全局变量

**[Nginx](https://haicoder.net/nginx/nginx-tutorial.html)** rewrite 常用的全局变量如下：

| 变量 | 说明 |

| --- | --- |

| $args | 存放了请求 url 中的请求指令。比如 `<http://www.myweb.name/server/source?arg1=value1&arg2=value2>` 中的arg1=value1&arg2=value2 |

| $content_length | 存放请求头中的 Content-length 字段 |

| $content_type | 存放了请求头中的 Content-type 字段 |

| $document_root | 存放了针对当前请求的根路径 |

| $document_uri | 请求中的 uri，不包含请求指令 ，比如比如 `<http://www.myweb.name/server/source?arg1=value1&arg2=value2>` 中的 /server/source |

| $host | 存放了请求 url 中的主机字段，比如 `<http://www.myweb.name/server/source?arg1=value1&arg2=value2>` 中的 `[www.myweb.name](http://www.myweb.name)`。如果请求中的主机部分字段不可用或者为空，则存放 nginx 配置中该 server 块中 server_name 指令的配置值 |

| $http_user_agent | 存放客户端的代理 |

| $http_cookie | cookie |

| $limit_rate | nginx 配置中 limit_rate 指令的配置值 |

| $remote_addr | 客户端的地址 |

| $remote_port | 客户端与服务器端建立连接的端口号 |

| $remote_user | 变量中存放了客户端的用户名 |

| $request_body_file | 存放了发给后端服务器的本地文件资源的名称 |

| $request_method | 存放了客户端的请求方式，如 get,post 等 |

| $request_filename | 存放当前请求的资源文件的路径名 |

| $requset_uri | 当前请求的 uri,并且带有指令 |

| $query_string | `$args`含义相同 |

| $scheme | 客户端请求使用的协议，如 http, https, ftp 等 |

| $server_protocol | 客户端请求协议的版本，如 ”HTTP/1.0”, ”HTTP/1.1” |

| $server_addr | 服务器的地址 |

| $server_name | 客户端请求到达的服务器的名称 |

| $server_port | 客户端请求到达的服务器的端口号 |

| $uri | 同 `$document_uri` |
