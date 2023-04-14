---
id: "doc-faa70248d7e0"
title: "HTTP GET与POST对比"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "PHP", "CSRF", "日志分析", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68657199.html"
---

# HTTP GET与POST对比

## HTTP GET与POST对比

**[HTTP](https://haicoder.net/http/http-tutorial.html)** 中的 **[GET](https://haicoder.net/http/http-get.html)** 一般用于获取/查询资源信息，也就是从指定的资源请求数据。 而 **[POST](https://haicoder.net/http/http-post.html)** 一般用于向指定的资源提交要被处理的数据，也就是更新资源信息。

## GET与POST比较

下面的表格比较了两种 HTTP 方法：GET 和 POST。

|  | GET | POST |

| --- | --- | --- |

| 后退按钮/刷新 | 无害 | 数据会被重新提交（浏览器应该告知用户数据会被重新提交） |

| 书签 | 可收藏为书签 | 不可收藏为书签 |

| 缓存 | 能被缓存 | 不能缓存 |

| 编码类型 | application/x-www-form-urlencoded | application/x-www-form-urlencoded 或 multipart/form-data。为二进制数据使用多重编码。 |

| 历史 | 参数保留在浏览器历史中。 | 参数不会保存在浏览器历史中。 |

| 对数据长度的限制 | 是的。当发送数据时，GET 方法向 URL 添加数据；URL 的长度是受限制的（URL 的最大长度是 2048 个字符） | 无限制 |

| 对数据类型的限制 | 只允许 ASCII 字符 | 没有限制，也允许二进制数据 |

| 安全性 | 与 POST 相比，GET 的安全性较差，因为所发送的数据是 URL 的一部分。在发送密码或其他敏感信息时绝不要使用 GET | POST 比 GET 更安全，因为参数不会被保存在浏览器历史或 web 服务器日志中 |

| 可见性 | 数据在 URL 中对所有人都是可见的 | 数据不会显示在 URL 中 |

## GET和POST的区别

GET 请求的数据会附在 URL 之后（就是把数据放置在 HTTP 协议头中），以 `?` 分割 URL 和传输数据，参数之间以 `&` 相连，如：

`login.action?name=hyddd&password=[已脱敏]`

如果数据是英文字母或数字，则原样发送；如果是空格，转换为 `+`；如果是中文或其他字符，则直接把字符串用 BASE64 加密，得出如：%E4%BD%A0%E5%A5%BD，其中 ％XX 中的 XX 为该符号以 16 进制表示的 ASCII 码值。而与之对应的，POST 把提交的数据放置在 HTTP 包的包体中。

POST 的安全性要比 GET 的安全性高。注意：这里所说的安全性和上面 GET 提到的 “安全” 不是同个概念。上面 “安全” 的含义仅仅是不作数据修改，而这里安全的含义是真正的 Security 的含义。比如：通过 GET 提交数据，用户名和密码将明文出现在 URL 上，因为：(1)登录页面有可能被浏览器缓存，(2)其他人查看浏览器的历史纪录，那么别人就可以拿到你的账号和密码了，除此之外，使用 GET 提交数据还可能会造成 Cross-site request forgery 攻击（CSRF,跨站请求伪造，也被称为：one click attack/session riding）。

银行网站A，它以GET请求来完成银行转账的操作，如：`<http://www.mybank.com/Transfer.php?toBankId=11&money=1000>`
危险网站B，它里面有一段HTML的代码如下：`< img src=<http://www.mybank.com/Transfer.php?toBankId=11&money=1000/>>`

首先，你登录了银行网站 A，然后访问危险网站 B，噢，这时你会发现你的银行账户少了 1000 块。

为什么会这样呢？原因是银行网站 A 违反了 HTTP 规范，使用 GET 请求更新资源。在访问危险网站 B 之前，你已经登录了银行网站 A，而 B 中的 `<img …/>` 以 GET 的方式请求第三方资源（这里的第三方就是指银行网站 A 了。原本这是一个合法的请求，但这里被不法分子利用了），所以你的浏览器会带上你的银行网站 A 的 **Cookie** 发出 Get 请求，去获取资源 `“<http://www.mybank.com/Transfer.php?toBankId=11&money=1000>”`，结果银行网站服务器收到请求后，认为这是一个更新资源操作（转账操作），所以就立刻进行转账操作。

为了杜绝上面的问题，银行改用 POST 请求完成转账操作。

## GET和POST的误区

误区一：POST 可以比 GET 提交更多更长的数据？

由于使用 GET 方法提交数据时，数据会以 `&` 符号作为分隔符的形式，在 URL 后面添加需要提交的参数，有人会说，浏览器地址栏输入的参数是有限的，而 POST 不用再地址栏输入，所以 POST 就比 GET 可以提交更多的数据。难道真的是这样的么？

而实际上，URL 不存在参数上限的问题，HTTP 协议规范没有对 URL 长度进行限制。这个限制是特定的浏览器及服务器对它的限制。IE 对 URL 长度的限制是 2083 字节(2K+35)。对于其他浏览器，如 Netscape、FireFox 等，理论上没有长度限制，其限制取决于操作系统的支持。所以 POST 也是没有大小长度限制的，HTTP 协议规范也没有进行大小限制。起限制作用的是服务器的处理能力。总归一句话，这个限制是针对所有 HTTP 请求的，与 GET、POST 没有多少关系。

## GET和POST区别总结

1. GET 使用 URL 或 Cookie 传参，而 POST 将数据放在 BODY 中，这个是因为 HTTP 协议用法的约定。并非它们的本身区别。
2. GET 方式提交的数据有长度限制，则 POST 的数据则可以非常大，这个是因为它们使用的操作系统和浏览器设置的不同引起的区别。也不是 GET 和 POST 本身的区别。
3. POST 比 GET 安全，因为数据在地址栏上不可见，这个说法没毛病，但依然不是 GET 和 POST 本身的区别。
