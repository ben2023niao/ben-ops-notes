---
id: "doc-a38e91dd9ce9"
title: "线上前置日本服务器替换与备案域名 COS 直连关系"
date: "2026-08-04T20:12:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2012-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%2B%E9%93%BE%E8%B7%AF%E6%94%B9%E9%80%A0%E3%80%91%E7%BA%BF%E4%B8%8A%E5%89%8D%E7%BD%AE%E6%97%A5%E6%9C%AC%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%9B%BF%E6%8D%A2%E4%B8%8E%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8DCOS%E7%9B%B4%E8%BF%9E%E5%85%B3%E7%B3%BB.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2012-【运维记录+链路改造】线上前置日本服务器替换与备案域名COS直连关系.md"
sourceSha256: "eef4a09d93aa6a215ae608976fc6ead7409e419728bd92ec8c414ec15d6c4487"
sourceSystem: "project-doc"
---

# 线上前置日本服务器替换与备案域名 COS 直连关系

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608042012-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-%E7%BA%BF%E4%B8%8A%E5%89%8D%E7%BD%AE%E6%97%A5%E6%9C%AC%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%9B%BF%E6%8D%A2%E4%B8%8E%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%20COS%20%E7%9B%B4%E8%BF%9E%E5%85%B3%E7%B3%BB.md)

> 整理日期：2026-08-04 20:12｜日期依据：文件名日期

环境标签：线上前置 / 测试环境 / 腾讯云备案域名 / 前端静态资源 / COS 绑定域名

记录时间：2026-08-04 20:12

## 本次核心结论

- 原线上前置候选服务器 `43.241.16.84` 外部 HTTP 80 不可用，本轮不再作为 PC/H5 上线前模拟测试入口首选。
- 日本服务器已接入为新的线上前置候选，主 SSH 入口为 `root@138.252.248.139:38927`，密码不写入文档和仓库。
- 日本服务器实际绑定公网 IP 为 `138.252.248.24`、`138.252.248.139`、`138.252.248.249`；聊天中出现的 `38.252.248.24` 外部连接超时，按机器网卡事实应使用 `138.252.248.24`。
- 已在日本服务器完成 Docker、Docker Compose、原生 Nginx 初始化，并部署游点涩线上前置 PC/H5 Nginx 配置。
- 已将 ben-bot 线上前置 H5/PC 发版入口目标从 `43.241.16.84:22` 改为 `138.252.248.139:38927`。
- 本次未触发真实前端发布，未切换 DNS/CDN/COS 绑定，未修改云厂商资源。

## 服务器关系

| 用途 | 服务器 | 状态 |
| --- | --- | --- |
| 旧线上前置候选 | `43.241.16.84` | 外部 HTTP 80 阻塞，本轮替换 |
| 新线上前置主入口 | `138.252.248.139:38927` | SSH 免密、Docker、Nginx、Host 健康页已验证 |
| 新线上前置备用公网 IP | `138.252.248.24`、`138.252.248.249` | 公网 80 均返回 Nginx 200 |

日本服务器配置记录：`JP 6138*1-32G-1T NVME-20Mcn2-3IP`。

## 已完成操作

1. 已通知 `稳定备案域名+腾讯云原厂`、`18game运维`、`18GAME_ 上线群（正式環境）`，说明开始接入日本服务器替换 43 机器。
2. 已只读核验三条 IP，确认 `138.252.248.139`、`138.252.248.249` 可 SSH 登录，机器实际也绑定 `138.252.248.24`。
3. 已配置 ben-bot/发布脚本 SSH 公钥到日本服务器 `root` 用户，本机和 ben-bot 容器均验证免密登录成功。
4. 已安装并启用 Docker 29.1.3、Docker Compose 2.40.3、原生 Nginx 1.24.0。
5. 已验证公网 80：`138.252.248.24`、`138.252.248.139`、`138.252.248.249` 均返回 Nginx 200。
6. 已部署 Nginx 配置 `/etc/nginx/conf.d/10-youdianse-preprod-frontends.conf`。
7. 已验证 Host 头健康页：
   - `main-h5.hbabaxb.cn` -> `200 ok`
   - `main-h5.hbazuua.cn` -> `200 ok`
   - `test-pc.hbabaxb.cn` -> `200 ok`
   - `test-pc.hbazuua.cn` -> `200 ok`
   - `main-pc.hbabaxb.cn` -> `200 ok`
   - `main-pc.hbazuua.cn` -> `200 ok`
8. 已同步 ben-bot 线上前置 H5/PC 发版入口到宿主机和容器，容器内 `py_compile` 与 `list_json` 干跑通过。

## 当前备案域名关系

### 测试环境

