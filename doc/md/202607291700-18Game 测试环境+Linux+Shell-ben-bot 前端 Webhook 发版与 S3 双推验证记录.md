---
id: "doc-c6bbe78f6e03"
title: "ben-bot 前端 Webhook 发版与 S3 双推验证记录"
date: "2026-07-29T17:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1700-%E3%80%90%E4%BC%98%E5%8C%96%2B%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%2B%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91ben-bot%E5%89%8D%E7%AB%AFWebhook%E5%8F%91%E7%89%88%E4%B8%8ES3%E5%8F%8C%E6%8E%A8%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1700-【优化+架构改造+问题排查】ben-bot前端Webhook发版与S3双推验证记录.md"
sourceSha256: "4fd63beb99922cde8cf864c5913374975e309d620c13bbbaacdbef89b76b5e6f"
sourceSystem: "project-doc"
---

# ben-bot 前端 Webhook 发版与 S3 双推验证记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1700-【优化+架构改造+问题排查】ben-bot前端Webhook发版与S3双推验证记录.md`

> 整理日期：2026-07-29 17:00｜日期依据：文件名日期

环境标签：测试环境

## 1. 文档信息

- 日期：2026-07-29
- 分类：优化、架构改造、问题排查、发布验证
- 范围：ben-bot 机器人部署机、测试环境游点涩 H5/PC 前端发布、GitLab webhook、AWS S3、腾讯新加坡 COS、腾讯 CDN/EdgeOne 刷新、飞机群进度通知
- 原则：本文只记录可公开运维信息，不记录服务器密码、Telegram Token、云密钥、私钥内容或群敏感配置。

## 2. 服务器边界

| 服务器 | 用途 | 连接方式 | 关键路径 |
| --- | --- | --- | --- |
| `52.79.252.255` | ben-bot 机器人真实运行服务器 | `ubuntu` + SSH key | `/opt/telegram/18game_devops/devops/python/ben-bot` |
| `38.92.8.34` | 游点涩测试 H5/PC 宝塔发布目标 | `root` + 安全渠道凭据 | `/www/wwwroot/18game_h5_client`、`/www/wwwroot/18game_pc_client` |

补充说明：

- 机器人真实运行在 `52.79.252.255`，不是测试发布目标服务器。
- `38.92.8.34` 只作为 H5/PC 前端构建、容器启动、Nginx/宝塔访问目标。
- 敏感连接信息只维护在 `devops/python/ben-bot/doc/private/服务器登录信息.local.md`，该目录已加入 `.gitignore`。
- 公开服务器索引维护在 `devops/ai_context/servers.yml`，只写 IP、用户、用途、路径、密钥文件路径和环境变量名。

## 3. 本次目标

1. 明确 ben-bot 真实部署服务器和测试发布目标服务器，避免继续误判运行位置。
2. 优化 H5/PC 发布进度框，将 AWS S3、腾讯 COS、腾讯 CDN 刷新等关键步骤纳入实时进度。
3. 给前端 GitLab webhook 自动发布补齐与按钮发布一致的资源同步链路。
4. 验证 H5/PC 前端构建产物同步到 AWS 前端桶和腾讯新加坡 COS 桶。
5. 验证页面优先加载腾讯 CDN 前端资源，并修复/确认 CORS 响应头。
6. 每一步操作同步通知飞机群，便于团队看到运维进度。

## 4. 资源分类

| 类型 | H5 | PC | 说明 |
| --- | --- | --- | --- |
| 前端代码仓库 | `web/youdianse-h5`，`test` 分支 | `web/youdianse-pc`，`dev` 分支 | 前端发布只拉前端仓库，不从后端仓库构建 |
| AWS 前端静态桶 | `18game-nuxt-static-test-h5` | `18game-nuxt-static-test-pc` | 构建后同步 `.output/public`，公开桶域名可访问 |
| 腾讯新加坡 COS | `18game-nuxt-static-test-h5-sg-1450169938` | `18game-nuxt-static-test-pc-sg-1450169938` | 私有桶，不允许 COS 原始域名公网直连 |
| 腾讯 CDN/EdgeOne | `https://test-h5-s3.hbabaxb.cn` | `https://test-pc-s3.hbabaxb.cn` | 页面前端 `_nuxt`、CSS、JS、静态图优先走这里 |
| 发布目标容器 | `youdianse_test_18game_h5_client_3003` | `youdianse_pc_dev_18game_pc_client_3004` | 部署在 `38.92.8.34` |
| 页面入口 | `https://h5.youdianse-test.xyz` | `https://pc.youdianse-test.xyz` | 页面 HTML 由前端容器提供 |

