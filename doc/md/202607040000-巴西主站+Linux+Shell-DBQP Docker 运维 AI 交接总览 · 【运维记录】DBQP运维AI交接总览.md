---
id: "doc-220ce174fcf6"
title: "DBQP Docker 运维 AI 交接总览 · 【运维记录】DBQP运维AI交接总览"
date: "2026-07-04T00:00:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91DBQP%E8%BF%90%E7%BB%B4AI%E4%BA%A4%E6%8E%A5%E6%80%BB%E8%A7%88.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/【运维记录】DBQP运维AI交接总览.md"
sourceSha256: "06869aff8664b23e9b6c3aeacaff969af12326ccc20e727db10b4b794df968b7"
sourceSystem: "project-doc"
---

# DBQP Docker 运维 AI 交接总览 · 【运维记录】DBQP运维AI交接总览

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/【运维记录】DBQP运维AI交接总览.md`

> 整理日期：2026-07-04 00:00｜日期依据：正文日期

这份文档是给各类 AI / Codex / 运维助手接手 DBQP Docker 运维使用的长期背景资料。

新会话快速恢复优先读取轻量工作台：

```text
docker/workbench/START_HERE.md
docker/workbench/CURRENT_TASK.md
docker/workbench/CURRENT_STATE.md
docker/workbench/MACHINE_ACCESS_MATRIX.md
docker/workbench/PROJECT_RUNTIME_CHAINS.md
docker/workbench/DECISIONS.md
```

需要查历史背景时，再阅读本文、`docker/README.md`、`docker/deploy/README.md`、`docker/ben-bot/README.md`。

## 近期维护记录

大范围线上维护、域名调整、宝塔/Nginx 映射、发布策略或机器人能力改造后，需要在 `docker/doc` 新增一份日期格式 prompt 文档，方便后续 AI 直接接手。

- `2026-07-04-【网络调整】PG拆分静态域名池维护说明.md`：PG3 / PG4 / PG5 特殊资源包静态域名池扩成 22 个，宝塔 Nginx 同步映射 66 个静态域名，发布 `platform-api 442378e`。
- `2026-07-04-【优化+修复Bug】后端磁盘清理与PG65启动问题排查.md`：后端 01/02 保守清理 7 天以上 Docker 历史垃圾，发布脚本固化 75% 历史清理阈值；定位 PG65 `/cdn-cgi/rum` 为 Cloudflare RUM 噪音；修复 PG 新版客户端请求 `api.*` 验证接口导致的 520/CORS 问题，并整理 verify `gm[0].gid` 给开发排查。
- `2026-07-04-【修复Bug+网络调整】PG接口跨域与API反代修复说明.md`：PG 麻将胡了 `N1000PHFIYR04` 专项排查与修复文档，说明 `api.*` 未被活跃宝塔站点接住导致 520/CORS，记录 `api.*` 接入 PG 反代、OPTIONS 204、`/api/report/timing` 204、线上验证和回滚方式。
- `2026-07-04-【架构改造】PG拆分静态资源接入GCS和CDN说明.md`：PG3 / PG4 / PG5 新静态目录未进 GCS/Cloud CDN 导致慢加载，记录新增 live/backup sync、backend bucket、URL map、Cloudflare DNS 灰云和验证方式。
- `2026-07-06-【问题排查+网络调整】PG阿努比斯与玻尔修斯网络问题排查.md`：PG 阿努比斯 `1623475` / 玻尔修斯传奇 `128` 卡 50% 专项排查，确认静态资源不是主因，定位 `pg-games.t6qv8m.icu` 会误拼 verify host 为 `pg-games.t6qv8api.icu`，导致 DNS 失败、请求未到后端，并给出后端 API host 生成逻辑修复建议。
- `2026-07-06-【网络调整】PG动态入口m.icu域名下线特例说明.md`：记录 PG 客户端会把 `m.icu` 动态入口误拼成 `api.icu` 的特例，已从 `pg.json` 的 default / pg3 / pg4 / pg5 `game_hosts` 下线 `pg-games.t6qv8m.icu`、`pg-games.6qv8m.icu`，并在发布脚本加预检拦截后续同类域名。
- `2026-07-06-【修复Bug】PG卡50百分比问题修复上线复测记录.md`：记录 `e127daa` 发布到两台 `platform-api`、之前 6 个 PG 卡 50% 问题游戏运行态域名池复测、最近日志确认无 `t6qv8api` 命中，以及飞机群通知 `message_id=2642`。
- `2026-07-08-【补静态资源】PG126鼠鼠福福静态资源补文件与GCS同步记录.md`：记录 PG126 鼠鼠福福 brazil 多语言未显示问题，宝塔 `pg-static/126` 缺 12 个静态文件，已从 `docker/补宝塔游戏静态文件/126` 补齐到 273 个文件并同步 GCS live/backup，公开域名巡检全部 OK，飞机群通知 `message_id=2643`。
- `2026-07-09-【修复Bug+网络调整】PG四大神兽静态资源CORS修复与全游戏巡检记录.md`：记录 PG3 四大神兽 `1849515` 静态资源 `shared/.../index.json` CORS 报错处理，已补跑 PG 静态相关 5 个 GCS bucket CORS，复测 88 个静态域名代表资源和 127 个宝塔实际游戏目录样本失败 0，飞机群通知 `message_id=2644`。
- `2026-07-09-【问题排查】测试问题表运维排查与可修复项复核记录.md`：按测试问题表整理运维可处理项，复核 PG/TADA/PP/Playson 静态链路；确认 PG71、TADA 摇钱树、PP 沉睡之龙历史图片、PG 多个目录 GCS live/backup 同步无缺口；标记 Playson 公网入口源、PG 金蛇/招财喵语言参数与资源包为需入口源站或开发处理。
- `2026-07-09-【问题排查+网络调整】未修复问题逐项复查与PG风险域名拦截记录.md`：按新测试附件逐项复查 16 条未闭环问题；修复宝塔默认站点仍可接住旧 PG `m.icu` 风险动态域名的问题，域名同步脚本过滤 PG 的 `t6qv8m.icu` / `6qv8m.icu` 动态入口和对应 `api.*`，并在共享反代层对旧 `pg-games/api` 风险 Host 返回 410；同时复核 PG/PP 静态资源、GCS、CORS 和后端日志。
- `2026-07-13-【补静态资源】PG1312883黄金摇钱树静态资源补文件与GCS同步记录.md`：记录 PG1312883 黄金摇钱树资源包校验，确认宝塔原目录缺 10 个文件且已有 296 个文件哈希一致；只新增缺失文件并同步 GCS live/backup，原缺失文件 22 域名巡检及整包 CDN/GCS 巡检共 832 次请求失败 0。
- `2026-07-16-【补静态资源】PG4静态资源完整包增量补齐与GCS同步记录.md`：记录从 AWS S3 下载并校验 `pg4static.tar.gz`，向宝塔 `pg4-static` 只新增 4,975 个缺失文件，同步 GCS live/backup，按 host 刷新 22 个 PG4 Cloud CDN 域名；GCS 内容抽检 44 次、CDN 验证 66 次失败均为 0，飞机群通知 `message_id=2691`。
- `2026-07-16-【修复Bug】TADA幸运鹦鹉lm斜杠对象漏同步修复记录.md`：记录幸运鹦鹉两层故障：实际入口 `/lm/?...` 命中旧 32KB GCS 斜杠对象，以及新页面运行阶段仍把 `.cyou/.icu` 后端错误追加 `.com`。已加入 Fetch/XHR 域名规范化补丁，同步 live/backup 的 `/lm/` 与 `/lm/index.html` 四个对象，完成 22 域名 × 2 入口的 CDN 刷新和 44/44 公开校验；无临时注入的 Docker Chromium 已进入 `JOGAR` 页面，`/lm/req` 两次 200、错误域名和 `MSG 999.2` 均为 0，飞机群截图通知 `message_id=2693`。
- `2026-07-16-【修复Bug】TADA阿里巴巴ali规则界面loading修复记录.md`：记录阿里巴巴 `GameID=110` 规则页问题。首轮兼容对象和 `110 -> intro1.html` 发布后定位到专用 chunk 缺失；开发正式修复 `fbf75231` 已发布 TADA 01/02，新版 `intro` 与 `INTRO_ALI` 数据在 22/22 域名通过，4 个代表节点的页面脚本 56/56 通过，旧缺失 chunk 已不再被引用。部署验证文档已发飞机群，`message_id=2714`；当前仅剩真实浏览器“齿轮 -> 叹号”点击截图待补，尚未标记完整 UI 闭环。
- `2026-07-17-【补静态资源】TADATCB巴西静态资源缺失文件补齐与GCS同步记录.md`：记录 TCB / GameID 460 巴西静态资源补齐。开发 ZIP 与预发布来源一致；宝塔原有 231 文件全部哈希一致，只新增 4 个缺失文件并同步 GCS live/backup；22 个 `tada-statics1` CDN host 的 `/tcb/*` invalidation 全部 `DONE`，生产 22 域名 × 6 路径共 132/132 HTTP 与 SHA256 验证通过，预发布复核 6/6 通过；最终文档通知 `message_id=2732`。
- `2026-07-20-【修复Bug+架构改造】巴西PG71归入PG3与跨域修复记录.md`：记录 PG71 同步归入 platform-api、PG 运行时和宝塔生成器的 PG3 分组，提交 `abe3e08c` 发布到 PG/API 双后台 4/4 成功，宝塔实际生成脚本已备份、补齐并通过只生成验证；同时重写 PG3 live/backup CORS，对四大神兽报错路径执行 22/22 Cloud CDN 精确刷新，最终 22 域名 OPTIONS/GET 44/44 和两台巴西后台各 10/10 复测通过，最终飞机文档附件 `message_id=2798`。
- `2026-07-20-【数据维护】巴西PP结果集GCS源包替换记录.md`：记录使用当前 Google Cloud 账号的 `gs://dbqp-storage-slots-statics/game-results/pp_db.tar.gz`，将宝塔源目录和两台巴西后端从旧单库 `pp.db` 原子切换为 85 个分库；三处文件数、总字节数及清单 SHA256 一致，两台后端 170 次 SQLite `quick_check` 全部通过，PP 容器和公开反代链路正常，三处旧目录均保留可回滚，飞机文档附件 `message_id=2810`。
- `2026-07-20-【修复Bug+网络调整】巴西PG3四大神兽Token预检跨域修复记录.md`：记录四大神兽 `1849515` 的普通 GET 有 ACAO、但携带 `Token` 时 OPTIONS 预检失败的真实根因；已在 PG3 live/backup bucket 和宝塔持久同步模板中加入 `Token`，对 22 个 PG3 host 精确刷新报错路径，最终 GET 22/22、OPTIONS 22/22、两台巴西后台 10/10 通过，飞机文档附件 `message_id=2814`。
- `2026-07-20-【架构改造】香港禅道服务器Docker部署与每日快照配置记录.md`：记录在 `asia-east2-a` 创建 2C/8G、100GB `pd-balanced` 的独立禅道服务器 `dbqp-hk-zentao-prod-01`，部署官方 Docker 禅道 18.5，公网地址 `34.96.128.22:80`，SSH 为 root 公钥认证且不开放 3306；禅道与现有香港 Nginx 磁盘均绑定每日快照、保留 7 天。当前 Web 首次安装向导可访问，管理员账号待页面设置，飞机文档附件 `message_id=2820`。

更新时间：2026-07-20
当前关键发布提交：`abe3e08c fix: route PG 71 through pg3 static pool`

## 你的角色

你是 DBQP 项目的 Docker 运维协作助手。你的主要职责是：

- 维护 `docker/` 目录内的运维脚本、机器人、发布配置、部署文档。
- 协助发布 PG/TADA/PP/PPK/PLAYSON/PANDA/platform-api。
- 协助排查发布失败、容器日志、端口、镜像构建、宝塔反代、静态资源同步、机器人交互问题。
- 在需要兼容开发最新业务代码时，优先只改 `docker/` 下运维代码。

非常重要：

- 运维侧默认不能修改开发业务代码，除非用户明确授权。业务目录如 `pg/`、`tada/`、`pp/`、`ppk/`、`playson/`、`panda/`、`platform-api/`、`configs.py` 等，原则上只读分析。
- 如果开发提交导致部署不兼容，先通过 `docker/` 的 Dockerfile、部署脚本、服务配置、机器人逻辑去兼容。
- 不要提交密钥、token、密码、`.env` 内容。
- 不要回滚用户已有改动，不要用 `git reset --hard`、`git checkout -- <file>` 这类破坏性命令，除非用户明确要求。
- 运维核验、配置扫描和通知尽量用 Python 实现；shell 只做启动器，避免多层 ssh / docker exec / here-doc 引号错乱。

## 强制规则：线上操作分步飞机群通知

本条作为强制运维规则长期落库：凡是生产部署、云资源、DNS、数据同步等多步骤操作，每完成一个可验证步骤就必须立即发送一次飞机群进度，不能只在最后汇总。适用范围包括但不限于：代码发布、宝塔/Nginx 调整、静态资源补齐、GCS 同步、CDN 刷新、域名配置、数据备份/恢复和线上故障修复。

规则落库飞机群通知：`监控报警群 message_id=2735`（2026-07-17）。

“巴西项目”强制标识规则通知：`监控报警群 message_id=2741`（2026-07-17）。

执行要求：

1. 开始操作前发送“任务开始”通知，说明来源、目标、影响范围和当前正在执行的第一步。
2. 先把任务拆成有明确完成条件的阶段；每完成一个阶段，立即发送一次进度通知，不等待全部任务结束。
3. 每条进度通知必须包含：任务名称、`步骤 X/Y`、本步完成内容、关键验证证据、当前状态和下一步。
4. 每条开始、过程、失败和最终通知都必须明确带上“巴西项目”标识；标题统一使用 `【巴西项目｜<任务名称>｜步骤 X/Y】`，正文同时包含 `项目：巴西`，不能只依赖群上下文判断项目。
5. 验证证据优先给出可复核数字，例如文件数、对象数、HTTP 成功数、SHA256、CDN operation `DONE` 数、双后台成功数。
6. 阶段失败、被阻塞或只完成部分内容时，也必须立即通知；明确失败点、线上是否已发生变更、回滚/保留状态和后续处理，禁止静默等待到最终汇总。
7. 未完成对应验证前禁止发送“成功”通知。只通过服务端、资源链路或部分节点时，必须明确标注验证边界和剩余待验项。
8. 全部阶段完成后发送最终汇总；有运维文档、日志或截图时一并作为附件发送。
9. 把开始、各步骤和最终通知的 Telegram `message_id` 回写到事件文档，方便后续交接和审计。
10. “一步”指有意义的操作阶段，不是每一条 shell 命令；在保证群内可见进度的同时避免无信息量刷屏。
11. 通知统一使用宝塔现有 `dbqp-ben-bot` 和监控报警群，禁止在日志、文档或命令输出中泄露 bot token。
12. 涉及运维配置包、规则包或交接文档更新时，在当次最终通知中同时说明本规则已经执行或启用。

推荐阶段模板：

```text
【巴西项目｜任务名称｜开始】
项目：巴西

【巴西项目｜任务名称｜步骤 1/N】来源与完整性校验
【巴西项目｜任务名称｜步骤 2/N】差异预演与备份
【巴西项目｜任务名称｜步骤 3/N】执行线上变更
【巴西项目｜任务名称｜步骤 4/N】同步、刷新和全链路验证
【巴西项目｜任务名称｜步骤 5/N】最终汇总、文档和附件
```

## 当前线上概况

线上分为三类机器：

1. 宝塔服务器：`35.247.205.6`
   - 宿主机仓库路径：`/opt/pgserver`
   - ben-bot 容器名：`dbqp-ben-bot`
   - ben-bot 容器内仓库挂载：`/workspace/pgserver`
   - 宝塔静态目录挂载：`/www/wwwroot`
   - 宝塔面板目录挂载：`/www/server`
   - 机器人实例：宝塔为备用空闲实例（idle 不轮询），身份标识「宝塔备用实例（空闲）」。

2. 后台 01：`dbqp-saopaulo-sanic-prod-01`
   - 内网 IP：`203.0.113.1`
   - 发布容器后缀：`-01`

3. 后台 02：`dbqp-saopaulo-sanic-prod-02`
   - 内网 IP：`203.0.113.1`
   - 发布容器后缀：`-02`

4. 后台 03：`dbqp-saopaulo-sanic-prod-03`（2026-08-07 起生产业务后端）
   - 内网 IP：`203.0.113.1`
   - 发布容器后缀：`-03`

5. 备用流量入口机：`dbqp-saopaulo-nginx-standby-01`（2026-08-07 创建）
   - 内网 IP：`203.0.113.1`；公网静态 IP：`34.151.249.53`
   - 运行 Docker + Nginx 1.30（镜像宝塔配置/证书/静态资源，被动备援，未切 DNS）
   - 机器人容器：`dbqp-ben-bot-standby`（当前活动实例，poll 轮询）
   - 机器人部署原则：后续机器人统一部署到备用 nginx 服务器（run_standby_bot.sh）
   - 切回宝塔：先停备用机 poll，再在宝塔执行 `CONTAINER_NAME=dbqp-ben-bot ... run_standby_bot.sh poll`
   - 环境文件：`/opt/benbot-runtime.env`（root 600，含凭据，不入库）

机器人日志查看已覆盖 prod-01/prod-02/prod-03（三台后端小时日志）；03 日志维护栈（logrotate + S3 归档 + systemd timer）已于 2026-08-07 补齐。

6. 香港入口机：`dbqp-hongkong-game-results-data-bt`（34.92.13.108 / 203.0.113.1，独立环境）

7. 东京 GitLab/CICD：`dbqp-tokyo-gitlab-cicd-01`（34.146.121.225，旧代码仓库 + Beszel Hub；代码 origin 已于 2026-08-11 迁移至 gitlab.zg-qptest.com/platgames/server-release）

完整服务器用途与关系见 `docker/线上服务器信息/服务器用途与关系.md`。

最近一次全量发布验证记录：

- 曾执行 `all latest --strategy single-build --image-transfer internal`。
- 两台后台发布成功，`PG/TADA/PP/PPK/PLAYSON/PANDA/api` 全部 Up。
- 当时游戏服务镜像统一为 `pgserver:master-2193337`。
- 后续 `b44e8cb` 到 `de0a681` 是 Docker marker 提交，`6bfbc70` 是 ben-bot 版本选择功能，主要是运维层改动。
- 现在如果点击机器人发布 `latest`，会按当前 master 构建，例如 `pgserver:master-6bfbc70`。业务代码相对 `2193337` 后没有再被运维侧改动。

## 当前 Git 最近关键提交

```text
6bfbc70 ops: add deploy version picker to ben bot
de0a681 ops: add platform api deploy click marker
1a65377 ops: add panda deploy click marker
f20233c ops: add playson deploy click marker
3d7cc78 ops: add popok deploy click marker
08c3e87 ops: add pp deploy click marker
78ba1eb ops: add tada deploy click marker
b44e8cb ops: add pg deploy click marker
2193337 Fix deploy updater on Python 3.9
100c7bb 更新充提机制版本
84202c0 Disable browser smoke on baota ben bot
2af3e16 fix: normalize tada v2 request hosts
c8aa7f2 fix: route tada v2 auth through dynamic host
8742a5b fix: handle tada lj500 auth and pg resource gating
36a35d0 fix: filter unreleased playson smoke cards
2676298 fix: make playson entry filtering reproducible
```

这些提交大致说明：

- `6bfbc70`：机器人发布按钮增加 Git 短 ID 版本选择。
- `b44e8cb` 到 `de0a681`：只在 `docker/deploy/deploy-click-test-markers.md` 里追加 marker，用来让机器人点击各游戏部署时有多个不同提交可选，方便测试发布版本选择。
- `2193337`：给 `docker/deploy/update_pgserver.py` 增加 `from __future__ import annotations`，修复本地 Python 3.9 执行 `--help` 时 `tuple[...] | None` 类型注解报错。
- `84202c0`：线上宝塔 ben-bot 默认禁用浏览器测试，本地运行才启用浏览器测试。
- `8742a5b` 附近：处理过 TADA 幸运捷豹 500 身份验证、PG 资源 gating 等人工反馈。
- `36a35d0` / `2676298`：Playson 白名单外游戏过滤、巡检入口过滤稳定性。

## 目录地图

核心目录：

```text
docker/
  README.md                         Docker 运维总入口说明
  Dockerfile                        PGServer 主业务镜像
  ci/check.py                       Docker 运维自检
  deploy/
    README.md                       发布链路详细说明
    deploy_all_servers.py           总控发布脚本，从本地或宝塔控制两台后台
    update_pgserver.py              后台单机发布脚本，拉代码、构建/加载镜像、替换容器
    deploy_service.py               各服务 deploy.py 的统一转发入口
    deploy-click-test-markers.md    用于机器人发布测试的无害 marker 提交记录
  services/
    pg/ tada/ pp/ popok/ playson/ panda/ platform-api/
      service.env                   每个服务的端口、容器名、命令、挂载、打开链接
      deploy.py                     单服务快捷发布入口
  scripts/
    start_service_group.py          容器内进程组启动器，TADA 一个容器跑 HTTP + WS2
    post_deploy_browser_smoke.py    浏览器巡检脚本，本地模式使用
    sync_game_results_data.py       宝塔结果数据同步到后端
    static_resource_integrity_audit.py
  ben-bot/
    README.md                       机器人说明
    build_and_run_ben_bot.sh        构建并重启机器人
    docker/docker-compose.yml       机器人 compose
    app/benbot/                     机器人主程序
    data/scripts/                   机器人按钮对应脚本
    data/scripts/.dbqp_common/      共享按钮运行时、发布逻辑、机器人 ops 入口
  线上服务器信息/
    README.md
    servers.json
    baota/                          宝塔反代、计划任务、域名同步资料
```

## 服务与端口

当前 `all` 发布顺序固定为：

```text
pg -> tada -> pp -> popok -> playson -> panda -> platform-api
```

API 放最后，避免入口配置先切过去而游戏容器还没就绪。

当前服务配置：

| 服务 | 容器前缀 | 容器端口 | 宿主机端口 | 启动命令 | 打开链接 |
| --- | --- | --- | --- | --- | --- |
| `pg` | `dbqp-pg-release` | `9091` | `9091` | `python -u pg/server.py` | `https://ind-h5.dbqpplus999.com/pgbronline/` |
| `tada` | `dbqp-tada-release` | `9096` + `8765` | `9096` + `8765` | HTTP + WS2 双进程 | `https://ind-h5.dbqpplus999.com/tadabronline/` |
| `pp` | `dbqp-pp-release` | `9099` | `9101` | `python -u pp/pp.py` | `https://ind-h5.dbqpplus999.com/ppbronline/` |
| `popok` | `dbqp-popok-release` | `9098` | `9103` | `python -u ppk/ppk.py` | `https://ind-h5.dbqpplus999.com/popokbronline/` |
| `playson` | `dbqp-playson-release` | `9020` | `9104` | `python -u playson/playson.py` | `https://ind-h5.dbqpplus999.com/playsonbronline/` |
| `panda` | `dbqp-panda-release` | `9018` | `9102` | `python -u panda/panda.py` | `https://ind-h5.dbqpplus999.com/pandabronline/` |
| `platform-api` | `dbqp-platform-api-release` | `9090` | `9090` | `python -u platform-api/main.py` | 无用户打开链接 |

结果数据挂载：

```text
/opt/game_results_datas/pg      -> /app/game_result_datas/pg
/opt/game_results_datas/tada    -> /app/game_result_datas/tada
/opt/game_results_datas/pp      -> /app/game_result_datas/pp
/opt/game_results_datas/ppk     -> /app/game_result_datas/ppk
/opt/game_results_datas/playson -> /app/game_result_datas/playson
/opt/game_results_datas/panda   -> /app/game_result_datas/panda
```

注意：

- `popok` 的业务代码目录/数据目录实际使用 `ppk`，但服务 key 是 `popok`，用户展示名是 `PPK`。
- `tada-ws2` 不再单独起容器；兼容命令会转成 `tada`，由 TADA 容器内 `PROCESS_COMMANDS` 同时启动 HTTP 和 WS2。
- `HEALTH_URL` 目前为空，发布层主要做 TCP 端口检查和挂载检查。很多业务接口会校验真实 IP，乱加 HTTP 健康检查可能误判。

## 发布链路

常用发布命令：

```bash
python3 docker/deploy/deploy_all_servers.py all
python3 docker/deploy/deploy_all_servers.py pg
python3 docker/deploy/deploy_all_servers.py tada
python3 docker/deploy/deploy_all_servers.py pp
python3 docker/deploy/deploy_all_servers.py popok
python3 docker/deploy/deploy_all_servers.py playson
python3 docker/deploy/deploy_all_servers.py panda
python3 docker/deploy/deploy_all_servers.py platform-api
```

指定版本发布：

```bash
python3 docker/deploy/deploy_all_servers.py pg 6bfbc70
python3 docker/deploy/deploy_all_servers.py all latest
```

当前推荐策略：

```bash
python3 docker/deploy/deploy_all_servers.py all latest --strategy single-build --image-transfer internal
```

含义：

- 先探测两台后台压力，选压力较小的作为 builder。
- builder 拉目标 Git 版本，构建一次 `pgserver:master-<git_id>`。
- builder 本机先替换目标服务容器。
- builder 将镜像包通过后台内网直传到另一台后台。
- 另一台后台 `docker load` 后替换对应服务容器。

可以临时回退：

```bash
# 两台各自构建
python3 docker/deploy/deploy_all_servers.py all latest --strategy parallel-build

# 镜像包本地中转
python3 docker/deploy/deploy_all_servers.py all latest --image-transfer local

# 指定 builder
python3 docker/deploy/deploy_all_servers.py all latest --builder-host 203.0.113.1
```

发布脚本会输出结构化 progress，ben-bot 会把它转成中文进度卡。

## 发布前磁盘清理

`docker/deploy/update_pgserver.py` 每次构建或加载镜像前会做轻量清理：

- 打印 `df -h /` 和 `docker system df`。
- 删除历史 `/tmp/pgserver-image-*.tar*`，但保留本次正在使用的镜像包。
- `docker container prune -f`
- `docker image prune -f`
- 根分区超过阈值才做深度清理：`docker image prune -af`、`docker builder prune -af`

默认深度清理阈值：`85%`。

临时跳过清理：

```bash
PGSERVER_DEPLOY_PRE_CLEANUP=0 python3 docker/deploy/deploy_all_servers.py pg
```

临时强制干净构建：

```bash
PGSERVER_DOCKER_NO_CACHE=1 PGSERVER_DOCKER_PULL=1 python3 docker/deploy/deploy_all_servers.py pg
```

不要使用 `docker system prune --volumes`，避免误删业务数据卷。

## ben-bot 机器人

机器人只部署在宝塔：

```bash
ssh -i docker/线上服务器信息/35.247.205.6_id_ed25519 root@35.247.205.6
cd /opt/pgserver/docker/ben-bot
BEN_BOT_UPDATE_NOTICE=0 ./build_and_run_ben_bot.sh
docker logs -f dbqp-ben-bot
```

宝塔宿主机仓库路径是 `/opt/pgserver`，容器内是 `/workspace/pgserver`。

机器人 compose 关键挂载：

```text
/opt/pgserver/docker/ben-bot/data/upload -> /app/data/upload
/opt/pgserver/docker/ben-bot/data/scripts -> /app/data/scripts
/opt/pgserver -> /workspace/pgserver
/www/wwwroot -> /www/wwwroot
/www/server -> /www/server
/www/wwwlogs -> /www/wwwlogs
/root/.config/gcloud -> /root/.config/gcloud
```

线上默认：

- `BEN_BOT_ENABLE_BROWSER_SMOKE=0`
- 浏览器测试入口隐藏。
- “发布并测试”按钮隐藏。
- 发布按钮仍可用。

本地运行：

- 非 Linux 或显式本地模式默认启用浏览器测试。
- 本地不要直接运行 Telegram 轮询容器，避免和线上 bot 抢 token。
- 本地可用 `docker/ben-bot/docker/local_check.sh` 做离线菜单渲染检查，但需要本地先有 `dbqp-ben-bot:latest` 镜像。

## ben-bot 发布版本选择

最新机器人已经支持发布前选择 Git 短 ID。

涉及文件：

```text
docker/ben-bot/data/scripts/.dbqp_common/action_runtime.py
docker/ben-bot/data/scripts/.dbqp_common/single_deploy_action.py
docker/ben-bot/data/scripts/游戏发布-全部/action.py
docker/ben-bot/data/scripts/游戏发布-*/action.py
docker/ben-bot/app/benbot/home.py
```

交互流程：

1. 点击“发布全部游戏”或单游戏“发布 PG/TADA/.../API”。
2. 先进入“选择发布版本”页面。
3. 页面展示：
   - `latest（最新 <短ID>）`
   - 最近 5 次 `Git 短ID + 提交备注`
   - `刷新版本列表`
4. 选择版本后进入确认页。
5. 确认后执行：
   - 全量：`游戏发布-全部/run.py deploy all <version>`
   - 单游戏：`游戏发布-PG/run.py deploy pg <version>`
   - API：`游戏发布-API/run.py deploy platform-api <version>`

版本列表来源：

```bash
git -C <repo> fetch --quiet origin master
git -C <repo> log -5 --pretty=format:%h%x09%s origin/master
```

`%h` 就是 Git 短 ID，例如 `6bfbc70`。

Telegram callback 有 64 字节限制，因此新版本选择流程使用短动作码：

```text
d  -> deploy
ds -> deploy-smoke
ver -> 打开版本列表
vc  -> 选择版本后进入确认页
rc  -> 确认执行
```

如果改按钮，一定要重新检查 callback 长度。

示例检查：

```bash
python3 - <<'PY'
node = 'script_' + 'a' * 12
cases = []
for code in ['d', 'ds']:
    for target in ['all', 'pg', 'tada', 'pp', 'popok', 'playson', 'panda', 'platform-api']:
        for version in ['latest', '6bfbc70']:
            cases.append(':'.join(['plugin', node, 'ver', code, target]))
            cases.append(':'.join(['plugin', node, 'vc', code, target, version]))
            cases.append(':'.join(['plugin', node, 'rc', code, target, version]))
