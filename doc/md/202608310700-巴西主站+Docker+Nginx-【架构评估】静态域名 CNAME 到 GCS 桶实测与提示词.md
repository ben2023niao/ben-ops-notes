---
id: "doc-7397df4f74fb"
title: "【架构评估】静态域名 CNAME 到 GCS 桶实测与提示词"
date: "2026-08-31T07:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "监控告警", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-08-31-0700-%E3%80%90%E6%9E%B6%E6%9E%84%E8%AF%84%E4%BC%B0%E3%80%91%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8DCNAME%E5%88%B0GCS%E6%A1%B6%E5%AE%9E%E6%B5%8B%E4%B8%8E%E6%8F%90%E7%A4%BA%E8%AF%8D.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-08-31-0700-【架构评估】静态域名CNAME到GCS桶实测与提示词.md"
sourceSha256: "66e7ef0e925004167f6c2d26eb4f6f03edf125969ea4c958e02a4317f195046f"
sourceSystem: "project-doc"
---

# 【架构评估】静态域名 CNAME 到 GCS 桶实测与提示词

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608310700-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BDocker%2BNginx-%E3%80%90%E6%9E%B6%E6%9E%84%E8%AF%84%E4%BC%B0%E3%80%91%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8D%20CNAME%20%E5%88%B0%20GCS%20%E6%A1%B6%E5%AE%9E%E6%B5%8B%E4%B8%8E%E6%8F%90%E7%A4%BA%E8%AF%8D.md)

> 整理日期：2026-08-31 07:00｜日期依据：文件名日期

时间：2026-08-31 07:00（Asia/Manila）
项目：某业务公司 / PGServer master
执行人：Codex（本地工作区 + Cloudflare API + GCS）

## 一、用户需求

1. `platform-api static_hosts` 移除 S3(东京桶) 域名（已完成，发布 `7d706e2a`）；
2. 静态资源域名在 Cloudflare 中 CNAME 到巴西桶 S3 域名（单地区桶，全部静态域名）。

## 二、决定性实测（vendor_a-statics1 → bizops-gcs-vendor_a-statics1-sa）

```text
方法：真实存在的桶对象 _nuxt/01e19b71f78691f07a2e.js（直出 200），
      DNS 改 CNAME(proxied) 后等待 10 分钟+，对比字节
结果：CNAME 路径 404（cf-cache-status BYPASS，GCS content-length 133 报错）
原因：CF 边缘已切到桶源站，但 GCS 校验 Host 头 = 记录名（域名）≠ 桶名 → 拒绝
此前 2026-08-28 的 404 亦是此因（非对象不存在；对象不存在是 NoSuchKey 404）
验证记录已还原为 A -> 宝塔(192.0.2.8, proxied)，服务恢复（对象 200）
```

## 三、结论

```text
黄云 CNAME 直指 GCS 桶在当前套餐（Free/Pro）不可行：
  GCS 校验 Host；Origin Rules Host 改写仅 Enterprise；
  Transform Rules 禁改 Host；Snippets Free 不可用。
维持现有架构：CF(黄云) -> 宝塔 nginx（改写 Host）-> GCS 桶（-sa 巴西）。
```

## 四、提示词 A：CNAME 版（用户要求，已标注 404 风险）

