---
id: "doc-c180723d861e"
title: "【详细笔记】静态域名 CNAME→GCS + Workers 全量改造"
date: "2026-08-31T18:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "Nginx", "监控告警", "CDN", "DNS", "安全运维"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-08-31-1800-%E3%80%90%E7%AC%94%E8%AE%B0%E3%80%91%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8DCNAME%E4%B8%8EWorkers%E5%85%A8%E9%87%8F%E6%94%B9%E9%80%A0%E8%AF%A6%E7%BB%86%E6%93%8D%E4%BD%9C%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-08-31-1800-【笔记】静态域名CNAME与Workers全量改造详细操作记录.md"
sourceSha256: "a66ec31275b0a9e1309d8afb1eb938b8fe8bfe071bdd790e7bddf9b3f65541ee"
sourceSystem: "project-doc"
---

# 【详细笔记】静态域名 CNAME→GCS + Workers 全量改造

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-08-31-1800-【笔记】静态域名CNAME与Workers全量改造详细操作记录.md`

> 整理日期：2026-08-31 18:00｜日期依据：文件名日期

时间：2026-08-31（Asia/Manila）
项目：DBQP / PGServer master
执行人：Codex（本地工作区 + 宝塔 35.247.205.6 + Cloudflare API）
范围：巴西 22 套 zone × 11 静态前缀 = 242 个静态域名；香港 cn 分支不受影响

## 一、背景与目标

```text
目标：静态资源域名不再经宝塔 nginx 中转，改为
  静态域名 -> Cloudflare 黄云 -> Worker(summer-wave-c94f) 改写 Host -> GCS -sa 桶直出
  并开启边缘缓存（Cache Rule + Workers Caching），提升全球加载速度。
平台-api static_hosts 全量写入 22 套 zone 静态域名（含 3 套 Argo 域），
不写 storage.googleapis.com 原始 S3 域名。
```

## 二、关键研究结论（为什么直接 CNAME 不行）

```text
1. Cloudflare proxied CNAME 回源默认以「原始记录名」作为 Host 头发给源站，
   不会自动改成 CNAME 目标域名（官方文档 custom-origin 明确）。
2. GCS 靠 Host 头解析桶名 -> Host=域名≠桶名 -> 404（content-length 133）。
3. 改 Host 的官方能力 Origin Rules 仅 Enterprise；Snippets Free 不可用。
4. 实测：3 套 Argo zone 静态 CNAME 32/33 失败（仅 pg4-static.xqv9m8 边缘例外）；
   用户面板手动 CNAME + 等待约 20 分钟后部分记录生效（边缘传播/行为不一致）。
5. 结论：可靠方案 = Workers 改写 Host（朋友方案一致），已全量落地。
```

## 三、操作时间线与详细步骤

### 1. 08-31 07:00 评估与首个实测

```text
- 创建评估文档；tada-statics1 -> -sa 桶 CNAME 实测 404（GCS Host 校验）
- 确认官方机制 + 文档引用；写入评估文档第一~八节
- 提示词 A（CNAME 版，标注 404 风险）/ 提示词 B（Workers 版）
```

### 2. 08-31 下午 3 套 Argo zone CNAME 全量测试

```text
- 工具：新增 docker/scripts/cf_static_cname_switch.py（转换/逐条字节验证/回滚）
- tada-cdn-2026.icu 11/11 失败、cdn-tokyo-dbqp.icu 11/11 失败 -> 全部还原 A->宝塔
- xqv9m8.icu 试点 10/11 失败（上午）-> 已还原；pg4 CNAME 例外保留
- 巴西+香港 GCS S3 域名清单（24 个）整理发群
- 评估文档第九节落档
```

### 3. 08-31 晚 用户手动 CNAME 生效确认 + 监控上线

```text
- 用户面板手动配置 4 条 CNAME（pg4-static.xqv9m8/6qv8m、tada-statics1.cdn-tokyo-dbqp.icu/.cyou）
  等待约 20 分钟后生效，4/4 字节比对一致
