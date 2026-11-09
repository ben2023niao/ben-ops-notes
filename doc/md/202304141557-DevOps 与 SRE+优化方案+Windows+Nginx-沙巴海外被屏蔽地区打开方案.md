---
id: "doc-fbf85301c156"
title: "沙巴海外被屏蔽地区打开方案"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Windows", "Nginx", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/79921761.html"
---

# 沙巴海外被屏蔽地区打开方案

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BWindows%2BNginx-%E6%B2%99%E5%B7%B4%E6%B5%B7%E5%A4%96%E8%A2%AB%E5%B1%8F%E8%94%BD%E5%9C%B0%E5%8C%BA%E6%89%93%E5%BC%80%E6%96%B9%E6%A1%88.md)

1 外网VDI登录 <https://cloud.google.com/> 制作模板服务器
![文档配图](../media/9c38f8e84c84ba7e1f.png)
![文档配图](../media/e265996d7f4d440548.png)![文档配图](../media/49fecc5eaff6fd1bba.png)

2 克隆 shaba-proxy-02 模块服务器 选择 日本地区 部署

![文档配图](../media/6d1ee833ea3b22bd34.png)
![文档配图](../media/73ac681d4ffb5ae10d.png)![文档配图](../media/24ce7cf7133e28c5e3.png)
![文档配图](../media/474d84842d88f977fc.png)

3 创建负载均衡器

![文档配图](../media/fcf6913c12bede0fb8.png)
![文档配图](../media/d3d858b46af341ec46.png)

![文档配图](../media/3cb655eb4b131fb19e.png)

![文档配图](../media/2e70c3d6caab933d6f.png)
![文档配图](../media/f121f701bdd0a11ee3.png)

![文档配图](../media/a303f6d0c8d8290d76.png)

![文档配图](../media/4d23272b1f679b63cd.png)

![文档配图](../media/295939e970c9a673d7.png)
![文档配图](../media/006158b05442361dc2.png)

4 域名加 * 的A记录解析到新部署的 SLB 负载均衡节点 IP
![文档配图](../media/dbd8cef00393619517.png)

5 外租机添加Jump [Jenkins (bstops.com)](https://sabdt-jenkins.bstops.com/job/外租机添加Jump/build?delay=0sec)
添加前

![文档配图](../media/07fc1eb496d71354f3.png)
![文档配图](../media/6526bf645952b38ccf.png)
 8     | a04-shaba-proxy-jp-02                                                                         | 203.0.113.1                            | 日本地区节点
![文档配图](../media/9f3ed5d8299c069ee4.png)

6 登录服务器 修改一下默认 nginx 配置的域名 和 证书就是  （更换域名 或者 加域名教程演示）
![文档配图](../media/c9e5b3b02911626cc1.png)

7 测试
curl -v -I --referer 302.xxx.com --user-agent 'Chrome/54.0 (Windows NT 10.0)' [https://www.](https://www.$1)[xxx.com](http://xxx.com)
