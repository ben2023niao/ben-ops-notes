---
id: "doc-b3ffd5dfd4f9"
title: "18game 网关高负载复核与静态资源缓存降载"
date: "2026-10-24T00:10:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "监控告警", "自动化", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-24-0010-%E3%80%90%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%E3%80%9118game%E7%BD%91%E5%85%B3%E9%AB%98%E8%B4%9F%E8%BD%BD%E5%A4%8D%E6%A0%B8%E4%B8%8E%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E7%BC%93%E5%AD%98%E9%99%8D%E8%BD%BD.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-24-0010-【性能优化】18game网关高负载复核与静态资源缓存降载.md"
sourceSha256: "f1b365bb0d0cdb84021b092188c00336ecadd67ad8c699302768f094de4f1805"
sourceSystem: "project-doc"
---

# 18game 网关高负载复核与静态资源缓存降载

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610240010-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BDocker%2BNginx-18game%20%E7%BD%91%E5%85%B3%E9%AB%98%E8%B4%9F%E8%BD%BD%E5%A4%8D%E6%A0%B8%E4%B8%8E%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E7%BC%93%E5%AD%98%E9%99%8D%E8%BD%BD.md)

> 整理日期：2026-10-24 00:10｜日期依据：文件名日期

- 时间：2026-10-24 00:00–00:10（Asia/Manila）
- 环境：游点涩/18game 线上
- 主机：游点涩-网关-H5/PC回源-16.208.38.88
- Beszel 系统 ID：`jeorh1zglvr4y9t`
- 结论：监控数据不是旧缓存，也不是单点授权安全测试。主要压力是大量 H5/PC 静态资源回源 Node SSR；
  增加网关本地代理缓存后，整机 CPU 从接近 100% 降至约 45%，load 从 19.9 降至 7.25。

## 一、复核结果

Beszel 最近一分钟原始采样：

| 时间 UTC | CPU | load1 | 内存 |
| --- | ---: | ---: | ---: |
| 15:59 | 84.61% | 14.11 | 47.08% |
| 16:00 | 85.20% | 13.99 | 43.17% |
| 16:01 | 99.96% | 19.90 | 45.86% |
| 16:02 | 79.61% | 16.38 | 47.25% |
| 16:03 | 50.86% | 10.34 | 47.69% |
| 16:04 | 44.56% | 7.25 | 48.38% |

24 小时趋势显示 CPU 随业务量从约 35% 持续升至 87%，不是历史曲线残留：

- 10-22 18:30 UTC：约 38%
- 10-23 00:30 UTC：约 38%
- 10-23 09:30 UTC：约 49%
- 10-23 14:30 UTC：约 67%
- 10-23 15:50 UTC：约 87%

## 二、流量拆解

15:57:23–16:00:27 UTC 的 20 万条访问日志样本：

| 类型 | 请求数 | 占样本 |
| --- | ---: | ---: |
| `_nuxt` 静态文件 | 84,556 | 42.3% |
| `/images` 静态文件 | 40,953 | 20.5% |
| API | 63,780 | 31.9% |
| 动态页面及其他 | 10,711 | 5.4% |

样本约 184 秒、平均 1,087 req/s，其中静态资源约 683 req/s。静态资源仍在回源 Nuxt 容器，
是 CPU 高位的主要放大器。

同期 Meta 爬虫请求 2,542 次，只占约 1.3%，并且已全部返回 403；登录探测源
`3.1.244.240` 仍持续请求，但全部返回 444。两者都不是本轮 CPU 高位的主因。

后端 3 分钟内处理 69,204 次 API，来自 3,789 个 IP、2,010 个登录用户和 7,678 个设备，
流量呈真实业务分布式特征，没有单客户端打满。

## 三、修复

网关增加只读本地代理缓存：

```nginx
proxy_cache_path /var/cache/nginx/youdianse_static levels=1:2
                 keys_zone=yds_static:100m max_size=5g inactive=7d use_temp_path=off;
```

- `/_nuxt/`：HTTP 200 缓存 7 天；
- `/images/`：HTTP 200 缓存 10 分钟；
- 缓存键包含 H5/PC 后端目标，避免两套前端构建混用；
- 只缓存静态资源，不缓存 API 和动态页面；
- `proxy_cache_lock on`，避免热门资源失效时并发击穿 Node；
- 磁盘总量上限 5GB，当前磁盘使用约 37%，容量充足。
- 新 H5/新 PC 发布成功后自动轮换缓存目录并重启 Nginx，旧目录保留 2 天供回滚。

## 四、验证

- 同一图片和 `_nuxt` 文件：第一次 `MISS`，第二次 `HIT`；
- 缓存目录：约 30MB，且持续预热；
- 普通浏览器访问 www/h5：200；
- 后台 PHP：正常；
- 缓存服务重启后 `perip_ssr` 限流错误新增：0；
- 120k 请求样本中 5xx：9 个，其中 8 个为单一来源请求登录接口导致，守卫已临时封禁；
- H5 容器整机 CPU 占比：53.13% → 24.10%；
- PC 容器整机 CPU 占比：26.54% → 13.46%；
- H5 容器网络：约 15.38MB/s → 约 2.33MB/s；
- 整机 CPU：99.96% → 44.56%；
- 整机 load：19.90 → 7.25。

## 五、回滚

线上备份：

- `/etc/nginx/conf.d/10-youdianse-prod-maps.conf.bak.static-cache-20261023-160156`
- `/etc/nginx/conf.d/20-youdianse-prod-unified.conf.bak.static-cache-20261023-160156`

回滚时恢复对应备份，执行 `nginx -t`，然后重启 Nginx。缓存目录可以保留，
不影响回滚后的业务运行。

## 六、后续建议

1. 继续观察 `yds_static` 命中率、缓存大小和磁盘增长；达到 4GB 时提前评估容量。
2. 埋点接口仍占 API 的主要部分，前端后续应按批次合并上报。
3. 静态资源继续优先由 CloudFront 命中；源站本地缓存作为二线兜底。
4. 当整机 CPU 再次持续高于 80% 或 load 高于 24 时，优先查看静态回源、页面 SSR 与业务峰值，
   不应直接按 抗压能力测试 处置。

## 七、持续监控

- 2026-10-24 00:17（Asia/Manila）在监控机启动 6 小时盯盘任务。
- 每 20 分钟连续采样 3 分钟，报告整机 CPU/load、QPS、5xx、H5/PC、缓存、限流和页面状态。
- 6 小时共 19 份报告（含启动基线），同时发送线上群与运维群。
- 报告记录在监控机 `state/gateway_watch_reports.jsonl`，任务只读，不修改线上配置。
- 首轮 16:17:13–16:20:14 UTC 样本：CPU 均值 51.99%、load 均值 4.63、QPS 1,117.6，
  HTTP 5xx 2/201,168，www/h5 均 200，缓存 45MB，新增 `perip_ssr` 错误 0。
