---
id: "doc-34975f53c553"
title: "测试 H5/PC 静态资源 CORS 反复异常止血与 COS 直连域名规划"
date: "2026-08-04T20:44:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "自动化", "CDN", "DNS", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2044-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E9%93%BE%E8%B7%AF%E6%95%B4%E7%90%86%E3%80%91%E6%B5%8B%E8%AF%95H5-PC%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90CORS%E5%8F%8D%E5%A4%8D%E5%BC%82%E5%B8%B8%E6%AD%A2%E8%A1%80%E4%B8%8ECOS%E7%9B%B4%E8%BF%9E%E5%9F%9F%E5%90%8D%E8%A7%84%E5%88%92.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2044-【修复Bug+链路整理】测试H5-PC静态资源CORS反复异常止血与COS直连域名规划.md"
sourceSha256: "a9489f9280eb1516c2c32541029ca11ac14c6d367bb7437418a4089d73c11cbb"
sourceSystem: "project-doc"
---

# 测试 H5/PC 静态资源 CORS 反复异常止血与 COS 直连域名规划

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608042044-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%B5%8B%E8%AF%95%20H5-PC%20%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%20CORS%20%E5%8F%8D%E5%A4%8D%E5%BC%82%E5%B8%B8%E6%AD%A2%E8%A1%80%E4%B8%8E%20COS%20%E7%9B%B4%E8%BF%9E%E5%9F%9F%E5%90%8D%E8%A7%84%E5%88%92.md)

> 整理日期：2026-08-04 20:44｜日期依据：文件名日期

环境标签：测试环境 / 腾讯云备案域名 / COS / EdgeOne / H5 / PC

记录时间：2026-08-04 20:44

## 本次结论

- 截图里的问题已复现：`test-pc-s3.hbabaxb.cn` 同一个 CSS 对象在部分 EdgeOne 边缘节点返回 `200`，但缺少 `Access-Control-Allow-Origin`，浏览器因此按 CORS 拦截样式。
- COS 桶 CORS 本身正确：测试 H5/PC 两个腾讯 COS 桶均配置 `AllowedOrigin=*`、`AllowedMethod=GET,HEAD`、`AllowedHeader=*`。
- 当前反复出现的核心原因：`test-h5-s3.hbabaxb.cn`、`test-pc-s3.hbabaxb.cn` 名称虽然叫 `s3`，但 DNS 实际仍 CNAME 到 EdgeOne `*.eo.dnse4.com`，不是 COS 直连；边缘缓存节点响应头不一致导致问题反复。
- 本次已对旧 EdgeOne 静态域执行前缀刷新，截图中的 CORS 缺头问题已止血。
- 已新增 `hbbfuub.cn` 两条测试静态资源 COS 直连候选域名，但 COS 对外访问仍返回 `UserCnameInvalid`，所以没有切发布脚本，避免把测试环境切到不可用域名。

## 备案域名费用与用途

| 域名 | 周期 | 费用 | 本次规划 |
| --- | --- | --- | --- |
| `hbabaxb.cn` | 08.11 ~ 09.11 | 200u | 当前测试主备案域，页面和旧静态资源仍在用 |
| `hbazuua.cn` | 08.11 ~ 09.11 | 200u | 当前测试备用备案域，页面和图片备用链路 |
| `hbbfuub.cn` | 08.04 ~ 09.04 | 200u | 新增备案域名，优先用于测试 H5/PC 静态资源 COS 直连 |
| `hbakjja.cn` | 08.04 ~ 09.04 | 200u | 新增备案域名，建议预留给线上前置/线上静态资源 COS 直连 |

## 当前域名关系

### 测试环境

| 类型 | 当前域名 | 当前状态 | 规划 |
| --- | --- | --- | --- |
| H5 页面 | `h5.youdianse-test.xyz`、`test-h5.hbabaxb.cn`、`test-h5.hbazuua.cn` | 页面入口仍走既有链路 | 保持页面入口稳定 |
| H5 前端静态资源 | `test-h5-s3.hbabaxb.cn` | DNS 仍指向 EdgeOne，已刷新止血 | 最终迁到 COS 直连域 |
| H5 COS 直连候选 | `test-h5-s3.hbbfuub.cn` | DNSPod 与 COS 自定义源站域名已配置，但访问仍 `UserCnameInvalid` | 待 COS 生效后再切 H5 发布脚本 |
| PC 页面 | `pc.youdianse-test.xyz`、`test-pc.hbabaxb.cn`、`test-pc.hbazuua.cn` | 页面入口仍走既有链路 | 保持页面入口稳定 |
| PC 前端静态资源 | `test-pc-s3.hbabaxb.cn` | DNS 仍指向 EdgeOne，已刷新止血 | 最终迁到 COS 直连域 |
| PC COS 直连候选 | `test-pc-s3.hbbfuub.cn` | DNSPod 与 COS 自定义源站域名已配置，但访问仍 `UserCnameInvalid` | 待 COS 生效后再切 PC 发布脚本 |
| 后端上传资源 | `test-img.hbabaxb.cn`、`test-img.hbazuua.cn` | 后端 uploads 图片展示链路，仍走腾讯云 CDN/反代 | 与前端构建资源继续分离 |

### 线上/线上前置

| 类型 | 建议域名 | 规划 |
| --- | --- | --- |
| H5 页面 | `main-h5.备案域名` | 回源线上前置或正式线上 H5 |
| H5 前端静态资源 | `main-h5-s3.备案域名` | 独立腾讯 COS/S3 绑定域名直连，不走腾讯 CDN/EdgeOne 缓存 |
| PC 页面 | `main-pc.备案域名` | 建议不要复用测试环境 `test-pc` 名称 |
| PC 前端静态资源 | `main-pc-s3.备案域名` | 独立腾讯 COS/S3 绑定域名直连，不走腾讯 CDN/EdgeOne 缓存 |
| 后端上传资源 | `main-img.备案域名` | 线上 uploads 独立链路，可继续走腾讯云 CDN/反代 |

