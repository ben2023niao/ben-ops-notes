---
id: "doc-8c411ccc0453"
title: "游点涩 PC 测试环境发布改造记录"
date: "2026-07-22T15:03:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-22_1503-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E6%B8%B8%E7%82%B9%E6%B6%A9PC%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%8F%91%E5%B8%83%E6%94%B9%E9%80%A0.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-22_1503-【架构改造】游点涩PC测试环境发布改造.md"
sourceSha256: "f5dc0e3ad43c3f4deeddd15161777dc2c82b8eb291cf230df80b0c68cc0823cf"
sourceSystem: "project-doc"
---

# 游点涩 PC 测试环境发布改造记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-22_1503-【架构改造】游点涩PC测试环境发布改造.md`

> 整理日期：2026-07-22 15:03｜日期依据：文件名日期

环境标签：测试环境

## 1. 文档信息

- 实施日期：2026-07-22
- 改造对象：`ben-bot` 测试环境前端发布能力
- 新增入口：`🖥️ 测试环境-游点涩-pc-发版`
- 测试地址：<https://pc.youdianse-test.xyz>
- 代码改造提交：`b4b30a9 新增游点涩PC测试环境发布`
- 首次验证的 PC 代码版本：`707f00cf54b00b54db7bac76e319d5a45f641ec0`（短版本 `707f00c`）
- 当前状态：已上线并完成端到端验证

> 本文仅记录可公开到运维仓库的配置和操作。服务器密码、Git 凭据、Telegram Token、群 ID 等敏感信息不得写入文档或群消息，应通过现有安全配置和安全渠道使用。

## 2. 背景与需求判断

游点涩 PC 项目由 H5 项目演进而来，构建方式、Nuxt/PM2/Docker 部署方式以及测试环境业务配置基本一致。因此，继续维护两套完整发布实现会产生重复代码，后续修复也容易出现 H5 与 PC 行为不一致。

本次采用“共享发布引擎、隔离运行资源”的方案：

- 共享 H5 已稳定运行的 Git 拉取、提交选择、远程脚本上传、镜像构建、容器切换、日志与进度回传能力。
- PC 通过独立适配入口传入仓库、分支、项目名、域名、端口和目录等参数。
- PC 与 H5 的代码目录、缓存、镜像、固定容器、端口、日志和远程临时脚本全部隔离，避免互相覆盖。
- PC 复用 H5 测试环境的业务配置，但不复制或记录其中的密钥内容。

该方案满足“构建及部署模式基本一致”的需求，同时保留两个站点独立发布和独立回滚的能力。

## 3. 目标架构

| 项目 | H5 测试环境 | PC 测试环境 |
| --- | --- | --- |
| Git 项目 | `youdianse-h5` | `youdianse-pc` |
| 分支 | H5 现有测试分支 | `dev` |
| 发布引擎 | H5 Nuxt/PM2/Docker 引擎 | 复用 H5 引擎 |
| 代码根目录 | H5 原有目录 | `/www/wwwroot/18game_pc_client` |
| 远程脚本目录 | H5 原有目录 | `/tmp/ben-bot-youdianse-pc-test` |
| 固定容器 | H5 原有容器 | `youdianse_pc_dev_18game_pc_client_3004` |
| 服务端口 | `3003` | `3004` |
| 访问域名 | `h5.youdianse-test.xyz` | `pc.youdianse-test.xyz` |
| 发布日志 | H5 原有日志 | `data/package/youdianse_pc_test_ssh_release.log` |

发布链路如下：

```text
ben-bot 菜单
  -> 拉取 youdianse-pc/dev 最近提交
  -> 运维选择目标提交
  -> 上传共享远程发布模块
  -> 使用 H5 测试环境配置构建 PC 镜像
  -> 切换 PC 固定容器（3004）
  -> Nginx/HTTPS 反向代理
  -> https://pc.youdianse-test.xyz
```

## 4. 代码改造内容

### 4.1 新增 PC 发布插件

新增目录：

```text
devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/
├── .benbot.json
├── benbot_plugin.py
├── nginx/
│   └── pc.youdianse-test.xyz.conf
└── youdianse_test_18game_pc_client.py
```

