---
id: "doc-0e332c589e13"
title: "【故障修复】静态域 CORS 重复头导致游戏加载失败与修复记录"
date: "2026-08-29T20:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "CDN", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-08-29-2030-%E3%80%90%E6%95%85%E9%9A%9C%E4%BF%AE%E5%A4%8D%E3%80%91%E9%9D%99%E6%80%81%E5%9F%9FCORS%E9%87%8D%E5%A4%8D%E5%A4%B4%E5%AF%BC%E8%87%B4%E6%B8%B8%E6%88%8F%E5%8A%A0%E8%BD%BD%E5%A4%B1%E8%B4%A5%E4%B8%8E%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-08-29-2030-【故障修复】静态域CORS重复头导致游戏加载失败与修复记录.md"
sourceSha256: "e82a581d3f39e3d46e29bbb64bd65744f3cff8e52a90ebef67fabc10feffa012"
sourceSystem: "project-doc"
---

# 【故障修复】静态域 CORS 重复头导致游戏加载失败与修复记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-08-29-2030-【故障修复】静态域CORS重复头导致游戏加载失败与修复记录.md`

> 整理日期：2026-08-29 20:30｜日期依据：文件名日期

时间：2026-08-29 20:30（Asia/Manila）
项目：DBQP / PGServer master
执行人：Codex（本地工作区 + 宝塔/备用机 + 备用机浏览器）

## 一、故障现象

用户反馈游戏加载不出来，提供一条 PG 65（麻将胡了）启动链接：

```text
https://pg-games.m7v8k3.cyou/65/index.html?or=pg4-static.m7v8k3.cyou&...
```

HTTP 层全部 200（页面/静态/桶均通），但浏览器中游戏卡在加载。

## 二、根因（浏览器实测定位）

Playwright 打开故障链接，控制台报错：

```text
Access to XMLHttpRequest at 'https://pg4-static.m7v8k3.cyou/shared/3c4695a542/index.json'
from origin 'https://pg-games.m7v8k3.cyou' has been blocked by CORS policy:
The 'Access-Control-Allow-Origin' ...
```

原因：静态域名切 CF CDN（nginx -> GCS）后，响应里出现**两个**
`Access-Control-Allow-Origin: *`（nginx `add_header` 一个 + GCS 桶自带一个），
浏览器按 CORS 规范拒绝多值 ACAO 头，游戏 XHR 被拦。
此前桶直出时只有 GCS 一个头，所以未触发。

## 三、修复

nginx 静态 vhost（宝塔 + 备用机各 12 个）`location /` 增加：

```nginx
proxy_hide_header Access-Control-Allow-Origin;
proxy_hide_header Access-Control-Allow-Methods;
proxy_hide_header Access-Control-Allow-Headers;
proxy_hide_header Access-Control-Expose-Headers;
add_header Access-Control-Expose-Headers "Content-Type,Token,Content-Length,Range,Content-Range,Accept-Ranges,ETag,Cache-Control" always;
```

只保留 nginx 自己输出的一套 CORS 头；已 reload，并同步到
`sync_all_game_domains_to_baota.py` 模板（后续 cron 重新生成不回退）。

## 四、验证

- 响应头 ACAO 从 2 个变 1 个；
- Playwright 重测故障 URL：画布 6s、点「继续」成功、**0 失败请求**
  （仅剩无害的 service-worker scope 警告）。

## 五、修复后与竞品对比（3 轮）

```text
我方（H5+Argo+CF CDN）：14.0s / 11.4s / 11.4s，均值 12.3s；画布 1.2-2.4s
竞品（m6kk678n）：12.6s / 15.4s / 12.6s，均值 13.5s；画布 2.1-3.6s
结论：我方均值快约 1.2s；画布出现整体更快
```

6 条带水印视频已发群。

## 六、变更

- 宝塔/备用机 nginx 静态 vhost（服务器侧，已 reload）；
- `docker/线上服务器信息/baota/scheduled-tasks/sanitized/sync_all_game_domains_to_baota.py`
  模板补 CORS 去重；
- 本记录文档。