```text
请对我的 Cloudflare 账户（[邮箱已脱敏]）执行以下 DNS 批量修改，只改静态子域：
1. 对 22 个巴西根域下每个静态子域（pg-static/pg3/pg4/pg5/vendor_a-statics/vendor_a-statics1/
   vendor_a-statics2/pp-static/ppk-static/vendor_c-static/vendor_d-static/g759-static），
   把现有 A 记录（192.0.2.8）改为 CNAME：
   content = 对应桶.storage.googleapis.com（映射见下），proxied=true，TTL=Auto
2. 不要动 api/*-games 动态记录、通配符、TXT、其他记录
3. 输出每 zone 修改数量 + 失败列表
4. 抽查 1-2 个域名 GET dns_records 确认类型 CNAME + proxied
桶映射：
pg-static->bizops-gcs-pg-static-sa / pg3-static->bizops-gcs-pg3-static-sa /
pg4-static->bizops-gcs-pg4-static-sa / pg5-static->bizops-gcs-pg5-static-sa /
vendor_a-statics->bizops-gcs-vendor_a-statics-sa / vendor_a-statics1->bizops-gcs-vendor_a-statics1-sa /
vendor_a-statics2->bizops-gcs-vendor_a-statics2-sa / pp-static->bizops-gcs-pp-static-sa /
ppk-static->bizops-gcs-ppk-static-sa / vendor_c-static->bizops-gcs-vendor_c-static-sa /
vendor_d-static->bizops-gcs-vendor_d-static-sa / g759-static->bizops-gcs-g759-static
⚠️ 注意：实测该 CNAME 在当前套餐返回 404（GCS Host 校验），
仅当套餐升级 Enterprise 或启用 Host 改写后才能生效。
```

## 五、提示词 B：Cloudflare Workers 版（推荐替代，CF 直接回源桶）

```text
请为以下 3 个 zone（xqv9m8.icu / vendor_a-cdn-2026.icu / cdn-tokyo-bizops.icu）
创建 Worker：static-gcs-proxy
代码（入口）：
  export default {
    async fetch(request) {
      const url = new URL(request.url);
      const host = url.hostname;
      const map = {
        "pg-static": "bizops-gcs-pg-static-sa.storage.googleapis.com",
        "pg3-static": "bizops-gcs-pg3-static-sa.storage.googleapis.com",
        "pg4-static": "bizops-gcs-pg4-static-sa.storage.googleapis.com",
        "pg5-static": "bizops-gcs-pg5-static-sa.storage.googleapis.com",
        "vendor_a-statics": "bizops-gcs-vendor_a-statics-sa.storage.googleapis.com",
        "vendor_a-statics1": "bizops-gcs-vendor_a-statics1-sa.storage.googleapis.com",
        "vendor_a-statics2": "bizops-gcs-vendor_a-statics2-sa.storage.googleapis.com",
        "pp-static": "bizops-gcs-pp-static-sa.storage.googleapis.com",
        "ppk-static": "bizops-gcs-ppk-static-sa.storage.googleapis.com",
        "vendor_c-static": "bizops-gcs-vendor_c-static-sa.storage.googleapis.com",
        "vendor_d-static": "bizops-gcs-vendor_d-static-sa.storage.googleapis.com",
        "g759-static": "bizops-gcs-g759-static.storage.googleapis.com"
      };
      const prefix = host.split(".")[0];
      const bucket = map[prefix];
      if (!bucket) return new Response("Not Found", { status: 404 });
      const req = new Request("https://" + bucket + url.pathname + url.search, request);
      req.headers.set("Host", bucket);
      return fetch(req);
    }
  }
然后把 zone 内所有 <prefix>-static 子域的路由指向该 Worker（proxied 保持）。
不要动 api/*-games、其他记录。
输出：Worker 名 | 路由数 | 验证 curl 示例
```

## 六、状态

```text
static_hosts：已去除 S3 域名（master-7d706e2a，3/3 发布）
测试记录：已还原，服务正常
待用户选择：A 维持 nginx / B Workers（推荐）
```

## 七、xqv9m8 单 zone 试点与回滚（2026-08-31）

用户手动将 `pg4-static.xqv9m8.icu` CNAME 到
`bizops-gcs-pg4-static.storage.googleapis.com`（东京桶，黄云）→ **验证通过**
（/126/ 200、字节与桶直出一致、PNG x-goog 头直出）。

随后 API 批量将 xqv9m8 其余 10 条静态记录 CNAME 到巴西 -sa 桶：

