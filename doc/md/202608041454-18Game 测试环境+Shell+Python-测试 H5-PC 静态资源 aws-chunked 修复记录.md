---
id: "doc-85cfd796413a"
title: "测试 H5/PC 静态资源 aws-chunked 修复记录"
date: "2026-08-04T14:54:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "自动化", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1454-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E6%B5%8B%E8%AF%95H5-PC%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90aws-chunked%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1454-【修复Bug+网络调整】测试H5-PC静态资源aws-chunked修复记录.md"
sourceSha256: "9e974dfc402acdc6331ab9e8d8092298c1523f006dbdcffb4388ea667a0bab64"
sourceSystem: "project-doc"
---

# 测试 H5/PC 静态资源 aws-chunked 修复记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1454-【修复Bug+网络调整】测试H5-PC静态资源aws-chunked修复记录.md`

> 整理日期：2026-08-04 14:54｜日期依据：文件名日期

环境标签：测试环境、游点涩、H5、PC、前端静态资源、AWS S3、腾讯 COS、EdgeOne、CDN

记录时间：2026-08-04 14:54

## 背景

用户反馈 `https://pc.youdianse-test.xyz/` 浏览器 F12 Network 中静态资源读取异常，并要求同步检查 `https://test-h5.hbabaxb.cn`、`test-pc` 等测试环境域名。

本次按 workbench 规则读取了工作台与历史文档，参考了测试 H5/PC 前端发版、静态资源 S3/COS 双推、前端静态资源不鉴权、后端 uploads 防盗刷等既有记录。

## 通知范围

本次每个明确阶段均已同步通知以下 Telegram 群：

- `稳定备案域名+腾讯云原厂`
- `18game运维`
- `18GAME_ 上线群（正式環境）`

通知内容只包含操作摘要、结果和下一步，不包含密钥、token、Secret Key、Cookie 或完整敏感配置。

## 现象

- PC 页面 HTML 本身返回 200。
- 页面引用的 `https://test-pc-s3.hbabaxb.cn/_nuxt/...` 静态资源在浏览器 Network 表现为加载异常。
- 抽检异常对象时，曾发现腾讯静态域名资源存在 `content-encoding: aws-chunked` 或 GET 请求卡住/HTTP2 异常。
- AWS S3 源桶同名对象可正常返回，说明问题集中在腾讯 COS/EdgeOne 静态资源链路或对象上传兼容性，不是页面入口和业务代码主体不可用。

## 根因判断

本次发布模板使用 AWS CLI v2 对腾讯 COS 的 S3 兼容 endpoint 执行 `aws s3 sync`。在部分对象上，AWS CLI v2 的 checksum/streaming 行为与腾讯 COS/边缘链路兼容性不佳，容易残留或触发 `aws-chunked` 相关响应/传输异常，导致浏览器加载 CSS/JS 失败或长时间挂起。

本次修复方向是：在腾讯 COS 同步阶段显式关闭非必要 checksum/streaming 行为，使用更保守的 S3 兼容配置重新上传对象，并强制重建 H5/PC 前端镜像触发全量同步和 CDN 刷新。

## 修改内容

本地与 ben-bot 远程发布模板均已更新：

- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_templates.py`
  - COS 同步阶段增加：
    - `AWS_REQUEST_CHECKSUM_CALCULATION=when_required`
    - `AWS_RESPONSE_CHECKSUM_VALIDATION=when_required`
    - AWS config `request_checksum_calculation = when_required`
    - AWS config `response_checksum_validation = when_required`
    - AWS config `payload_signing_enabled = false`
    - 保留 `addressing_style = virtual`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_config.py`
  - 发布镜像 schema 从 `tooling-v20-frontend-static-no-auth` 调整为 `tooling-v21-cos-checksum`，用于强制测试 H5/PC 下次发布重建镜像并重新同步静态资源。

远程备份：

- `remote_youdianse_h5_templates.py.bak.static_cos_checksum_20260804_142918`
- `remote_youdianse_h5_config.py.bak.static_cos_schema_20260804_143158`

