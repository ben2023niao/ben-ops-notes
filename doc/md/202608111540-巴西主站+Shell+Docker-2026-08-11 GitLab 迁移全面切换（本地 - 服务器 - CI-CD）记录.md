---
id: "doc-906dc84cc8ee"
title: "2026-08-11 GitLab 迁移全面切换（本地 / 服务器 / CI-CD）记录"
date: "2026-08-11T15:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "自动化", "安全运维", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-08-11-1540-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91GitLab%E8%BF%81%E7%A7%BB%E5%85%A8%E9%9D%A2%E5%88%87%E6%8D%A2%E6%9C%AC%E5%9C%B0%E6%9C%8D%E5%8A%A1%E5%99%A8CI-CD%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-08-11-1540-【运维】GitLab迁移全面切换本地服务器CI-CD记录.md"
sourceSha256: "c13c72226ad67719eeb899903d0a513035d6b972eee7f5aa14a613f000b94b3f"
sourceSystem: "project-doc"
---

# 2026-08-11 GitLab 迁移全面切换（本地 / 服务器 / CI-CD）记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-08-11-1540-【运维】GitLab迁移全面切换本地服务器CI-CD记录.md`

> 整理日期：2026-08-11 15:40｜日期依据：文件名日期

时间：2026-08-11 15:40（Asia/Manila）
项目：DBQP / PGServer master
范围：本地（VS Code）、服务器仓库、机器人 CI/CD 全面切换到新 GitLab
执行人：Codex（本地工作区 + 宝塔/备用机）

## 任务边界

用户要求：

```text
验证 master 分支迁移情况；
本地（VS Code）origin 修改为新的 GitLab；
服务器也修改为新的 GitLab 仓库地址；
机器人 CI/CD 也修改为新的。
新仓库：https://gitlab.zg-qptest.com/platgames/server-release.git
按标准工作流：workbench、逐步群通知、完成后验证、汇总文档发群、最后合并提交本地代码。
```

账号密码仅用于认证，未写入仓库/文档/群通知。

## 一、核查

```text
master 迁移：本地 master=50581e11；新 origin master=50581e11、cn=5b1e79c2 —— 一致。
本地（VS Code）：origin 已是新 GitLab（URL 无凭据），credential.helper=osxkeychain。
CI/CD：仓库内无 .gitlab-ci.yml；脚本无硬编码旧 GitLab 地址；
      机器人 CI/CD = docker/ci/check.py（本地检查）+ 发布/热更新脚本（基于仓库 git）。
服务器：宝塔 /opt/pgserver 与备用机 /opt/pgserver 的 origin 仍指向旧 GitLab。
```

## 二、切换

```text
1. 本地：确认 origin=https://gitlab.zg-qptest.com/platgames/server-release.git（此前已切），osxkeychain 就绪。
2. 宝塔 /opt/pgserver：
   - 旧 origin 保留为 old-gitlab remote；
   - origin set-url 为新 GitLab（凭据内嵌于 .git/config，root 仅服务器可读，未入库）；
   - git fetch origin master 成功（origin/master=50581e11）。
3. 备用机 /opt/pgserver：同上切换并验证；机器人容器内 git fetch/ls-remote 正常。
4. 机器人 CI/CD：随仓库 origin 指向新 GitLab（无独立 CI 配置需改）。
```

## 三、验证

```text
宝塔/备用机：git fetch origin master -> origin/master=50581e11 成功；
机器人容器：git ls-remote origin（master=50581e11、cn=5b1e79c2）、CI 检查通过、热更新 dry-run 通过。
```

## 飞机群通知 message_id

```text
3393：步骤 1/5 任务开始
3394：步骤 2/5 核查结果
3395：步骤 3/5 切换完成
3396：步骤 4/5 验证通过
3397：步骤 5/5 最终汇总
3398：文档附件（本事件文档）
```

## 最后安全点 / 遗留事项

```text
当前 master：50581e11（本地 = 新 origin）。
服务器 origin：宝塔/备用机均指向 gitlab.zg-qptest.com/platgames/server-release（旧 origin 保留 old-gitlab remote）。
服务器凭据：位于各机 /opt/pgserver/.git/config（root 权限），未入库/文档/群通知；如账号轮换需同步更新两处。
遗留：
  - 仓库内无 .gitlab-ci.yml；如后续需要新 GitLab 跑流水线，可另行补充。
  - 新仓库 main 分支未处理（用户仅要求 master+cn）。
```