主要职责：

- `.benbot.json`：声明插件入口和菜单元数据。
- `benbot_plugin.py`：接入提交列表、发布确认、执行状态和进度面板。
- `youdianse_test_18game_pc_client.py`：将 PC 专属参数映射到共享的 H5 发布客户端。
- `nginx/pc.youdianse-test.xyz.conf`：保存可追踪、可复用的站点配置模板。

### 4.2 参数化共享 H5 发布引擎

原 H5 发布实现补充参数入口，使其可以在保持 H5 默认值不变的情况下服务 PC 项目。PC 适配层设置的核心参数如下：

| 参数用途 | PC 配置 |
| --- | --- |
| Git 分支 | `dev` |
| 项目名 | `youdianse-pc` |
| 发布环境名 | `测试环境-游点涩-pc-发版` |
| 远程脚本 | `/tmp/ben-bot-youdianse-pc-test/youdianse_test_18game_pc_client.py` |
| 远程代码根目录 | `/www/wwwroot/18game_pc_client` |
| 对外地址 | `https://pc.youdianse-test.xyz` |
| 容器端口 | `3004` |
| 项目标识 | `youdianse_pc` |
| 代码目录名 | `18game_pc_client` |
| 仓库缓存名 | `youdianse_18game_pc_client_dev` |

共享引擎同时对项目显示名、项目标识、代码根目录、端口、远程入口和缓存名进行参数化，确保镜像名、容器名、版本文件和日志内容都能正确区分 H5 与 PC。

### 4.3 菜单、权限和帮助信息

- 在机器人首页新增 PC 测试发布入口。
- 将 PC 插件纳入功能注册和权限校验。
- 接入统一的忙碌状态和发布进度类型 `youdianse_pc`。
- 在帮助中心与 README 中补充 PC 发布能力说明。
- 将服务器用途、关键路径、容器及常用检查命令登记到 `devops/ai_context/servers.yml`。

## 5. 服务器部署配置

### 5.1 构建与容器

- 拉取 `youdianse-pc` 的 `dev` 分支，并允许从机器人最近 3 个提交中选择发布版本。
- 复用 H5 测试环境配置和 Nuxt/PM2/Docker 构建链路。
- 使用 PC 独立镜像名和固定容器名，监听 `3004`。
- 首次部署镜像：`youdianse_pc_dev_707f00c_18game_pc_client_3004`。
- 首次部署固定容器：`youdianse_pc_dev_18game_pc_client_3004`。
- 版本信息通过容器内 `/version.json` 暴露，便于核对分支、提交和端口。

### 5.2 Nginx 与 HTTPS

生产化配置文件：

```text
/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf
```

仓库模板：

```text
devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/pc.youdianse-test.xyz.conf
```

路由规则：

- HTTP 请求统一 `301` 跳转 HTTPS。
- `/api`、`/channel`、`/customer` 路由反向代理到 `203.0.113.1:8088`。
- 其余请求反向代理到 PC 容器 `203.0.113.1:3004`。
- HTTPS 复用现有覆盖 `*.youdianse-test.xyz` 的通配证书。
- 访问策略验证 `.env`、Git 目录、依赖锁文件、日志和数据库备份等敏感路径。

### 5.3 DNS

测试域名使用现有 `*.youdianse-test.xyz` 泛解析，目标为测试环境服务器，因此无需新增单独的 `pc` A 记录。部署时仍需通过 DNS 查询和 HTTPS 请求确认实际解析结果。

## 6. 实施步骤与验证结果

