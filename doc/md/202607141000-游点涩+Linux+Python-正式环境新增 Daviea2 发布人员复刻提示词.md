---
id: "doc-f5a36d79ebe1"
title: "正式环境新增 Daviea2 发布人员复刻提示词"
date: "2026-07-14T10:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Python", "Docker", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-14-1000-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%88%B0%E6%AD%A3%E5%BC%8F%E7%8E%AF%E5%A2%83%E6%96%B0%E5%A2%9EDaviea2%E5%8F%91%E5%B8%83%E4%BA%BA%E5%91%98%E5%A4%8D%E5%88%BB%E6%8F%90%E7%A4%BA%E8%AF%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-14-1000-【运维记录】测试环境到正式环境新增Daviea2发布人员复刻提示词.md"
sourceSha256: "be92a9d428575df79332e1eab8b3807d1b567d12d8f2eebddfe0baf7d4d8b898"
sourceSystem: "project-doc"
---

# 正式环境新增 Daviea2 发布人员复刻提示词

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-14-1000-【运维记录】测试环境到正式环境新增Daviea2发布人员复刻提示词.md`

> 整理日期：2026-07-14 10:00｜日期依据：文件名日期

环境标签：混合

文档日期：2026-07-14
环境：游点涩测试环境（dev 分支；正式环境复刻参考）
分类：运维记录

用途：参考测试环境 dev 分支的改动，在正式环境 main 分支为 CICD Web 增加新运维发布人员 `@Daviea2`。

把下面整段提示词发给 AI，补齐正式环境占位符后执行。

```text
你是运维自动化助手。请在“正式环境 / main 分支”的 CICD Web 发布人员列表中新增一名运维。

新增人员：
- Telegram 用户名：@Daviea2
- CICD Web 显示名：运维-@Daviea2

目标：
1. 修改 `cicd-web/config/settings.json` 的 `publish.operators`。
2. 把 `运维-@Daviea2` 放在现有运维人员之后、后端人员之前。
3. 保留全部现有运维和后端人员，不改变人员顺序。
4. 本次只增加发布页面操作人；不要修改 `telegram.ops_mentions`、token、密码、chat_id、webhook、业务配置、分支或域名。
5. 提交并推送 main 分支，在正式服务器拉取后重启 CICD Web，并验证新名单已经加载。

正式环境信息：
- 本地运维仓库：<LOCAL_MAIN_REPO_PATH>
- 正式服务器 SSH：<MAIN_SSH_USER>@<MAIN_SERVER_IP>
- 服务器运维目录：<MAIN_SERVER_OPS_DIR>
- CICD Web 地址：<MAIN_CICD_URL>

执行步骤：

1. 检查本地 main 分支和工作区，避免覆盖无关改动：
   git branch --show-current
   git status --short --branch

2. 修改 `cicd-web/config/settings.json`，让运维名单包含：
   - `运维-@Ben_Bird`
   - `运维-@jett_yunwei`
   - `运维-@Kermit0824`
   - `运维-@melo_sre`
   - `运维-@Daviea2`

3. 本地验证 JSON、名单和差异：
   python3 -m json.tool cicd-web/config/settings.json >/dev/null
   python3 - <<'PY'
   import json
   cfg = json.load(open('cicd-web/config/settings.json', encoding='utf-8'))
   operators = cfg['publish']['operators']
   assert operators.count('运维-@Daviea2') == 1
   assert operators.index('运维-@Daviea2') < next(i for i, item in enumerate(operators) if item.startswith('后端-'))
   print('\n'.join(operators))
   PY
   git diff --check
   git diff -- cicd-web/config/settings.json

4. 只提交本次相关文件并推送 main：
   git add cicd-web/config/settings.json
   git commit -m "Add Daviea2 to CICD operators"
   git push origin main

5. 登录正式服务器并部署：
   ssh <MAIN_SSH_USER>@<MAIN_SERVER_IP>
   cd <MAIN_SERVER_OPS_DIR>
   git status --short --branch
   git pull --ff-only origin main
   ./cicd-web.sh restart
   ./cicd-web.sh status

6. 在服务器验证配置，不输出任何敏感值：
   python3 - <<'PY'
   import json
   cfg = json.load(open('cicd-web/config/settings.json', encoding='utf-8'))
   operators = cfg['publish']['operators']
   assert operators.count('运维-@Daviea2') == 1
   print('\n'.join(operators))
   PY
   curl -fsS http://203.0.113.1:18090/ >/dev/null

7. 打开 `<MAIN_CICD_URL>`，确认操作人下拉列表出现 `运维-@Daviea2`。

如果服务器工作区不干净、main 无法 fast-forward、CICD Web 重启失败或健康检查失败，立即停止，不要强制覆盖；保留错误信息并汇报。

完成后汇报：
1. main 分支提交号。
2. 正式服务器当前提交号。
3. CICD Web 运行状态和健康检查结果。
4. `运维-@Daviea2` 是否已出现在发布人员列表中。
```

测试环境参考：dev 分支的 `cicd-web/config/settings.json` 已在现有运维人员之后新增 `运维-@Daviea2`；仅发布人员名单变化，通知 @ 名单保持不变。
