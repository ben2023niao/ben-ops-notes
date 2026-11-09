---
id: "doc-2f01999fb5bd"
title: "测试 H5/PC 静态资源日本 Nginx 启动失败修复"
date: "2026-08-05T16:15:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Nginx", "自动化", "DNS", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-05_1615-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E6%A0%B9%E5%9B%A0%E6%B1%87%E6%80%BB%E3%80%91%E6%B5%8B%E8%AF%95H5-PC%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E6%97%A5%E6%9C%ACNginx%E5%90%AF%E5%8A%A8%E5%A4%B1%E8%B4%A5%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-05_1615-【修复Bug+根因汇总】测试H5-PC静态资源日本Nginx启动失败修复.md"
sourceSha256: "56a4f18660b8691ad7db26e0c0bc1d0f563cbed89f70a687202f1fad946cbb73"
sourceSystem: "project-doc"
---

# 测试 H5/PC 静态资源日本 Nginx 启动失败修复

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608051615-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-%E6%B5%8B%E8%AF%95%20H5-PC%20%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E6%97%A5%E6%9C%AC%20Nginx%20%E5%90%AF%E5%8A%A8%E5%A4%B1%E8%B4%A5%E4%BF%AE%E5%A4%8D.md)

> 整理日期：2026-08-05 16:15｜日期依据：文件名日期

环境标签：测试环境、H5、PC、前端静态资源、腾讯 COS、日本 Nginx、Nginx 启动修复

时间：2026-08-05 16:15

## 一、问题现象

用户反馈测试环境 H5/PC 又出现静态资源异常，浏览器 F12 大量报错：

- `ERR_CONNECTION_REFUSED`
- `ERR_CONNECTION_CLOSED`

主要失败域名：

- `https://test-h5-s3.hbbfuub.cn/...`
- `https://test-pc-s3.hbbfuub.cn/...`

页面入口本身可以返回 HTML，但 CSS、JS、图片等 `_nuxt/images` 静态资源加载失败，页面表现为样式和图片缺失。

## 二、排查结果

### 1. 页面入口正常

以下页面入口验证 200：

```text
test-h5.hbbfuub.cn
test-h5.hbakjja.cn
pc.youdianse-test.xyz
test-pc.hbbfuub.cn
test-pc.hbakjja.cn
```

说明测试前端页面服务器 `38.92.8.34` 没有整体故障。

### 2. 静态资源域名解析正常

```text
test-h5-s3.hbbfuub.cn -> 138.252.248.139
test-pc-s3.hbbfuub.cn -> 138.252.248.139
```

DNS 关系正确，仍然指向日本 Nginx 静态资源反代机。

### 3. 日本 Nginx 80/443 未监听

外部探测：

```text
138.252.248.139:80   Connection refused
138.252.248.139:443  Connection refused
138.252.248.139:38927 SSH 正常
```

登录服务器后确认：

```text
nginx.service = failed
80/443 未监听
```

### 4. 根因

Nginx 上一次启动失败日志：

```text
host not found in upstream "admin.youdianse.com"
in /etc/nginx/conf.d/10-youdianse-preprod-frontends.conf
```

配置中原来存在：

```nginx
proxy_pass https://admin.youdianse.com;
```

Nginx 会在启动阶段解析这种写法里的域名；当时 `admin.youdianse.com` 解析失败，导致整份 Nginx 配置启动失败。由于静态资源反代和线上前置页面配置在同一个 Nginx 服务里，结果是 80/443 整体没有监听，测试 H5/PC 静态资源也被一起拖停。

## 三、修复操作

### 1. 恢复服务

已执行：

```text
systemctl start nginx
```

恢复后：

```text
nginx.service = active
80/443 已监听
```

### 2. 加固远端 Nginx 配置

已备份：

```text
/etc/nginx/conf.d/10-youdianse-preprod-frontends.conf.bak.avoid_dns_boot_fail_20260805_081116
```

