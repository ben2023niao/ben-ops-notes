---
id: "doc-c87396134965"
title: "测试环境域名与资源链路总览 · 【运维记录】测试环境域名与资源链路总览"
date: "2026-07-30T19:39:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN", "DNS"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1939-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%9F%9F%E5%90%8D%E4%B8%8E%E8%B5%84%E6%BA%90%E9%93%BE%E8%B7%AF%E6%80%BB%E8%A7%88.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1939-【运维记录】测试环境域名与资源链路总览.md"
sourceSha256: "d6f167c9d3217dbc097250a04d9a8a7b631665b2f4e2a338f15eeaa62c02cd66"
sourceSystem: "project-doc"
---

# 测试环境域名与资源链路总览 · 【运维记录】测试环境域名与资源链路总览

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607301939-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%9F%9F%E5%90%8D%E4%B8%8E%E8%B5%84%E6%BA%90%E9%93%BE%E8%B7%AF%E6%80%BB%E8%A7%88%20%C2%B7%20%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%9F%9F%E5%90%8D%E4%B8%8E%E8%B5%84%E6%BA%90%E9%93%BE%E8%B7%AF%E6%80%BB%E8%A7%88.md)

> 整理日期：2026-07-30 19:39｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-30 19:39

分类：运维记录、网络调整、备案域名、S3/COS、EdgeOne

## 1. 文档目的

把当前测试环境域名和资源链路按用途拆开，避免把前端构建静态资源、后端 uploads 图片、后端接口、客户端包下载和备用 S3 域名混在一起。

简单理解：

- 页面入口：用户打开 H5/PC 页面。
- 前端静态资源：前端构建出来的 `_nuxt`、JS、CSS、前端自带图片。
- 后端 uploads 图片：后台上传后由接口返回的图片。
- 后端接口：页面调用 `/api`、`/channel`、`/customer` 等业务接口。
- 备用/历史 S3 域名：曾用于后端 AWS 到腾讯 COS 同步验证或预备链路，不等于当前页面主展示域名。

## 2. 总体关系

```text
用户浏览器
├─ H5 页面
│  ├─ https://h5.youdianse-test.xyz
│  ├─ https://test-h5.hbabaxb.cn
│  └─ https://test-h5.hbazuua.cn
├─ PC 页面
│  ├─ https://pc.youdianse-test.xyz
│  ├─ https://test-pc.hbabaxb.cn
│  └─ https://test-pc.hbazuua.cn
├─ 前端静态资源
│  ├─ H5: https://test-h5-s3.hbabaxb.cn
│  └─ PC: https://test-pc-s3.hbabaxb.cn
├─ 后端 uploads 图片
│  ├─ 主用: https://test-img.hbabaxb.cn/uploads/...
│  ├─ 候选: https://test-img.hbazuua.cn/uploads/...
│  └─ AWS 源/兜底: https://d1rct3ku9n07y3.cloudfront.net/uploads/...
└─ 后端接口
   ├─ 页面同域 /api、/channel、/customer 反代到测试后端
   └─ 前端 env 仍记录 https://admin.youdianse-test.xyz 作为测试 API 域名
```

## 3. H5 页面链路

H5 发布入口：`测试环境-游点涩-h5-发版`

页面域名：

- AWS/原测试入口：`https://h5.youdianse-test.xyz`
- 备案入口 1：`https://test-h5.hbabaxb.cn`
- 备案入口 2：`https://test-h5.hbazuua.cn`

源站和容器：

- 测试服务器：`38.92.8.34`
- H5 Nuxt 容器端口：`3003`
- `h5.youdianse-test.xyz` 直接解析到测试服务器。
- `test-h5.hbabaxb.cn`、`test-h5.hbazuua.cn` 通过腾讯 EdgeOne 回源测试服务器。

前端静态资源：

