---
id: "doc-bff788e7dbec"
title: "2026-07-16 TADA 阿里巴巴 ali 规则界面 loading 修复记录"
date: "2026-07-16T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "监控告警", "自动化", "CDN", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-07-16-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91TADA%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4ali%E8%A7%84%E5%88%99%E7%95%8C%E9%9D%A2loading%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-07-16-【修复Bug】TADA阿里巴巴ali规则界面loading修复记录.md"
sourceSha256: "64907852b2f9f7b08f22a30adf6d6c39e2e99f69192ff9fd4518d0a8edd990bd"
sourceSystem: "project-doc"
---

# 2026-07-16 TADA 阿里巴巴 ali 规则界面 loading 修复记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-07-16-【修复Bug】TADA阿里巴巴ali规则界面loading修复记录.md`

> 整理日期：2026-07-16 00:00｜日期依据：文件名日期

本文记录 TADA 阿里巴巴点击右下角齿轮菜单中的叹号后，规则界面长期停留在 loading 的排查、静态兼容对象补齐、规则模板路由修复、TADA 双后台发布、GCS 双桶同步、Cloud CDN 刷新和浏览器验证过程。

## 问题现象

游戏映射：

```text
游戏：阿里巴巴 / AliBaba
GameID：110
静态代码：ali
宝塔源目录：/www/wwwroot/tada-statics/ali
```

游戏主场景可以加载，但点击齿轮菜单中的叹号后，规则界面只显示棕色遮罩和白色 loading 动画，无法显示规则正文。

浏览器 Network 中可见失败的规则公共配置请求：

```text
GET /ali/htt/smallicon/setting.json
HTTP 404
响应：NoSuchKey
```

## 排查过程

### 1. 确认游戏和目录

平台游戏映射确认：

```text
110: {"name": "ali", "desc": "AliBaba(阿里巴巴)"}
```

宝塔存在完整阿里巴巴包：

```text
/www/wwwroot/tada-statics/ali
```

初始源目录共有 155 个游戏文件；与 GCS live、GCS backup 比较时，没有发现常规 `ali` 游戏包文件差集。因此问题不是阿里巴巴主包整体漏同步。

### 2. 定位规则公共配置路径

公开静态根路径正常：

```text
https://tada-statics.m7v8k3.cyou/smallicon/setting.json
HTTP 200
size: 1528 bytes
```

阿里巴巴旧 Cocos 包实际请求带游戏前缀和 `htt` 兼容层的路径：

```text
https://tada-statics.m7v8k3.cyou/ali/htt/smallicon/setting.json
HTTP 404
```

规则公共配置存在于静态根目录，但缺少阿里巴巴旧包需要的兼容对象别名。

### 3. 浏览器候选修复预演

正式发布前，在一次性 Docker Chromium 会话内只对缺失路径做响应映射预演，不修改线上内容：

```text
/ali/htt/smallicon/setting.json
  -> /smallicon/setting.json
```

预演后阿里巴巴成功越过 TaDa loading，进入葡语介绍页并显示 `Continuar`，证明兼容对象方向正确。预演截图不作为最终线上成功证据。

### 4. 定位第二层规则模板路由问题

兼容对象上线后，正式 Docker Chromium 验证确认以下请求均恢复为 `HTTP 200`：

```text
/ali/htt/smallicon/setting.json
/pt-BR/intro?game=110
/comm_intro_1.0.4.js
规则页所需的 13 个 _nuxt 脚本
```

但是点击齿轮菜单中的叹号后，规则页仍停留在棕色 loading。继续检查服务端模板选择代码发现，旧版规则组件需要 `intro1.html`，而对应分支只包含其他 GameID，没有包含阿里巴巴 `110`。

对相同的线上规则请求做一次性浏览器 A/B 验证：

