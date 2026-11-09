---
id: "doc-4ff863f951e9"
title: "【架构改造】静态域名黄云 GCS 回源 + Argo Smart Routing 评估记录"
date: "2026-08-29T19:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "Nginx", "CDN", "DNS", "安全运维", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-08-29-1930-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8D%E9%BB%84%E4%BA%91GCS%E5%9B%9E%E6%BA%90%E4%B8%8EArgo%E5%BC%80%E9%80%9A%E8%AF%84%E4%BC%B0%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-08-29-1930-【架构改造】静态域名黄云GCS回源与Argo开通评估记录.md"
sourceSha256: "3777ec08f2577bf9cf089d29d618a08940de175b5cc04c0406570ee3947b6c66"
sourceSystem: "project-doc"
---

# 【架构改造】静态域名黄云 GCS 回源 + Argo Smart Routing 评估记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-08-29-1930-【架构改造】静态域名黄云GCS回源与Argo开通评估记录.md`

> 整理日期：2026-08-29 19:30｜日期依据：文件名日期

时间：2026-08-29 19:30（Asia/Manila）
项目：某业务公司 / PGServer master
执行人：Codex（本地工作区 + 宝塔/备用机 + Cloudflare API）

## 一、需求

1. 静态域名 CNAME 到对应 GCS 桶域名，巴西/香港都回源，开启黄云用 CF CDN；
2. 接口（api/game）域名开通 Argo Smart Routing；
3. 出明细发群（含费用与续费提醒）。

## 二、验证结论（重要）

1. **黄云 CNAME 直指 GCS 桶不可行（实测）**：`pg-static.xqv9m8.icu` 改
   CNAME → `bizops-gcs-pg-static-sa.storage.googleapis.com` + 黄云后返回 404，
   GCS 校验 Host 头必须等于桶域名；
2. **CF Free 无法改写 Host**：Origin Rules 的 Host 改写仅 Enterprise
   （官方文档 Availability 表确认），Transform Rules/Snippets Free 不可用；
3. 测试记录已还原（A 192.0.2.9 灰云 → 恢复 200），无副作用。

## 三、落地：nginx 改 Host 方案（巴西）

架构：`CF(黄云) -> 宝塔/备用 nginx -> GCS 桶（nginx 改写 Host + SNI）`

### 1. nginx vhost（宝塔 + 备用机 192.0.2.13，各 12 个静态 vhost）

`location /` 由本地目录直出改为 GCS proxy：

```nginx
location / {
    resolver 192.0.2.31 192.0.2.30 ipv6=off valid=300s;   # 强制 IPv4（GCS AAAA 在 GCP 无 IPv6 导致 502）
    set $gcs_upstream bizops-gcs-<prefix>-sa.storage.googleapis.com;
    proxy_pass https://$gcs_upstream;
    proxy_set_header Host bizops-gcs-<prefix>-sa.storage.googleapis.com;
    proxy_ssl_server_name on;
    proxy_ssl_name bizops-gcs-<prefix>-sa.storage.googleapis.com;
    ...
}
```

12 前缀 → 圣保罗 -sa 桶（g759-static 本就在圣保罗，无 -sa）：
`pg-static/pg3/pg4/pg5`、`vendor_a-statics/1/2`、`pp-static`、`ppk-static`、
`vendor_c-static`、`vendor_d-static`、`g759-static`。

### 2. 生成脚本模板

`sync_all_game_domains_to_baota.py`（宝塔 `/www/server/panel/script/` 与仓库一致）：
静态 spec 增加 `static_prefix`，`static_server_conf` 按 `STATIC_BUCKET_HOSTS[prefix][0]`
（-sa 桶）输出 proxy 模板；已重新生成并 reload，后续 cron 不会回退。
备份：`/root/all_game_domain_sync_backup_20260829_191818`。

### 3. btwaf cookie 跳过（关键）

宝塔 WAF 注入 `server_name_session` cookie 导致 CF 不缓存（DYNAMIC）。
`/www/server/btwaf/header.lua` 第 194 行追加：

```lua
and not string.match(ngx.var.host or "", "%-statics?%.")
```

即 `-static.` / `-statics.` 域名跳过 cookie 注入（备份 `.bak-20260829`）。
备用机无 WAF，天然无 cookie。

### 4. Cloudflare DNS（巴西）

