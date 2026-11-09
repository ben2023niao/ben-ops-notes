---
id: "doc-ec4caa46da45"
title: "测试环境 Webhook 自动发布清理业务工作区提示词"
date: "2026-07-09T10:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-09-1000-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83Webhook%E8%87%AA%E5%8A%A8%E5%8F%91%E5%B8%83%E6%B8%85%E7%90%86%E4%B8%9A%E5%8A%A1%E5%B7%A5%E4%BD%9C%E5%8C%BA%E6%8F%90%E7%A4%BA%E8%AF%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-09-1000-【修复Bug】测试环境Webhook自动发布清理业务工作区提示词.md"
sourceSha256: "576afe21234b96fc1e7a836c3498cc21012e04bb6bd70fd543f1ca1e930ccab5"
sourceSystem: "project-doc"
---

# 测试环境 Webhook 自动发布清理业务工作区提示词

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607091000-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20Webhook%20%E8%87%AA%E5%8A%A8%E5%8F%91%E5%B8%83%E6%B8%85%E7%90%86%E4%B8%9A%E5%8A%A1%E5%B7%A5%E4%BD%9C%E5%8C%BA%E6%8F%90%E7%A4%BA%E8%AF%8D.md)

> 整理日期：2026-07-09 10:00｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-07-09
环境：游点涩测试环境（dev 分支）
分类：修复Bug

用途：给 AI 或运维同学复刻“测试环境 webhook 自动发布遇到业务代码本地未提交修改时，自动清理工作区并继续发布”的完整操作流程。

把下面整段提示词发给 AI，让 AI 先确认当前环境和分支，再执行。

