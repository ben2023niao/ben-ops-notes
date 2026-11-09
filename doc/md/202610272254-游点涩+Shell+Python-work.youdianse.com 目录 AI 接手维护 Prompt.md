---
id: "doc-7bd874a596f9"
title: "work.youdianse.com 目录 AI 接手维护 Prompt"
date: "2026-10-27T22:54:15+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Nginx", "CDN", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/work.youdianse.com/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/work.youdianse.com/doc/prompt.md"
sourceSha256: "0eb07cdbecd7ed9ced05fb524f750d0a231e94260c4ce094c572cf8576603511"
sourceSystem: "project-doc"
---

# work.youdianse.com 目录 AI 接手维护 Prompt

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610272254-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BPython-work.youdianse.com%20%E7%9B%AE%E5%BD%95%20AI%20%E6%8E%A5%E6%89%8B%E7%BB%B4%E6%8A%A4%20Prompt.md)

> 整理日期：2026-10-27 22:54｜日期依据：文件创建/修改时间

你正在接手 `devops/work.youdianse.com` 项目。这个目录是一个静态网页导航站，基于 MyNav 风格仿 Windows 桌面，用来集中打开运维常用系统、CICD、宝塔、Cloudflare、AWS、Google 文档等入口。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- 服务器上下文：`devops/ai_context/doc/prompt.md`
- ben-bot 机器人菜单：`devops/python/ben-bot/doc/prompt.md`
- PHP 工具站入口：`devops/php/doc/prompt.md`
- 周报生成：`work-运维部工作进度-周报/doc/prompt.md`

这个静态站是人工点击入口，ben-bot 是飞机构按钮入口。新增或调整运维工具时，常常需要同时考虑这两个入口，但二者权限模型和打开方式不同，不能互相替代。

## 1. 项目定位

- 目录路径：`devops/work.youdianse.com`
- 类型：静态 HTML/CSS/JS 导航页面
- 入口：`index.html`
- 样式：`main.css`
- 交互：`main.js`
- WebSocket 工具页：`ws.html`
- 静态资源：`images/`、`vendor/`
- 运行方式：静态站点，PHP/宝塔/Nginx 直接托管即可

## 2. 当前结构

```text
work.youdianse.com/
├── README.md
├── index.html
├── main.css
├── main.js
├── ws.html
├── images/
├── vendor/
│   ├── jquery/
│   ├── jquery-ui/
│   └── websocket-tool/
├── .well-known/pki-validation/
└── doc/
    └── prompt.md
```

## 3. 核心机制

### 图标配置

所有桌面图标主要写在 `index.html` 的 `icons` 数组里：

```js
var icons = [
  {
    name: "显示名称",
    url: "https://example.com",
    image: "images/icons/example.png",
    openInNewWindow: true
  }
];
```

字段含义：

- `name`：桌面显示名称
- `url`：点击后打开的目标地址
- `image`：图标图片或 data SVG
- `openInNewWindow`：
  - `true`：新窗口打开
  - `false`：在当前页面内创建 iframe 窗口

### 点击行为

`main.js` 中的逻辑：

1. 页面加载后遍历 `icons`。
2. 为每个 icon 创建桌面图标。
3. 双击图标。
4. 如果 `openInNewWindow = true`，调用 `window.open(icon.url)`。
5. 如果 `false`，在页面里创建一个可拖拽、可缩放的窗口，里面嵌入 iframe。

## 4. 外部资源本地化

当前页面应尽量使用 `vendor/` 下本地资源，而不是外部 CDN。

当前已使用：

- `vendor/bootstrap/3.3.0/css/bootstrap.min.css`
- `vendor/jquery-ui/1.12.1/jquery-ui.min.css`
- `vendor/jquery/1.11.1/jquery.min.js`
- `vendor/jquery-ui/1.12.1/jquery-ui.min.js`
- `vendor/websocket-tool/...`

维护规则：

- 新增 JS/CSS 依赖时优先放到 `vendor/`。
- 不要直接引用 `cdn.bootcss.com`、`cdn.jsdelivr.net` 等外部地址，除非用户明确要求。
- 如果引入新库，记录来源版本和用途。

## 5. `openInNewWindow` 选择规则

一些站点不能被 iframe 打开，原因包括：

- `X-Frame-Options`
- CSP `frame-ancestors`
- 登录系统跳转限制
- 浏览器安全策略

建议：

- 内部简单页面、允许 iframe 的后台系统：`openInNewWindow: false`
- AWS、Cloudflare、Godaddy、Google Drive、Google Sheets、宝塔、第三方登录系统：`openInNewWindow: true`
- 如果用户反馈“内部打开空白/拒绝连接”，优先改成 `true`。
- 如果用户希望像桌面窗口一样嵌入，先测试目标是否允许 iframe。

## 6. 证书验证文件

`.well-known/pki-validation/` 下是证书或 CA 验证文件。维护时：

- 不要随意删除。
- 如果证书签发失败，确认 CA 要求的文件名和内容。
- 新增验证文件时保留路径结构。

## 7. 二次开发建议

### 新增导航入口

1. 准备图标：
   - 使用已有 `images/icons/*.png`
   - 或使用 data SVG
2. 在 `index.html` 的 `icons` 数组追加对象。
3. 根据目标站点选择 `openInNewWindow`。
4. 本地打开 `index.html` 验证。

### 修改图标文案

只改 `name` 字段即可。

### 修改目标链接

只改 `url` 字段。注意不要把包含敏感 token 的一次性链接写进仓库。

### 调整窗口默认大小

改 `main.js` 中：

- `left`
- `top`
- `height`
- `width`
- 最大高度 600
- 最大宽度 800

### 调整页面样式

改 `main.css`。保持桌面导航风格，不要把它改成复杂后台系统。

## 8. 常见坑

### 双击后页面空白

目标站点很可能禁止 iframe。把对应 icon 的：

```js
openInNewWindow: true
```

### 图标显示 error.png

检查 `image` 路径是否存在。`main.js` 里有 fallback：

```js
onerror="this.src='images/error.png';"
```

### 新增 CDN 资源线上加载失败

优先本地化到 `vendor/`，并用相对路径引用。

### 修改后没生效

可能是浏览器缓存。强刷或给静态资源加版本号。

## 9. 验证清单

本地静态检查：

```bash
cd devops/work.youdianse.com
python3 -m http.server 8000
```

浏览器打开：

```text
http://203.0.113.1:8000
```

检查：

- 图标是否都显示。
- 双击是否按预期打开。
- 内部 iframe 是否能加载。
- 新窗口站点是否打开。
- 控制台是否有 404。
- vendor 资源是否本地加载。

## 10. 安全边界

- 不在 URL 中提交明文账号、密码、token。
- 不把一次性登录链接写进 `index.html`。
- 不删除 `.well-known` 验证文件，除非确认不再使用。
- 不重新引入外部 CDN，除非用户明确要求。
- 不把后台管理入口公开给不该知道的人；如有访问控制需求，应在服务器/Nginx 层实现。

## 11. AI 接手流程

1. 先读 `README.md`。
2. 再读 `index.html` 的 `icons` 数组。
3. 如是打开方式问题，检查 `openInNewWindow`。
4. 如是资源问题，检查 `vendor/` 和浏览器 404。
5. 修改后本地起静态服务验证。
6. 回复用户时列出改了哪些入口、哪些改为新窗口、哪些仍内部打开。