| 阶段 | 操作 | 验证结果 |
| --- | --- | --- |
| 需求审计 | 对比 H5 与 PC 构建结构、配置和目标服务器 | 确认可复用发布引擎，运行资源必须隔离 |
| 插件实现 | 新增 PC 菜单、插件、适配脚本和权限 | 插件可注册，菜单可见，权限校验通过 |
| 静态检查 | 校验 JSON、YAML、Python 语法与注册表 | 全部通过 |
| 提交列表 | 调用 PC `list_json` | 成功返回 `dev` 最近 3 个提交 |
| 镜像验证 | 本地构建 `ben-bot:pc-test-validation` | 构建成功 |
| PC 发布 | 构建并启动 PC 固定容器 | 容器健康，端口 `3004` 可访问 |
| 版本验证 | 读取本机及公网 `/version.json` | 分支 `dev`、提交 `707f00c`、端口 `3004` 一致 |
| H5 回归 | 检查 H5 容器和 `3003` 服务 | H5 保持健康，未被 PC 发布影响 |
| Nginx | 执行配置检查并加载站点 | 配置检查通过，HTTP 正确跳转 HTTPS |
| HTTPS | 校验证书和公网首页 | TLS 校验通过，首页返回 HTTP 200 |
| API 路由 | 请求 PC 域名下的同域 API 路径 | 已进入 `8088` 后端链路，不落到前端容器 |
| 搜索引擎隔离 | 检查公网响应头 | 返回 `X-Robots-Tag: noindex, nofollow` |
| 机器人部署 | 更新服务器仓库并重建 `ben-bot` | 容器健康，启动日志无 Python 导入或语法异常 |
| 机器人回归 | 容器内检查 PC 菜单、权限和提交列表 | 全部通过 |

实施过程中已按“每完成一步先验证、再通知”的要求，将模块完成、容器上线、域名 HTTPS 和机器人入口上线四个阶段的结果发送到运维飞机群。

## 7. 日常发布方式

### 7.1 机器人发布

1. 打开 `ben-bot` 首页。
2. 点击 `🖥️ 测试环境-游点涩-pc-发版`。
3. 从 `dev` 最近 3 个提交中选择目标版本。
4. 核对提交信息后确认发布。
5. 观察进度消息，等待构建、容器切换及健康检查完成。
6. 访问 <https://pc.youdianse-test.xyz/version.json> 核对最终版本。

### 7.2 常用检查

在测试服务器上执行：

```bash
docker ps --filter name=youdianse_pc_dev_18game_pc_client_3004
curl -fsS http://203.0.113.1:3004/version.json
curl -fsS https://pc.youdianse-test.xyz/version.json
nginx -t
```

外部检查：

```bash
curl -I http://pc.youdianse-test.xyz
curl -I https://pc.youdianse-test.xyz
curl -fsS https://pc.youdianse-test.xyz/version.json
```

预期结果：HTTP 跳转 HTTPS、HTTPS 返回成功、版本文件与发布提交一致。

## 8. 回滚方案

### 8.1 应用版本回滚

1. 在机器人 PC 发布入口选择上一条已验证提交。
2. 重新执行发布，等待固定容器切换完成。
3. 检查容器状态、`version.json`、首页和 API 路由。
4. 确认 H5 的 `3003` 服务仍正常。

发布引擎按提交生成独立镜像，因此只要目标镜像仍保留，也可以在服务器上根据现有镜像记录辅助恢复；正常情况下优先通过机器人重新发布，保证日志和版本信息完整。

### 8.2 Nginx 回滚

1. 恢复修改前备份的 PC 站点配置，或临时停用 PC 虚拟主机。
2. 执行 `nginx -t`，只有检查通过后才允许重载。
3. 重载 Nginx 并验证 H5、后台和其他测试域名未受影响。

### 8.3 隔离要求

回滚或清理时只操作以下 PC 资源：

- `youdianse_pc_dev_18game_pc_client_3004` 容器。
- `youdianse_pc_dev_*_18game_pc_client_3004` 镜像。
- `/www/wwwroot/18game_pc_client` 目录。
- `/tmp/ben-bot-youdianse-pc-test` 临时目录。
- `pc.youdianse-test.xyz` Nginx 配置。

不得停止 H5 容器、删除 H5 镜像或修改 H5 的 `3003` 端口。

## 9. 已知提示与后续建议