## 发布执行

### PC 测试环境

- 发布脚本：`测试环境-游点涩-pc-发版`
- 发布 commit：`c842f12`
- 操作结果：
  - Docker 镜像重新构建成功。
  - AWS S3 静态资源同步成功。
  - 腾讯 COS 静态资源同步成功。
  - 腾讯 EdgeOne/CDN 刷新成功，JobId：`3tczl74jxdef`
  - 测试 PC 容器重启成功。

### H5 测试环境

- 发布脚本：`测试环境-游点涩-h5-发版`
- 发布 commit：`9d3d113`
- 操作结果：
  - Docker 镜像重新构建成功。
  - AWS S3 静态资源同步成功。
  - 腾讯 COS 静态资源同步成功。
  - 腾讯 EdgeOne/CDN 刷新成功，JobId：`3tczzkaf4dnb`
  - 测试 H5 容器重启成功。

构建观察项：

- H5 构建中出现 `pnpm-lock.yaml` 自动合并提示，构建脚本使用 `--no-frozen-lockfile`，未阻断发布。
- H5/PC 构建均有常规前端构建 warning，例如部分图片运行时解析、大 chunk 提醒；本次未发现其导致静态资源故障。

## 验证结果

验证方式：执行端浏览器控制器本轮不可用，因此使用等价的 Network 级验证：入口 HTML 请求、`HEAD` 响应头、HTTP/2 `GET` 完整下载、AWS 源桶对照、腾讯静态域名抽检。

### 入口域名

| 域名 | 结果 |
| --- | --- |
| `https://pc.youdianse-test.xyz/` | 200，HTML 正常返回 |
| `https://test-pc.hbabaxb.cn/` | 200，HTML 正常返回 |
| `https://h5.youdianse-test.xyz/` | 200，HTML 正常返回 |
| `https://test-h5.hbabaxb.cn/` | 200，HTML 正常返回 |
| `https://test-pc.hbazuua.cn/` | 证书域名不匹配 |
| `https://test-h5.hbazuua.cn/` | 证书域名不匹配 |

### 静态资源抽检

| 对象 | 结果 |
| --- | --- |
| PC `https://test-pc-s3.hbabaxb.cn/_nuxt/entry.K3NpkUUj.css` | HTTP/2 GET 可完整下载，大小 65534 bytes |
| PC AWS 源桶同名 entry CSS | HTTP/2 GET 可完整下载，大小 65534 bytes |
| H5 `https://test-h5-s3.hbabaxb.cn/_nuxt/entry.9fJ8Knpu.css` | HTTP/2 GET 可完整下载，大小 52632 bytes |
| H5 AWS 源桶同名 entry CSS | HTTP/2 GET 可完整下载，大小 52632 bytes |
| PC 当前 HTML 引用的 CSS 抽样 | 多个样本 200 且可完整下载 |
| H5 当前 HTML 引用的 CSS 抽样 | 多个样本 200 且可完整下载 |

抽检响应头未再发现 `content-encoding: aws-chunked`。

## 遗留与建议

- `hbazuua.cn` 的 H5/PC 备用入口当前证书域名不匹配，若要正式作为测试入口使用，需要补齐 EdgeOne/CDN 域名证书绑定后再验证。
- PC 静态域名在本机网络下仍观察到个别 EdgeOne 边缘 IP 连接超时，但对象层、AWS 源桶和主访问链路已恢复；如用户侧仍复现，建议保留 Network 失败请求的边缘 IP、Request ID 和时间点，再提交腾讯云侧排查。
- 浏览器侧如仍看到旧资源异常，优先强制刷新或清理 Service Worker/浏览器缓存，再复测当前 HTML 引用的新资源。

## 结论

本次已完成测试 H5/PC 静态资源上传兼容性修复、双端重新发布、腾讯 COS 重新同步和 EdgeOne/CDN 刷新。主入口与 `hbabaxb.cn` 备案入口验证正常，核心 CSS/JS 静态资源可完整下载，原 `aws-chunked` 类静态资源加载问题已恢复。
