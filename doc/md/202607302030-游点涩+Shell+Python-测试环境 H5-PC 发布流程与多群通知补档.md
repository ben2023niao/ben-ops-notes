---
id: "doc-2a8809ecb12e"
title: "测试环境 H5/PC 发布流程与多群通知补档"
date: "2026-07-30T20:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "监控告警", "自动化", "CDN", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-2030-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83H5-PC%E5%8F%91%E5%B8%83%E6%B5%81%E7%A8%8B%E4%B8%8E%E5%A4%9A%E7%BE%A4%E9%80%9A%E7%9F%A5%E8%A1%A5%E6%A1%A3.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-2030-【运维记录】测试环境H5-PC发布流程与多群通知补档.md"
sourceSha256: "9c27acdd4e3c609fc4fd00ba9dfbf72f3789700f42a81f786baf2c36896ef5ee"
sourceSystem: "project-doc"
---

# 测试环境 H5/PC 发布流程与多群通知补档

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-2030-【运维记录】测试环境H5-PC发布流程与多群通知补档.md`

> 整理日期：2026-07-30 20:30｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-30 20:30

2026-08-07 更新：Webhook 自动发布通知不再发 18game运维 群，只发原运维监控报警群（服务器 secrets.env 的 `TG_WEBHOOK_CHAT_IDS`）；人工发布、文档与步骤通知仍发已配置群。详见 `docs/2026-08-07-1830-【运维记录】测试环境Webhook自动发布通知收口到原运维群.md`。

## 背景

用户要求：

```text
1. 用上 workbench 文件夹。
2. 每次操作都留下文档。
3. 文档都发各个 Telegram 群。
4. 18game运维 新增群也要收到各种变动通知。
5. 之前的通知都补进新增群。
6. 整理 AI 一看就能用的完整测试环境 H5/PC 代码发布流程。
```

## 当前结论

```text
已新增 H5/PC 发布流程手册：
workbench/TEST_ENV_H5_PC_RELEASE_FLOW.md

已补充本事件记录：
docs/2026-07-30-2030-【运维记录】测试环境H5-PC发布流程与多群通知补档.md

2026-07-30 21:18 更新：当前 Telegram runtime secrets 已可解析 2 个群。
未发现新增的 18game运维 群进入 /opt/docker-youdianse-php/cicd-web/runtime/secrets.env。
ben-bot known_chat_ids.json 中也未匹配到 18game运维。
```

因此：

```text
当前通知和文档默认发送到已配置的 2 个群：原运维监控报警群和 18game运维。
18game运维 群要收到通知，需要先把该群 chat_id 加入测试服务器 secrets.env。
```

2026-07-31 补充：

```text
每次测试环境 H5/PC 发布后，必须清理对应 CDN/EdgeOne 缓存。
未完成 CDN 清缓存和清缓存后验证，不允许发送“发布完成”收口通知。
workbench 文件只在仓库里留痕，不作为 Telegram 附件发送。
```

## 通知群接入规则

测试服务器通知配置：

```text
/opt/docker-youdianse-php/cicd-web/runtime/secrets.env
```

发送脚本会合并以下字段：

```text
TG_CHAT_ID
TG_CHAT_IDS
TG_EXTRA_CHAT_IDS
YOUDIANSE_HEALTH_TG_CHAT_ID
TG_HEALTH_CHAT_ID
```

新增 `18game运维` 群推荐写入：

```ini
TG_EXTRA_CHAT_IDS=<18game运维群chat_id>
```

如果已有值：

```ini
TG_EXTRA_CHAT_IDS=<原群>,<18game运维群chat_id>
```

安全要求：

```text
不要把 chat_id 写入 Git。
不要把 chat_id 写入 docs/workbench。
不要在终端或最终回复中输出 chat_id。
更新后只输出“解析到 N 个群”。
```

## H5 当前发布事实

```text
当前容器：youdianse_test_18game_h5_client_3003
当前镜像：youdianse_test_5fe65ff_18game_h5_client_3003
当前源码/制品目录：/www/wwwroot/18game_h5_client/youdianse_test_5fe65ff_18game_h5_client_3003
当前 Git HEAD：5fe65ff
分支：test
端口：3003
构建命令：pnpm build
Node 镜像：node:22.19.0-alpine
静态资源域名：https://test-h5-s3.hbabaxb.cn
AWS S3：s3://18game-nuxt-static-test-h5
腾讯 COS：18game-nuxt-static-test-h5-sg-1450169938
```

H5 ben-bot 入口：

```text
菜单名：测试环境-游点涩-h5-发版
脚本目录：/www/wwwroot/18game_devops/devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版
入口脚本：youdianse_test_18game_h5_client.py
命令：
  /script 测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py list
  /script 测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py run <git短ID或完整ID>
```

## PC 当前发布事实

```text
当前容器：youdianse_pc_dev_18game_pc_client_3004
当前镜像：youdianse_pc_dev_0b07686_18game_pc_client_3004
当前源码/制品目录：/www/wwwroot/18game_pc_client/youdianse_pc_dev_0b07686_18game_pc_client_3004
当前 Git HEAD：0b07686
分支：dev
端口：3004
构建命令：pnpm build
Node 镜像：node:22.19.0-alpine
静态资源域名：https://test-pc-s3.hbabaxb.cn
AWS S3：s3://18game-nuxt-static-test-pc
腾讯 COS：18game-nuxt-static-test-pc-sg-1450169938
```

PC ben-bot 入口：

```text
菜单名：测试环境-游点涩-pc-发版
脚本目录：/www/wwwroot/18game_devops/devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版
入口脚本：youdianse_test_18game_pc_client.py
命令：
  /script 测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py list
  /script 测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py run <git短ID或完整ID>
