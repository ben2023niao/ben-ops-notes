---
id: "doc-8c823041e319"
title: "vendor_a 部分游戏加载不出来：排查记录与可人工打开的链接清单"
date: "2026-09-16T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "CDN", "DNS", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-16-%E3%80%90%E6%8E%92%E6%9F%A5%E3%80%91vendor_a%E9%83%A8%E5%88%86%E6%B8%B8%E6%88%8F%E5%8A%A0%E8%BD%BD%E4%B8%8D%E5%87%BA%E6%9D%A5-%E5%8F%AF%E4%BA%BA%E5%B7%A5%E6%89%93%E5%BC%80%E7%9A%84%E9%93%BE%E6%8E%A5%E6%B8%85%E5%8D%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-16-【排查】vendor_a部分游戏加载不出来-可人工打开的链接清单.md"
sourceSha256: "7894e8e5afaca8529c61838e71385c8f79e58acb6729d59b9eba91c855b9c76d"
sourceSystem: "project-doc"
---

# vendor_a 部分游戏加载不出来：排查记录与可人工打开的链接清单

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-16-【排查】vendor_a部分游戏加载不出来-可人工打开的链接清单.md`

> 整理日期：2026-09-16 00:00｜日期依据：文件名日期

时间：2026-09-16
反馈人：Saya（巴西线上，iPhone 14 Pro Max / iOS 26.6.1，香港 VPN，Safari + Chrome）
现象：点击游戏后加载页 logo 跑完就卡住，刷新后 1 分钟仍进不去；同时有 12 款游戏可以正常进入。

## 一、已确认的事实（都有实测数据）

1. 静态资源不缺：把 AWS S3 当作基准逐个游戏比对，12 款失败游戏在 GCS 里**一个都不缺**
   （S3 有的 key GCS 全都有），正常组的 12 款同样不缺。
2. 静态入口可达：12 款失败游戏的 index.html 在两个静态域名下都是 200，且字节数一致。
3. DNS 与边缘正常：12 个静态域名 + 2 个接口域名全部解析到 Cloudflare，health.json 都是 200。
4. WebSocket 可达：`/lifeservice/ws2` 在两个接口域名上握手都是 101 Switching Protocols。
5. 后端没有 protobuf 解析失败：最近 3 小时 `解析 Request 失败` 次数为 0。
6. 平台的域名池每个厂家有两个域名，启动时**随机二选一**：
   `<前缀>.xqv9m8.icu` 和 `<前缀>.vendor_a-cdn-2026.icu`；
   接口域名同理：`vendor_a-games.xqv9m8.icu` / `vendor_a-games.vendor_a-cdn-2026.icu`。
   → 所以同一个游戏、同一台手机，**换一个域名就可能表现不同**，符合"有的能进有的不能进"。
7. 平台的静态域名归属（来自 `/app/platform-api/conf/domains/vendor_a.json`）：
   失败游戏分布在 vendor_a-statics3 / vendor_a-statics4 / vendor_a-statics5 三组。

## 二、可人工打开的链接（12 款失败游戏 + 1 款对照）

每款给两个域名（A = xqv9m8.icu，B = vendor_a-cdn-2026.icu），两个都点一下对比。
注意：要真正登入游戏需要有效的 ssoKey，人工验证建议直接在站点面板点卡片；
下面这些链接主要用来确认「静态资源能不能加载、卡在哪一步」。

### 1. 骰子与掉落 Dice and Roll（gameID 595，目录 dad，桶 vendor_a-statics4）
https://vendor_a-statics4.xqv9m8.icu/dad/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/dad/
https://vendor_a-statics4.xqv9m8.icu/dad/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/dad/index.html

### 2. 三币猛虎 3 Coin Wild Tiger（gameID 622，目录 tcwt，桶 vendor_a-statics4）
https://vendor_a-statics4.xqv9m8.icu/tcwt/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/tcwt/
https://vendor_a-statics4.xqv9m8.icu/tcwt/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/tcwt/index.html

### 3. 财富钩 Fortune Hook（gameID 393，目录 bite，桶 vendor_a-statics4）
https://vendor_a-statics4.xqv9m8.icu/bite/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/bite/
https://vendor_a-statics4.xqv9m8.icu/bite/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/bite/index.html

### 4. 聚宝盆-豪华版 Money Pot DELUXE（gameID 541，目录 mpt2，桶 vendor_a-statics4）
https://vendor_a-statics4.xqv9m8.icu/mpt2/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/mpt2/
https://vendor_a-statics4.xqv9m8.icu/mpt2/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/mpt2/index.html

### 5. 超新星 Supernova（gameID 597，目录 gb，桶 vendor_a-statics4）
https://vendor_a-statics4.xqv9m8.icu/gb/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/gb/
https://vendor_a-statics4.xqv9m8.icu/gb/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/gb/index.html

### 6. 埃及遗产 Rise Of Egypt（gameID 711，目录 roe，桶 vendor_a-statics4）
https://vendor_a-statics4.xqv9m8.icu/roe/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/roe/
https://vendor_a-statics4.xqv9m8.icu/roe/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/roe/index.html

### 7. 罗马X 10000 ROMA X 10000（gameID 637，目录 rx10000，桶 vendor_a-statics3）
https://vendor_a-statics3.xqv9m8.icu/rx10000/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/rx10000/
https://vendor_a-statics3.xqv9m8.icu/rx10000/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/rx10000/index.html

### 8. 幸运草金币4x4 Clover Coins 4x4（gameID 590，目录 cc4x4，桶 vendor_a-statics3）
https://vendor_a-statics3.xqv9m8.icu/cc4x4/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cc4x4/
https://vendor_a-statics3.xqv9m8.icu/cc4x4/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cc4x4/index.html

### 9. 马戏团小丑 4096 Circus Joker 4096（gameID 518，目录 cj，桶 vendor_a-statics3）
https://vendor_a-statics3.xqv9m8.icu/cj/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cj/
https://vendor_a-statics3.xqv9m8.icu/cj/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cj/index.html

### 10. 祥狮招福 3 LUCKY LION（gameID 463，目录 tll，桶 vendor_a-statics3）
https://vendor_a-statics3.xqv9m8.icu/tll/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/tll/
https://vendor_a-statics3.xqv9m8.icu/tll/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/tll/index.html

### 11. 寻宝任务 Treasure Quest（gameID 307，目录 tsq，桶 vendor_a-statics3）
https://vendor_a-statics3.xqv9m8.icu/tsq/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/tsq/
https://vendor_a-statics3.xqv9m8.icu/tsq/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/tsq/index.html

### 12. 水晶777 豪华版 Crystal 777 DELUXE（gameID 447，目录 c7d，桶 vendor_a-statics5）
https://vendor_a-statics5.xqv9m8.icu/c7d/
https://vendor_a-statics5.vendor_a-cdn-2026.icu/c7d/
https://vendor_a-statics5.xqv9m8.icu/c7d/index.html
https://vendor_a-statics5.vendor_a-cdn-2026.icu/c7d/index.html

### 对照：亚瑟王 King Arthur（gameID 214，目录 ka，桶 vendor_a-statics4）——用户反馈能进
https://vendor_a-statics4.xqv9m8.icu/ka/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/ka/
https://vendor_a-statics4.xqv9m8.icu/ka/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/ka/index.html

## 三、人工验证建议（照这个顺序做，一次就能定位）

1. 两个域名各点一次同一个游戏：如果 A 能进、B 不能进（或反过来），就是域名池里有一个域名有问题。
2. 手机浏览器打开 `https://vendor_a-statics4.xqv9m8.icu/cdn-cgi/trace`，看 `loc=`：
   不是 BR/SG/HK/AE 的话会命中 Worker 的国家白名单被 403。