```text
结果：pg/pg3/pg4/pg5/pp/ppk/vendor_c/vendor_d 根路径 200；
      vendor_a-statics / vendor_a-statics1 真实对象 404（持续 20 分钟+）
隔离：直出桶 200、宝塔本地 200、CF 路径 404（content-length 133 = GCS 报错）
结论：同一 CNAME 机制对不同记录表现不一致（CF 边缘对部分记录仍以
      记录名为 Host 回源 GCS → Host 校验 404）→ 不可全量应用
```

已回滚：10 条恢复 A -> 宝塔(192.0.2.8, proxied)，服务验证 200；
`pg4-static.xqv9m8.icu` 保留用户手动 CNAME（东京桶，验证可用）。

清单（保留 CNAME）：

```text
pg4-static.xqv9m8.icu -> bizops-gcs-pg4-static.storage.googleapis.com
```

清单（已还原 A->宝塔）：

```text
pg-static / pg3-static / pg5-static / vendor_a-statics / vendor_a-statics1 /
vendor_a-statics2 / pp-static / ppk-static / vendor_c-static / vendor_d-static
（均 .xqv9m8.icu）
```

待用户选择：A 维持 nginx（现状） / B Workers（推荐，确定性可控）。

## 八、为什么不能直接 CNAME：官方机制研究（2026-08-31 补充）

### 8.1 Cloudflare 官方机制

```text
Cloudflare 官方文档明确：proxied（橙云）CNAME 记录回源时，
默认以「原始记录名（你的域名）」作为 Host 头发送给源站，而不会
自动改成 CNAME 目标域名。

引用：Custom origin 文档（Advanced settings）
  "By default, Cloudflare sends the original custom hostname as the
   Host header."
  https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/start/advanced-settings/custom-origin/

要改 Host 头的官方能力是 Origin Rules（源站规则）：
  https://developers.cloudflare.com/rules/origin-rules/features/
  其中 Host header 覆盖（Host override）仅 Enterprise 套餐可用。
```

### 8.2 为什么 GCS 桶会 404

```text
GCS 通过 HTTP Host 头解析要访问的存储桶：
  storage.googleapis.com 收到请求后，用 Host 决定 bucket。

因此 CNAME 记录 pg-static.xqv9m8.icu ->
bizops-gcs-pg-static-sa.storage.googleapis.com 时：
  CF 连接目标 = 桶（SNI/连接用 CNAME 目标）
  Host 头 = pg-static.xqv9m8.icu（记录名，按官方默认行为）
  GCS 找不到名为 pg-static.xqv9m8.icu 的桶 -> 404
  （响应 content-length 133 = GCS Host 校验报错）
```

### 8.3 pg4 为什么例外（不可依赖）

```text
pg4-static.xqv9m8.icu 手动 CNAME -> bizops-gcs-pg4-static（东京桶）
验证通过（x-goog-generation 与桶直出一致）。

推测：CF 边缘节点对部分记录恰好把 CNAME 目标同时用于连接与 Host，
而该边缘未强制 Host 校验；属于边缘行为不一致的例外，
实测同 zone 其余 10 条 CNAME 大面积 404（vendor_a-statics 持续 20 分钟+）
即可证明不可全量依赖。
```

### 8.4 结论与可选路径

```text
当前套餐（Free/Pro）下「全部静态域名直接 CNAME 到 GCS 桶」：
  按官方机制不可行（404），pg4 为边缘例外，不能作为依据。

可靠路径：
  A. 维持现状：CF 黄云 -> 宝塔 nginx 改写 Host -> 巴西桶（稳定，已验证）
  B. Workers 改写 Host：CF 边缘 Worker fetch 时设置 Host 为桶域名，
     行为确定可控，免费额度内（推荐；提示词见第五节）
  C. 升级 Enterprise + Origin Rules Host override（成本高）
```

## 九、3 套 Argo 域静态 CNAME 全量测试与回滚（2026-08-31 下午）

### 9.1 测试范围