- 2026-07-24 补充优化：PC 适配层已内置测试 PC 独立 CDN/S3/COS 默认值，避免 PC 静态变量漏配时继承 H5 桶；共享发布引擎的 S3/COS 同步默认关闭删除远端多余文件，仅在显式设置 `YOUDIANSE_H5_TEST_STATIC_SYNC_DELETE=1` 时才删除。
- 2026-07-24 实机排查：历史 `ben-bot` 部署机是 `52.79.252.255`，宝塔 `38.92.8.34` 只作为 H5/PC 测试发布目标。宝塔临时启动 `ben-bot` 会和历史部署机抢 Telegram polling，触发 `getUpdates` conflict。
- 2026-07-24 已在历史部署机重建 `ben-bot`，停止宝塔临时 `ben-bot` 后冲突消失；H5/PC 测试发版已带步骤级飞机群通知。
- 2026-07-24 已实发 PC `e9398b9` 和 H5 `2af36b4`。PC 静态资源确认同步到 `18game-nuxt-static-test-pc` 与 `18game-nuxt-static-test-pc-1450169938`，未再继承 H5 桶。
- 2026-07-24 图片验证：常见图片 `/images/placeholder.png`、`/images/mine/profile-logo.png` 在站点和对应 S3 桶返回 `200 image/png`；`/images/game-controller-icon.png`、`/images/email.png`、`/images/sms.png`、`/images/pwd.png` 为前端源码引用但资源缺失，需由前端仓库补图或调整引用。
- 2026-07-24 F12 复查：H5/PC 多数不可见图片来自后端接口返回的上传图域名 `18game-storage-dev-uploads-1450169938.cos.ap-guangzhou.myqcloud.com`，不是 Nuxt 静态包。Chrome 对多张图片拿到腾讯 COS `451 application/xml`，错误码 `UnavailableForLegalReasons`，消息为 `The specified key is unavailable due to content illegal`，随后表现为 `net::ERR_BLOCKED_BY_ORB`。另有 `imgpublic.ycomesc.live` DNS 不解析。后续优化应处理上传图 AWS -> 腾讯 COS 同步/合规/展示域名策略，不能只重发 PC/H5 前端。
- 2026-07-24 上传图修复：测试后端 Mongo 配置 `cdn_image` 已将 `free/aws` 展示域名切到 AWS CloudFront `https://d1rct3ku9n07y3.cloudfront.net`，避免当前腾讯上传桶 451 影响前台；`tencent=>https://18game-storage-dev-uploads-1450169938.cos.ap-guangzhou.myqcloud.com` 仍保留为可选配置。确认 PHP 上传代码只写 AWS S3，前端发布脚本只同步 Nuxt `.output/public` 静态资源，不能替代后端上传图同步。
- 2026-07-24 `imgpublic.ycomesc.live` 修复：该域名是 Mongo `game` 记录中的历史完整 URL，后端 `getCdnUrl()` 会原样返回，不能靠 `cdn_image` 改写。已备份 476 条受影响记录到测试 PHP 容器 `/var/www/html/youdianse-php/runtime/logs/game_imgpublic_backup_20260724_223619.jsonl`，并最小替换 193 条可用 `cover/banner` 兜底的 `icon` 字段；正文 `content` 暂不批量改写。
- 2026-07-24 修复后 Chrome 复查：H5/PC `imgpublic` 请求 0、腾讯上传桶请求 0、可见坏图 0。少量派生 `_large.webp/_square.webp` 404 会回退到原始 JPG，不影响页面显示。
- 首次构建出现部分静态图片路径和大体积 chunk 提示，但未导致构建或运行失败；建议由前端后续清理无效资源引用并优化拆包。
- PC 测试站点当前明确返回 `noindex, nofollow`，适合测试环境，正式环境上线前需重新评估搜索引擎策略。
- 共享 H5 发布引擎后，修改公共逻辑时必须同时执行 H5 和 PC 回归，至少检查提交列表、容器命名、端口、版本文件和日志隔离。
- 若未来 PC 的构建方式或环境配置与 H5 明显分叉，应将差异继续参数化；只有公共引擎无法清晰表达时，再拆分独立实现。

## 10. 结论

本次改造已完成 PC 测试环境从代码提交选择、镜像构建、容器部署、域名 HTTPS 到机器人操作入口的闭环。方案复用了已验证的 H5 发布能力，同时将 PC 的可变运行资源完全隔离；PC 与 H5 均已通过运行和公网回归检查，可以交付日常运维使用。
