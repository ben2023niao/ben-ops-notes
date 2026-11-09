---
id: "doc-e4ea2ecc302f"
title: "2026-08-11 GitLab 迁移 · cn 分支全面切换（本地 / 服务器 / CI-CD）记录"
date: "2026-08-11T18:01:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "自动化", "安全运维", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-08-11-1801-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91GitLab%E8%BF%81%E7%A7%BBcn%E5%88%86%E6%94%AF%E5%88%87%E6%8D%A2%E6%9C%AC%E5%9C%B0%E6%9C%8D%E5%8A%A1%E5%99%A8CI-CD%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-08-11-1801-【运维】GitLab迁移cn分支切换本地服务器CI-CD记录.md"
sourceSha256: "d436cb5596fbe5a7994c7bb93442ae1e9351e835a1da9fc0fc5d6c05fa666a5d"
sourceSystem: "project-doc"
---

# 2026-08-11 GitLab 迁移 · cn 分支全面切换（本地 / 服务器 / CI-CD）记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-08-11-1801-【运维】GitLab迁移cn分支切换本地服务器CI-CD记录.md`

> 整理日期：2026-08-11 18:01｜日期依据：文件名日期

时间：2026-08-11 18:01（Asia/Manila）
项目：某业务公司 / PGServer cn（香港轻量运维分支）
范围：cn 分支迁移至 gitlab.zg-qptest.com/platgames/server-release；本地（VS Code）、服务器、机器人 CI/CD 全面切换到新 GitLab
执行人：Codex（本地工作区 + 宝塔/备用机只读复核）

## 任务边界

用户要求：

```text
参考 master 分支最近的操作；
验证 cn 分支迁移情况；
本地（VS Code）origin 修改为新的 GitLab；
服务器也修改为新的 GitLab 仓库地址；
机器人 CI/CD 也修改为新的；
把 cn 分支迁移到 gitlab.zg-qptest.com/platgames/server-release。
按标准工作流：workbench、逐步群通知、完成后验证、汇总文档发群、最后合并提交本地代码。
```

账号密码仅用于认证，未写入仓库/文档/群通知。

## 一、前置情况

```text
master 迁移已先行完成（2026-08-11 15:35-15:40）：本次复核新仓库 master=856aa42e、cn=5b1e79c2。
cn 本地分支：8ed099bf，领先新仓库 cn（5b1e79c2）4 个提交：
  e574fb9b docs: record hong kong resource sync
  c4a54355 docs: record hong kong vendor_d static sync
  a25b251b docs: add hong kong ops workbench
  8ed099bf ops: add hong kong vendor_c routing
服务器：宝塔/备用机 /opt/pgserver origin 已在 master 任务切换为新 GitLab（旧 origin 保留 old-gitlab）。
工作区未提交内容：2026-08-06 vendor_c/PG 资源同步补录文档与 workbench 更新，本次一并提交。
```

## 二、执行

```text
1. 本地 cn：
   - origin 保留为 old-gitlab（http://192.0.2.15:180/root/pgserver.git，可回退）；
   - 新增 origin=https://gitlab.zg-qptest.com/platgames/server-release.git；
   - osxkeychain 认证 fetch 成功（cn=5b1e79c2、master=856aa42e、main=d6ca9e20）。
2. 推送 cn：5b1e79c2..8ed099bf（快进，新增 4 个提交）。
3. 修正上游跟踪：remote rename 会把分支上游带到 old-gitlab，
   已执行 branch --set-upstream-to=origin/cn，保证后续 push/pull 走新仓库。
4. 服务器复核（宝塔 192.0.2.8 / 备用机 192.0.2.13）：
   - /opt/pgserver origin 均为新 GitLab（凭据内嵌 .git/config，root 权限，未入库）；
   - git fetch origin 成功：origin/master=856aa42e、origin/cn=8ed099bf。
5. 机器人 CI/CD：
   - 随仓库 origin 指向新 GitLab；cn 与 master 仓库均无 .gitlab-ci.yml、无硬编码旧 GitLab 地址；
   - ben-bot 容器挂载 /opt/pgserver，容器内 git rev-parse origin/cn=8ed099bf。
```

## 三、验证

```text
新仓库 ls-remote：master=856aa42e、cn=8ed099bf（与本地一致）。
宝塔/备用机 fetch 后：origin/master=856aa42e、origin/cn=8ed099bf。
机器人容器：origin/cn=8ed099bf，随仓库 origin 指向新 GitLab。
本地 cn CI：python3 docker/ci/check.py 全部通过（docker ops checks passed）。
旧仓库回退通道：old-gitlab ls-remote 正常（master=b42e0219、cn=5b1e79c2）。
分支上游：cn -> origin/cn（新仓库）。
```

## 飞机群通知 message_id

```text
3399：步骤 1/5 任务开始
3400：步骤 2/5 核查结果
3401：步骤 3/5 切换完成
3402：步骤 4/5 验证通过
3403：步骤 5/5 最终汇总
3404：文档附件（本事件文档）
```

## 最后安全点 / 遗留事项

```text
最后安全点：
  - 本地 cn=8ed099bf（新 origin），上游跟踪 origin/cn；master=856aa42e（新 origin）。
  - 宝塔/备用机 origin 均指向新 GitLab；旧 origin 保留 old-gitlab remote。
  - 服务器凭据位于各机 /opt/pgserver/.git/config（root 权限）；账号轮换需同步更新两处。
遗留：
  - 宝塔 /opt/pgserver 工作区有未跟踪 macOS 残留文件 docker/ben-bot/app/benbot/._home.py
    （2026-08-06 同步产生），会使机器人容器 docker/ci/check.py 编译检查报 null bytes；
    与本次迁移无关，建议删除该未跟踪文件后重跑机器人 CI。
  - 新仓库 main 分支未处理（用户仅要求 master+cn）。
```