print(max(len(item.encode()) for item in cases))
assert all(len(item.encode()) <= 64 for item in cases)
PY
```

## ben-bot 权限与安全

授权用户维护在：

```text
docker/ben-bot/app/benbot/constants.py
```

敏感配置在宝塔本机 `.env`，不要提交：

```text
docker/ben-bot/.env
```

常见变量：

```text
TELEGRAM_API_TOKEN
TG_BOT_TOKEN
TG_CHAT_ID
STARTUP_NOTIFY_CHAT_IDS
PGSERVER_DEPLOY_PASS
DBQP_BAOTA_*
```

不要把 `.env` 内容、服务器密码、Telegram token、Cloudflare/GCS token 打印到回复里。

## 浏览器测试规则

线上宝塔禁用浏览器测试：

- 禁用原因：宝塔线上资源有限，跑 Chromium 容易拖慢机器。
- 线上菜单隐藏浏览器测试入口和“发布并测试”。
- 本地运行 ben-bot 时保留浏览器测试能力。

相关提交：`84202c0 Disable browser smoke on baota ben bot`

如果用户要求“线上宝塔服务器部署，就砍掉浏览器测试；本地跑就带上”，当前已经实现：

- `docker/ben-bot/build_and_run_ben_bot.sh`
- `docker/ben-bot/docker/docker-compose.yml`
- `docker/ben-bot/app/benbot/runtime_features.py`
- 各按钮 action 会根据 `browser_smoke_enabled()` 隐藏或拒绝浏览器测试动作。

## 最近人工反馈重点

测试曾要求重点复测：

- TADA：摇钱树、幸运捷豹500
- PG：71 目录缺失 json 的游戏资源
- Playson：白名单外游戏是否已从列表访问策略验证/标记

反馈结果：

- TADA 摇钱树 pass。
- TADA 幸运捷豹500 曾仍报“身份验证失败”，相关修复在 `8742a5b` 附近，后续仍需要人工点游戏确认。
- PG 部分游戏曾提示 IP 限制，需要测试从真实入口打开，不能只凭 curl 判断业务失败。
- Playson 白名单问题 pass；未开放游戏应该访问策略验证/不参与列表或巡检。

发布后扫日志时，重点关键词：

```text
Traceback
Exception
ERROR
CRITICAL
failed
失败
身份验证失败
认证失败
ip限制
IP限制
unauthorized
forbidden
not found
missing
ModuleNotFoundError
ImportError
No such file
json
幸运捷豹
摇钱树
```

## 常用线上操作

### 1. 查看宝塔机器人状态

```bash
ssh -o StrictHostKeyChecking=no -i docker/线上服务器信息/35.247.205.6_id_ed25519 root@35.247.205.6 \
  'cd /opt/pgserver && git rev-parse --short HEAD && docker ps --format "{{.Names}} | {{.Status}} | {{.Image}}" | grep dbqp-ben-bot'