```text
zone：xqv9m8.icu / vendor_a-cdn-2026.icu / cdn-tokyo-bizops.icu
对象：每 zone 11 个静态子域（pg/pg3/pg4/pg5/vendor_a-statics/1/2/pp/ppk/
      vendor_c/vendor_d），A→宝塔(192.0.2.8, proxied) 改为
      CNAME→巴西 -sa 桶 storage.googleapis.com（proxied）
g759-static：无独立 DNS 记录（通配符覆盖），不参与
工具：docker/scripts/cf_static_cname_switch.py
      （--convert / --verify / --revert，逐条 3 次字节比对）
```

### 9.2 结果：32/33 失败，仅 pg4-static.xqv9m8.icu 可用

```text
vendor_a-cdn-2026.icu：11/11 全 404（GCS Host 校验）→ 已还原
cdn-tokyo-bizops.icu：11/11 全 404 → 已还原
xqv9m8.icu：当天上午试点 10/11 404 → 已还原；pg4 例外保留

按厂家失败清单（32 个域名）：
  PG：pg-static×3、pg3-static×3、pg5-static×3、pg4-static×2（xqv9m8 可用）
  vendor_a：vendor_a-statics/1/2 ×3 zone = 9
  PP：pp-static ×3
  PPK：ppk-static ×3
  vendor_c：vendor_c-static ×3
  PANDA：vendor_d-static ×3
```

### 9.3 验证与恢复

```text
还原后核验：32 条 A→宝塔(192.0.2.8, proxied) + 1 条 CNAME
  （pg4-static.xqv9m8.icu → bizops-gcs-pg4-static-sa，字节一致可用）
生产链路复测（真实对象 vs 桶直出）：
  pg4-static.{3 zone}/1/*.png、vendor_a-statics/_nuxt/*.js、
  pp-static/_probe/*.txt、vendor_d-static/__MACOSX/* 全部 200 且字节 SAME
platform-api static_hosts 3 套 Argo 域配置已在上游 master 发布
  （7d706e2a），无需再发布，当前生效链路 = CF 黄云→宝塔 nginx→桶。
```

### 9.4 巴西 / 香港 GCS S3 域名清单（CNAME 目标）

```text
巴西（圣保罗 southamerica-east1，-sa 桶）：
  pg-static→bizops-gcs-pg-static-sa.storage.googleapis.com
  pg3-static→bizops-gcs-pg3-static-sa.storage.googleapis.com
  pg4-static→bizops-gcs-pg4-static-sa.storage.googleapis.com
  pg5-static→bizops-gcs-pg5-static-sa.storage.googleapis.com
  vendor_a-statics→bizops-gcs-vendor_a-statics-sa.storage.googleapis.com
  vendor_a-statics1→bizops-gcs-vendor_a-statics1-sa.storage.googleapis.com
  vendor_a-statics2→bizops-gcs-vendor_a-statics2-sa.storage.googleapis.com
  pp-static→bizops-gcs-pp-static-sa.storage.googleapis.com
  ppk-static→bizops-gcs-ppk-static-sa.storage.googleapis.com
  vendor_c-static→bizops-gcs-vendor_c-static-sa.storage.googleapis.com
  vendor_d-static→bizops-gcs-vendor_d-static-sa.storage.googleapis.com
  g759-static→bizops-gcs-g759-static.storage.googleapis.com（本就在圣保罗）

香港/亚洲（东京 asia-northeast1，无后缀桶）：
  pg-static→bizops-gcs-pg-static.storage.googleapis.com
  pg3-static→bizops-gcs-pg3-static.storage.googleapis.com
  pg4-static→bizops-gcs-pg4-static.storage.googleapis.com
  pg5-static→bizops-gcs-pg5-static.storage.googleapis.com
  vendor_a-statics→bizops-gcs-vendor_a-statics.storage.googleapis.com
  vendor_a-statics1→bizops-gcs-vendor_a-statics1.storage.googleapis.com
  vendor_a-statics2→bizops-gcs-vendor_a-statics2.storage.googleapis.com
  pp-static→bizops-gcs-pp-static.storage.googleapis.com
  ppk-static→bizops-gcs-ppk-static.storage.googleapis.com
  vendor_c-static→bizops-gcs-vendor_c-static.storage.googleapis.com
  vendor_d-static→bizops-gcs-vendor_d-static.storage.googleapis.com
  g759-static→bizops-gcs-g759-static-asia.storage.googleapis.com

以上 24 个域名均已核实存在、公共可读，已发群。
```

