---
id: "doc-2061364330f6"
title: "测试前端发布完成通知补备案域名记录"
date: "2026-07-29T17:55:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "自动化", "CDN", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1755-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E6%B5%8B%E8%AF%95%E5%89%8D%E7%AB%AF%E5%8F%91%E5%B8%83%E5%AE%8C%E6%88%90%E9%80%9A%E7%9F%A5%E8%A1%A5%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1755-【优化】测试前端发布完成通知补备案域名记录.md"
sourceSha256: "4bad7e05c8569a310248df15aac6fbbd36c31332e9916719c6404892aeda56c1"
sourceSystem: "project-doc"
---

# 测试前端发布完成通知补备案域名记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607291755-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%B5%8B%E8%AF%95%E5%89%8D%E7%AB%AF%E5%8F%91%E5%B8%83%E5%AE%8C%E6%88%90%E9%80%9A%E7%9F%A5%E8%A1%A5%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-29 17:55｜日期依据：文件名日期

环境标签：测试环境

## 1. 背景

测试环境 H5/PC 发布完成后，机器人最终通知原来只展示：

- AWS CDN 域名
- 腾讯 CDN 静态资源域名
- version.txt / version.json
- git 短 id、env 附件、部署日志附件、耗时和退出码

当前备案域名也需要在最后一条成功通知里展示，便于测试、前端、产品直接确认备案访问入口。

## 2. 本次调整

| 文件 | 调整 |
| --- | --- |
| `app/benbot/executor.py` | 新增读取 `BEN_BOT_ICP_ACCESS_URL`，最终进度框和日志附件 caption 均展示“备案访问域名” |
| `data/scripts/测试环境-游点涩-h5-发版/benbot_plugin.py` | H5 按钮发布注入 `BEN_BOT_ICP_ACCESS_URL=https://test-h5.hbabaxb.cn` |
| `data/scripts/测试环境-游点涩-pc-发版/benbot_plugin.py` | PC 按钮发布注入 `BEN_BOT_ICP_ACCESS_URL=https://test-pc.hbabaxb.cn` |
| `data/scripts/测试环境-游点涩-h5-发版/server_config.py` | 新增脚本直连配置 `YOUDIANSE_H5_TEST_ICP_ACCESS_URL`，默认 H5 备案入口 |
| `data/scripts/测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py` | 脚本自身成功摘要、审计输出和控制台结果补“备案访问域名” |
| `data/scripts/测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py` | PC 复用 H5 引擎时注入 `YOUDIANSE_H5_TEST_ICP_ACCESS_URL=https://test-pc.hbabaxb.cn` |

## 3. 最终通知格式

H5 发布完成后应包含：

```text
测试环境-游点涩-h5-发版：成功 #
AWS CDN 域名：https://h5.youdianse-test.xyz
备案访问域名：https://test-h5.hbabaxb.cn
腾讯 CDN 域名：https://test-h5-s3.hbabaxb.cn
腾讯 CDN 版本信息：https://test-h5-s3.hbabaxb.cn/version.txt
AWS CDN 版本信息：https://h5.youdianse-test.xyz/version.txt
AWS CDN 版本 JSON：https://h5.youdianse-test.xyz/version.json
git 短id：xxxxxxx
env 配置：env.txt 已发送 txt 附件
部署日志附件：yyyyMMdd-HHmmss-测试环境-游点涩-h5-发版-1.txt
耗时/退出码：xxx.xs / 0
```

PC 发布完成后应包含：

```text
测试环境-游点涩-pc-发版：成功 #
AWS CDN 域名：https://pc.youdianse-test.xyz
备案访问域名：https://test-pc.hbabaxb.cn
腾讯 CDN 域名：https://test-pc-s3.hbabaxb.cn
腾讯 CDN 版本信息：https://test-pc-s3.hbabaxb.cn/version.txt
AWS CDN 版本信息：https://pc.youdianse-test.xyz/version.txt
AWS CDN 版本 JSON：https://pc.youdianse-test.xyz/version.json
git 短id：xxxxxxx
env 配置：env.txt 已发送 txt 附件
部署日志附件：yyyyMMdd-HHmmss-测试环境-游点涩-pc-发版-1.txt
耗时/退出码：xxx.xs / 0
```

## 4. 验证项

- H5 备案访问域名：`https://test-h5.hbabaxb.cn`
- PC 备案访问域名：`https://test-pc.hbabaxb.cn`
- H5 静态资源 CDN：`https://test-h5-s3.hbabaxb.cn`
- PC 静态资源 CDN：`https://test-pc-s3.hbabaxb.cn`

验证重点：

- 按钮发布最终进度框包含“备案访问域名”。
- 日志附件 caption 包含“备案访问域名”。
- webhook 或脚本直连发布时，脚本自身成功摘要也包含“看备案访问域名”。

## 5. 文档命名规则补充

从本次开始，新运维文档统一使用：

```text
YYYY-MM-DD_HHMM-【分类】项目或问题简述.md
```

这样 VSCode 和终端按文件名排序时，最新文档会排在同日期文档的后面，方便快速定位。