```text
A：game=110 使用线上默认 intro.html
   size: 7703 bytes
   结果：25 秒后仍显示 loading

B：game=110 仅在本地测试会话替换为 intro1.html
   size: 11085 bytes
   SHA256: 93c35a5c03bf2a81100ddfb5e6a59846a7b528432c948db28f493e8cb854a184
   结果：Vue 页面成功 hydration，title=Ali Baba - instructions，loading 消失
```

该 A/B 结果确认最终阻断点就是 `GameID=110` 漏进 `intro1.html` 分支。

## 根因

本问题由两个连续阻断点叠加造成。

### 根因一：旧 Cocos 兼容对象缺失

阿里巴巴使用较旧的 Cocos 静态包。规则/说明组件启动时通过相对 `htt` 路径读取公共设置：

```text
ali/htt/smallicon/setting.json
```

现有静态资源只提供根对象：

```text
smallicon/setting.json
```

GCS backend bucket 不会把两个对象名自动映射为同一文件，因此浏览器得到 `404 NoSuchKey`。规则组件缺少初始化配置后无法完成加载，界面持续显示 loading。

### 根因二：阿里巴巴 GameID 漏出旧规则模板分支

阿里巴巴规则页使用旧版 `comm_intro_1.0.4.js`，必须配套 `intro1.html`。服务端模板选择集合没有 `110`，导致请求错误返回默认 `intro.html`。脚本文件虽然全部为 `HTTP 200`，但页面模板与客户端规则组件不匹配，Vue 无法完成 hydration，因此界面继续显示 loading。

## 修复前状态记录

目标对象修复前不存在，已在宝塔留下缺失状态记录：

```text
/root/dbqp-static-import/ali-setting-before-20260716-213608.txt
```

修复采用新增兼容对象，不覆盖阿里巴巴已有游戏文件。

## 修复内容

### 1. 补齐旧 Cocos 静态兼容对象

以现有 TADA 根公共配置为唯一来源：

```text
/www/wwwroot/tada-statics/smallicon/setting.json
```

新增宝塔兼容文件：

```text
/www/wwwroot/tada-statics/ali/htt/smallicon/setting.json
```

文件校验：

```text
size: 1528 bytes
mode: 0644
SHA256: c457c578561fd3016da699855d3f482a93eda3b0e42bc44659f801cf184592a0
```

同步两个 GCS 对象：

```text
gs://dbqp-gcs-tada-statics/ali/htt/smallicon/setting.json
generation: 1784208974918779

gs://dbqp-game-statics-gcs/tada-statics/ali/htt/smallicon/setting.json
generation: 1784208981420867
```

两个对象属性一致：

```text
Content-Type: application/json
Cache-Control: public,max-age=3600
Content-Length: 1528
GCS md5: G3B1gpGtJMMD+2tYMe11eg==
```

### 2. 修正规则模板路由

在两个兼容入口中同时把阿里巴巴 `GameID=110` 加入 `intro1.html` 分支：

```text
tada/tada.py
tada/jili.py
```

修复后的分支：

```python
if game in {"110", "593", "594", "573", "574", "460", "379", "547", "392"}:
    file_path = f"./{lang}/intro1.html"
```

本地校验：

```text
python3 -m py_compile tada/tada.py tada/jili.py：通过
GameID 110 模板映射断言：通过
git diff --check：通过
```

代码版本：

```text
commit: 7a76d354
subject: fix: route TADA Ali Baba rules to legacy intro
branch: master
push: 完成
```

## Cloud CDN 刷新

从线上配置读取 `default.static_hosts` 的 22 个 `tada-statics.*` 域名，对每个 host 刷新精确路径：

```text
/ali/htt/smallicon/setting.json
```

operation 结果：

```text
目标：22
DONE：22
其他状态：0
```

operation 清单：

```text
/root/dbqp-static-import/tada-ali-setting-invalidation-ops-20260716-2136.txt
```

## 公开对象验证

GCS live 和 backup 公开 URL 均验证通过：

```text
HTTP 200
size: 1528 bytes
SHA256: c457c578561fd3016da699855d3f482a93eda3b0e42bc44659f801cf184592a0
```

