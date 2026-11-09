---
id: "doc-638124df7083"
title: "看自己出口国家（loc 不是 BR/SG/HK/AE 就会被 Worker 国家白名单 403）"
date: "2026-09-16T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "CDN", "DNS", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-16-vendor_a%E5%A4%B1%E8%B4%A5%E6%B8%B8%E6%88%8FURL%E6%B8%85%E5%8D%95.txt"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-16-vendor_a失败游戏URL清单.txt"
sourceSha256: "dc353adf2352499fbabc722ee525978552d21e0bddd78d8af2c0792aaf773c71"
sourceSystem: "project-doc"
---

# 看自己出口国家（loc 不是 BR/SG/HK/AE 就会被 Worker 国家白名单 403）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609160000-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BCDN%2BDNS-%E7%9C%8B%E8%87%AA%E5%B7%B1%E5%87%BA%E5%8F%A3%E5%9B%BD%E5%AE%B6%EF%BC%88loc%20%E4%B8%8D%E6%98%AF%20BR-SG-HK-AE%20%E5%B0%B1%E4%BC%9A%E8%A2%AB%20Worker%20%E5%9B%BD%E5%AE%B6%E7%99%BD%E5%90%8D%E5%8D%95%20403%EF%BC%89.md)

> 整理日期：2026-09-16 00:00｜日期依据：文件名日期

vendor_a 部分游戏加载不出来 —— 可人工打开的 URL 清单
整理时间：2026-09-16
来源：测试反馈（巴西线上，iPhone 14 Pro Max / iOS 26.6.1，香港 VPN，Safari + Chrome）
说明：每款游戏给出两个域名的链接（A = xqv9m8.icu，B = vendor_a-cdn-2026.icu），
      两个都点一次做对比；加 /index.html 是直接打开游戏入口文件。
      要真正登入游戏需要有效的 ssoKey，人工验证建议直接在站点面板点卡片。
      全部链接已于 2026-09-16 实测，返回 200。

========== 失败组（12 款） ==========

1) 骰子与掉落 Dice and Roll    gameID 595    目录 dad    桶 vendor_a-statics4
https://vendor_a-statics4.xqv9m8.icu/dad/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/dad/
https://vendor_a-statics4.xqv9m8.icu/dad/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/dad/index.html

2) 三币猛虎 3 Coin Wild Tiger    gameID 622    目录 tcwt    桶 vendor_a-statics4
https://vendor_a-statics4.xqv9m8.icu/tcwt/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/tcwt/
https://vendor_a-statics4.xqv9m8.icu/tcwt/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/tcwt/index.html

3) 财富钩 Fortune Hook    gameID 393    目录 bite    桶 vendor_a-statics4
https://vendor_a-statics4.xqv9m8.icu/bite/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/bite/
https://vendor_a-statics4.xqv9m8.icu/bite/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/bite/index.html

4) 聚宝盆-豪华版 Money Pot DELUXE    gameID 541    目录 mpt2    桶 vendor_a-statics4
https://vendor_a-statics4.xqv9m8.icu/mpt2/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/mpt2/
https://vendor_a-statics4.xqv9m8.icu/mpt2/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/mpt2/index.html

5) 超新星 Supernova    gameID 597    目录 gb    桶 vendor_a-statics4
https://vendor_a-statics4.xqv9m8.icu/gb/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/gb/
https://vendor_a-statics4.xqv9m8.icu/gb/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/gb/index.html

6) 埃及遗产 Rise Of Egypt    gameID 711    目录 roe    桶 vendor_a-statics4
https://vendor_a-statics4.xqv9m8.icu/roe/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/roe/
https://vendor_a-statics4.xqv9m8.icu/roe/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/roe/index.html

7) 罗马X 10000 ROMA X 10000    gameID 637    目录 rx10000    桶 vendor_a-statics3
https://vendor_a-statics3.xqv9m8.icu/rx10000/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/rx10000/
https://vendor_a-statics3.xqv9m8.icu/rx10000/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/rx10000/index.html

8) 幸运草金币4x4 Clover Coins 4x4    gameID 590    目录 cc4x4    桶 vendor_a-statics3
https://vendor_a-statics3.xqv9m8.icu/cc4x4/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cc4x4/
https://vendor_a-statics3.xqv9m8.icu/cc4x4/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cc4x4/index.html

9) 马戏团小丑 4096 Circus Joker 4096    gameID 518    目录 cj    桶 vendor_a-statics3
https://vendor_a-statics3.xqv9m8.icu/cj/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cj/
https://vendor_a-statics3.xqv9m8.icu/cj/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cj/index.html