- 线上 platform-api static_hosts 确认为 22 套 zone（用户手动扩展，含 game_hosts）
- 全量域名+CNAME 清单（242 个）发群；4 已配置 / 238 待配置
- 新增 docker/scripts/cf_static_cname_monitor.py（每 10 分钟扫描 CNAME 并字节验证，
  状态变化才发群）；宝塔 cron */10；token /root/dbqp-cf-dns.env
- Workers 限制与费用查询（API zone 套餐 5 Pro+37 Free + 官方文档）发群，评估文档第十一节
```

### 4. 08-31 深夜 platform-api 配置同步 + Worker 复用方案

```text
- 线上 9 个厂商配置同步 master（pg/tada/pp/popok/playson/panda 扩 22 zone，
  g759 保持线上外部测试域，jdb/jili 不变；无原始 S3 域名）
- 用户创建 Worker「summer-wave-c94f」，手动配置 6qv8m/cdn-tokyo-dbqp.icu/.cyou 路由
- 发现缺口：*-statics1.* 只覆盖 tada-statics1，漏 tada-statics/tada-statics2
- 复用方案发群：所有 zone 路由指向同一 Worker（19 zone × 2 + 3 补丁）
- 评估文档第十二、十三节落档
```

### 5. 用户创建全权限 API Token

```text
- token 名 sweet-surf-7056，权限策略 Write all resources（区域级 42+ 项、账户级 118+ 项）
- 客户端 IP 过滤：35.247.205.6（宝塔）+ 34.151.249.53（备用机）
- 过期：2027-09-01（1 年，使用后应撤销）
- 存放：宝塔 /root/dbqp-cf-workers.env（root-only 600），未入库/未发群
```

### 6. 全量部署执行（API）

```text
a) Worker 代码更新（PUT summer-wave-c94f）：
   - 显式 12 前缀 -> 桶映射（修复 g759-static 拼错桶名 dbqp-gcs-g759-static-sa）
   - 非静态前缀 passthrough（api/games 动态域名不受影响）
   - 保留 CORS 头（Access-Control-Allow-Origin: *）
   - 源码：docker/scripts/summer-wave-static-proxy.js
b) Workers 路由 90 条（0 失败）：
   - 22 zone × 4 条：*-static.<zone>/* + tada-statics.<zone>/* +
     tada-statics1.<zone>/* + tada-statics2.<zone>/*
   - 说明：CF 路由通配符只允许主机名开头，tada-statics*.* 不合法 -> 用显式 3 条
   - cdn-tokyo-dbqp.icu/.cyou 保留旧 *-statics1.*（冗余无害）
c) Cache Rules 22 条（0 失败）：
   - 名称 statics；筛选仅静态子域（ends_with http.host "-static.<zone>" 或
     starts_with http.host "tada-statics.<zone>"）
   - 动作 set_cache_settings cache=true + edge_ttl override_origin 604800（7 天）
   - 优化：3 个已有 zone 从「全部请求」收窄为「仅静态子域」（防 api 动态缓存 7 天）
   - Workers Caching 开启（PATCH settings cache.enabled=true），实测 HIT
d) DNS 238 条 A->CNAME（-sa 桶）：
   - cf_static_cname_switch.py --convert 逐 zone，0 失败
   - 加上原 4 条 CNAME = 242 条全量
e) 全量验证：242/242 静态域名与 GCS 桶直出字节一致（0 失败）
f) 监控：cron 自动纳入，242 CNAME 全 OK、A=0
```

## 四、最终状态清单

```text
Worker  ：summer-wave-c94f（标准计费，Cache 开启，源码已入库）
路由    ：90 条（22 zone × 4，另 2 条冗余）
Cache   ：22 zone「statics」规则（仅静态子域 + Edge TTL 7 天）
DNS     ：242 条静态 CNAME -> -sa 桶（A=0）
验证    ：242/242 字节一致（0 失败）
监控    ：宝塔 cron */10（cf_static_cname_monitor.py），状态变化发群
platform-api：master == 线上（22 zone static/game hosts，无原始 S3）
Git     ：master ff6bd7ed（未 push，领先 origin 8 提交）
```

## 五、费用

```text
Workers：Free 10 万请求/天；Paid $5/月含 1000 万请求 + 3000 万 CPU-ms，
         超出 $0.30/百万请求、$0.02/百万 CPU-ms；出网免费