### 9.5 结论

```text
3 套 Argo 域直接 CNAME→桶在 Free/Pro 下同样按官方机制 404，
Argo 不影响 Host 头行为。可靠改造仅剩：
  A. 维持现状（CF→宝塔 nginx 改写 Host→桶，已验证稳定）
  B. Workers 改写 Host（需 Workers 权限 token 或 Agent Lee 部署，
  提示词见第五节；DNS token 无 Workers 权限）
```

## 十、用户手动 CNAME 生效确认 + 全量清单 + 每 10 分钟监控（2026-08-31 晚）

### 10.1 用户手动 CNAME 实测生效（推翻「需长时间等待」疑虑）

```text
用户面板手动配置的 4 条 CNAME → 巴西 -sa 桶，等待约 20 分钟后全部生效：
  pg4-static.xqv9m8.icu ✅
  pg4-static.6qv8m.icu ✅
  vendor_a-statics1.cdn-tokyo-bizops.icu ✅
  vendor_a-statics1.cdn-tokyo-bizops.cyou ✅
逐条 3 次 cache-buster 字节比对：4/4 与桶直出完全一致（x-goog 头正常）。
说明：API 批量创建后 90s-4min 内验证 404，可能与边缘传播未完成有关；
面板手动创建 + 等待 ~20 分钟可正常生效。
```

### 10.2 线上 platform-api 已发布配置（用户手动改）

```text
后端 01/02/03 线上 /opt/pgserver/platform-api/conf/domains/*.json static_hosts
已扩为 22 套巴西 zone（共 242 个静态域名）：
  11 前缀 × 22 zone（pg/pg3/pg4/pg5/vendor_a-statics/1/2/pp/ppk/vendor_c/vendor_d）
另含 11 个外部测试域（g759-test/jdb-test/vendor_b-static*，非本账户 CF zone）
22 zone 清单见第九节文档 & 群消息。
```

### 10.3 每 10 分钟 CNAME 生效监控（已上线）

```text
工具：docker/scripts/cf_static_cname_monitor.py
运行：宝塔 cron */10（/root/bizops-cf-dns.env 存 DNS token，root-only 600）
逻辑：扫描 42 zone DNS → 提取 static 前缀且 CNAME→storage.googleapis.com 的记录
      → 逐条与桶直出字节比对 → 状态变化（新增/恢复/异常/移除）才发群
状态文件：/root/bizops-cf-cname-state.json（宝塔）
首次运行：4 条 CNAME 全 OK，仍 A→宝塔 238 条待配置（已发群）
```

### 10.4 朋友方案：Workers（与推荐 B 一致）

```text
用户反馈「另一个朋友是通过 Workers 实现的」——与本方案推荐 B 一致：
Workers 改写 Host 后 CF 直回源桶，行为确定可控，不依赖边缘传播。
提示词已备（第五节）。若手动 CNAME 出现持续 404 的域名，
对该域名走 Workers 即可，监控会自动纳入验证。
```

## 十一、Workers 限制与费用查询（2026-08-31，已发群）

### 11.1 API 查询结果

```text
42 个 zone 套餐：5 Pro（xqv9m8/t6qv8m/q7m9v8/vendor_a-cdn-2026/cdn-tokyo-bizops）
                + 37 Free
Workers 订阅/用量/account-settings 接口：当前 DNS token 无权限
  （Authentication error），需 Workers 权限 token 或面板查询
```

