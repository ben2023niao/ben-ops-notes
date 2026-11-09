---
id: "doc-c14c5058d206"
title: "health 心跳加个密码 和 IP 限制 更安全方案"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Nginx", "权限管理", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/66980002.html"
---

# health 心跳加个密码 和 IP 限制 更安全方案

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BNginx%2B%E6%9D%83%E9%99%90%E7%AE%A1%E7%90%86-health%20%E5%BF%83%E8%B7%B3%E5%8A%A0%E4%B8%AA%E5%AF%86%E7%A0%81%20%E5%92%8C%20IP%20%E9%99%90%E5%88%B6%20%E6%9B%B4%E5%AE%89%E5%85%A8%E6%96%B9%E6%A1%88.md)

health 加个密码 和 IP 限制 更安全

参考源文 <https://zzzmh.cn/single?id=71>

## 需求

如题，Swagger-UI页面需要加权限验证拦截，但又不想搞太麻烦，于事就决定用Nginx的指定URL权限验证，来实现拦截swagger-ui.html

## 实现

以Centos为例

```bash
# 安装工具
yum -y install httpd

# 创建密码
htpasswd -c /etc/nginx/passwd admin
# 然后根据提示输入两次密码
New password:
[已脱敏] new password:
# 结束后在/etc/nginx/目录下就多了一个passwd文件
```

修改配置文件
`/etc/nginx/nginx.conf`

```nginx
# 修改Nginx配置 加上这一段即可
location /swagger-ui.html {
 auth_basic "There place don't have three hundred silver in here.";
 auth_basic_user_file /etc/nginx/passwd;
 # 下面这段根据自己情况配置
 proxy_pass http://localhost:8080/service/swagger-ui.html;
 proxy_set_header Host $host;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header X-Forwarded-Proto https;
 proxy_connect_timeout 30;
 proxy_read_timeout 30;
 proxy_send_timeout 30;

 access_log off;
 break;
}
# 要是觉得还不保险，再加一个IP限制
location /swagger-ui.html {
 # 代表IP4位全部对上才允许访问
 allow 203.0.113.1;
 # 代表IP前两位能对上就允许访问(用于某些运营商公网IP后两位经常变更)
 allow 203.0.113.1/16;
 deny all;
 ......
}
```

## END