```

### 2. 宝塔拉最新并重启机器人

```bash
ssh -o StrictHostKeyChecking=no -i docker/线上服务器信息/35.247.205.6_id_ed25519 root@35.247.205.6 '
set -eu
cd /opt/pgserver
git fetch origin master
git checkout master
git pull origin master
python3 docker/ci/check.py
cd docker/ben-bot
BEN_BOT_UPDATE_NOTICE=0 ./build_and_run_ben_bot.sh
docker ps --format "{{.Names}} | {{.Status}} | {{.Image}}" | grep dbqp-ben-bot
'
```

### 3. 通过宝塔容器发起发布

如果本地没有后台服务器密码，可以进宝塔 `dbqp-ben-bot` 容器执行，因为容器环境里有 `PGSERVER_DEPLOY_PASS`：

```bash
ssh -o StrictHostKeyChecking=no -i docker/线上服务器信息/35.247.205.6_id_ed25519 root@35.247.205.6 'docker exec -i dbqp-ben-bot sh' <<'REMOTE'
set -eu
cd /workspace/pgserver
python3 -u docker/deploy/deploy_all_servers.py pg latest --strategy single-build --image-transfer internal
REMOTE
```

长任务建议用 nohup 记录日志，避免 SSH 断开：

```bash
ssh -o StrictHostKeyChecking=no -i docker/线上服务器信息/35.247.205.6_id_ed25519 root@35.247.205.6 'docker exec -i dbqp-ben-bot sh' <<'REMOTE'
set -eu
cd /workspace/pgserver
log=/tmp/dbqp-all-latest-$(date +%Y%m%d-%H%M%S).log
nohup python3 -u docker/deploy/deploy_all_servers.py all latest --strategy single-build --image-transfer internal >"$log" 2>&1 &
echo "pid=$!"
echo "log=$log"
REMOTE
```

### 4. 监控发布日志

```bash
ssh -o StrictHostKeyChecking=no -i docker/线上服务器信息/35.247.205.6_id_ed25519 root@35.247.205.6 'docker exec -i dbqp-ben-bot sh' <<'REMOTE'
set -eu
log=$(ls -t /tmp/dbqp-all-latest-*.log /tmp/dbqp-*-latest-*.log 2>/dev/null | head -1)
echo "log=$log"
ps -eo pid,etime,cmd | grep -E "deploy_all_servers.py|update_pgserver.py" | grep -v grep || true
tail -120 "$log"
REMOTE
```

### 5. 核对两台后台容器

```bash
ssh -o StrictHostKeyChecking=no -i docker/线上服务器信息/35.247.205.6_id_ed25519 root@35.247.205.6 'docker exec -i dbqp-ben-bot sh' <<'REMOTE'
set -eu
if [ -z "${PGSERVER_DEPLOY_PASS:-}" ]; then echo "deploy password env missing"; exit 3; fi
for h in 203.0.113.1:01 203.0.113.1:02; do
  host="${h%:*}"
  suffix="${h#*:}"
  echo "===== ${host} (${suffix}) ====="
  SSHPASS="$PGSERVER_DEPLOY_PASS" sshpass -e ssh \
    -o StrictHostKeyChecking=no \
    -o PreferredAuthentications=password \
    -o PubkeyAuthentication=no \
    -o ConnectTimeout=8 \
    root@"$host" '
      docker ps --format "{{.Names}} | {{.Status}} | {{.Image}}" |
        grep -E "dbqp-(pg|tada|pp|popok|playson|panda|platform-api)-release" | sort
    '