### 11.2 Workers 限制（官方 limits 页 2026-07 版）

```text
请求数    ：Free 100,000/天（UTC 重置）｜Paid 无上限（含 10M/月）
CPU       ：Free 10ms/请求｜Paid 默认 30s（可调至 5min）
内存      ：128MB（两者）
子请求    ：Free 50/请求｜Paid 10,000/请求
Worker 数 ：Free 100/账户｜Paid 500/账户
路由      ：每 zone 1,000 条（Free/Paid 同）；自定义域每 zone 100
代码体积  ：Free 3MB｜Paid 10MB
日志      ：Free 200k/天保留3天｜Paid 20M/月+$0.60/百万保留7天
```

### 11.3 Workers 费用（Standard 计费，账户级）

```text
基础订阅 ：$5/月
请求      ：含 10M/月，超出 $0.30/百万
CPU       ：含 30M CPU-ms/月，超出 $0.02/百万 CPU-ms
出网/带宽 ：免费
注意      ：Workers Static Assets 请求免费；普通代理请求（含缓存命中）按请求计费
```

### 11.4 我方方案费用预估

```text
路由：22 zone × 2 条通配（*-static.<zone>/* + vendor_a-statics*.<zone>/*）= 44 条
      （远低于 1000/zone 上限；只匹配静态子域，动态 api/games 不经过 Worker）
成本：日常约 $5/月；月 2000 万请求约 $8-13/月
对比：Argo 22 zone 全开 $110/月；Workers 全站静态代理 $5 起
部署前提：Workers 权限 token 或 Agent Lee 执行（提示词见第五节，需扩为 22 zone）
```

## 十二、全部静态域名 Workers + CNAME 全量方案（2026-08-31 深夜）

### 12.1 platform-api 配置同步 master（已完成）

```text
线上 9 个厂商文件已同步 master（后端 01/02/03 线上为用户手动编辑版）：
  pg/vendor_a/pp/popok/vendor_c/vendor_d：static_hosts 扩为 22 套 zone
    （含 3 套 Argo 域 xqv9m8/vendor_a-cdn-2026/cdn-tokyo-bizops），game_hosts 同步扩
    pg 游戏 20 个（t6qv8m/6qv8m 不在游戏列表，与线上一致）
  g759：线上为 g759-test.bxgjnet.com + g759-api.repair127.com（保持原样）
  jdb/vendor_b：与 master 一致
  校验：无 storage.googleapis.com 原始 S3 域名；JSON 全部合法
  fc.json：master 有、线上未部署，未动
```

### 12.2 Worker 部署（Agent Lee 提示词已发群，待执行）

```text
Worker：static-gcs-proxy（12 前缀 → -sa 桶映射，非静态前缀 passthrough）
路由：22 zone × 2 条通配 = 44 条
  a) *-static.<zone>/*   （pg/pg3/pg4/pg5/pp/ppk/vendor_c/vendor_d/g759）
  b) vendor_a-statics*.<zone>/* （vendor_a-statics/1/2）
建议开启 Workers Caching（如面板可选）
验证地址已写入提示词（pg /126/、vendor_a _nuxt js、vendor_d 根路径等）
```

### 12.3 待办（Worker 部署后）

```text
1. 批量把剩余 238 条静态 DNS 改 CNAME → -sa 桶（cf_static_cname_switch.py）
2. 逐条字节验证，失败立即还原
3. platform-api 发布（配置已同步 master）
4. 每 10 分钟监控继续跟踪（已上线）
5. 汇总发群
```

## 十三、Worker 复用方案（summer-wave-c94f，2026-09-01）

### 13.1 现状核实（用户手动配置）

