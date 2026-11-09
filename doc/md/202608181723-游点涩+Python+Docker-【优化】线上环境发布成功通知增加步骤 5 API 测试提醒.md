---
id: "doc-7d48b378331e"
title: "【优化】线上环境发布成功通知增加步骤 5 API 测试提醒"
date: "2026-08-18T17:23:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Python", "Docker", "Redis", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-18-1723-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E5%8F%91%E5%B8%83%E6%88%90%E5%8A%9F%E9%80%9A%E7%9F%A5%E5%A2%9E%E5%8A%A0%E6%AD%A5%E9%AA%A45API%E6%B5%8B%E8%AF%95%E6%8F%90%E9%86%92.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-18-1723-【优化】线上环境发布成功通知增加步骤5API测试提醒.md"
sourceSha256: "a3b2702af60a780e49445488d89ea30801a60b19dd9c1cdb125ab82938022289"
sourceSystem: "project-doc"
---

# 【优化】线上环境发布成功通知增加步骤 5 API 测试提醒

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608181723-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BPython%2BDocker-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E5%8F%91%E5%B8%83%E6%88%90%E5%8A%9F%E9%80%9A%E7%9F%A5%E5%A2%9E%E5%8A%A0%E6%AD%A5%E9%AA%A4%205%20API%20%E6%B5%8B%E8%AF%95%E6%8F%90%E9%86%92.md)

> 整理日期：2026-08-18 17:23｜日期依据：文件名日期

文档日期：2026-08-18 17:23
环境：游点涩线上环境（main 分支）
分类：优化
标签：线上环境、后端、CICD、发布通知、步骤5、API 测试

## 需求背景

用户新增固定工作流程与发布流程要求：

```text
固定工作流程（每次任务不得跳过）：
检查仓库状态及最新提交 -> 读取 doc 历史 -> 使用 Workbench 分析并执行 -> 每步发群通知
-> 完成后验证代码 -> 更新/汇总 doc -> 汇总及文档发群 -> 最后提交本地 Git -> 提交结果发群
注意：开始前确认本地/远程最新提交及未提交修改；验证失败先修复，禁止直接提交；
默认只本地 Commit，未经明确要求禁止 Push。

线上发布流程：
步骤 1：产品和开发确认本次发布的功能和改动范围
步骤 2：开发填写上线模版申请发布（平台/是否影响用户/影响范围/前后端/环境/git id/开发/测试/运维/升级内容）
步骤 3：产品确认后通知运维发布
步骤 4：运维执行发布
步骤 5：每次更新之后 @Ocean6160 @kuli5918 跑一遍 API 测试，测试/产品/开发同步验证
```

本次改动目标：CICD 每次发布成功后的群通知固定追加“步骤 5”测试提醒，确保测试同学收到跑 API 测试的指令。

## 现状

发布结果通知由 `cicd-web/core.py` 的 `build_deploy_report` 生成（Web 发布与 CLI 发布共用）：

```text
【项目】发布成功
人 / 机器 / 后台 / 业务日志
版本 / 服务 / 镜像
检查：HTTP / Session / Hosts / Redis / MongoDB
结论：SUCCESS
@运维名单
```

成功、警告、失败共用同一格式，成功时没有测试通知。

## 改动内容

`cicd-web/core.py` `build_deploy_report`：

- `SUCCESS` 时在结论后追加：

```text

步骤 5｜测试：@Ocean6160 @kuli5918 请跑一遍 API 测试；测试/产品/开发同步验证，有问题及时反馈。
```

- `FAILED` / `WARNING` 保持原格式；运维 @ 名单（@Ben_Bird @jett_yunwei @Kermit0824 @melo_sre @Daviea2）始终保留。

## 验证结果

```text
本地：python3 -m py_compile cicd-web/core.py 通过
生产 venv：加载新 core.py 调用 build_deploy_report 实测
  SUCCESS：包含“步骤 5｜测试：@Ocean6160 @kuli5918 请跑一遍 API 测试；测试/产品/开发同步验证，有问题及时反馈。”，运维名单保留
  FAILED：不包含步骤 5，原格式不变
```

## 提交与上线状态

```text
本地提交：见本次提交记录（默认只本地 Commit，未经明确要求禁止 Push）
上线方式：用户确认后 push origin/main -> 线上 cicd-web-auto-update 自动拉取并重启 CICD Web 生效
```

## 通知记录

```text
步骤 1 仓库状态与文档/workbench 就绪   message_id 9762
步骤 2 发布成功通知优化方案            message_id 9763
步骤 3 发布成功通知代码修改            message_id 9764
步骤 4 验证通过                        message_id 9765
最终总结                              见群内后续消息
```

## 回滚

```text
git revert 对应提交并 push（推送前仅本地回滚）；线上同步后 ./cicd-web.sh restart。
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据。