本方案：静态代理日常约 $5/月（静态缓存命中率高，CPU 极低）
对比  ：22 zone Argo 全开 $110/月；Workers 全站静态代理 $5 起
```

## 六、待办与风险

```text
1. 撤销全权限 token sweet-surf-7056（任务已完成，面板 API 令牌处删除）
2. g759-static 无独立 DNS 记录（通配符覆盖），Worker 映射已含，勿删通配符
3. 香港 cn 分支（hkcloudplay* / CloudFront）未动
4. 若后续新增厂商/前缀，需同步：Worker 映射 + 路由 + Cache Rule + platform-api 配置
5. Worker 免费额度不够时升级 Workers Paid（$5/月）
```

## 七、核对结论（依据笔记逐项复验，见验证记录）

```text
待复验：仓库 / DNS 242 CNAME / 路由 90 / Cache 22 / Worker 代码 / 监控 / platform-api
复验结果全部通过后，本文档发群。
```

## 八、CDN 多地区预热 + 健康检查文件（2026-08-31 追加）

### 8.1 健康检查标准

```text
动态：/<vendor>-games.<zone>/health 与 api.<zone>/health
      返回 {"rcode":0,...,"msg":"succ"} 即正常（HTTP 200）
静态：每个游戏目录放 health.json（内容参考动态格式）：
      {"rcode":0,"data":{"provider":"pg","host":"pg4-static",
       "path":"126/","bucket":"dbqp-gcs-pg4-static-sa"},"msg":"succ"}
```

### 8.2 静态 health.json（已完成）

```text
生成：304 个游戏目录（PG 104 / TADA 83 / PP 1 / PPK 1 / PLAYSON 50 /
      PANDA 52 / G759 13），逐目录 health.json
上传：12 个 -sa 桶全部成功（首次 cp -r 传错嵌套路径，已清理并按正确路径重传）
验证：912/912 通过 CF 静态域名返回 200（3 套 Argo zone）
动态 /health 全量探测：153/157 rcode=0 正常
  4 个 410：api/pg-games .t6qv8m.icu 与 .6qv8m.icu（线上配置已排除这两个 zone，疑似未启用）
```

### 8.3 缓存根因修复（重要）

```text
问题：预热后 cf-cache-status=DYNAMIC，缓存未生效
根因：Worker 响应不走 Cache Rules / Page Rules（Worker 即源站）；
      Workers Caching 开关经 API 无法可靠开启（deployment metadata cache=None）
修复：Worker 内置 Cache API——GET 200 响应缓存 7 天（max-age=604800），
      实测第二次请求 HIT（确定生效，不依赖面板开关）
      源码：docker/scripts/summer-wave-static-proxy.js（已更新）
```

### 8.4 多地区预热（用户主要地区）

```text
地区：巴西（宝塔 GRU）/ 香港（HKG）/ 马尼拉（本地）/ 东京（GCP 临时
      e2-micro asia-northeast1）/ 新加坡（GCP 临时 e2-micro asia-southeast1）
内容：全部厂家全部游戏入口 HTML + 页面 JS/CSS + health.json
工具：docker/scripts/cdn_warm_static.py（发现+预热，含重试）、
      docker/scripts/cdn_warm_urls.py（按 URL 列表预热）
规模：912 任务/地区（304 游戏 × 3 zone）+ 912 health/地区
状态：5 地区全部完成且回验 HIT
  马尼拉 main 912/912、health 912/912
  巴西 main 714/912（198 为空格/括号垃圾副本，已在新版脚本排除）、health 912/912
  东京 main 714/912（同上）、health 912/912
  新加坡 main 912/912、health 912/912
  香港 main 912/912、health 912/912
  全部地区回验 cf-cache-status=HIT ✅
说明：Free/Pro 无"预热全部节点"接口，按地区预热覆盖主要用户 PoP；
      GCP 临时实例（东京/新加坡 e2-micro）已删除
      Worker 缓存修复：Cache API 7 天（第二次请求 HIT）
```