- 展示域名：`https://test-h5-s3.hbabaxb.cn`
- AWS 公开桶：`s3://18game-nuxt-static-test-h5`
- AWS 区域：`ap-southeast-1`
- AWS 公开桶域名：`https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com`
- 腾讯 COS 私有桶：`18game-nuxt-static-test-h5-sg-1450169938`
- 腾讯 COS 区域：`ap-singapore`
- EdgeOne CNAME：`test-h5-s3.hbabaxb.cn.eo.dnse4.com`

当前规则：

- H5 构建后同步 `.output/public` 到 AWS 前端桶和腾讯新加坡 H5 COS 桶。
- 页面里的 `_nuxt`、JS、CSS、前端自带图片优先走 `test-h5-s3.hbabaxb.cn`。
- 发布后刷新 `https://test-h5-s3.hbabaxb.cn/_nuxt/`、`images/`、PWA 相关文件。
- 前端静态资源当前不做 token 加密。

## 4. PC 页面链路

PC 发布入口：`测试环境-游点涩-pc-发版`

页面域名：

- AWS/原测试入口：`https://pc.youdianse-test.xyz`
- 备案入口 1：`https://test-pc.hbabaxb.cn`
- 备案入口 2：`https://test-pc.hbazuua.cn`

源站和容器：

- 测试服务器：`38.92.8.34`
- PC Nuxt 容器端口：`3004`
- `pc.youdianse-test.xyz` 直接解析到测试服务器。
- `test-pc.hbabaxb.cn`、`test-pc.hbazuua.cn` 通过腾讯 EdgeOne 回源测试服务器。

前端静态资源：

- 展示域名：`https://test-pc-s3.hbabaxb.cn`
- AWS 公开桶：`s3://18game-nuxt-static-test-pc`
- AWS 区域：`ap-southeast-1`
- AWS 公开桶域名：`https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com`
- 腾讯 COS 私有桶：`18game-nuxt-static-test-pc-sg-1450169938`
- 腾讯 COS 区域：`ap-singapore`
- EdgeOne CNAME：`test-pc-s3.hbabaxb.cn.eo.dnse4.com`

当前规则：

- PC 构建后同步 `.output/public` 到 AWS 前端桶和腾讯新加坡 PC COS 桶。
- 页面里的 `_nuxt`、JS、CSS、前端自带图片优先走 `test-pc-s3.hbabaxb.cn`。
- 发布后刷新 `https://test-pc-s3.hbabaxb.cn/_nuxt/`、`images/`。
- 前端静态资源 token 加密已经回退，当前不再给 JS/CSS/前端图片加密。

## 5. 后端 uploads 图片链路

后端 uploads 图片是后台上传后，接口返回给 H5/PC 页面展示的图片，和前端构建产物不是一类资源。

当前主用展示域名：

- `https://test-img.hbabaxb.cn/uploads/...`

当前候选展示域名：

- `https://test-img.hbazuua.cn/uploads/...`

AWS 源站/兜底域名：

- `https://d1rct3ku9n07y3.cloudfront.net/uploads/...`

实际链路：

```text
浏览器
-> test-img.hbabaxb.cn 或 test-img.hbazuua.cn
-> 腾讯 EdgeOne
-> 测试服务器 Nginx 38.92.8.34
-> AWS CloudFront d1rct3ku9n07y3.cloudfront.net
-> AWS S3 后端 uploads 对象
```

当前安全规则：

- 后台上传不改，仍上传到 AWS S3。
- 后端接口返回 `test-img.*` 时会追加 `token/t`。
- 带 `token/t` 的 uploads 图片有效期内返回原图。
- 裸 uploads 图片或旧 `sign/t` 会返回默认占位图，不返回原图。
- `test-img.hbabaxb.cn` 是当前主域名；`test-img.hbazuua.cn` 已接入，可作为多域名候选。
- AWS CloudFront 老域名不加密，作为最后兜底和排查源链路。

后端配置位置：

- 服务器 env：`/opt/docker-youdianse-php/env/.env.dev`
- 后端签名代码：`youdianse-php/app/Services/Common/CommonService.php`
- 配置段：`[cdn.tencent.test-img.hbabaxb.cn]`、`[cdn.tencent.test-img.hbazuua.cn]`
- 密钥只保存在 env 或 key_file，文档不记录明文。