3. 卡住时在手机上抓一下控制台/网络（Safari 可用"显示网页检查器"，Chrome 可用 remote debugging）：
   把 `index.html`、`src/*.bundle.*.js`、`/req` 三个请求的状态码和耗时截图发我。
4. 换巴西 VPN 再测同样的游戏：如果巴西能进、香港不能进，就是链路或国家策略问题，不是资源问题。

## 四、结论与后续

从目前证据看：**这 12 款游戏的静态资源在 GCS 上是完整的（与 AWS S3 一一对应，零缺失）**，
CDN 与接口域名、WebSocket 都正常，后端也没有解析类报错。
因此"加载不出来"更可能出在（按可能性排序）：

1. 平台启动时随机选的域名里，有一个在**客户端所在网络**下不可用（香港 VPN 环境）；
2. 账号/线路差异：本次排查用的测试账号 55955158380 的游戏列表里没有这 12 款，
   测试账号 ONBRLTEST_999 才看得到，说明列表是按线路/账号下发的，需要按测试账号复现；
3. 客户端侧的缓存（静态资源浏览器缓存 7 天）。

下一步需要测试同学配合：用出问题的账号 + 香港 VPN，按第三节第 1、2、3 步各抓一次，
把两个域名的结果和截图发回来，就能确定是哪一种。