```

PC 发布脚本复用 H5 发布引擎，只覆盖 PC 分支、项目名、端口、访问地址、远端代码根目录和静态资源桶。

## 发布流程摘要

详细流程见：

```text
workbench/TEST_ENV_H5_PC_RELEASE_FLOW.md
```

核心步骤：

```text
1. 更新 workbench/CURRENT_TASK.md，记录发布目标和禁止事项。
2. 发步骤开始/准备完成通知。
3. 通过 ben-bot list 查看目标提交。
4. 通过 ben-bot run <git id> 发布。
5. 发布脚本生成独立制品目录。
6. Docker build 使用 node:22.19.0-alpine 执行 pnpm build。
7. 构建产物 .output/public 同步 AWS S3 + 腾讯 COS。
8. 清理对应 CDN/EdgeOne 缓存。
9. run.sh 校验 image_schema 并替换固定容器。
10. 验证页面入口、version.json、静态 version、uploads 图片 token/t。
11. 更新 docs/workbench。
12. 正式 docs 文档通过 Telegram sendDocument 发所有已配置群；workbench 不发群。
13. 同步测试服务器 /opt 文档记录。
```

## 2026-07-31 补充：发布后 CDN 清缓存硬规则

当前测试服务器未安装腾讯云 CLI/SDK，且运行密钥未配置 EdgeOne API 凭据，因此本规则先作为发布后的强制人工/控制台步骤执行。

H5 每次发布后清理：

```text
https://h5.youdianse-test.xyz/
https://test-h5.hbabaxb.cn/
https://test-h5.hbazuua.cn/
https://test-h5-s3.hbabaxb.cn/
https://test-h5-s3.hbabaxb.cn/_nuxt/
```

PC 每次发布后清理：

```text
https://pc.youdianse-test.xyz/
https://test-pc.hbabaxb.cn/
https://test-pc.hbazuua.cn/
https://test-pc-s3.hbabaxb.cn/
https://test-pc-s3.hbabaxb.cn/_nuxt/
```

如发布涉及 uploads 图片展示、广告图、图片签名或默认图问题，同时清理：

```text
https://test-img.hbabaxb.cn/uploads/
https://test-img.hbazuua.cn/uploads/
```

收口要求：

```text
1. 记录 CDN 清缓存任务 ID、操作者、时间和清理范围。
2. 清缓存后复测页面入口和静态资源 version。
3. H5/PC 图片仍需验证 test-img 全部带 token/t、sign=0、裸链=0。
4. Telegram 收口通知必须写明 CDN 缓存已清理。
```

后续自动化方向：

```text
补齐 Tencent EdgeOne API SecretId/SecretKey、ZoneId 和权限后，可在 H5/PC 共用发布引擎中调用 CreatePurgeTask。
Tencent EdgeOne 官方支持 CreatePurgeTask，Type 可用 purge_url、purge_prefix、purge_host、purge_all 等。
官方文档：https://www.tencentcloud.com/document/product/1145/50536
```

## 历史通知补档摘要

新增 `18game运维` 群后，需要补发以下摘要：

```text
【测试环境｜历史通知补档】图片 CDN 与前端发布流程

补档范围：
1. 广告缓存旧 sign/t 已刷新，页面图片恢复 token/t。
2. CDN 配置已改为 [cdn.tencent._default] + [cdn.tencent.test-img] domains。
3. key_file 方案已回退为 env 直接 key=，key_file=。
4. H5 /game 裸链回归已修复，test-img=123、敏感凭据：[已脱敏]
5. 测试环境域名关系和资源链路已补档。
6. H5/PC 完整发布流程已补档。

当前版本：
外层运维仓库：<当前 HEAD>
内层后端仓库：25fd3260

注意：
env/.env.dev 包含 CDN key 明文，只能留在本地和测试服务器，不能提交 Git。
```

需要作为附件补发的文档：

```text
docs/2026-07-30-1850-【修复Bug】测试图片默认图与广告缓存旧签名修复记录.md
docs/2026-07-30-1939-【运维记录】测试环境域名与资源链路总览.md
docs/2026-07-30-2030-【运维记录】测试环境H5-PC发布流程与多群通知补档.md
workbench/TEST_ENV_CDN_RELEASE_FLOW.md
workbench/TEST_ENV_DOMAIN_RELATIONS.md
workbench/TEST_ENV_H5_PC_RELEASE_FLOW.md
```

## 本次核验记录

```text
本地外层 HEAD：30d0304
本地内层 HEAD：25fd3260
本地状态：仅 env/.env.dev 为预期敏感运行态改动
测试服务器 Telegram 群数量：1
18game运维 群：未进入当前 secrets 可用配置
H5 当前版本：5fe65ff
PC 当前版本：0b07686
```

## 后续动作

```text
1. 用户或运维把 18game运维 群 chat_id 加入测试服务器 secrets.env。
2. 重新核验 Telegram 解析群数量。
3. 对所有群发送历史通知补档摘要。
4. 对所有群发送上述文档附件。
5. 更新 workbench/CURRENT_TASK.md 记录补发成功群数量。
6. 提交并同步 /opt。
```