后端资源边界：

- 测试后端 uploads 图片和 APK/App 下载仍继续走现有 AWS 后端 S3/CloudFront。
- 前端发布只处理 Nuxt 构建产物，不替代后端上传图同步。
- 前端接口返回的 AWS 后端资源属于后端资源链路，不属于本次前端 `_nuxt` 资源问题。

## 5. 代码优化

### 5.1 进度框细化

提交：`01d756e fix: expand youdianse release progress steps`

改造内容：

- 将游点涩发布进度从粗略步骤扩展为细步骤。
- 新增/明确以下节点：
  - 接收任务
  - 上传远程脚本
  - 连接远程服务器
  - 检查远程环境
  - 准备代码版本
  - 写入配置文件
  - Docker 构建开始
  - AWS 身份校验
  - AWS S3 静态资源同步
  - 腾讯 COS 静态资源同步
  - Docker 构建完成
  - 腾讯 CDN 缓存刷新
  - 启动容器
  - 验证访问结果
  - 发布完成
- 最终进度框保留完整步骤列表，不再只显示“前面若干步骤已完成”。

### 5.2 前端 webhook 补齐发布链路

提交：`54a5371 feat: support youdianse frontend webhook release`

改造内容：

- H5 发布脚本新增 `webhook` action，从 GitLab Push Hook JSON 读取：
  - `ref`
  - `checkout_sha`
  - `after`
  - `user_username/user_name/user_email`
- webhook 会校验分支，只允许当前脚本配置分支发布。
- webhook 发布与按钮发布共用同一个 `handle_run`，因此共享：
  - SSH 上传远程发布脚本
  - 前端仓库拉取
  - Docker build
  - AWS S3 同步
  - 腾讯新加坡 COS 同步
  - 腾讯 CDN/EdgeOne 刷新
  - 容器启动
  - 进度框和步骤通知
- PC 发布入口复用 H5 发布引擎，因此同步具备 `webhook` action。

## 6. 部署方式

机器人部署机：`52.79.252.255`

处理方式：

1. 确认真实机器人服务器为 `52.79.252.255`。
2. 由于远程仓库存在现场修改和 root-owned 文件，未执行强制 reset。
3. 对目标文件做备份后单文件同步：
   - `app/benbot/executor.py`
   - `data/scripts/测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py`
4. 远程执行 `build_and_run_ben_bot.sh` 重建并启动 `ben-bot` 容器。
5. 验证 `ben-bot` 容器运行正常，日志无启动失败。

## 7. 验证记录

### 7.1 webhook 分支保护

- 使用错误分支 payload 做无害测试。
- 结果：脚本拒绝发布，提示分支不匹配。
- 结论：webhook 分支保护生效。

### 7.2 H5 webhook 验证

最终验证版本：

| 项目 | 值 |
| --- | --- |
| 分支 | `test` |
| Git 短 ID | `36e273c` |
| Git ID | `36e273cae703e9a415c28b2492b4c37fe6365341` |
| 页面入口 | `https://h5.youdianse-test.xyz` |
| 腾讯 CDN | `https://test-h5-s3.hbabaxb.cn` |

结果：

- 前端仓库拉取成功。
- Docker build 重新执行，未跳过构建。
- AWS 前端静态桶 `18game-nuxt-static-test-h5` 同步成功。
- 腾讯新加坡 COS 桶 `18game-nuxt-static-test-h5-sg-1450169938` 同步成功。
- 腾讯 CDN/EdgeOne 刷新成功：
  - `https://test-h5-s3.hbabaxb.cn/_nuxt/`
  - `https://test-h5-s3.hbabaxb.cn/images/`
- H5 容器 `youdianse_test_18game_h5_client_3003` 启动成功。

注意：

- 曾使用未构建过的 `79fe79f` 验证“确实会触发上传”，验证后立即重新发布当前最新 `36e273c`，避免测试环境停留在旧版本。

### 7.3 PC webhook 验证

最终验证版本：

| 项目 | 值 |
| --- | --- |
| 分支 | `dev` |
| Git 短 ID | `32ecf54` |
| Git ID | `32ecf54a4a19be0d6fcc56bd03990e41611c4ff1` |
| 页面入口 | `https://pc.youdianse-test.xyz` |
| 腾讯 CDN | `https://test-pc-s3.hbabaxb.cn` |

结果：