对 22 个 `tada-statics.*` 域名请求不带 cache-bust 的精确路径，结果：

```text
HTTP 200：22/22
size=1528：22/22
SHA256 匹配：22/22
Content-Type=application/json：22/22
失败：0
```

## Docker Chromium 功能验证

使用本地 `dbqp-ben-bot:latest` 容器内的 Chromium，从公开 TADA 巴西线上测试大厅启动：

```text
https://ind-h5.dbqpplus999.com/tadabronline/
```

验证参数与路径：

```text
lang=pt
GameID=110
公开静态路径=/ali/
```

正式验证不使用请求拦截或临时脚本注入。已确认：

```text
/ali/htt/smallicon/setting.json -> HTTP 200
葡语介绍页显示 -> 通过
Continuar -> 通过
PLAY -> 通过
阿里巴巴转轴主场景 -> 通过
```

### 规则模板修复后的正式点击结果

代码发布后，使用真实游戏会话完整执行：

```text
TADA 大厅 -> GameID 110 -> Continuar -> PLAY
-> 阿里巴巴主转轴 -> 右下角齿轮 -> 叹号
```

验证结果：

```text
/ali/htt/smallicon/setting.json：HTTP 200
/pt-BR/intro?game=110：HTTP 200，已返回 intro1.html
comm_intro_1.0.4.js：HTTP 200
规则页标题：Ali Baba - instructions
旧棕色 loading：已消失
规则页框架和返回按钮：已显示
规则正文：未显示，黑屏
```

浏览器最终定位到唯一业务资源失败：

```text
GET /_nuxt/43b425ca4f1c87250140.js
HTTP 404
```

该文件是 `intro1` webpack runtime 中 `components/intro-id-ali` 的专用 chunk：

```text
webpack chunk id: 1045
webpack module id: 2224
component: components/intro-id-ali
```

因此当前状态不能判定为完整修复通过。

### 四模板同参数矩阵验证

为排除模板选择仍有误，保留同一个真实阿里巴巴会话的有效规则参数，并行验证四个模板：

```text
intro：不 hydration，正文长度 0
intro1：识别 Ali Baba，缺 43b425ca4f1c87250140.js
intro2：识别 Ali Baba，缺 2fa50ef1c953510b3e43.js
intro3：不 hydration，正文长度 0
```

结论：`110 -> intro1.html` 分支选择正确；剩余问题是阿里巴巴规则专用资源缺失，不是 `cocos.com` 请求。`cocos.com` 是旧 WebView 导航/占位噪音，不是当前黑屏的阻断请求。

## TADA 双后台发布

发布参数：

```text
target: tada
version: 7a76d354
strategy: single-build
image-transfer: internal
```

结果：

```text
backend-01 / dbqp-tada-release-01：成功
backend-02 / dbqp-tada-release-02：成功
汇总：成功 2，失败 0
```

两台容器一致性：

```text
image: pgserver:master-7a76d354
image sha256: 99b1957980e55a1a8776c0a64558cdbbdffc6b86c0b9e1c9c92b564fb74ed68d
9096：通过
8765：通过
```

两台直连规则响应一致：

```text
size: 11085 bytes
SHA256: 93c35a5c03bf2a81100ddfb5e6a59846a7b528432c948db28f493e8cb854a184
intro1 marker: OK
```

## 缺失资源来源排查

已检查以下位置，均未找到 `43b425ca4f1c87250140.js`：

```text
当前 Git 工作树和完整 Git 历史
宝塔 tada-statics / tada-statics1 / tada-statics2
/www/server/ops/tada-static-20260714/tadaallstatic.zip
backend-01 / backend-02 的历史 pgserver 镜像
现有全部 DBQP GCS live/backup bucket
```

TaDa 官方公开试玩可以进入同一 `ali` 包，但本次探针在当前网络环境停留于 TaDa 首屏，没有返回规则 chunk，未将其作为文件来源。