10) 祥狮招福 3 LUCKY LION    gameID 463    目录 tll    桶 vendor_a-statics3
https://vendor_a-statics3.xqv9m8.icu/tll/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/tll/
https://vendor_a-statics3.xqv9m8.icu/tll/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/tll/index.html

11) 寻宝任务 Treasure Quest    gameID 307    目录 tsq    桶 vendor_a-statics3
https://vendor_a-statics3.xqv9m8.icu/tsq/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/tsq/
https://vendor_a-statics3.xqv9m8.icu/tsq/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/tsq/index.html

12) 水晶777 豪华版 Crystal 777 DELUXE    gameID 447    目录 c7d    桶 vendor_a-statics5
https://vendor_a-statics5.xqv9m8.icu/c7d/
https://vendor_a-statics5.vendor_a-cdn-2026.icu/c7d/
https://vendor_a-statics5.xqv9m8.icu/c7d/index.html
https://vendor_a-statics5.vendor_a-cdn-2026.icu/c7d/index.html

========== 正常组对照（用户反馈可以进，挑 3 款） ==========

亚瑟王 King Arthur    gameID 214    目录 ka    桶 vendor_a-statics4
https://vendor_a-statics4.xqv9m8.icu/ka/
https://vendor_a-statics4.vendor_a-cdn-2026.icu/ka/
https://vendor_a-statics4.xqv9m8.icu/ka/index.html
https://vendor_a-statics4.vendor_a-cdn-2026.icu/ka/index.html

宙斯 Zeus    gameID 252    目录 zeus    桶 vendor_a-statics5
https://vendor_a-statics5.xqv9m8.icu/zeus/
https://vendor_a-statics5.vendor_a-cdn-2026.icu/zeus/
https://vendor_a-statics5.xqv9m8.icu/zeus/index.html
https://vendor_a-statics5.vendor_a-cdn-2026.icu/zeus/index.html

吉利财神 vendor_b Caishen    gameID 144    目录 cai    桶 vendor_a-statics3
https://vendor_a-statics3.xqv9m8.icu/cai/
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cai/
https://vendor_a-statics3.xqv9m8.icu/cai/index.html
https://vendor_a-statics3.vendor_a-cdn-2026.icu/cai/index.html

========== 辅助排查链接 ==========

https://vendor_a-statics4.xqv9m8.icu/cdn-cgi/trace

https://vendor_a-statics.xqv9m8.icu/health.json
https://vendor_a-statics.vendor_a-cdn-2026.icu/health.json
https://vendor_a-statics1.xqv9m8.icu/health.json
https://vendor_a-statics1.vendor_a-cdn-2026.icu/health.json
https://vendor_a-statics2.xqv9m8.icu/health.json
https://vendor_a-statics2.vendor_a-cdn-2026.icu/health.json
https://vendor_a-statics3.xqv9m8.icu/health.json
https://vendor_a-statics3.vendor_a-cdn-2026.icu/health.json
https://vendor_a-statics4.xqv9m8.icu/health.json
https://vendor_a-statics4.vendor_a-cdn-2026.icu/health.json
https://vendor_a-statics5.xqv9m8.icu/health.json
https://vendor_a-statics5.vendor_a-cdn-2026.icu/health.json

https://vendor_a-games.xqv9m8.icu/health
https://vendor_a-games.vendor_a-cdn-2026.icu/health

wss://vendor_a-games.xqv9m8.icu/lifeservice/ws2
wss://vendor_a-games.vendor_a-cdn-2026.icu/lifeservice/ws2

========== 人工验证步骤 ==========

1. 同一款游戏，A、B 两个域名各点一次。若一个能进、一个不能进，就是域名池里有一个域名有问题。
2. 打开上面的 cdn-cgi/trace，确认 loc= 是 BR/SG/HK/AE（香港 VPN 正常应为 HK）。
3. 卡住时抓 index.html、src/*.bundle.*.js、/req 三个请求的状态码与耗时，截图留存。
4. 换巴西 VPN 再测同样游戏：巴西能进、香港不能进 = 链路或国家策略问题，不是资源问题。

========== 本次比对结论 ==========

- 以 AWS S3 为基准逐游戏比对：12 款失败游戏在 GCS 里缺失 0（正常组同样 0），静态资源完整。
- 12 款游戏的 index.html 在两个域名下均 200，且字节数一致。
- 12 个静态域名 + 2 个接口域名 DNS/health 全 200；/lifeservice/ws2 握手 101。
- 后端最近 3 小时无 protobuf 解析失败记录。
- 平台按 conf/domains/vendor_a.json 的域名池随机二选一下发静态域名与接口域名，
  因此同机不同域名表现可能不同，这是当前最可疑的方向。