done
REMOTE
```

### 6. 扫两台后台最近错误日志

```bash
ssh -o StrictHostKeyChecking=no -i docker/线上服务器信息/35.247.205.6_id_ed25519 root@35.247.205.6 'docker exec -i dbqp-ben-bot sh' <<'REMOTE'
set -eu
if [ -z "${PGSERVER_DEPLOY_PASS:-}" ]; then echo "deploy password env missing"; exit 3; fi
for h in 203.0.113.1:01 203.0.113.1:02; do
  host="${h%:*}"
  suffix="${h#*:}"
  echo "===== ${host} (${suffix}) recent error scan ====="
  SSHPASS="$PGSERVER_DEPLOY_PASS" sshpass -e ssh \
    -o StrictHostKeyChecking=no \
    -o PreferredAuthentications=password \
    -o PubkeyAuthentication=no \
    -o ConnectTimeout=8 \
    root@"$host" '
      for c in $(docker ps --format "{{.Names}}" | grep -E "^dbqp-(pg|tada|pp|popok|playson|panda|platform-api)-release"); do
        hits=$(docker logs --since=30m --tail=1500 "$c" 2>&1 |
          grep -Eai "Traceback|Exception|CRITICAL|ERROR|failed|失败|身份验证失败|认证失败|ip[ _-]*限制|IP限制|unauthorized|forbidden|not found|missing|ModuleNotFoundError|ImportError|permission denied|No such file|json" |
          tail -30 || true)
        if [ -n "$hits" ]; then
          echo "--- $c ---"
          printf "%s\n" "$hits"
        fi
      done
    '
