---
id: "doc-8ebbc1b3b304"
title: "Agent 工作日志：敏感词词库 + admin 创建主播返 initpassword D3"
date: "2026-05-31T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "监控告警", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-streamer-forbidden-d3.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-streamer-forbidden-d3.md"
sourceSha256: "b8aea1feedbe5dd08221920fd82d29b4836c02dd35a05bb0333c5a5496ceec32"
sourceSystem: "project-doc"
---

# Agent 工作日志：敏感词词库 + admin 创建主播返 initpassword D3

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-streamer-forbidden-d3.md`

> 整理日期：2026-05-31 00:00｜日期依据：文件名日期

日期:2026-05-31
Agent:siggod / go-app
任务:实现弹幕敏感词缓存 + 检测;admin 新增主播自动生成 8 位临时密码并返回

## 输入资料

- PRD:`docs/prd/modules/kickoff-admin.md` §直播运营违规告警、ADM-303 主播签约
- 需求 ID:LIVE-101 D3
- 接口/契约:`packages/contracts/openapi/v1.yaml` `/api/v1/admin/streamers` POST 调整
- 上游 commit:`cd20297 feat(streamer): 开播/下播/改房间 + Zego webhook 兜底 [LIVE-101 D2]`

## 本次目标

1. 敏感词词库内存缓存(原子指针),启动加载 + 5min 异步 reload,DB 失败保留旧值
2. 弹幕检测:BLOCK 拒发,MASK 替换 + 落库标记,ALERT 允许 + 落库标记
3. admin 创建主播:自动 username + 8 位 init_password(明文返回仅 1 次),bcrypt 落库,[敏感内容已脱敏]
4. live SendDanmaku 接入 forbidden checker,违规字段写入 live_chat_messages_*

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `packages/contracts/openapi/v1.yaml` | adminStreamerCreate 加 username 入参,返 init_password/username/streamer_no |
| `docs/api/openapi.yaml` | 重生 |
| `internal/model/forbidden_word.go` | NEW:ForbiddenWord 模型 + 严重度/动作常量 |
| `internal/repository/forbiddenword/repo.go` | NEW:ListEnabled() 一次性全量,用于启动 + 定时同步 |
| `internal/service/moderation/forbidden.go` | NEW:ForbiddenChecker 原子指针缓存 + Reload/StartAutoReload + Check;action 严重度走 priority 映射(BLOCK > ALERT > MASK > NONE) |
| `internal/service/moderation/forbidden_test.go` | NEW:8 个 case 覆盖 hit/mask/alert/block/严重度选最重/dict 为空/reload 失败保留旧值/重复词去重 |
| `internal/model/live.go` | LiveChatMessage 加 ViolationFlag/Severity/Action/Words/Handled 字段(B 段 migration 已加列) |
| `internal/service/live/service.go` | 加 DanmakuChecker 接口(避免 live 反向依赖 moderation) + SetForbiddenChecker;SendDanmaku 接检测 + 三动作分流 |
| `internal/service/live/forbidden_danmaku_test.go` | NEW:capturingChatRepo 捕获 inserted msg,4 个 case 覆盖 BLOCK/MASK/ALERT/无 checker |
| `internal/http/router/forbidden_adapter.go` | NEW:把 moderation.CheckResult 转 livesvc.ModerationResult,单向依赖 |
| `internal/http/router/public.go` | 装配 forbiddenChecker:启动加载 + 5min auto reload + 注入 liveService |
| `internal/dto/admin_modules.go` | 加 AdminStreamerCreateResponse(id/streamer_no/username/init_password) + 入参 username 可选 |
| `internal/service/admin/streamer.go` | Create 返 *AdminStreamerCreateResponse;生成 8 位 init_password(crypto/rand,排除易混 0/O/1/l/I)+ bcrypt + [敏感内容已脱敏] |
| `internal/service/admin/streamer_init_password_test.go` | NEW:3 case 覆盖长度/排除字符/随机性 |
| `internal/http/adminapi/streamer.go` | Create handler 返 res 透传(原 gin.H{id} → svc 自然返 envelope) |

## 核心决策

1. **缓存用 atomic.Pointer 而非 sync.RWMutex**:Check 是热路径(每条弹幕都调),原子指针读 0 锁,reload 整体替换;实测词量 < 1000 时 contains 扫一遍 < 100us
2. **action priority 映射函数化**:DB 数值(1=NONE 2=MASK 3=BLOCK 4=ALERT)与业务严重度顺序不一致,单独函数明确 BLOCK > ALERT > MASK > NONE 避免误读
3. **live → moderation 单向依赖**:live 包定义 `DanmakuChecker interface { Check(string) ModerationResult }`,router 装配时 adapter 转 shape;避免 live 反向 import 内容审核包
4. **init_password 排除易混字符**:字符集 53 个(去 0/O/o/1/l/L/I/i),8 位空间 ~6e13,运营截图/口传场景错认率显著下降
5. **[敏感内容已脱敏] 在 service.Create 写入**:与 D1 streamer.ChangePassword 联动,主播首登强制改密;无需 D1 端动手
6. **forbidden DB 失败不阻塞启动**:Reload 失败时 logger.Warn + checker 退化为空 dict(穿透模式),所有弹幕放行但有日志可追;比因为 forbidden_words 表暂时不可用导致 API server 启不起来更安全

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器,还是项目资产 | 项目资产 + atomic-pointer 内存缓存模式可外推 |
| 哪些内容可复用到下一个项目 | atomic.Pointer 词库缓存模式、init_password 字符集设计、live↔moderation 单向依赖 adapter |
| 哪些内容只属于当前项目 | live_chat_messages 月分表的 violation 列定义 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 缓存模式可,init_password 模式可,可以下沉成 pkg/passwordgen |
| 是否涉及 Scale Profile:mvp / growth / scale / enterprise | mvp(词量 < 1000);growth 阶段词量上来需换 AC 自动机 |
| 是否影响项目 Overlay | 否 |
| 是否增加了自动校验或 CI 门禁 | 单测 +15 个 case(moderation 8 + live 4 + admin 3) |
| 是否降低了 Agent 偷懒空间 | 否 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 D3 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | kickoff-admin.md §违规告警 + ADM-303 主播签约 |
| OpenAPI / Event / DTO | v1.yaml adminStreamerCreate 已重生 |
| 验收证据行 | 待 D smoke 阶段补 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | B 段已加 forbidden_words 表 + live_chat_messages.violation_* 列 |
| 是否使用表设计模板 | 是 |
| 是否影响账本、事务、幂等或审计 | 影响审计:audit.Log admin.streamer.create 加 username 字段 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否 |
| 涉及能力 | 缓存(atomic.Pointer 词库)+ 权限安全(主播首登强制改密)+ 内容审核 |
| 高风险触发项 | 主播账号安全(init_password 明文回包仅 1 次,运营泄漏即账号失守) |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响 cmd/api binary,启动多 1 个 reload goroutine,需重启 |
| 回滚 | git revert + 不存在依赖的 schema 变化 |
| 密钥 | 不影响 |
| 备份恢复 | 不影响 |
| 观测 | 启动 log "forbidden_words reloaded count=N",reload 失败 Warn |
| Runbook | 后台批量改完词需触发 reload(本期靠 5min 周期,运营改完 < 5min 生效) |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 检测在原文上做 contains,MASK 后立刻替换避免次轮误命中;priority 函数显式排序避免数值陷阱;crypto/rand 取代 math/rand 防 init_password 可预测 |
| 红队质疑 | (1) contains 算法无法识别拆字(草字头 → ⺾),v1.x 用 AC + 同形字归一;(2) init_password 仅一次返回,运营截图后聊天软件历史是授权安全测试面,Runbook 须强调即时清理;(3) reload goroutine 未做 ctx 取消测试,需 graceful shutdown 时校验 |
| 合入判断 | 合入(以上风险 v1.x 内迭代) |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go build ./...` | 通过 |
| `go vet ./...` | 通过 |
| `go test -race -count=1 ./internal/service/moderation/... ./internal/service/live/... ./internal/service/streamer/... ./internal/service/admin/...` | 全过 |
| `make openapi` | docs/api/openapi.yaml 重生 + swagger-cli 通过 |

## 风险与待办

1. forbidden_words 后台 CRUD 接口未做,运营暂时只能直接改 DB + 等 5min reload(本期不影响主播主流程)
2. 弹幕 MASK 后落库的是 mask 后文本,原文找不回;后台违规审计若要看原文,需后续加 raw_content 字段
3. live SendDanmaku 接口本期没改 OpenAPI(检测对前端透明:BLOCK 走 ErrParam,前端原有错误处理即可)

## 交接说明

下一位 Agent / 工程师需要知道:

1. 运营在后台改词,本期没接 Reload 触发接口,改完等 5min 自动 reload;手动可在 admin debug 接口里加 POST /admin/moderation/forbidden-words/reload 调 forbiddenChecker.Reload(ctx)
2. admin 创建主播返 init_password 明文,**前端必须只显示一次 + 提示运营截图发给主播**,不要存到任何持久化(localStorage / Cookie / 表单回填)
3. D smoke 待跑:重启 api → adminStreamerCreate 拿 username/init_password → streamer login → start live → 发弹幕(命中/不命中)→ stop live