- 前端仓库 `web/youdianse-pc.git` 拉取成功。
- Docker build 重新执行，未跳过构建。
- AWS 前端静态桶 `18game-nuxt-static-test-pc` 同步成功。
- 腾讯新加坡 COS 桶 `18game-nuxt-static-test-pc-sg-1450169938` 同步成功。
- 腾讯 CDN/EdgeOne 刷新成功：
  - `https://test-pc-s3.hbabaxb.cn/_nuxt/`
  - `https://test-pc-s3.hbabaxb.cn/images/`
- PC 容器 `youdianse_pc_dev_18game_pc_client_3004` 启动成功。

## 8. 页面与 CORS 抽样

H5：

| 检查项 | 结果 |
| --- | --- |
| 页面入口 | `https://h5.youdianse-test.xyz/` 返回正常 |
| 当前版本 | `36e273c` |
| 页面引用 | `_nuxt` 资源使用 `https://test-h5-s3.hbabaxb.cn` |
| 抽样 CSS | `HTTP/2 200`，`content-type: text/css` |
| CORS | `Access-Control-Allow-Origin: https://h5.youdianse-test.xyz` |

PC：

| 检查项 | 结果 |
| --- | --- |
| 页面入口 | `https://pc.youdianse-test.xyz/` 返回正常 |
| 当前版本 | `32ecf54` |
| 页面引用 | `_nuxt` 资源使用 `https://test-pc-s3.hbabaxb.cn` |
| 抽样 CSS | `HTTP/2 200`，`content-type: text/css` |
| CORS | `Access-Control-Allow-Origin: https://pc.youdianse-test.xyz` |

结论：

- 当前未复现前端 `_nuxt` 资源 CORS 问题。
- 资源加载问题的核心修复点是：构建后直接双推 AWS 和腾讯新加坡 COS，并在发版后刷新对应腾讯 CDN 目录。

## 9. 飞机群通知

已通知目标群：稳定备案域名 + 腾讯云原厂。

通知节点：

- 确认 ben-bot 真实运行服务器。
- 部署进度框优化。
- 部署 webhook 发布能力。
- H5 webhook 无害分支保护测试。
- H5 真实 webhook 构建、AWS S3 同步、腾讯 COS 同步、CDN 刷新、成功汇总。
- PC 真实 webhook 构建、AWS S3 同步、腾讯 COS 同步、CDN 刷新、成功汇总。
- 最终页面与 CORS 抽样结果。

## 10. 回滚与排查

回滚思路：

- 代码回滚：回退 `01d756e`、`54a5371` 之后重新部署 ben-bot。
- 临时关闭腾讯 CDN 刷新：
  - H5：`YOUDIANSE_H5_TEST_TENCENT_CDN_PURGE_ENABLED=0`
  - PC：`YOUDIANSE_PC_TEST_TENCENT_CDN_PURGE_ENABLED=0`
- 临时排查 COS 同步：
  - 检查机器人容器内腾讯云环境变量是否存在。
  - 检查远程 Docker build 日志是否出现 `COS 静态资源同步: 成功`。
- 临时排查 AWS 同步：
  - 检查机器人容器内 AWS 环境变量是否存在。
  - 检查远程 Docker build 日志是否出现 `S3 静态资源同步: 成功`。
- 排查 CORS：
  - 带 `Origin` 请求 CDN 资源，确认是否返回 `Access-Control-Allow-Origin`。
  - 若 COS 原始响应正常、CDN 不正常，优先刷新 `_nuxt/` 与 `images/` 目录缓存。

常用公开检查命令：

```bash
curl -fsS https://h5.youdianse-test.xyz/version.txt
curl -fsS https://pc.youdianse-test.xyz/version.txt
curl -I -H 'Origin: https://h5.youdianse-test.xyz' https://test-h5-s3.hbabaxb.cn/_nuxt/entry.9fJ8Knpu.css
curl -I -H 'Origin: https://pc.youdianse-test.xyz' https://test-pc-s3.hbabaxb.cn/_nuxt/entry.DnB0JDod.css
```

## 11. 后续维护

- H5/PC 前端发布按钮和 webhook 自动发布必须保持同一套资源同步步骤。
- 每次测试环境发布后必须刷新腾讯 CDN/EdgeOne，至少刷新 `_nuxt/` 和 `images/`。
- 后端 uploads 与 APK/App 下载仍按后端 AWS 链路单独规划，不要混入前端发版流程。
- 修改服务器、桶、CDN、域名、webhook、机器人部署信息后，应同步更新：
  - `devops/ai_context/servers.yml`
  - `devops/ai_context/README.md`
  - `devops/python/ben-bot/doc/`
  - `devops/python/ben-bot/doc/private/服务器登录信息.local.md`（仅本机私密）