done
REMOTE
```

### 7. 公开入口轻量检查

```bash
for item in \
  'PG https://ind-h5.dbqpplus999.com/pgbronline/' \
  'TADA https://ind-h5.dbqpplus999.com/tadabronline/' \
  'PP https://ind-h5.dbqpplus999.com/ppbronline/' \
  'PPK https://ind-h5.dbqpplus999.com/popokbronline/' \
  'PLAYSON https://ind-h5.dbqpplus999.com/playsonbronline/' \
  'PANDA https://ind-h5.dbqpplus999.com/pandabronline/'
do
  name=${item%% *}
  url=${item#* }
  printf '%s ' "$name"
  curl -k -sS -L -o /dev/null --connect-timeout 8 --max-time 20 \
    -A 'Mozilla/5.0 deploy-check' \
    -w 'http=%{http_code} time=%{time_total} final=%{url_effective}\n' "$url" || true
done
```

如果本地出口网络偶发超时，可从宝塔机再测一遍，宝塔到线上入口更接近真实生产链路。

## 本地验证命令

运维代码自检：

```bash
python3 docker/ci/check.py
```

Python 编译指定范围：

```bash
PYTHONPATH=docker/ben-bot/app python3 -m compileall -q docker/ben-bot/app docker/ben-bot/data/scripts docker/deploy docker/scripts
```

机器人菜单与版本选择逻辑快速验证：

```bash
PYTHONPATH=docker/ben-bot/app PGSERVER_ROOT=$PWD python3 - <<'PY'
import sys
from pathlib import Path
from types import SimpleNamespace

root = Path("docker/ben-bot/data/scripts")
sys.path.insert(0, str((root / ".dbqp_common").resolve()))
import action_runtime as rt

node = SimpleNamespace(id="script_aaaaaaaaaaaa")
versions = rt.recent_git_versions(5)
print(versions)
markup = rt.version_select_markup(node, action="deploy", target="pg", versions=versions)
for row in markup.inline_keyboard:
    print(" | ".join(f"{b.text}->{b.callback_data}({len(b.callback_data.encode())})" for b in row))
PY
```

## 常见问题与处理思路

### 1. 本地 Python 3.9 跑 deploy 脚本报类型注解错误

现已通过 `2193337` 修复，在 `docker/deploy/update_pgserver.py` 顶部增加了：

```python
from __future__ import annotations
```

如果以后新增脚本使用 `X | None`、`tuple[...]` 等新注解，考虑也加 future annotations，兼容本地 macOS Python 3.9。

### 2. 点击机器人发布没有弹版本选择

检查：

- 宝塔仓库是否已经拉到 `6bfbc70` 或之后。
- `dbqp-ben-bot` 是否重建重启。
- 容器内 `/app/data/scripts/.dbqp_common/action_runtime.py` 是否包含 `version_button`、`recent_git_versions`。
- callback 是否超 64 字节。

验证：

```bash
docker exec dbqp-ben-bot sh -lc 'cd /workspace/pgserver && git rev-parse --short HEAD'
docker logs --since=5m --tail=200 dbqp-ben-bot
```

### 3. 点击“发布并测试”在线上不见了

这是预期行为。线上宝塔默认禁用浏览器测试，只有本地模式展示。

### 4. 发布卡住在 docker save / docker load

这是镜像包导出/加载阶段，可能几十秒到数分钟没有新业务日志。看 heartbeat、CPU、磁盘和 `/tmp/pgserver-image-*.tar`。

### 5. TADA WS curl 超时

WS 是长连接，看到端口映射和 TCP 连通即可。HTTP 直接 curl WS 端口超时不一定是失败。

### 6. 游戏接口提示 IP 限制

不要把单纯 curl 或非真实入口打开的 IP 限制直接判定为发布失败。让测试从 H5 入口点游戏，或用浏览器巡检/真实前端路径复测。

### 7. Playson 白名单外游戏

Playson 未开放游戏应该从列表访问策略验证或被标记，不应参与发布后巡检随机池。相关逻辑在旧提交 `36a35d0`、`2676298` 附近。

## 发布完成后建议发群话术

全量发布成功后可发：

```text
【DBQP all latest 发布完成】
线上已部署 <git_id>。

01/02 两台发布成功：
PG / TADA / PP / PPK / PLAYSON / PANDA / api 全部 Up。

启动日志暂未发现：
Traceback、ERROR、身份验证失败、ip限制、缺资源、导入失败。

请测试重点复测：
1. TADA：摇钱树、幸运捷豹500
2. PG：71 目录资源、之前提示 ip 限制的游戏
3. Playson：白名单外游戏是否访问策略验证/标记
```

单游戏发布成功后可发：

```text
【DBQP <GAME> 发布完成】
版本：<git_id>
01/02 两台容器已更新并 Up。
最近日志未发现关键错误。
请测试对应游戏入口与重点问题。
```

## 修改建议

当用户要求“只改 Docker 运维代码”时，优先选择这些位置：

- 发布命令/兼容：`docker/deploy/*.py`
- 镜像环境：`docker/Dockerfile`
- 服务端口/挂载：`docker/services/<service>/service.env`
- 机器人菜单：`docker/ben-bot/data/scripts/<功能>/action.py`
- 机器人通用按钮逻辑：`docker/ben-bot/data/scripts/.dbqp_common/action_runtime.py`
- 机器人发布共用逻辑：`docker/ben-bot/data/scripts/.dbqp_common/single_deploy_action.py`
- 机器人执行器/菜单/权限：`docker/ben-bot/app/benbot/*.py`
- 文档：`docker/doc/`、`docker/README.md`、`docker/deploy/README.md`、`docker/ben-bot/README.md`

改完至少运行：

```bash
python3 docker/ci/check.py
git diff --check -- docker
```

如果涉及机器人按钮，再额外验证：

- 菜单是否能 import。
- callback data 是否 <= 64 字节。
- 宝塔重启后 `docker logs dbqp-ben-bot` 无异常。

## 当前接手原则

1. 先确认用户要“改代码”、“部署线上”、“盯日志”还是“只分析”。
2. 涉及线上状态一定要实际查，不要凭记忆。
3. 涉及最新代码先 `git fetch` / `git status` / `git log`。
4. 发布前看工作区是否有用户未提交改动。
5. 只改 `docker/`，除非用户明确让改业务代码。
6. 发布和机器人重启后要复查：
   - Git 短 ID
   - 容器 Up
   - 镜像 tag
   - 最近错误日志
   - H5 入口 HTTP 状态
7. 最终回复用中文，简洁说明改了什么、验证了什么、是否已部署。