```text
用户面板创建 Worker「summer-wave-c94f」并配置 3 个 zone：
  6qv8m.icu / cdn-tokyo-bizops.icu / cdn-tokyo-bizops.cyou
路由：*-static.<zone>/* + *-statics1.<zone>/* → summer-wave-c94f
实测：3 zone 静态请求直出 GCS（x-goog 头），Worker 已生效
缺口：*-statics1.* 只匹配 vendor_a-statics1，vendor_a-statics / vendor_a-statics2 未路由
```

### 13.2 复用方式（其他域名静态部分）

```text
所有 zone 的静态子域路由指向同一个 Worker，无需复制代码：
  1) *-static.<zone>/*            → summer-wave-c94f（9 前缀）
  2) vendor_a-statics*.<zone>/*       → summer-wave-c94f（vendor_a-statics/1/2）
19 个未配 zone × 2 = 38 条 + 已配 3 zone 补 vendor_a 覆盖 3 条 = 41 条
```

### 13.3 缓存优化

```text
1. Worker 设置 Cache 当前 false → 开启 Workers Caching
2. 19 个未配 zone 各加 Cache Rule「statics」：*-static.* / vendor_a-statics*.*，
   缓存资格=符合缓存条件，Edge TTL=7 天
   （已配 3 zone 已有；xqv9m8/vendor_a-cdn-2026 已有 Cache Everything Page Rule）
```

### 13.4 Agent Lee 批量提示词（已发群）

```text
19 zone × 2 路由 + 3 补丁路由 + Workers Caching + 19 Cache Rule
验证地址：pg /126/、vendor_a _nuxt js、vendor_a wondershow、vendor_d 根路径
输出：路由数（应 44）| Cache Rule 数（应 22）| 验证结果
```

### 13.5 后续

```text
路由全量生效后：批量 238 条 DNS A→CNAME（-sa 桶，DNS token 可代做）
→ 逐条字节验证（cf_static_cname_switch.py）→ platform-api 发布 → 汇总
```

## 十四、全量部署完成（2026-09-01，全权限 token）

### 14.1 完成清单

```text
1. Worker summer-wave-c94f 代码更新（API）：
   - 显式 12 前缀→桶映射（修复 g759-static 拼错桶名）
   - 非静态前缀 passthrough；CORS 头保留
   - 源码留存：docker/scripts/summer-wave-static-proxy.js
2. Workers 路由：22 zone × 4 条 = 90 条（0 失败）
   - *-static.<zone>/* （pg/pg3/pg4/pg5/pp/ppk/vendor_c/vendor_d/g759）
   - vendor_a-statics.<zone>/*、vendor_a-statics1.<zone>/*、vendor_a-statics2.<zone>/*
   - 说明：CF 路由通配符仅允许主机名开头，vendor_a-statics*.* 不合法，用显式 3 条
   - cdn-tokyo-bizops.icu/.cyou 保留旧 *-statics1.*（冗余无害）
3. Cache Rules：22 zone「statics」规则（仅静态子域 + Edge TTL 7 天）
   - 优化：3 个已有 zone 从「全部请求」收窄为「仅静态子域」（防 api 动态缓存）
   - 实测：同一静态 URL 第二次请求 cf-cache-status=HIT（Workers Caching 已生效）
4. DNS CNAME：238 条 A→CNAME（-sa 桶）+ 原 4 条 = 242 条全量 CNAME
   - 转换 0 失败（cf_static_cname_switch.py --convert 逐 zone）
5. 全量验证：242/242 静态域名与 GCS 桶直出字节一致（0 失败）
6. 监控：宝塔 cron */10 自动扫描，当前 242 CNAME 全 OK、A=0
7. platform-api：配置已同步 master（22 zone static/game hosts，无原始 S3）
```

### 14.2 安全事项

```text
全权限 token（sweet-surf-7056，IP 限 192.0.2.8/192.0.2.13）：
  仅存宝塔 /root/bizops-cf-workers.env（600），未入库/未发群；
  部署完成后建议在面板撤销该 token 或缩短 TTL。
```
