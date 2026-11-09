---
id: "doc-269b3f7b9f57"
title: "通用型原型对比与实现 Skill 设计稿"
date: "2026-06-12T03:49:41+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "Docker", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/prototype-diff-implementation-skill-design.md"
sourcePath: "~/Projects/work/game/ghome/docs/prototype-diff-implementation-skill-design.md"
sourceSha256: "e337a800799100f30db1e9ffda0ee23f23def5c9bb8e5f9968e002918cfddb85"
sourceSystem: "project-doc"
---

# 通用型原型对比与实现 Skill 设计稿

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606120349-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BShell-%E9%80%9A%E7%94%A8%E5%9E%8B%E5%8E%9F%E5%9E%8B%E5%AF%B9%E6%AF%94%E4%B8%8E%E5%AE%9E%E7%8E%B0%20Skill%20%E8%AE%BE%E8%AE%A1%E7%A8%BF.md)

> 整理日期：2026-06-12 03:49｜日期依据：文件创建/修改时间

## 目标定位

设计一个通用型 `prototype-diff-implementation` skill，用于将产品原型与现有应用进行逐页对比，生成差异基准，辅助人工确认，并按确认结果实施改造与验证。

该 skill 不限定 Next.js。执行过程可以参考 Ghome 本次 `20260522` 原型对齐，但能力目标应覆盖 React、Vue、Nuxt、UniApp 等常见前端项目。

核心原则：

```text
原型决定目标体验，当前系统决定真实实现方式。
```

## 最低输入要求

用户至少需要提供：

| 输入项 | 示例 | 说明 |
| --- | --- | --- |
| 原型入口 | `docs/ghome-20260522.html` | HTML / Figma 导出 / URL / 截图目录 |
| 当前应用入口 | `http://localhost:3000` | 本地或测试环境 URL |
| 代码库路径 | 当前 workspace | 需要可读取页面、组件、样式、数据层 |
| 页面范围 | 全站 / 指定页面 / 指定路由 | 明确本轮对比边界 |
| 输出目录 | `docs/prototype-diff/20260522` | 存放差异基准和扫描结果 |
| 验证命令 | `typecheck` / `test` / `build` | 用于改造后的回归验证 |

Ghome 本次参考输入：

```text
原型：docs/ghome-20260522.html
当前应用：http://localhost:3000
代码库：D:\work\code\remote\ghome\web
输出：docs/prototype-diff/20260522
验证：docker exec ghome-web pnpm --filter @ghome/web typecheck/test
```

## 框架识别层

skill 应先识别项目结构，不应预设 Next.js。

识别规则示例：

| 项目类型 | 识别方式 | 主要路由位置 |
| --- | --- | --- |
| Next.js App Router | `package.json` 包含 `next`，存在 `app/**/page.tsx` | `app/**/page.tsx` |
| Next.js Pages Router | 存在 `pages/**` | `pages/**` |
| React + Vite | 包含 `react` / `@vitejs/plugin-react` | `src/router`、`src/pages` |
| Vue + Vite | 包含 `vue` / `@vitejs/plugin-vue` | `src/router`、`src/views` |
| Nuxt | 存在 `nuxt.config.*` | `pages/**` |
| UniApp | 存在 `pages.json` | `pages.json`、`pages/**` |
| 未知项目 | 通过 `package.json` 和目录结构推断 | 先建立路由索引 |

工作顺序：

```text
识别框架 → 找路由 → 找组件 → 找样式 → 找数据层 → 决定改造位置
```

## 原型解析层

根据原型质量分级处理。

| 原型质量 | 特征 | 处理方式 |
| --- | --- | --- |
| 高质量 | HTML + 路由 + `data-spec` + 需求说明 | 按模块精确对比 |
| 中质量 | HTML + 页面结构 + 静态文案 | 按页面和文案对比 |
| 低质量 | 截图 / 图片 / PDF | 主要输出视觉差异，需更多人工确认 |

优先提取：

- 路由
- 页面标题
- 模块标题
- `data-spec`
- 静态文案
- 字段说明
- 交互说明
- 链接跳转
- 响应式要求

## 对比输出层

每页生成一份差异基准文档。

表格模板：

```markdown
| 编号 | 模块 | 差异点 | 原型表现 | 当前表现 | 当前来源类型 | 建议状态 |
| --- | --- | --- | --- | --- | --- | --- |
```

`当前来源类型` 建议枚举：

- 代码静态内容
- 数据库查询
- API 返回
- 后台配置
- fixture/mock
- 样式/布局
- 路由
- 非内容配置

`建议状态` 建议枚举：

- 待确认
- 按原型改
- 保留当前
- 接口满足则按原型
- 已确认无差异
- 拆分为后端/数据任务

## 人工确认层

skill 应支持用户用简短方式反馈确认结果。

示例：

```text
H-001 按原型改
H-002 保留当前
H-003 如果接口满足则按原型
优质 App 导航：H-021 和 H-026 保持现状，其他按原型
```

确认后应更新差异基准文档，并按确认结果进入代码改造。

## 实现原则层

该 skill 不能机械地“原型是什么就改成什么”，应遵循以下原则：

- 不把原型 mock 数据硬写死到真实业务页面。
- 当前数据库/API 已能支持原型效果时，优先改 UI。
- 当前接口不支持时，标记为接口/数据任务。
- 公共组件优先改组件，不逐页复制。
- 响应式问题单独验证。
- 保留当前系统中更真实、更一致的业务逻辑。

Ghome 本次参考案例：

| 场景 | 判断 |
| --- | --- |
| 热播精选 top4 | 原型是静态，但实现应来自数据库播放量 top4 |
| 搜索结果 | 原型是 mock，但当前应保留 Prisma 查询 |
| 分类链接 | 按当前系统统一走 `/videos/list?cat=...` |
| App 下载入口 | 保留原型移动端体验，同时结合当前 redirect 状态处理 |

## 验证层

建议固定验证项：

- 类型检查
- 单元测试
- 构建检查
- 页面 HTTP 200
- 关键 DOM / `data-spec` 命中
- 移动端横向滚动检查
- 桌面/移动截图

推荐视口：

```text
320 × 568
390 × 844
768 × 1024
1440 × 900
```

横向滚动检查核心指标：

```text
document.documentElement.scrollWidth === document.documentElement.clientWidth
```

## 提交与 MR 层

skill 可辅助生成：

- MR 标题
- 修改内容
- 验证记录
- 未纳入范围
- 风险点
- 后续任务

提交策略：

- 一个原型版本通常建议一个 MR。
- 回归小修可以追加到同一 MR，也可以视风险拆独立小 MR。
- 排除运行产物，例如 `output/`。
- 排除无关本地环境文件，例如本地 `docker-compose.yml` secret 补充。
- 不混入与原型对齐无关的部署改动。

## 建议 Skill 结构

第一版可先做轻量版：

```text
prototype-diff-implementation/
└── SKILL.md
```

成熟版可扩展：

```text
prototype-diff-implementation/
├── SKILL.md
├── scripts/
│   ├── detect_project.py
│   ├── extract_html_prototype.py
│   ├── check_overflow.py
│   └── route_inventory.py
└── references/
    ├── framework-adapters.md
    ├── diff-table-template.md
    └── ghome-case-notes.md
```

建议先创建 v1，只沉淀工作流和判断原则；等下一次真实原型迭代时，再补脚本和框架适配细节。