2026-07-16 晚间与开发确认：开发已知该资源问题，计划次日更新正式资源解决。为避免和正式资源冲突，本次不制作临时规则 HTML、不人工重造 webpack chunk。

## 2026-07-17 开发资源更新与重新发布

开发于 2026-07-17 更新正式规则页面和语言资源：

```text
commit: fbf75231 修复tada规则页面
主要内容：
- 新增 pt-BR_INTRO_ALI.json 等规则语言数据；
- 更新 pt-BR/intro.html 及相关规则模板；
- GameID=110 恢复使用新版默认 intro.html；
- 新页面不再引用缺失的 43b425ca4f1c87250140.js。
```

重新发布参数：

```text
target: tada
version: fbf75231
strategy: single-build
image-transfer: internal
```

双后台结果：

```text
backend-01 / dbqp-tada-release-01：成功
backend-02 / dbqp-tada-release-02：成功
镜像：pgserver:master-fbf75231
容器状态：running / running
容器重启次数：0 / 0
9096：通过
8765：通过
```

两台后台直连校验一致：

```text
/pt-BR/intro?game=110：HTTP 200
size：12827 bytes
SHA256：87cf735bfbd7875a67f728b6663db591f0e258b50ae591bb35ef84944a1f204e
/language/pt-BR?GroupIds[]=INTRO_ALI：HTTP 200
i18_INTRO_ALI_1 marker：OK
```

公开域名和资源校验：

```text
22 个 tada-games 域名新版 intro：22/22 HTTP 200 / hash OK
22 个 tada-games 域名 INTRO_ALI 数据：22/22 HTTP 200 / marker OK
东京、马尼拉、Cloudflare 等 4 个代表节点 × 14 个页面脚本：56/56 HTTP 200
TADA 公开入口：https://ind-h5.dbqpplus999.com/tadabronline/：HTTP 200
```

旧文件 `/_nuxt/43b425ca4f1c87250140.js` 仍为 HTTP 404，但开发新版 `pt-BR/intro.html` 已不再引用该文件；当前页面引用的 14 个脚本均返回 HTTP 200。

本轮应用内浏览器没有可用实例，无法完成“进入阿里巴巴 -> 齿轮 -> 叹号”的真实点击和成功截图。因此当前可判定为**双后台发布和公开资源链路验证通过**，但不能把真实 UI 点击验收标记为已完成。

## 飞机群通知

2026-07-16 已向 `监控报警群` 发送当前排查记录原文件：

- 通知标题：`TADA 阿里巴巴规则页排查记录｜待开发更新资源`
- 飞机群消息 ID：`2695`
- 通知状态明确标注为“等待开发更新资源、尚未闭环”，未宣告修复成功。

2026-07-17 开发正式资源发布并完成服务端/公开资源校验后，已再次向 `监控报警群` 发送部署验证汇总和更新后的本文原文件：

- 通知标题：`TADA 阿里巴巴规则页｜开发资源部署验证`
- 飞机群消息 ID：`2714`
- 通知明确标注 `fbf75231` 双后台和公开资源链路通过，同时标注真实 UI 点击截图待补，未误报完整 UI 闭环。

最终功能验证通过后，再向 `监控报警群` 补发：

1. 规则界面成功截图和修复汇总；
2. 本 Markdown 修复记录原文件。

当前尚未发送“修复成功”通知，避免把规则正文黑屏误报为通过。开发资源更新并复测通过后，在本文补录最终成功通知消息 ID。

## 结论

开发正式资源 `fbf75231` 已发布到 TADA 双后台。两台后台直连、新版规则 HTML、`INTRO_ALI` 葡语数据、22 个公开游戏域名和新版页面引用资源均已验证通过；旧缺失 chunk 已从新版页面依赖中移除。

事件状态：**开发资源已发布，服务端与公开资源链路验证通过；真实浏览器 UI 点击截图待补**。浏览器可用后仍需执行“阿里巴巴 -> 齿轮 -> 叹号”，确认规则正文完整可见，再补发最终 UI 成功截图并正式闭环。