## 6. 测试后端 S3/COS 备用链路

域名：

- `https://test-s3.hbabaxb.cn`

用途：

- 测试后端 S3/COS 资源预备或历史验证域名。
- 对应腾讯新加坡 COS 私有桶：`18game-storage-dev-uploads-sg-1450169938`
- EdgeOne CNAME：`test-s3.hbabaxb.cn.eo.dnse4.com`

当前说明：

- `test-s3.hbabaxb.cn` 不等于当前 H5/PC 页面后端 uploads 图片主展示域名。
- 当前页面后端 uploads 图片主展示域名是 `test-img.hbabaxb.cn`。
- ben-bot 中 `测试环境-游点涩后台-s3-同步` 旧按钮已下线，不再通过常驻按钮做后台 AWS 到腾讯 COS 手动同步。

## 7. 客户端包 / 下载入口

域名：

- `https://package.hbazuua.cn`

用途：

- 客户端包/下载入口 EdgeOne 域名。
- 不属于 H5/PC 前端构建静态资源域名。
- 不属于后端 uploads 图片展示域名。

DNS：

- EdgeOne CNAME：`package.hbazuua.cn.eo.dnse4.com`

## 8. DNSPod 与 EdgeOne 关系

`hbabaxb.cn`：

- NS：`a.dnspod.com`、`b.dnspod.com`、`c.dnspod.com`

测试相关记录：

| 域名 | CNAME | 用途 |
| --- | --- | --- |
| `test.hbabaxb.cn` | `test.hbabaxb.cn.eo.dnse4.com` | 测试聚合/旧映射入口 |
| `test-h5.hbabaxb.cn` | `test-h5.hbabaxb.cn.eo.dnse4.com` | H5 备案页面入口 |
| `test-pc.hbabaxb.cn` | `test-pc.hbabaxb.cn.eo.dnse4.com` | PC 备案页面入口 |
| `test-h5-s3.hbabaxb.cn` | `test-h5-s3.hbabaxb.cn.eo.dnse4.com` | H5 前端静态资源 |
| `test-pc-s3.hbabaxb.cn` | `test-pc-s3.hbabaxb.cn.eo.dnse4.com` | PC 前端静态资源 |
| `test-s3.hbabaxb.cn` | `test-s3.hbabaxb.cn.eo.dnse4.com` | 测试后端 S3/COS 备用资源域 |
| `test-img.hbabaxb.cn` | `test-img.hbabaxb.cn.eo.dnse4.com` | 后端 uploads 图片主展示域 |

`hbazuua.cn`：

- NS：`a.dnspod.com`、`b.dnspod.com`、`c.dnspod.com`

测试相关记录：

| 域名 | CNAME | 用途 |
| --- | --- | --- |
| `test-h5.hbazuua.cn` | `test-h5.hbazuua.cn.eo.dnse4.com` | H5 第二备案页面入口 |
| `test-pc.hbazuua.cn` | `test-pc.hbazuua.cn.eo.dnse4.com` | PC 第二备案页面入口 |
| `test-img.hbazuua.cn` | `test-img.hbazuua.cn.eo.dnse4.com` | 后端 uploads 图片候选展示域 |
| `package.hbazuua.cn` | `package.hbazuua.cn.eo.dnse4.com` | 客户端包/下载入口 |

当前没有启用：

- `test-h5-s3.hbazuua.cn`
- `test-pc-s3.hbazuua.cn`

也就是说，hbazuua 目前补的是页面入口和图片候选域名，不是 H5/PC 前端静态资源 S3 域名。

## 9. 后端接口域名

前端 env 里仍记录：

- `https://admin.youdianse-test.xyz`

页面访问时：

- H5/PC 页面可通过同域 `/api`、`/channel`、`/customer` 路由进入测试后端。
- PC Nginx 模板里这些路径反代到测试后端链路。

当前验证：

- `https://admin.youdianse-test.xyz/` 根路径返回 `404`，这是根路径没有页面内容，不等于接口不可用。
- 接口可用性要按具体 `/api/...` 业务路径验证。