241 条静态记录（A 192.0.2.9 灰云）全部改为：`A 192.0.2.8 + 黄云(proxied)`，
API 批量 PATCH，0 失败；验证无残留 `A 192.0.2.9` 记录。

### 5. 验证结果

- 公网：pg-static/126/ 200、pg4-static/126/ 200、g759-static 游戏页 200、
  vendor_d-static 游戏页 200（各厂商桶路径不同，缺失路径 404 属正常）；
- `.js` 静态资源 `cf-cache-status: HIT`（CF CDN 缓存生效，age 递增）；
- HTML 页面默认 DYNAMIC（CF 默认只缓存静态扩展名；如需全缓存可加 Cache Rule，
  需 Zone Config 权限，待办）。

## 四、香港（待协调）

香港域名（hkcloudplay01-05 / hkplaycore）当前走 **AWS CloudFront**（DNS-only CNAME），
由 cn 分支管理。切到 CF 黄云 + 东京桶需与 cn 分支协调后实施，
本记录预留：香港 nginx 192.0.2.14 相同 proxy 模板 → 东京桶
（`STATIC_BUCKET_HOSTS[prefix][1]`，g759 用 `bizops-gcs-g759-static-asia`）。

## 五、Argo Smart Routing 评估

### 现状与结论

- 42 个 zone 全部 Free 套餐；Argo 需付费套餐（Pro 及以上）+ 按 zone 计费；
- 现有 DNS token 调 `PUT /zones/{id}/argo/smart_routing` → Authentication error
  （无 Zone Settings 权限），需新 token 或 CF 面板 Agent Lee 执行；
- 动态域名盘点：199 条黄云 A → 192.0.2.8
  （api.<22根域> 22、<6厂商>-games.<22根域> 132、通配/www/socket 等 45）。

### 费用估算（Argo 按 zone，非按 hostname）

```text
Pro 套餐：$20/zone/月（Argo 前置条件）
Argo Smart Routing：$5/zone/月
若开 22 个巴西根域：($20+$5)×22 = $550/月
若开 20 个：$500/月 ≈ 500U（1 个月试跑）
```

### 待办

1. 确认开通 zone 清单（建议：22 巴西根域或缩到实际在用的 ~20 个）；
2. 充值/扣费确认（500U，亨利侧信用卡）；
3. 升级套餐 + 开 Argo：用 Agent Lee 指令或提供 Zone Settings 权限 token；
4. **续费提醒**：Argo/Pro 按月计费，每月需预充值，否则下月停服。

## 五之二、Argo 开通 zone 清单与 Agent Lee 提示词（2026-08-29 补充）

### 清单

```text
A. 巴西游戏根域 22 个（api.<root> + 6 厂商 games.<root>，推荐）：
   xqv9m8.icu t6qv8m.icu p8m7xv.cyou m7v8k3.cyou q7m9v8.icu m6xv8q.cyou
   qv9m8.icu 6qv8m.icu 8m7xv.cyou 7v8k3.cyou 7m9v8.icu 6xv8q.cyou
   vendor_a-cf-2026.cyou vendor_a-host-game.icu vendor_a-cf-game.cyou vendor_a-cdn-2026.icu
   vendor_a-cdn-game.icu vendor_a-host-2026.icu cdn-tokyo-bizops.icu cdn-tokyo-bizops.cyou
   cdn-manila-bizops.icu cdn-manila-bizops.cyou
B. 接口/商户 5 个：shanghu01.cc shanghu02.cc shanghu03.cc pgofficialbx.com
   playgame-api.vip
C. 香港 6 个（cn 分支协调后）：hkcloudplay01-05.com hkplaycore.com
```

### Agent Lee 提示词（粘贴到 CF 面板 AI 执行）

```text
请对我的 Cloudflare 账户（[邮箱已脱敏]）执行以下操作，只操作下面列出的
zone，不要动 DNS 和其他设置：
1. 先检查账户余额/绑定的支付方式可用；
2. 对每个 zone：把套餐升级为 Pro（如当前是 Free），再通过 API 开启
   Argo Smart Routing（PUT /zones/{zone_id}/argo/smart_routing {"value":"on"}）；
3. 逐个 GET 验证 smart_routing 状态为 on，失败的列出原因。
zone 清单：
xqv9m8.icu t6qv8m.icu p8m7xv.cyou m7v8k3.cyou q7m9v8.icu m6xv8q.cyou
qv9m8.icu 6qv8m.icu 8m7xv.cyou 7v8k3.cyou 7m9v8.icu 6xv8q.cyou
vendor_a-cf-2026.cyou vendor_a-host-game.icu vendor_a-cf-game.cyou vendor_a-cdn-2026.icu
vendor_a-cdn-game.icu vendor_a-host-2026.icu cdn-tokyo-bizops.icu cdn-tokyo-bizops.cyou
cdn-manila-bizops.icu cdn-manila-bizops.cyou
执行完输出：zone 名 | 套餐 | Argo 状态 | 失败原因
```

