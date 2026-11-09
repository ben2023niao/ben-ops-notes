---
id: "doc-c156727f1b7e"
title: "Coin of Lightning"
date: "2026-09-10T23:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "MySQL", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-10-2330-%E3%80%90%E6%8E%92%E6%9F%A5%E3%80%91vendor_a623%E6%89%93%E4%B8%8D%E5%BC%80%E6%A0%B9%E5%9B%A0%E5%AE%9A%E4%BD%8D%2Bhtt%E8%B5%84%E6%BA%90%E9%83%A8%E7%BD%B2%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-10-2330-【排查】vendor_a623打不开根因定位+htt资源部署记录.md"
sourceSha256: "a50c935e783a0c45aa2a65cf314699d056a98f5b482d88ed412df742137158c6"
sourceSystem: "project-doc"
---

# Coin of Lightning

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609102330-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BPython-Coin%20of%20Lightning.md)

> 整理日期：2026-09-10 23:30｜日期依据：文件名日期

时间：2026-09-10 23:30（Asia/Manila）
项目：某业务公司 / PGServer master
结果：✅ htt 资源已补到 GCS 三路 + client.git；
❗真因确认不是静态资源，而是 `sso-login.api` 验签失败（后端商户密钥问题）

## 一、现象与初始判断修正

623（闪电币 Coin of Lightning，目录 `col`，前缀 `vendor_a-statics5`）点开一直加载不出来。

此前已做的静态覆盖（561 文件、checksum 全等、CDN 200）并未解决，说明卡点不在静态层。
用真实浏览器（bot 容器 Chromium，`game_load_probe.py`）带 `ssoKey` 打开后确认：

```text
title: "Coin of Lightning"
Success to load scene db://assets/Scene/MainGame.scene   （引擎/场景加载成功）
request_failed: []                                        （静态资源 0 失败）
404  https://vendor_a-statics5.cdn-tokyo-bizops.icu/col/htt/smallicon/setting.json
500  https://vendor_a-games.cdn-tokyo-bizops.icu/sso-login.api
```

## 二、htt 资源部署（厂商补包）

C++ 提供 `htt.zip`（7 个文件 / 892KB），要求放到 static5 的 col 下。

```text
htt/smallicon/setting.json
htt/smallicon/lang/{en-US,hi-IN,id-ID,pt-BR,vi-VN,zh-CN}/strings.json
```

目标路径：`<game>/htt/...`（与本游戏请求的 `/col/htt/smallicon/setting.json` 一致）。
注意：全部 vendor_a 游戏的 git 仓库里此前**都没有** `htt/` 目录，属新增目录。

### 双写位置

```text
GCS（7 个文件，全部到位）
  gs://bizops-gcs-vendor_a-statics5-sa/col/htt/
  gs://bizops-gcs-vendor_a-statics5/col/htt/
  gs://bizops-game-statics-gcs/vendor_a-statics5/col/htt/

client.git
  e93428a04a -> 1c2aa9737a
  "vendor_a: add missing htt/smallicon resources for 623 (col)"
  新增 7 个文件，全部 A(新增)，0 修改 0 删除
```

### 验证

```text
CDN  https://vendor_a-statics5.cdn-tokyo-bizops.icu/col/htt/smallicon/setting.json  -> 200
     （部署前 404；内容为合法 JSON，含 CloseClick / CloseAutoChange /
       IgnoreEventNo / ApiIdToTitleName）
浏览器重放 /col/  -> htt 的 404 消失，静态失败请求 0
场景仍正常：Success to load scene (146ms)
```

### ⚠️ 后续更正：htt 是测试资源，已回滚删除

厂商随后确认 `htt/smallicon` 属于**测试资源**，不应对生产生效，要求删除。

```text
GCS 删除（只删我们加的那一份）
  gs://bizops-gcs-vendor_a-statics5-sa/col/htt/          7 -> 0
  gs://bizops-gcs-vendor_a-statics5/col/htt/             7 -> 0
  gs://bizops-game-statics-gcs/vendor_a-statics5/col/htt/ 7 -> 0

client.git 回滚（revert 提交，不改写历史）
  1c2aa9737a -> e1223a93c2 "Revert vendor_a: add missing htt/smallicon ..."
  远端 vendor_astatic5/col/htt 文件数 = 0

col 生产静态未受影响：561 文件 + 1 目录别名 = 562 对象，CDN 200
```

残留：Worker 的 Cache API 仍缓存这两条 URL 的旧 200（7 天 TTL）。

```text
GET  .../col/htt/smallicon/setting.json -> 200（内容就是被删的测试文件 md5 1b707582…）
HEAD 同一 URL                          -> 404（Worker 只缓存 GET）
GCS 直连                                -> 404（源站已干净）
```

Cache API 不受 zone purge 影响，只能用「缓存盐升级 + 重新部署 Worker」失效，
需要一个对账户级 Workers API 有效的 Cloudflare 令牌。

### ✅ 已完成：Worker 缓存盐升级（2026-09-10 09:13:28Z）