已将 H5/PC 两处 API 反代从启动期解析改为运行时解析：

```nginx
set $admin_origin admin.youdianse.com;
proxy_pass https://$admin_origin;
proxy_ssl_server_name on;
proxy_ssl_name $admin_origin;
proxy_set_header Host admin.youdianse.com;
```

效果：

- Nginx 启动阶段不再因为 `admin.youdianse.com` 一次解析失败而整服务失败。
- 请求真正打到 `/api`、`/channel`、`/customer` 时才按 resolver 解析上游。
- 静态资源反代不会再被该 API 上游 DNS 抖动连带拖停。

### 3. 同步 ben-bot 模板

已同步修改：

```text
devops/python/ben-bot/data/scripts/线上前置-游点涩-前端配置/nginx/youdianse-preprod-frontends.conf
```

同步范围：

- 本地仓库模板
- ben-bot 宿主机模板
- ben-bot 容器内模板

避免以后重新部署模板时把旧风险写法覆盖回去。

## 四、验证结果

### 1. Nginx 重启验证

```text
nginx -t                  通过
systemctl restart nginx   通过
nginx.service             enabled + active
80/443                    正常监听
```

### 2. 静态资源域名验证

以下域名 `version.txt` 均返回 `200 + CORS:* + no-store`：

```text
test-h5-s3.hbbfuub.cn
test-pc-s3.hbbfuub.cn
main-h5-s3.hbakjja.cn
main-pc-s3.hbakjja.cn
test-h5-s3.hbabaxb.cn
test-pc-s3.hbabaxb.cn
test-h5-s3.hbazuua.cn
test-pc-s3.hbazuua.cn
```

### 3. 页面真实引用抽样

已从以下页面 HTML 提取真实静态资源引用，每个页面抽 12 个资源：

```text
h5.youdianse-test.xyz       refs=87  sample_ok=12  sample_fail=0
test-h5.hbbfuub.cn          refs=87  sample_ok=12  sample_fail=0
test-h5.hbakjja.cn          refs=87  sample_ok=12  sample_fail=0
pc.youdianse-test.xyz       refs=92  sample_ok=12  sample_fail=0
test-pc.hbbfuub.cn          refs=92  sample_ok=12  sample_fail=0
test-pc.hbakjja.cn          refs=92  sample_ok=12  sample_fail=0
```

### 4. CSS / 图片抽样

```text
https://test-h5-s3.hbbfuub.cn/images/index-new/main-game.svg  HTTP/2 200  image/svg+xml  CORS:*
https://test-h5-s3.hbbfuub.cn/_nuxt/entry.9fJ8Knpu.css       HTTP/2 200  text/css       CORS:*
https://test-pc-s3.hbbfuub.cn/images/index-new/main-game.svg  HTTP/2 200  image/svg+xml  CORS:*
https://test-pc-s3.hbbfuub.cn/_nuxt/entry.Btel_iqu.css        HTTP/2 200  text/css       CORS:*
```

## 五、核心原因总结

这次不是 COS 文件丢失，也不是 CORS 配置再次坏掉。

核心原因是：日本 Nginx 静态资源反代服务因为线上前置 API 上游域名 `admin.youdianse.com` 在启动时解析失败，导致整个 Nginx 服务 failed，80/443 没有监听。测试 H5/PC 静态资源域名都指向这台日本 Nginx，所以浏览器看到大量 `ERR_CONNECTION_REFUSED` 和 `ERR_CONNECTION_CLOSED`。

已修复为运行时解析，降低后续同类 DNS 短抖把整台静态资源反代拖停的风险。

## 六、当前结论

- 测试 H5/PC 页面入口正常。
- 测试 H5/PC 静态资源域名已恢复。
- 日本 Nginx 已通过完整 restart 验证。
- 本地、ben-bot 宿主机、ben-bot 容器内模板已同步修复。
- 本次未改 DNS，未改 COS 桶策略，未触发 H5/PC 重新发布。
