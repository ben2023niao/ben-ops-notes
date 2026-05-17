---
id: "doc-4376c4b2ea9b"
title: "Agent 配对(公开 Skill.md → 短配对码 → owner 登录态确认)设计"
date: "2026-05-18T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/specs/2026-05-18-agent-self-pairing-design.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/specs/2026-05-18-agent-self-pairing-design.md"
sourceSha256: "c45504b02b82fe2dc3d435fd9f66ebcf68ae7ac1215c651e69d25f72495939f4"
sourceSystem: "project-doc"
---

# Agent 配对(公开 Skill.md → 短配对码 → owner 登录态确认)设计

> 来源文件：`~/Projects/work/game/ghome/docs/superpowers/specs/2026-05-18-agent-self-pairing-design.md`

> 整理日期：2026-05-18 00:00｜日期依据：文件名日期

> 状态:待评审 · 日期:2026-05-18 · 范围:`apps/admin`
> 本文是 [Admin Agent 数据接入 API 设计](2026-05-18-admin-agent-data-api-design.md) 的**配套附录**,复用其 AgentClient/token/scope/dispatcher/agent-clients UI。
> **本版修订**:配对完成方式由"Agent 凭长码自助 POST 无人审批"改为 **"Agent 拿短码 → 其 owner 登录 Admin 输入短码、后台校验通过"**。手工凭空建 Agent 的入口此前已移除;现在 Agent 进入系统的唯一路径就是本流程。git 历史保留旧版设计。
> **可用性修订(2026-05-19)**:① 公开引导端点 `GET /agent/skill.md` → **`GET /agent/pair.md`**(旧名移除),消除与鉴权 `GET /api/agent/v1/skill.md` 的同名混淆;引导文档须含**醒目区分**(这是配对引导页、不是 API 文档,API 文档是带 Bearer 的 `/api/agent/v1/skill.md`)。② agent-clients 列表行新增「轮换」动作(复用 `rotateAction`+`ConfirmSubmitButton`),让"错过一次性 token"可一键重取。本轮为聚焦后续,另起实现计划;§8 切片表为上一版构建留存。

## 0. 背景与目标

外部 Agent(OpenClaw / Hermes 等)接入:给一个**固定公开 Skill.md 地址**,Agent 在线读取 → 后台即时铸一枚**8 位短配对码** → Agent 把短码交给它的 **owner** → owner 用自己的账号**登录 Admin**、在「输入配对码」页填入该码 → 后台校验(通道开 / 码存在 / 未用 / 未过期)→ 建 AgentClient 并**在 Admin 页面一次性显示 Bearer token** → owner 复制 token 配进 Agent。完成。之后沿用原数据 API 与个性化 Skill.md。

**确认的核心决策**

