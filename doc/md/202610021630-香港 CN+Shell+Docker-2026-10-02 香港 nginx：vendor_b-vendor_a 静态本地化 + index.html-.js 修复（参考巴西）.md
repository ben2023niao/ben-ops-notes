---
id: "doc-f84889d5e225"
title: "2026-10-02 香港 nginx：vendor_b/vendor_a 静态本地化 + index.html/.js 修复（参考巴西）"
date: "2026-10-02T16:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Shell", "Docker", "Nginx", "监控告警", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-10-02-1630-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AFnginx%E7%9A%84vendor_b-vendor_a%E9%9D%99%E6%80%81%E6%9C%AC%E5%9C%B0%E5%8C%96%E4%B8%8Eindex-js%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-10-02-1630-【架构改造】香港nginx的vendor_b-vendor_a静态本地化与index-js修复.md"
sourceSha256: "0e0cf71f839a60fcf66f59862e106843fecc3785f8bddda8721c8eabc244d9c7"
sourceSystem: "project-doc"
---

# 2026-10-02 香港 nginx：vendor_b/vendor_a 静态本地化 + index.html/.js 修复（参考巴西）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/cn/docker/doc/2026-10-02-1630-【架构改造】香港nginx的vendor_b-vendor_a静态本地化与index-js修复.md`

> 整理日期：2026-10-02 16:30｜日期依据：文件名日期

## 一、需求

```text
用户：① 备份目前香港 nginx 这台服务器上的配置；
     ② 参考巴西处理 vendor_a 的 index.html 的方式，处理香港 nginx 上 vendor_b/vendor_a 的同类问题：
          root /data/static/vendor_astatic2;
          index  index.html index.htm index.php;
          location ~* \.js$ { default_type application/javascript;
                              add_header Content-Type "application/javascript; charset=utf-8"; }
本轮按要求不发送飞机群通知。
```

## 二、配置备份（已完成）

```text
· standby（192.0.2.37，本轮操作的香港 nginx）：/root/nginx-config-backup-20261002.tgz（/etc/nginx 全量）
  → 已同步入仓：docker/deploy/hongkong/nginx-backup/nginx-standby-etc-nginx-20261002.tgz
· 逐步备份（同目录 /etc/nginx/sites-available/）：
  *.bak-20260925-0155 / -0204、-20260926-0321、-20260930-m4q7z1 / -speedtest、
  -20261002-k8x2v9 / -p3w9n5、本轮的 -20261002-vendor_b-static
· 老入口机（192.0.2.14）的 /etc/nginx 也打包在 /root/nginx-config-backup-20261002.tgz
```

## 三、问题定位

```text
vendor_b/vendor_a 的静态资源原来是 S3 直出（vendor_b-static* → bizops-s3-vendor_b-static*）：
· 目录请求（/xxx/）拿不到 index.html，游戏启动页进不去；
· 部分 .js 的 Content-Type 不是 application/javascript，浏览器拒绝执行 → 游戏卡住；
· 且 bizops-s3-vendor_b-static 桶里基本只有 favicon.ico（555B），真实内容不在 HK/大阪的新桶里，
  真正的 vendor_a 静态内容在巴西的公开 GCS 桶（newgg2-bizops-gcs-vendor_a-statics{,1,2}）。
巴西线上是宝塔 nginx 直接把 vendor_a 静态放在本地目录（/data/static/vendor_astatic2）再对外，
本轮把香港对齐成同样的做法。
```

## 四、实施

### 4.1 把 vendor_a/vendor_b 静态内容拉到香港 nginx 本地

```text
· standby 上安装 rclone（v1.75.1），配置匿名 GCS remote：
    /root/.config/rclone/rclone.conf  ->  [gcs-public] type = google cloud storage / anonymous = true
· 拉取脚本 /root/pull-vendor_astatic.sh（nohup 后台执行），日志 /root/vendor_astatic-sync.log：
    rclone copy gcs-public:newgg2-bizops-gcs-vendor_a-statics  /data/static/vendor_astatic
    rclone copy gcs-public:newgg2-bizops-gcs-vendor_a-statics1 /data/static/vendor_astatic1
    rclone copy gcs-public:newgg2-bizops-gcs-vendor_a-statics2 /data/static/vendor_astatic2
· 数据量：vendor_a-statics 2.095 GiB / 17,992 对象；vendor_a-statics1 597 MiB；vendor_a-statics2 194 MiB / 1,083 对象
· 本轮结束时仍在后台拉取（vendor_astatic 已 700MB+），完成后可用下面命令核对：
    rclone check gcs-public:newgg2-bizops-gcs-vendor_a-statics /data/static/vendor_astatic --size-only
    du -sh /data/static/*
```