费用：A 22 个 = ($20 Pro + $5 Argo) × 22 = $550/月 ≈ 500U 试跑 1 个月；
A+B 27 个 = $675/月；加 C 香港 6 个 = $825/月（需 cn 分支确认）。

## 五之三、缩到「1 套测试 → 3-5 套正式」（2026-08-29 用户调整）

用户确认：域名是一套一套的（一个根域 = 一套，含 api/games/statics 全套），
实际配置 3-5 套就够，先配 1 套测试。

### 推荐选择

```text
测试 1 套：xqv9m8.icu（所有厂商 platform-api 配置第一顺位、线上测试 URL 主用）
正式 3-5 套建议：xqv9m8.icu、t6qv8m.icu、q7m9v8.icu、vendor_a-cdn-2026.icu、
cdn-tokyo-bizops.icu（覆盖主用 + vendor_a 系列 + cdn 系列代表根域；可按需替换）
```

### 费用（按套）

```text
1 套 = $25/月（Pro $20 + Argo $5）
3 套 = $75/月；5 套 = $125/月
```

### Agent Lee 提示词（单套测试版，粘贴到 CF 面板 AI）

```text
请对我的 Cloudflare 账户（[邮箱已脱敏]）执行以下操作，只操作下面列出的
zone，不要动 DNS 和其他设置：
1. 先检查账户余额/绑定的支付方式可用；
2. 对该 zone：把套餐升级为 Pro（如当前是 Free），再通过 API 开启
   Argo Smart Routing（PUT /zones/{zone_id}/argo/smart_routing {"value":"on"}）；
3. GET 验证 smart_routing 状态为 on。
zone 清单：xqv9m8.icu
执行完输出：zone 名 | 套餐 | Argo 状态 | 失败原因
```

正式 3-5 套时把 zone 清单换成上面建议列表即可。

## 五之四、测试套核验（2026-08-29，xqv9m8.icu）

用户通过 Agent Lee 完成两步：Pro 升级 + Argo 启用（$25/月）。

### 我方 API 独立核验

```text
套餐：Pro Website ✅（GET /zones 确认）
DNS：24 条记录；11 静态 A + 7 动态 A 全部黄云 -> 192.0.2.8；
     无 192.0.2.9 残留 ✅
动态 TTFB 基线（马尼拉视角）：api ~1.0-1.5s；pg-games ~1.0-1.2s
Argo/SSL 状态：现有 DNS token 无 Zone Settings 权限，交 Agent Lee 复核
```

### Agent Lee 复核提示词

```text
请核查 zone xqv9m8.icu：
1. GET /zones/{zone_id}/argo/smart_routing 输出 smart_routing 状态；
2. GET /zones/{zone_id}/settings/ssl 输出 SSL/TLS 模式；
3. 确认套餐 Pro 与 Argo 计费生效。
输出：zone 名 | 套餐 | Argo | SSL模式
```

### 后续

- 跑通后扩到 3-5 套：t6qv8m.icu、q7m9v8.icu、vendor_a-cdn-2026.icu、
  cdn-tokyo-bizops.icu 重复同样两步（Agent Lee 提示词换清单即可）。

### Agent Lee 复核结果（2026-08-29 第二轮回）

```text
SSL/TLS 优化：最低 TLS 1.0 -> 1.2 ✅；Always Use HTTPS on ✅；
自动 HTTPS 重写 on ✅
套餐：Pro Website ✅
SSL 模式：Full ✅（与 nginx 源站证书匹配策略一致，勿切 Full strict）
Argo Smart Routing：API 读到 off ⚠️（面板疑似显示已启用，可能 Smart Shield
总开关或 API 同步延迟）
```

### Argo 重新启用 + 验证提示词