- **完成方式**:owner(登录态管理员)输入短码、后台校验通过才算配对完成。不再有公开免鉴权的自助兑换端点。
- **短码**:8 位,大写字母+数字+少量安全特殊符,去易混字符;**单次、30 分钟 TTL、原子焚码**;公开 `GET /agent/pair.md` 每次被读即铸一枚(非管理员预建)。
- **公开地址**:固定单一 URL `GET /agent/pair.md`,免鉴权,仅铸码+回引导文档。
- **Token 交付**:校验通过后 Admin 页面**一次性明文显示**(复用现有 `TokenRevealBanner` + `?敏感凭据：[已脱敏] 回显机制),owner 手动填回 Agent。库内仅存 token 哈希,不可再查。
- **scope 策略**:配对出的 AgentClient 固定 `content:published`;更高权限由管理员事后在现有「编辑」页勾选提权(已审计)。确认页**不**选 scope。
- **方案 A**:复用现有 token 一次性回显机制 + 现有编辑/提权/吊销/配对码日志/通道开关,新增面最小。
- **通道开关**:公开通道全局开关(单行 `AgentPairingConfig`),**出厂默认关闭**,管理员显式开启才生效。

## 1. 流程总览

```
管理员  Admin → Agent 接入 → 开启「公开自助配对通道」(出厂默认关)
   │
Agent   GET /agent/pair.md  (公开免鉴权)
        通道关 → 200 markdown:已关闭,联系管理员(不铸码)
        通道开 → 铸一枚 8 位短码(单次,30min)→ 返回引导文档:含短码 +
                 "把这串码交给你的 owner;owner 登录 Admin → Agent 接入 → 输入配对码"
   │
owner   用本人账号登录 Admin → /agent-clients/pair → 填短码(+ 可选 Agent 名)→ 提交
   │
后台    校验(通道开 / sha256 命中 / 未用 / 未过期)→ 原子焚码 →
        建 AgentClient(origin=self-paired, scopes=["content:published"],
        createdByAdminId=该管理员)→ 重定向 /agent-clients/{id}/edit?敏感凭据：[已脱敏]
   │
Admin   编辑页用现有 TokenRevealBanner 一次性显示 token(库内仅哈希)
owner   复制 token 配进自己的 Agent
   │
之后    Agent 持 token 调 GET /api/agent/v1/skill.md(个性化文档)/ /api/agent/v1/apps …
管理员  agent-clients 列表见该 Agent(来源=自助);需更高权限→编辑页提权(审计);
        可吊销;配对码日志只读审计;通道一键开关
```

## 2. 数据模型(无需迁移,复用现有 `AgentPairingCode`)

现有表 `AgentPairingCode { id, codePrefix, codeHash @unique, expiresAt, usedAt, usedByAgentClientId?, createdAt }` 字段沿用,语义调整:

- `codeHash` = `sha256(短码)` —— 唯一查找键(不变)。
- `codePrefix` —— **改存一个与密文无关的随机 8 位"工单号"**(纯内部/日志关联用,不可反推短码;短码本身永不入任何列)。
- `usedAt` / `usedByAgentClientId` —— 不变。
- `createdByAdminId`(在 `AgentClient` 上,已是可空):配对完成时填**确认配对的管理员 id**(此前自助路径为 null;现在恒有值——记录"谁完成了配对")。

`AgentPairingConfig`(单行,公开通道开关)与 `AgentClient.origin`(默认 `admin`,配对建的写 `self-paired`)均沿用,无改动。

> 不新增列、不改类型 → **无 Prisma 迁移**。

## 3. 短码格式

`apps/admin/lib/agent-api/pairing.ts` 的 `generatePairingCode()` 改写:

- **固定 8 位**。字符集(共 39 个,去易混):
  - 大写字母 `ABCDEFGHJKMNPQRSTUVWXYZ`(去 `O I L`)
  - 数字 `23456789`(去 `0 1`)
  - 安全特殊符 `#$%@*+=-`(不含引号/反斜杠/空格/`/`,避免手输错或 shell/复制踩坑)
- 拒绝采样、无 modulo 偏置(沿用现有 `token.ts` 生成器写法)。熵 ≈ `log2(39^8) ≈ 42 bit`。
- `hashToken`(通用 sha256,`token.ts` 既有)复用于短码哈希;原 `codePrefix(raw)` 前缀函数移除(短码不可暴露前缀),改由 db 层生成随机工单号写入 `codePrefix` 列。
- `PAIRING_CODE_TTL_MS` 由 10min **改为 30min**(owner 人工中转需时间)。

## 4. 端点 / 路由

### 4.1 公开 `GET /agent/pair.md`(免鉴权,保留)
- 路由文件 `apps/admin/app/agent/pair.md/route.ts` 保留;middleware 仍精确放行 `pathname === "/agent/pair.md"`。
- 通道关 → `200 text/markdown` 关闭提示,**不铸码**。
- 通道开 → 铸一枚短码(`mintPairingCode()`,写 `codeHash`+随机 `codePrefix`+`expiresAt=now+30min`)→ 返回引导 Markdown:frontmatter、短码(明文,仅本响应)、有效期 30min/单次、**新指引**:"把这串配对码交给你的 owner;owner 用自己账号登录 Admin → 顶部导航『Agent 接入』→『输入配对码』,填入它即可完成配对并取得本 Agent 的 token。"(**不再含** `POST /agent/pair`;配对后取个性化文档仍是 `GET /api/agent/v1/skill.md` 带 Bearer——不变)。
- **醒目区分(必须)**:`renderPairingSkillMd` 与 `renderPairingClosedMd` **两态**文档顶部均须有一段显著提示,大意为:"⚠️ 这是**配对引导页**,不是 API 文档;本页每次访问都换一枚新配对码。配对完成、owner 在 Admin 校验后你会拿到 Bearer token;**真正的个性化 API 文档**是另一个地址且须带 敏感凭据：[已脱敏] /api/agent/v1/skill.md`(`Authorization: Bearer <token>`)。" 目的:杜绝把本引导页误当作鉴权后 API 文档(本轮修订动因)。

### 4.2 公开 `POST /agent/pair` —— 删除
- 删 `apps/admin/app/agent/pair/route.ts`;`apps/admin/middleware.ts` 公开白名单去掉 `pathname === "/agent/pair"`(**保留** `/agent/pair.md`)。无任何公开免鉴权的兑换端点。

### 4.3 登录态确认(新增,`(admin)` 分组,会话守卫)
- 页面 `apps/admin/app/(admin)/agent-clients/pair/page.tsx`:表单 = 配对码(必填)+ Agent 名称(可选)+ 提交;带 `?error=<code>` 时在表单上方显示友好中文错误(`invalid_request`/`invalid_code`/`code_used`/`code_expired`/`pairing_disabled`)。复用现有 `EditForm`/`FormRow`/`.btn-*` 风格。
- server action `confirmPairingAction(form)`(加入现有 `apps/admin/app/(admin)/agent-clients/actions.ts`,共用其顶部单一 `"use server"` 与 `adminId()`):
  1. `me = await adminId()`(会话守卫,未登录 `redirect("/signin")`)。
  2. 读 `code`(trim;空→`redirect("/agent-clients/pair?error=invalid_request")`)、可选 `name`。
  3. `res = await confirmPairingCode(code, me, name?)`。
  4. `!res.ok` → `redirect("/agent-clients/pair?error=" + res.code)`。
  5. `logAuditAction(me, "agentClient.pair", "agentClient", res.client.id, { after: { name: res.client.name, scopes: res.client.scopes, via: "pairing-code" } })`。
  6. `revalidatePath("/agent-clients")` → `redirect("/agent-clients/" + res.client.id + "/edit?敏感凭据：[已脱敏] + encodeURIComponent(res.rawToken))`(复用现有编辑页 `TokenRevealBanner` 一次性回显;与旧手工建/轮换同一机制)。

### 4.4 `agent-pairing-db.ts`
- `redeemPairingCode` → 改写为 `confirmPairingCode(rawCode: string, adminId: string, name?: string): Promise<ConfirmResult>`,`ConfirmResult = { ok: true; [敏感内容已脱敏]; client: AgentClient } | { ok: false; code: "invalid_code" | "code_used" | "code_expired" | "pairing_disabled" }`:
  - 先 `if (!(await isPairingEnabled())) return { ok:false, code:"pairing_disabled" }`(确认时通道已被关也拒)。
  - `sha256` 查 `AgentPairingCode`:无→`invalid_code`;`usedAt`→`code_used`;`expiresAt<now`→`code_expired`。
  - `prisma.$transaction`:条件 `updateMany(where:{id,usedAt:null},data:{usedAt:now})`;`count===0`→`code_used`;`resolveUniqueName(tx,name)`;`generateToken()`;`tx.agentClient.create({ name, tokenPrefix, tokenHash, scopes:[...SELF_PAIR_DEFAULT_SCOPES], origin:"self-paired", createdByAdminId: adminId })`;回填 `usedByAgentClientId`;返回 `{ok:true,rawToken,client}`。post-burn 抛错回滚(沿用现有原子语义)。
- `mintPairingCode()` 产 8 位短码 + 随机工单号写 `codePrefix`。`isPairingEnabled`/`setPairingEnabled`/`listPairingCodes` 不变。
- `SELF_PAIR_DEFAULT_SCOPES`(`scopes.ts`)= `["content:published"]`(不变)。

## 5. Admin UI

- 列表页 `agent-clients/page.tsx` header:在 `<h1>Agent 接入</h1>` 旁加 `<Link href="/agent-clients/pair" className="btn-primary">输入配对码</Link>`(新合法入口——完成 Agent 已发起的配对,非凭空建)。通道开关面板、表格(来源列)、配对码日志链接不变。
- 新 `agent-clients/pair/page.tsx`:配对码 + 可选 Agent 名 表单;带 `?error=<code>` 时显示友好中文错误,覆盖 `invalid_request`(空码)/`invalid_code`/`code_used`/`code_expired`/`pairing_disabled`。
- 配对码日志 `agent-clients/pairing-codes/page.tsx`:**不再显示码/前缀**;列改为 创建时间 / 过期 / 状态(`待确认` / `已用` / `已过期`,按 usedAt 与 now 推导)/ 确认管理员 / 兑换出的 Client。纯审计。
- 编辑页 `agent-clients/[id]/edit` + `TokenRevealBanner` + `?敏感凭据：[已脱敏] 回显:**完全复用,不改**。
- 提权/吊销:复用现有编辑页(已审计)。
- **列表行「轮换」动作(本轮新增)**:`agent-clients/page.tsx` 表格每行在「编辑」旁加一个 `<form action={rotateAction.bind(null, c.id)}>` 内含 `ConfirmSubmitButton`(确认文案如「轮换会立即作废 <name> 当前 token,确定?」)。**复用现有** `rotateAction(id)`(已 `rotateAgentToken`+审计 `agentClient.rotate`+`redirect('/agent-clients/{id}/edit?敏感凭据：[已脱敏] `ConfirmSubmitButton` 组件。零新增 action/组件/数据模型。动因:错过一次性 token 时可在列表一眼找到、一键重取。

## 6. 安全姿态

- **校验端点是登录态**:`confirmPairingCode` 只被 `(admin)` 会话守卫后的 server action 调用 → 匿名互联网暴力猜码打不进来(须先有 Admin 账号并登录)。8 位短码(≈42 bit)+ 单次 + 30min TTL + 原子焚码足够;**不做账号级锁定/限频**(YAGNI;唯一可尝试者是已登录管理员,每次 confirm 写审计 `agentClient.pair`)。
- 三层结构性兜底:① 配对出的 client 固定 `content:published`(敏感面结构不可达,提权走编辑页);② 短码单次+30min TTL+原子焚码;③ 公开通道出厂默认关 + 一键停用(关时不铸码、返回关闭提示;`confirmPairingCode` 亦在通道关时拒)。
- 短码**永不入库**(仅 `sha256`)、**永不进日志**、配对码日志页**不显示**;只出现在那一次 `/agent/pair.md` 响应体与 owner 手里。token 经现有 `TokenRevealBanner` 一次性回显、不持久化、不进审计 diff(diff 仅 name/scopes/via)。
- 可追溯链:`AgentPairingCode`(usedAt/usedBy + 关联确认管理员)→ 新 `AgentClient`(origin=self-paired, createdByAdminId=确认管理员, createdAt)+ 审计 `agentClient.pair`。
- 公开授权安全测试面仅剩"读 `/agent/pair.md` 触发铸一行短码"(出厂关 + 通道开关为主控),与原 spec 已记录残余风险同级,无新增免鉴权面(反而移除了公开 POST)。
- 延续隐私姿态:不存原始 IP/UA。

## 7. 测试策略(vitest 为主)

- 单元:短码生成(长度 8、字符集、无 `O0I1L`、无偏置、唯一);`confirmPairingCode`(合法→建 client 且 `createdByAdminId=该管理员`、scopes 恰为 `["content:published"]`、返回 token;复用→`code_used`;过期→`code_expired`;未知→`invalid_code`;通道关→`pairing_disabled`;并发双确认→仅 1 个 client,原子)。
- 集成:`GET /agent/pair.md` 通道开→写一行短码、markdown 含新指引且**不含** `POST /agent/pair`;**且含醒目区分语**(同时出现 `/api/agent/v1/skill.md` 与"不是 API 文档"意味的文案);通道关→不铸码+关闭提示(关闭提示亦含该区分语)。新 confirm 路径端到端(经 `confirmPairingCode`)。
- **改**:`pair-endpoints.test.ts` 导入路径 `@/app/agent/skill.md/route` → `@/app/agent/pair.md/route`;原断言保留并加上述区分语断言。
- E2E(改写):管理员开通道 → 取 `/agent/pair.md` 8 位短码 → 登录态打开 `/agent-clients/pair` 填码提交 → 跳编辑页、token 一次性可见 → 用该 token `GET /api/agent/v1/apps` 得 200 → 同码再确认显示错误提示 → **回 `/agent-clients` 列表对该行点「轮换」(接受确认弹窗)→ 跳编辑页拿到新 `^ghagt_` token 且仍能调 `/api/agent/v1/apps` 得 200**。
- 回归:全量 admin + db 套件、typecheck、build(`/agent-clients/pair` emitted、`/agent/pair` 不再 emitted)、lint 全绿。

## 8. 分阶段切片

| 阶段 | 内容 | 完成判据 |
|---|---|---|
| **C1 · 短码原语** | `generatePairingCode` 改 8 位短码字符集 + TTL 30min;移除旧 `codePrefix` 前缀函数 | 单元测试绿(格式/字符集/无偏置/唯一/TTL) |
| **C2 · confirmPairingCode** | `redeemPairingCode`→`confirmPairingCode(code,adminId,name?)`(通道关拒、原子焚码、createdByAdminId=adminId);`mintPairingCode` 写随机工单号 codePrefix | 单元/集成测试绿(全分支 + 并发) |
| **C3 · 删公开 POST + skill.md 文案** | 删 `agent/pair` 路由 + middleware 收口;`pairing-skill-md.ts` 改新指引 | `/agent/pair` 404;`GET /agent/pair.md` 含短码+新指引、不含 POST |
| **C4 · 登录态确认 UI** | `agent-clients/pair` 页 + `confirmPairingAction` + 列表入口;配对码日志改列;复用编辑页回显 | typecheck/build 绿,新路由 emitted;手工走查链路通 |
| **C5 · 测试 + E2E + spec 收尾** | 删旧 POST 用例、加 confirm 用例、改 E2E;全量回归 | 全套测试/lint/build/E2E 绿 |

## 9. 不在本 spec 范围(未来)

- 结构化提权审批队列(Agent 声明期望 scope → pending → 管理员批/驳)——日后真有提权频次再加。
- 公开 `GET /agent/pair.md` 硬限流 / per-IP 配额(延续延后;主控为出厂关+通道开关)。
- `AgentPairingCode` / `AgentAccessLog` 自动清理 prune(运维延后项;上线开通道前补)。
- 测试隔离:DB 级单行 `agent_pairing_config` 单例使测试需 `fileParallelism:false`;后续可加 snapshot/restore fixture。
- 多通道 / 每通道独立默认 scope / owner 自助选 scope(本设计单通道、固定安全默认、事后提权)。