### 4.2 nginx 配置（standby）

```text
新增两段（放在 m4q7z1 / k8x2v9 通用静态块**之前**，nginx 正则 server_name 取首个匹配）：
  map $host $bizops_vendor_b_static_root  -> /data/static/vendor_astatic{,1,2}
  map $host $bizops_vendor_b_s3_prefix    -> bizops-s3-vendor_b-static{,1,2}（本地没有时的兜底）
  server {
      server_name ~^vendor_b-static[0-9]?\.(m4q7z1|k8x2v9)\.shop$;
      root $bizops_vendor_b_static_root;
      index index.html index.htm;
      location ~* \.js$ { default_type application/javascript;
                          add_header Content-Type "application/javascript; charset=utf-8"; try_files $uri @vendor_b_s3; }
      location / { ...OPTIONS 204...; try_files $uri $uri/ @vendor_b_s3; }
      location @vendor_b_s3 { resolver 192.0.2.2 192.0.2.31; ... proxy_pass https://$bizops_vendor_b_s3_prefix.s3...; }
  }
说明：本地有就本地直出（含目录 -> index.html、.js 正确 MIME）；本地没有的路径仍回源原大阪桶，
     行为与改造前一致，保证切换期不回归。备份：bizops-hk-standby.conf.bak-20261002-vendor_b-static。
```

## 五、验证（实测）

```text
源站直测（Host: vendor_b-static.m4q7z1.shop）
  /sweetheart/                       -> 200  34745B  text/html        ← 目录请求现在给 index.html
  /sweetheart/index.html             -> 200  34745B  text/html
  /sweetheart/application.1fb0c.js   -> 200   3169B  application/javascript; charset=utf-8  ← MIME 修复
  /health.json                       -> 200     73B  application/json（本地文件）
兜底路径（本地没有时）
  vendor_b-static/favicon.ico            -> 200    555B（来自 bizops-s3-vendor_b-static，与直连 S3 一致）
  vendor_b-static1/favicon.ico           -> 403    243B（S3 无该对象，与直连 S3 一致）
经 EdgeOne（192.0.2.46，刷新缓存后）
  http://vendor_b-static.m4q7z1.shop/sweetheart/                     -> 200 text/html 34745B
  http://vendor_b-static.m4q7z1.shop/sweetheart/application.1fb0c.js -> 200 application/javascript; charset=utf-8
EdgeOne 缓存刷新：两个站点各提交一次 purge_host（vendor_b-static / vendor_b-static1 / vendor_b-static2）
  任务 JobId：m4q7z1 = 3vpb6cywzadn；k8x2v9 = 3vpb6d6onx3f（FailedList 均为空）
```

## 六、待办与注意

```text
1. 拉取仍在后台跑，完成后做一次完整性核对（rclone check + 抽测目录/JS）。
2. 本次只覆盖 EdgeOne 渠道的 vendor_b-static*（m4q7z1 / k8x2v9）。hkcloudplay06/07 的
   vendor_b-static 仍走 Cloudflare Worker → 空的大阪桶，本轮未改；若要同样修复，需要改 Worker 映射
   或让这两个域名走 nginx（另行确认）。
3. 本地优先会遮蔽 S3：如果开发后续往 bizops-s3-vendor_b-static* 上传新内容，需要重新拉取本地
   （或临时把本地目录里的对应文件删掉）。
4. /data/static 在 nginx 服务器上，不在同步范围内；建议后续纳入磁盘监控（当前 standby 磁盘 2%）。
```

## 七、关联

```text
docker/deploy/hongkong/nginx-standby.conf（本轮的 vendor_b/vendor_a 静态块）
docker/deploy/hongkong/nginx-backup/nginx-standby-etc-nginx-20261002.tgz（配置备份）
docker/doc/2026-10-02-1446-【架构改造】EdgeOne站点k8x2v9接入与香港后端域名切换.md
docker/doc/2026-09-10-2100-【运维】vendor_a缺资源补齐+巴西同步香港+Worker缓存盐准备记录.md（vendor_a 静态资源来源）
```