## 已执行操作

1. 已读取 workbench 当前任务、运行链路、通知目标、机器矩阵和历史静态资源修复记录。
2. 已通知 `稳定备案域名+腾讯云原厂`、`18game运维`、`18GAME_ 上线群（正式環境）` 开始排查。
3. 已复现旧 `test-pc-s3.hbabaxb.cn` 多边缘节点 CORS 不一致：
   - 部分节点：`200 + Access-Control-Allow-Origin:*`
   - 部分节点：`200` 但无 CORS 头
4. 已通过 Tencent Cloud API 查询 DNSPod：
   - `hbabaxb.cn`、`hbazuua.cn`、`hbbfuub.cn`、`hbakjja.cn` 均为 DNSPod。
   - `hbbfuub.cn`、`hbakjja.cn` 业务子域名原本为空。
5. 已通过 COS API 查询 CORS：
   - `18game-nuxt-static-test-h5-sg-1450169938`：CORS 正确。
   - `18game-nuxt-static-test-pc-sg-1450169938`：CORS 正确。
6. 已新增 `hbbfuub.cn` 两条 DNSPod 记录：
   - `test-h5-s3.hbbfuub.cn` -> `18game-nuxt-static-test-h5-sg-1450169938.cos.ap-singapore.myqcloud.com`
   - `test-pc-s3.hbbfuub.cn` -> `18game-nuxt-static-test-pc-sg-1450169938.cos.ap-singapore.myqcloud.com`
7. 已对两个测试 COS 桶执行 `PUT Bucket domain`：
   - `test-h5-s3.hbbfuub.cn` 返回配置 `ENABLED`
   - `test-pc-s3.hbbfuub.cn` 返回配置 `ENABLED`
8. 已对旧 EdgeOne 静态资源前缀执行刷新：
   - `https://test-pc-s3.hbabaxb.cn/_nuxt/`
   - `https://test-pc-s3.hbabaxb.cn/images/`
   - `https://test-h5-s3.hbabaxb.cn/_nuxt/`
   - `https://test-h5-s3.hbabaxb.cn/images/`
   - JobId：`3tdcf6zt6acu`
   - 失败数：`0`

## 验证结果

### 旧域名止血验证

PC 静态域 `test-pc-s3.hbabaxb.cn`：

- 抽检 EdgeOne A 节点：15 个
- `200 + Access-Control-Allow-Origin:*`：13 个
- 缺 CORS：0 个
- 连接超时：2 个

H5 静态域 `test-h5-s3.hbabaxb.cn`：

- 抽检 EdgeOne A 节点：15 个
- `200 + Access-Control-Allow-Origin:*`：13 个
- 缺 CORS：0 个
- 连接超时：2 个

页面资源抽检：

- PC 页面当前引用 `_nuxt` 资源 79 个。
- H5 页面当前引用 `_nuxt` 资源 74 个。
- 串行抽样 CSS、JS、meta 文件均返回 `200` 且带 CORS。

### 新 COS 直连候选验证

`test-h5-s3.hbbfuub.cn` 与 `test-pc-s3.hbbfuub.cn`：

- DNSPod `a/b/c` 权威 NS 已能返回 CNAME 到 COS endpoint。
- COS 桶自定义源站域名配置查询显示 `ENABLED`。
- 当前公网访问仍返回 `400 UserCnameInvalid`。
- 因此本次没有把测试 H5/PC 发布脚本静态域名切到 `hbbfuub.cn`。

## 为什么这次不能直接切新域名

如果现在把发布脚本改成 `test-h5-s3.hbbfuub.cn` / `test-pc-s3.hbbfuub.cn`，新构建页面会引用一个当前公网仍 `400` 的静态资源域，测试环境会直接不可用。

正确顺序应该是：

1. COS 自定义源站域名公网访问返回 `200`。
2. 带 `Origin` 请求返回 `Access-Control-Allow-Origin:*`。
3. 再改 H5/PC 发布脚本的 `STATIC_CDN_URL`。
4. 重发测试 H5/PC。
5. 浏览器 F12 验证 CSS/JS/图片/视频无 CORS 和加载失败。

## 后续彻底修复步骤

1. 在腾讯 COS 控制台或工单确认 `UserCnameInvalid` 原因。
2. 确认 `test-h5-s3.hbbfuub.cn`、`test-pc-s3.hbbfuub.cn` 可直接访问 COS 对象。
3. 修改测试 H5/PC 发布脚本静态资源域名到 `hbbfuub.cn`。
4. 发布测试 H5/PC 最新版本。
5. 浏览器 F12 验证：
   - CSS/JS 全部 200。
   - `Access-Control-Allow-Origin:*` 存在。
   - 页面不再请求 `test-*-s3.hbabaxb.cn`。
   - 图片/视频正常加载。
6. 待测试稳定后，将 `main-h5-s3`、`main-pc-s3` 按同样模式放到 `hbakjja.cn` 或指定线上备案域名。

## 官方依据

- Tencent Cloud COS 文档说明 `PUT Bucket domain` 用于为桶设置自定义域名，`GET Bucket domain` 用于查询自定义域名配置。
- Tencent Cloud COS 自定义域名文档说明，自定义源站域名开启后还需要配置 CNAME 域名解析才能生效。

参考：

- https://www.tencentcloud.com/document/product/436/34981
- https://www.tencentcloud.com/zh/document/product/436/31507