```text
令牌可用性更正：
  cfat 令牌调 /user/tokens/verify 仍 401，
  但 /accounts/{acct}/workers/scripts 的 GET/PUT 均 success
  -> 之前判断"令牌失效"不准确，user 级 verify 端点对这类令牌不适用

备份：/root/bizops-cf-backups/20260910-htt-purge/summer-wave-c94f.before.js
      与本地版本逐行 diff：只差缓存盐，无其它改动

部署：PUT /accounts/{acct}/workers/scripts/summer-wave-c94f
      CACHE_SALT: v4-20260910-vendor_a345 -> v5-20260910-vendor_a-backfill
      modified_on=2026-09-10T09:13:28.650218Z，脚本 3276B -> 3304B

验证：
  GET  /col/htt/smallicon/setting.json            -> 404（部署前因 Worker 缓存仍 200）
  GET  /col/htt/smallicon/lang/zh-CN/strings.json -> 404
  col 生产：index.html / config.d02cb.json / cocos-js/cc.af2c4.js / game.d02cb.zip -> 200
  全前缀抽检：vendor_a-statics/aa、vendor_a1/lj、vendor_a3/mp2、vendor_a4/dad、vendor_a5/c7d、
              pp-static、pg-static -> 全部 200
  new_game_static_check.py -> 32/32 OK
  浏览器复验 /col/ -> 场景正常（MainGame.scene 144ms），静态 0 失败
```

顺带完成：缓存盐升级即等于 **vendor_a 全站 CDN 缓存整体刷新**（此前挂起的需求）。

## 三、剩余卡点：sso-login.api 验签失败（后端）

```text
HTTP 500  https://vendor_a-games.cdn-tokyo-bizops.icu/sso-login.api

prod-01 /opt/pgserver/logs/bizops-vendor_a-release-01/vendor_a.log
  ERROR: Exception occurred while handling uri: sso-login.api
    File "/app/vendor_a/vendor_a.py", line 2212, in sso_login
      user_info = await get_user_info_by_tkstr(token_str)
    File "/app/vendor_a/vendor_a.py", line 960, in get_user_info_by_tkstr
      raise ValueError(...)
  ValueError: check_jwt_token exception:invalid 敏感凭据：[已脱敏] verification failed
```

定位线索：

```text
platform-api/main.py            测试入口用 make_jwt_token("testvendor_a","testvendor_a", params)
platform-api/agent_apis.py:676  tkstr = jwt_encode.make_jwt_token(merchantId, secret, params)
platform-api/agent_apis.py:248  merchant_info = await risk_merchant.get_merchant_from_mysql(app_key)
share.so                        share.check_jwt_token / share_libs/jwt_encode.py
                                get_merchant_from_mysql / merchant_config / app_key
  -> 验签用的商户密钥来自 MySQL（按 app_key 查商户）
```

本次 ssoKey 的 `app_key = SHONBRLTESTMCH1790`（`plat_id=ONBRLTEST`，测试商户）。
vendor_a 侧按该 app_key 取到的 secret 与签发方不一致（或该商户未登记）→ 验签失败。

**注意**：`check_jwt_token` 的验签发生在过期校验之前，因此**过期 token 也报同一句
`Signature verification failed`**，复测必须用新签发的 ssoKey。

需要 C++/运维确认：以哪一侧的商户密钥为准，把 `SHONBRLTESTMCH1790` 的 secret 对齐。

## 四、本轮新增工具

```text
docker/scripts/game_load_probe.py
  在带 Playwright 的容器里加载游戏 URL，输出：
  失败请求 / HTTP>=400（去重）/ console / pageerror / 页面文本 / title
  用法（容器内）：
    python3 /tmp/game_load_probe.py "<game url>" --wait 90
```

## 五、结论

1. 静态侧：623 的 561 个文件 + 补齐的 7 个 htt 文件，GCS 三路与 git 完全一致，CDN 全部 200。
2. 客户端侧：引擎与场景加载正常，静态请求无失败。
3. 阻塞点：`sso-login.api` 因 SSO JWT 验签失败返回 500 —— 属后端商户密钥配置，
   与静态资源、CDN、GCS 无关。

> 注：第 1 条的 htt 部分后来已按厂商要求回滚（测试资源），见第二节更正。

## 六、给开发的修复建议（已发群）

### 问题 A：sso-login 验签失败（当前唯一阻塞）

```text
现象 : https://vendor_a-games.cdn-tokyo-bizops.icu/sso-login.api -> 500
后端 : vendor_a.py:960 get_user_info_by_tkstr
       ValueError: check_jwt_token exception: invalid 敏感凭据：[已脱敏] verification failed

要点 :
  - 与 token 过期无关：用有效期内的 token 实测同样失败
    （验签先于过期校验，过期也报同一句 -> 复测必须用新签发的 ssoKey）
  - 与 623 无关：同一 ssoKey 打开 c7d(447) 也是 500 -> 商户层面问题
  - 密钥来源：share.get_merchant_from_mysql(app_key) 的 mapimd5 字段
    (platform-api/agent_apis.py:248/255)

修复建议 :
  1) 对齐商户 app_key=SHONBRLTESTMCH1790 的 mapimd5：
     签发方签 ssoKey 用的 secret 必须等于 vendor_a 读取的 MySQL 商户表 mapimd5
  2) 确认签发方与 vendor_a 读的是同一个库、同一行商户（警惕多环境串库）
  3) 换用新被测商户时，需先在商户表登记并让 vendor_a 能读到
  4) 复测用新签发 ssoKey（有效期 10 分钟）
```

### 问题 B：htt/smallicon（结论已更正为测试资源，不需要修）

调查期间发现每个 TaDa 客户端都会请求
`<game>/htt/smallicon/setting.json` 与 `<game>/htt/smallicon/lang/<locale>/strings.json`，
并整理过「187 个游戏 / 186 个受影响」的清单（`affected_games.tsv`）。
厂商确认该目录是测试资源后，本项作废，已回滚删除；清单仅留作分析记录。

```text
内容通用性（当时验证）：ali 与 col 的 setting.json md5 完全一致 1b70758291ad24c303fb6b5831ed757a
```