| 类型 | 域名规划 | 说明 |
| --- | --- | --- |
| H5 页面 | `test-h5.备案域名` | 页面入口，实际当前包括 `h5.youdianse-test.xyz`、`test-h5.hbabaxb.cn`、`test-h5.hbazuua.cn` |
| H5 前端静态资源 | `test-h5-s3.备案域名` | 独立腾讯 COS/S3 绑定域名直连，不走腾讯 CDN/EdgeOne 缓存 |
| PC 页面 | `test-pc.备案域名` | 页面入口，实际当前包括 `pc.youdianse-test.xyz`、`test-pc.hbabaxb.cn`、`test-pc.hbazuua.cn` |
| PC 前端静态资源 | `test-pc-s3.备案域名` | 独立腾讯 COS/S3 绑定域名直连，不走腾讯 CDN/EdgeOne 缓存 |
| 后端上传资源 | `test-img.备案域名` | AWS S3 uploads 通过腾讯云 CDN/反代域名展示，和前端静态资源分离 |

### 线上/线上前置环境

| 类型 | 域名规划 | 说明 |
| --- | --- | --- |
| H5 页面 | `main-h5.备案域名` | 回源日本线上前置服务器，后续稳定后再按正式线上流程推进 |
| H5 前端静态资源 | `main-h5-s3.备案域名` | 独立腾讯 COS/S3 绑定域名直连，不走腾讯 CDN/EdgeOne 缓存 |
| PC 页面 | `main-pc.备案域名` | 建议使用 `main-pc`，避免与测试环境 `test-pc` 入口混用 |
| PC 前端静态资源 | `main-pc-s3.备案域名` | 独立腾讯 COS/S3 绑定域名直连，不走腾讯 CDN/EdgeOne 缓存 |
| 后端上传资源 | `main-img.备案域名` | 线上 uploads 独立链路，和前端构建资源分离 |

备注：用户聊天中保留过 `test-pc.备案域名` 作为线上 PC 页面入口口径，但该名称与测试 PC 域名冲突。正式落地建议使用 `main-pc.备案域名`，或另开明确的线上前置 PC 域名。

## 静态资源改造规则

- `test-h5-s3.备案域名`
- `test-pc-s3.备案域名`
- `main-h5-s3.备案域名`
- `main-pc-s3.备案域名`

以上四类前端构建静态资源域名均按独立腾讯 COS/S3 桶绑定自定义域名访问，不走腾讯 CDN/EdgeOne 缓存，避免发布后缓存不一致导致 CSS/JS/图片资源异常。

发版脚本当前规则：

- 测试 H5、测试 PC、线上前置 H5、线上前置 PC 默认 `TENCENT_CDN_PURGE_ENABLED=0`。
- 构建资源仍同步到对应 AWS S3 和腾讯 COS/S3。
- 前端页面引用资源域名走 `*-s3.备案域名`，由 COS/S3 自定义域名直接提供。

## 日本服务器 Nginx 关系

| 域名 | Nginx 回源 |
| --- | --- |
| `main-h5.hbabaxb.cn`、`main-h5.hbazuua.cn` | `203.0.113.1:3003` |
| `test-pc.hbabaxb.cn`、`test-pc.hbazuua.cn` | `203.0.113.1:3004` |
| `main-pc.hbabaxb.cn`、`main-pc.hbazuua.cn` | `203.0.113.1:3004` |
| H5 静态路径 | `main-h5-s3.hbabaxb.cn` |
| PC 静态路径 | `main-pc-s3.hbabaxb.cn` |
| `/api`、`/channel`、`/customer` | `https://admin.youdianse.com` |

当前业务容器尚未发布，因此首页业务访问需等 H5/PC 线上前置发版后再验收；`/healthz` 已用于确认 Nginx 域名配置命中。

## 验证记录

- SSH：`root@138.252.248.139:38927` 本机和 ben-bot 容器免密成功。
- 系统：Ubuntu 24.04 LTS，kernel `6.8.0-31-generic`。
- 服务：Docker active，Nginx active。
- 公网 80：三条 `138.252.248.*` IP 均返回 Nginx 200。
- Nginx 配置：`nginx -t` 通过。
- Host 健康页：`main-h5`、`test-pc`、`main-pc` 本机和公网均 `200 ok`。
- ben-bot：线上前置 H5/PC 脚本已同步容器，`py_compile` 与 `list_json` 干跑通过。

## 待办与风险

- DNS/CDN/COS 自定义域名真实配置尚未切换；后续涉及 DNS、CDN、证书、COS 桶绑定均属于 P2，需要单独通知、留证和验证。
- `main-h5-s3.备案域名`、`main-pc-s3.备案域名` 必须绑定各自独立腾讯 COS/S3 桶，并确认不走腾讯 CDN/EdgeOne 缓存。
- 页面域名回源日本服务器前，需要确认使用主 IP `138.252.248.139` 还是备用 IP 组合策略。
- H5/PC 业务容器发布后，需要补充首页、`version.txt`、`version.json`、`_nuxt`、图片、视频、API 代理的浏览器和命令行验收。
