---
id: "doc-abba9e9e94fc"
title: "Agent 工作日志 · live-102-cf2-admin-crowdfund-stages"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf2-admin-crowdfund-stages.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf2-admin-crowdfund-stages.md"
sourceSha256: "57663776441f50a77d4ee6e44ec74b2f4b662d3db8a994a36d7b67a7236b2a7f"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-102-cf2-admin-crowdfund-stages

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606010000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20live-102-cf2-admin-crowdfund-stages.md)

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：siggod
任务：LIVE-102 CF-2 — admin 后台众筹解锁阶段配置 CRUD(service + handler + route + OpenAPI paths + admin Vue 页面)

## 输入资料

- PRD：见原型截图(用户众筹弹窗 + 主播工作台进度条)
- 需求 ID：LIVE-102(CF-2/7)
- 前置基础:CF-1 已落 DB / model / repo / DTO / schemas
- AI/工具控制文件：`CLAUDE.md` §5.6 严格模式
- 项目 Overlay：v0.3.6 直播能力扩展
- 用户拍板:阶段全局共用一份(Q2=A);本 commit 仅做 admin 后台,不绑直播

## 本次目标

1. admin 后台开放阶段 CRUD 4 接口(GET 列表 / POST 新增 / PATCH 编辑 / DELETE 软删),走 economy 模块同款简洁路径(仅 requireAdmin,无自定义 permission 点)
2. OpenAPI v1.yaml 增 4 paths,docs 站 admin 模块出现 `/api/v1/admin/crowdfund/stages` 入口,ts-sdk 同步
3. admin Vue 阶段管理页(列表 + 新增/编辑 modal + 软删二次确认)挂到 `/live/crowdfund/stages` 路由下,菜单文案"众筹解锁配置"

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/crowdfund.go` | CrowdfundService:List/Create/Update/Delete + 阶段号冲突检查 + audit.Log |
| `services/go-app/internal/http/adminapi/crowdfund.go` | CrowdfundHandler:4 个 gin handler |
| `services/go-app/internal/http/router/admin.go` | DI + 4 路由注册到 `/api/v1/admin/crowdfund/stages[/:id]` |
| `packages/contracts/openapi/v1.yaml` | 4 paths:`adminCrowdfundStageList/Create/Update/Delete`,tag `后台-直播-众筹` |
| `docs/api/openapi.yaml` | `make openapi` 重生产物 |
| `apps/admin/src/api/modules/crowdfund.ts` | crowdfundApi(listStages / createStage / updateStage / deleteStage) + 完整 TS 接口 |
| `apps/admin/src/api/index.ts` | export crowdfund 模块 |
| `apps/admin/src/views/live/crowdfund-stages.vue` | VxeGrid 列表 + VbenForm 新增/编辑 + ElMessageBox 删除二次确认 |
| `apps/admin/src/router/routes/modules/live.ts` | 路由 `/crowdfund/stages` 挂到 Live 菜单组 |
| `apps/admin/src/locales/langs/zh-CN/page.json` | 菜单文案"众筹解锁配置" |
| `apps/admin/src/locales/langs/en-US/page.json` | menu "Crowdfund Stages" |
| `apps/admin/src/locales/langs/zh-CN/crowdfund.json` | 模块内文案(form/col/common) |
| `apps/admin/src/locales/langs/en-US/crowdfund.json` | en 镜像 |

## 核心决策

1. **跟齐 economy 模块的简洁路径** — 仅 `requireAdmin` 中间件,不引入 `crowdfund:read/write` 权限点(现有 economy/gift 也没自定义点,统一权限模型由 admin 角色管)。CF-2 不打破现状,CF-3+ 也不需要补
2. **阶段号唯一校验在 service 层做** — 不走 DB unique key,留出未来「同阶段号多版本」灵活性(目前 admin UI 直接拒新增重号);软删后阶段号可被新阶段复用
3. **阶段管理菜单挂在 Live 组内**(不挂在 System 组),原因:阶段语义跟直播强相关,运营心智里属于直播管理;`page.live.crowdfund = "众筹解锁配置"`
4. **不引入拖排序 UI** — 用 `sort_order` 字段 + 数字输入即可,后续真要拖再加,KISS

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go build ./...` (services/go-app) | ✓ 编译过 |
| `make openapi` | ✓ docs/api/openapi.yaml 重生 9061 行 + swagger-cli validate 通过 |
| `make sdk` | ✓ ts-sdk schema.ts 重生含 `paths./api/v1/admin/crowdfund/stages` |
| `pnpm typecheck` (apps/admin) | ✓ vue-tsc --noEmit --skipLibCheck 通过 |
| `pnpm vite --mode development` 启动 + 探活 | ✓ ready in 1878ms,5174 LISTEN;`/` 与 `/src/views/live/crowdfund-stages.vue` 都 HTTP 200 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 仅原型有用户端弹窗(无 admin 配置面板设计),按 economy 模块的 list+modal 套路落地 |
| 真实手机视口 | N/A(后台 admin 仅桌面,vben 默认布局) |
| 桌面/平板视口 | 复用 vben Page + Grid 自适应,无新写 CSS |
| 公共组件拆分 | 复用 useVbenForm / useVbenVxeGrid / useVbenModal,无自造组件 |
| API 接口路径 | `/api/v1/admin/crowdfund/stages[/:id]` 4 个 |
| 后台权限与审计 | 中间件 `requireAdmin`;每次 Create/Update/Delete 落 audit.Log(actor=admin_id, action=admin.crowdfund_stage.*) |
| 根节点是否挂载 | dev 探活 `/src/views/live/crowdfund-stages.vue` 200 |
| console 是否无 error | vue-tsc 0 错 |
| 合入判断 | 入库;UI 视觉验收待用户开 dev 手动看一下表单字段名/中文文案是否合心意,有反馈再调 |

## 风险与待办

1. CF-3 起后端 service 层需要在 `StartLive` 时按 threshold 升序 snapshot 启用的阶段到 session 上下文(本场不变,运营改阶段不影响进行中直播)
2. CF-5 阶段达成事件 WS broadcast 需要拿 snapshot 后的 stage 列表去判,本 commit 没引入 session 快照机制,待 CF-3 给
3. admin UI 没做拖排序,如果运营反馈频繁调整阶段顺序再加(目前 sort_order 数字输入)
4. 没加 `apps/admin/src/router/routes/modules/live.ts` 的 `meta.authority`,任何登录的 admin 都能进。如果需要限制运营/客服角色,后续加 `authority: ['super_admin','content_ops']`

## 交接说明

下一位 Agent 或工程师需要知道:

1. **服务依赖**:`crowdfundSvc := adminsvc.NewCrowdfundService(c.DB)` 注入位置在 `router/admin.go:116`,handler 紧随其后行 144
2. **OpenAPI 文档**:CF-2 后 docs 站(admin-dev.54-151-131-132.sslip.io/docs)「后台-直播-众筹」分组下新增 4 接口;Schemas 里 `AdminCrowdfundStage` / `AdminCrowdfundStageInput` / `AdminCrowdfundStagePatch` 是 CF-2 强相关的契约
3. **admin Vue 命名**:列表页 `CrowdfundStages`(name),路由 `/crowdfund/stages`,菜单 i18n key `page.live.crowdfund`
4. **审计动作命名**:`admin.crowdfund_stage.create/update/delete`(下划线 stage),按 economy 模块同模式
5. **阶段号冲突的 UX**:前端不做提示,后端 service.findByStageNo 返回 ErrConflict 后由 ElMessage 错误 toast 兜底(同 economy)