```text
请在 zone xqv9m8.icu 重新启用 Argo Smart Routing 并验证：
1. 打开面板「流量 → Argo Smart Routing」，确认 Argo Smart Routing 独立开关为开
   （不是 Smart Shield 总开关）；
2. 用 API 显式开启：PUT /zones/{zone_id}/argo/smart_routing，body {"value":"on"}；
3. 等待 60 秒后 GET /zones/{zone_id}/argo/smart_routing 确认返回 on；
4. 若仍 off 或报错，输出完整错误信息。
输出：zone 名 | 面板开关 | API smart_routing | 失败原因
```

说明：Argo off 期间不产生 Argo 计费；确认 on 后才开始 $5/月计费。

### Agent Lee 最终确认（2026-08-29 第三轮回）

```text
xqv9m8.icu：Pro Website ✅｜API smart_routing = on ✅｜SSL Full ✅｜无失败
执行：PATCH /zones/{id}/argo/smart_routing {"value":"on"} -> on；GET -> on
（此前面板 Smart Shield 总开关误显示，以 API 为准）
月费：Pro $20 + Argo $5 = $25/月
```

### 扩 4 套（Agent Lee 提示词，待用户确认后执行）

```text
请对我的 Cloudflare 账户（[邮箱已脱敏]）对以下 4 个 zone 执行与
xqv9m8.icu 相同的操作并验证：
t6qv8m.icu q7m9v8.icu vendor_a-cdn-2026.icu cdn-tokyo-bizops.icu
1. 每个 zone：升级 Pro（如 Free）→ API 开启 Argo
   （PUT /zones/{zone_id}/argo/smart_routing {"value":"on"}）→ GET 验证 on；
2. 每个 zone：SSL 模式 Full；最低 TLS 1.2；Always Use HTTPS on；
   自动 HTTPS 重写 on；
3. 不动 DNS 记录和其他设置。
输出：zone 名 | 套餐 | Argo | SSL模式 | 失败原因
```

扩后月费：Pro 5×$20 + Argo 5×$5 = $125/月。

### 扩 4 套（2026-08-29 用户确认执行）

已核验 4 个 zone（每套 api + 6 games + 11 静态黄云，结构同 xqv9m8，均 Free）：

```text
t6qv8m.icu  q7m9v8.icu  vendor_a-cdn-2026.icu  cdn-tokyo-bizops.icu
```

Agent Lee 提示词（与 xqv9m8 相同操作）：

```text
请对我的 Cloudflare 账户（[邮箱已脱敏]）对以下 4 个 zone 执行与
xqv9m8.icu 相同的操作并验证：
t6qv8m.icu q7m9v8.icu vendor_a-cdn-2026.icu cdn-tokyo-bizops.icu
1. 每个 zone：升级 Pro（如当前是 Free）→ 用 API 开启 Argo Smart Routing
   （PUT /zones/{zone_id}/argo/smart_routing {"value":"on"}）→ GET 验证返回 on；
2. 每个 zone：SSL/TLS 模式 Full；最低 TLS 1.2；Always Use HTTPS on；
   自动 HTTPS 重写 on；
3. 不要动 DNS 记录和其他设置。
输出：zone 名 | 套餐 | API smart_routing | SSL模式 | 失败原因
```

扩后月费：5 套（含 xqv9m8）= $125/月。

## 五之五、对比口径统一（2026-08-29）

后续与竞品对比统一使用分阶段口径：

```text
分阶段耗时：登录 -｜点游戏 -｜画布 X.Xs｜点继续→加载出 Y.Ys
★ 点继续→加载出游戏 Y.Ys（同基准主指标）
★ 点击图标→完整加载 Z.Zs
```

对应脚本字段：`canvas_after_click_ms` / `continue_to_loaded_ms` /
`click_to_loaded_ms`，水印已按此标注。

## 六、变更文件

- `docker/线上服务器信息/baota/scheduled-tasks/sanitized/sync_all_game_domains_to_baota.py`：
  静态 vhost 模板 → GCS proxy（resolver ipv6=off + Host 改写）；
- 宝塔/备用机 nginx 12+12 静态 vhost、btwaf header.lua（服务器侧，备份 .bak-20260829）；
- 本记录文档。

## 七、回滚

- DNS：API 批量 PATCH 回 `A 192.0.2.9 proxied=false`；
- nginx：vhost `.bak-20260829` 还原 + reload；
- 生成脚本：仓库/宝塔均有旧版可回退。