```text
你是运维自动化助手。我要修复“游点涩测试环境 / dev 分支” webhook 自动发布经常因为业务代码工作区 dirty 而失败的问题。

核心背景：
1. 测试环境运维仓库路径：/opt/docker-youdianse-php。
2. 业务代码仓库路径：/opt/docker-youdianse-php/src/youdianse-php。
3. webhook 自动发布入口会部署当前运维分支对应的业务 dev 分支最新提交。
4. 近期测试服务器有人为了排查图片缩略图、白名单、密钥、容器配置等问题，进入业务目录或容器做过临时修改。
5. 旧逻辑在发布前统一执行 ensure_git_clean；只要业务仓库有本地未提交修改，webhook 自动发布就失败。
6. 失败日志示例：
   - 2026-07-08 21:04 webhook：业务代码存在本地未提交修改，自动发布失败。
   - 2026-07-08 22:39 webhook：业务代码存在本地未提交修改，自动发布失败。
   - 2026-07-08 23:39 webhook：业务代码存在本地未提交修改，自动发布失败。
7. 测试环境自动发布应该只部署 Git 远端提交，不应该把服务器上的临时改动带入镜像。

目标：
1. 只修复测试环境 dev 分支的 webhook 自动发布链路。
2. webhook 自动发布遇到业务代码 dirty 时，自动执行：
   git reset --hard HEAD
   git clean -fd
   然后继续 fetch / checkout / pull / build / deploy。
3. 清理前只记录 dirty 文件状态，不打印文件内容，不打印密钥。
4. 清理后必须再次确认业务工作区干净。
5. 网页人工发布仍然保持原保护：发现业务代码 dirty 就拒绝发布，提醒人工确认。
6. CLI 人工发布默认也保持原保护，不自动清理。
7. 修复后写文档、提交推送、测试服务器拉取、重启 CICD Web，并验证 webhook 真的可以自动清理 dirty 工作区。
8. 最后发送 Telegram 普通文本总结，并附上本提示词文档。

测试环境信息：
- 运维仓库本地路径：<LOCAL_DEV_REPO_PATH>
- 仓库分支：dev
- 测试服务器：root@38.92.8.34
- 服务器运维目录：/opt/docker-youdianse-php
- 业务仓库目录：/opt/docker-youdianse-php/src/youdianse-php
- CICD Web 测试访问地址：https://cicd.youdianse-test.xyz
- Webhook 自动发布本地入口：http://203.0.113.1:18090/auto-deploy/<YOUDIANSE_WEBHOOK_TOKEN>
- Telegram token/chat_id 来源：服务器本地 cicd-web/runtime/secrets.env 或 cicd-web/config/settings.json；不要打印敏感值。

边界要求：
1. 只操作测试环境，不要改线上 main 分支，不要登录线上服务器。
2. 不要打印服务器密码、SSH key、Telegram token、chat_id、发布密码、webhook token、私钥。
3. 不要把任何密码、token、chat_id 写进 Git。
4. 不要在日志里 cat 业务密钥文件、.env、白名单密钥文件内容。
5. 自动清理只用于 webhook 自动发布；人工网页发布不要自动清理。
6. 不要对运维仓库执行 reset/clean；只允许 webhook 自动发布清理业务仓库 src/youdianse-php。

排查步骤：
1. 进入本地运维仓库：
   cd <LOCAL_DEV_REPO_PATH>
2. 确认分支：
   git status --short --branch
   git branch --show-current
3. 搜索发布链路：
   rg -n "ensure_git_clean|prepare_business_code|run_deploy|webhook|auto-deploy|业务代码存在本地未提交修改" -S cicd-web README.md docs
4. 登录测试服务器，查看最近 webhook 发布日志：
   cd /opt/docker-youdianse-php
   find cicd-web/logs -maxdepth 1 -type f -name "*.log.txt" -printf "%T@ %TY-%Tm-%Td %TH:%TM %f\n" | sort -nr | head -30
   grep -RIl "Webhook\\|业务代码存在本地未提交修改\\|git pull" cicd-web/logs | xargs -r ls -lt | head -20
5. 查看最近 shell 操作记录，只做摘要，不输出敏感文件内容：
   tail -300 /root/.bash_history
   重点确认是否出现进入 src/youdianse-php 后编辑文件、进入容器改配置、手工 git reset/clean 等痕迹。
6. 查看业务仓库当前状态：
   git -C src/youdianse-php status --short --branch

本地修改：
1. 修改 cicd-web/core.py：
   - 保留 ensure_git_clean 给人工发布使用。
   - 新增 clean_business_worktree_for_auto_deploy(logger, notify_enabled)：
     a. git -C src/youdianse-php status --porcelain
     b. 如果干净，记录“Webhook 自动发布：业务代码工作区干净，无需清理。”
     c. 如果 dirty，记录 dirty 项数量和最多前 20 行状态。
     d. 记录说明：Webhook 自动发布只部署 Git 远端提交，本地临时改动不会带入镜像。
     e. 执行 git -C src/youdianse-php reset --hard HEAD
     f. 执行 git -C src/youdianse-php clean -fd
     g. 再次 git status --porcelain；仍 dirty 则失败并要求人工检查。
   - 修改 prepare_business_code(..., clean_worktree=False)：
     clean_worktree=True 时调用 clean_business_worktree_for_auto_deploy；
     clean_worktree=False 时调用 ensure_git_clean。
   - 修改 run_deploy(..., clean_business_worktree=False)，并把参数传给 prepare_business_code。
2. 修改 cicd-web/webhook.py：
   - webhook 调用 run_deploy 时传入 clean_business_worktree=True。
3. 修改 README：
   - 写清 webhook 自动发布会清理业务仓库 dirty。
   - 写清网页人工发布仍会拒绝 dirty 工作区。
4. 新增 docs/2026-07-09-1000-【修复Bug】测试环境Webhook自动发布清理业务工作区提示词.md。

本地验证：
1. Python 语法：
   python3 -m py_compile cicd-web.py cicd-web/core.py cicd-web/webhook.py cicd-web/config.py cicd-web/telegram.py cicd-web/command.py
2. JSON 校验：
   python3 -m json.tool cicd-web/config/settings.json >/tmp/youdianse-settings-check.json
3. Shell 语法：
   bash -n cicd-web.sh entrypoint/web-entrypoint.sh entrypoint/cron-entrypoint.sh entrypoint/cron-task-runner.sh entrypoint/queue-watchdog.sh
4. diff 检查：
   git diff --check
5. 搜索确认 webhook 已传 clean_business_worktree=True，人工发布没有传：
   rg -n "clean_business_worktree|clean_business_worktree=True|ensure_git_clean|clean_business_worktree_for_auto_deploy" -S cicd-web

提交推送：
1. git diff --stat
2. git add README.md cicd-web/core.py cicd-web/webhook.py docs/2026-07-09-1000-【修复Bug】测试环境Webhook自动发布清理业务工作区提示词.md
3. git commit -m "Auto clean business worktree for webhook deploys"
4. git push origin dev
5. git rev-parse --short HEAD

测试服务器部署：
1. SSH 登录测试服务器。
2. 进入运维目录：
   cd /opt/docker-youdianse-php
3. 确认状态：
   git status --short --branch
   git rev-parse --short HEAD
4. 拉取 dev：
   git pull --ff-only origin dev
5. 重启 CICD Web：
   ./cicd-web.sh restart
   ./cicd-web.sh status

Webhook 自动清理验证：
1. 在业务仓库制造一个安全的未提交测试文件，不要改真实业务密钥：
   cd /opt/docker-youdianse-php
   mkdir -p src/youdianse-php/runtime/webhook-clean-test
   echo "webhook clean test $(date)" > src/youdianse-php/runtime/webhook-clean-test/dirty.txt
   git -C src/youdianse-php status --porcelain
2. 从服务器本地触发 webhook，不打印 token：
   set -a
   . cicd-web/runtime/secrets.env
   set +a
   curl -sS "http://203.0.113.1:18090/auto-deploy/${YOUDIANSE_WEBHOOK_TOKEN}"
3. 等待发布完成，查看最新 webhook 日志：
   latest="$(ls -t cicd-web/logs/*Webhook-自动发布*.log.txt | head -1)"
   grep -nE "Webhook 自动发布：检测到业务代码工作区|git reset --hard HEAD|git clean -fd|工作区已恢复干净|综合结论：SUCCESS|发布结果" "$latest"
4. 验证测试 dirty 文件已被自动清理：
   test ! -e src/youdianse-php/runtime/webhook-clean-test/dirty.txt && echo "dirty test file removed: OK"
   git -C src/youdianse-php status --porcelain
5. 验证容器运行：
   docker ps --format "{{.Names}} {{.Image}} {{.Status}}" | grep -E "youdianse-dev-php-(web|cron|nginx)"

人工发布保护验证：
1. 不需要真的走网页发布删除文件。
2. 代码层确认 cicd-web/steps/publish.py 调用 run_deploy 时未传 clean_business_worktree=True。
3. 保持人工发布遇到 dirty 时仍走 ensure_git_clean，提醒人工确认。

Telegram 总结通知：
1. 发送前不要打印 token/chat_id。
2. 使用服务器本地 cicd-web/runtime/secrets.env 或 cicd-web/config/settings.json 读取 Telegram 配置。
3. 发送普通文本消息，并把本提示词文档作为文件附件发到运维飞机群。
4. 消息模板：

游点涩测试环境 Webhook 自动发布修复完成
<当前北京时间>

问题：测试服务器业务仓库 src/youdianse-php 偶尔存在本地未提交修改，导致 webhook 自动发布失败，需要人工上去 git reset --hard / git clean -fd。
排查：近期 shell 记录存在进入业务目录和容器做临时修改、之后手工 reset/clean 的操作；2026-07-08 多次 webhook 日志显示“业务代码存在本地未提交修改”。
修复：仅 webhook 自动发布增加部署前业务工作区自动清理，执行 git reset --hard HEAD 和 git clean -fd，再拉取 dev 最新提交发布。
边界：网页人工发布仍保持 dirty 工作区保护，不自动清理，避免误删人工排查改动。
验证：已制造安全 dirty 测试文件触发 webhook，自动清理成功，发布 SUCCESS，业务工作区恢复 clean。
文档附件：2026-07-09-1000-【修复Bug】测试环境Webhook自动发布清理业务工作区提示词.md

@Ben_Bird @jett_yunwei @Kermit0824 @melo_sre

完成后汇报：
1. 本地 dev 分支提交号。
2. 测试服务器是否已拉到最新 dev。
3. CICD Web 是否已重启。
4. webhook dirty 自动清理验证结果。
5. 最新 webhook 发布是否 SUCCESS。
6. 人工发布 dirty 保护是否保留。
7. Telegram 文本和文档附件是否发送成功。
```

## 本次排查结论

```text
测试服务器 shell 记录显示，近期存在进入业务仓库 src/youdianse-php 编辑文件、进入 youdianse-dev-php-web 容器排查、以及手工 git reset --hard / git clean -fd 的操作。
2026-07-08 21:04、22:39、23:39 的 webhook 自动发布日志均显示：业务代码存在本地未提交修改，默认拒绝发布。
现有人工网页发布的 dirty 保护是合理的，但 webhook 自动发布应只部署 Git 远端提交，因此改为 webhook 专用自动清理。
```