## 10. 发布规则

H5/PC 前端发布：

```text
拉取前端代码
-> 构建 .output/public
-> 同步 AWS 前端公开桶
-> 同步腾讯新加坡 COS 私有前端桶
-> 页面静态资源优先走 test-h5-s3 / test-pc-s3
-> 发布后刷新对应 EdgeOne/CDN 缓存
```

后端 uploads 图片：

```text
后台上传
-> AWS S3
-> AWS CloudFront
-> test-img.* EdgeOne 反代展示
-> token/t 有效时出原图；裸链出默认占位图
```

不要混淆：

- `test-h5-s3` / `test-pc-s3`：前端构建产物。
- `test-img`：后端 uploads 图片展示。
- `test-s3`：测试后端 S3/COS 备用或历史同步验证链路。
- `package`：客户端包/下载入口。

## 11. 本轮只读验证

执行时间：2026-07-30 19:39

DNS：

| 项目 | 结果 |
| --- | --- |
| `hbabaxb.cn` NS | `a.dnspod.com / b.dnspod.com / c.dnspod.com` |
| `hbazuua.cn` NS | `a.dnspod.com / b.dnspod.com / c.dnspod.com` |
| `test-h5/test-pc/test-img/test-s3/test-*-s3.hbabaxb.cn` | 均返回对应 EdgeOne CNAME |
| `test-h5/test-pc/test-img/package.hbazuua.cn` | 均返回对应 EdgeOne CNAME |

HTTP：

| URL | 结果 |
| --- | --- |
| `https://h5.youdianse-test.xyz/version.txt` | `200 text/plain` |
| `https://pc.youdianse-test.xyz/version.txt` | `200 text/plain` |
| `https://test-h5.hbabaxb.cn/version.txt` | `200 text/plain` |
| `https://test-pc.hbabaxb.cn/version.txt` | `200 text/plain` |
| `https://test-h5-s3.hbabaxb.cn/version.txt` | `200 text/plain` |
| `https://test-pc-s3.hbabaxb.cn/version.txt` | `200 text/plain` |
| `https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com/version.txt` | `200 text/plain` |
| `https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com/version.txt` | `200 text/plain` |
| `https://test-h5.hbazuua.cn/version.txt` | `200 text/plain` |
| `https://test-pc.hbazuua.cn/version.txt` | `200 text/plain` |
| `https://package.hbazuua.cn/` | `200 text/html` |
| `https://test-s3.hbabaxb.cn/` | ben-bot 服务器侧 `200 application/xml` |
| `https://test-img.hbabaxb.cn/uploads/...webp` 裸链 | ben-bot 服务器侧 `200 image/webp`，返回默认占位图，size=13716 |
| `https://test-img.hbazuua.cn/uploads/...webp` 裸链 | ben-bot 服务器侧 `200 image/webp`，返回默认占位图，size=13716 |

补充：

- HTTP 抽查使用 `curl -k` 兼容 EdgeOne 免费证书部署状态；本表用于判断访问链路和回源是否通，不替代证书状态巡检。
- 本机网络对个别 EdgeOne 节点出现过 `test-s3` / `test-img.hbabaxb.cn` 超时，ben-bot 服务器侧复查正常。
- 判断为边缘节点或本地网络差异，不作为域名关系错误处理。

## 12. 后续维护建议

- 新增页面备案域名：先在 EdgeOne 建页面域名，再补 DNSPod CNAME，再加测试服务器 Nginx `server_name`。
- 新增前端静态资源域名：必须确认对应独立 COS 桶、CORS、CDN 刷新规则和发布脚本 env。
- 新增后端图片展示域名：必须同步 Nginx `test-img` vhost、后端 env 签名 host、EdgeOne 和 DNSPod。
- 不要把后端 uploads 域名加进 H5/PC 前端静态资源桶。
- 不要恢复 ben-bot 后台 S3 同步常驻按钮；如需后台资源迁移，重新立项执行。
