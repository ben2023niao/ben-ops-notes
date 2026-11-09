---
id: "doc-02e0ac62f314"
title: "ben-bot AI 接手开发 Prompt"
date: "2026-07-13T00:00:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "监控告警", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/prompt.md"
sourceSha256: "f577df465581e02be9457d261705d370f38894197cf768bd7b74f471a8532b36"
sourceSystem: "project-doc"
---

# ben-bot AI 接手开发 Prompt

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607130000-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-ben-bot%20AI%20%E6%8E%A5%E6%89%8B%E5%BC%80%E5%8F%91%20Prompt.md)

> 整理日期：2026-07-13 00:00｜日期依据：正文日期

环境标签：通用

你正在接手 `ben-bot` 项目。请先完整阅读这份文档，再修改代码。这个项目是一个中文运维 Telegram 机器人，核心目标是把常用运维入口、发布入口、配置查看、值班表和脚本执行能力做成飞机群里的按钮工作台。

本文件是给各类 AI 助手使用的接手 prompt。它比普通 README 更偏操作视角：告诉你应该先看哪里、哪些行为不能做、菜单和权限如何生效、改完如何验证和部署。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- Python 项目总索引：`devops/python/doc/prompt.md`
- 服务器上下文：`devops/ai_context/doc/prompt.md`
- 运维导航站：`devops/work.youdianse.com/doc/prompt.md`
- Telegram Relay：`devops/python/telegram/doc/prompt.md`
- 周报生成：`work-运维部工作进度-周报/doc/2026-07-13-周报生成通用提示词.md`

ben-bot 是飞机构按钮工作台，和 `work.youdianse.com` 的网页导航互补。涉及服务器、容器、部署路径、线上拉取和重启时，以 `ai_context` 为上游事实；涉及周报通知或本次优化摘要时，提交后应使用 `@game18_report_bot` 把 commit、变更点和验证结果安全广播到它当前可达的所有已知运维群。发送前必须 dry-run 确认可达群，通知内容必须适合多群公开查看，不能包含密钥、chat id、服务器口令或 `.env` 明文。

## 1. 基本定位

- 项目名：`ben-bot`
- 位置：`devops/python/ben-bot`
- 运行形态：Docker 容器 `ben-bot`
- 主要语言：Python
- Telegram SDK：`python-telegram-bot` 13.x
- 运行 Python：容器里是 Python 3.11
- 主要入口：`app/bot.py`
- 主要包：`app/benbot`
- 菜单和脚本根目录：`data/scripts`
- 持久化运行数据：`data/upload`
- 构建日志：`data/package`

这个机器人当前不是纯聊天机器人，而是“按钮式运维控制台”。用户常用流程是：

1. 在飞机群发送 `/start`
2. 点击首页按钮
3. 进入某个目录或目录插件
4. 选择具体动作
5. 机器人执行脚本、远程发布或发送附件

## 2. 开发原则

你修改本项目时必须遵守：

- 优先读现有代码，不要凭想象重写。
- 菜单尽量通过 `data/scripts` 和 `.benbot.json` 扩展，不要把按钮硬编码回大文件。
- 复杂交互使用目录插件 `benbot_plugin.py`。
- 权限统一改 `app/benbot/permissions.py`，角色名单统一改 `app/benbot/constants.py`。
- Telegram 文本默认使用 MarkdownV2，输出动态内容要转义。
- 不要泄露 token、私钥、密码、原始 `.env` 内容。
- 不要把调试时读取到的敏感配置写进文档、日志摘要或提交说明。
- 线上 H5 发布权限保持运维专属，除非用户明确要求放开。
- `脱敏配置查看` 当前是公共功能，任何人都可以点击和执行。
- 本地工作区可能有用户未提交文件，提交前必须确认暂存范围。

## 3. 当前首页结构

首页结构由 `app/benbot/home.py` 和 `data/scripts` 注册结果共同决定。当前首页说明树是：

```text
.
├── 测试环境-游点涩-h5-发版
├── 线上环境-游点涩-h5-发版
├── 后端与定时任务
│   ├── 测试后端发布
│   ├── 测试定时任务
│   ├── 线上后端发布
│   └── 线上定时任务
├── 脱敏配置查看
│   ├── 测试配置查看
│   └── 线上配置查看
├── 域名接入
│   └── 线上增加前端域名
├── 文档与联系人
│   ├── 帮助文档
│   ├── 数据打包机域名
│   ├── 文档日常发布监控
│   ├── 文档更新
│   └── 疑难杂症业务模块
└── 运维值班表
```

当前实际首页按钮分区规则：

- `layout_section = "release"`：顶部发布区，当前包含两个 H5 发版根按钮。
- `layout_section = "workbench"`：中间工作台，默认折叠；当前可能为空。
- `layout_section = "duty"`：底部值班表按钮。
- 没有上述 section 的顶层目录会作为普通目录按钮展示。
- 顶层 `data/scripts/备份` 被 `plugin_registry.py` 隐藏，不进入首页。

## 4. 权限模型

权限代码在 `app/benbot/permissions.py`。

角色名单在 `app/benbot/constants.py`：

- `OPS_USERNAMES`
- `FRONTEND_USERNAMES`
- `TEST_USERNAMES`
- `BACKEND_USERNAMES`

当前公共路径在 `PUBLIC_ALLOWED_PATHS`：

```python
PUBLIC_ALLOWED_PATHS = (
    "测试环境-游点涩-h5-发版",
    "脱敏配置查看",
    "后端与定时任务",
    "域名接入",
    "文档与联系人",
    "运维值班表",
)
```

当前角色路径：

- 前端：可操作 `测试环境-游点涩-h5-发版`
- 测试：可操作 `测试环境-游点涩-h5-发版`
- 后端：可操作 `测试环境-游点涩-h5-发版`
- 运维：全部权限
- 访客：可操作公共路径

特别注意：

- `can_view_menu_path()` 当前直接返回 `True`，所以菜单可见性基本对所有人开放。
- 真正的执行权限由 `can_access_script_path()` 和 `can_access_menu_node()` 控制。
- 非运维用户不能使用 `/sh`、上传、下载。
- `脱敏配置查看/线上配置查看/view_env.py` 和 `脱敏配置查看/测试配置查看/view_env.py` 当前任何人都能执行。
- `线上环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py` 当前只有运维可以执行。

验证权限的常用脚本：

```bash
python3 - <<'PY'
import sys
from types import SimpleNamespace
sys.path.insert(0, 'devops/python/ben-bot/app')
from benbot.permissions import can_access_script_path, get_role_capability_text, get_user_role

u = SimpleNamespace(username='random_guest')
paths = [
    '脱敏配置查看/线上配置查看/view_env.py',
    '脱敏配置查看/测试配置查看/view_env.py',
    '线上环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py',
]
for path in paths:
    print(path, can_access_script_path(u, path))
print(get_user_role(u), get_role_capability_text(get_user_role(u)))
PY
```

## 5. 核心模块地图

### `app/bot.py`

薄入口，只调用 `benbot.main.run()`。

### `app/benbot/main.py`

负责：

- 创建 `Updater`
- 注册 `/start`、`/help`、`/sh`、`/download`、`/script`
- 注册文档上传 handler
- 注册所有 callback query
- 启动 polling
- 输出启动日志
- 发送启动通知

启动通知逻辑：

- `build_and_run_ben_bot.sh` 会写入 `data/upload/last_update_notice.txt`
- `main.py` 启动后读取并发送到 `STARTUP_NOTIFY_CHAT_IDS` 和 `known_chat_ids.json`
- 发送成功后会归档为 `last_update_notice.sent.<timestamp>.txt`

### `app/benbot/config.py`

负责环境变量和路径：

- `TELEGRAM_API_TOKEN`
- `STARTUP_NOTIFY_CHAT_IDS`
- `MAX_TASK_OUTPUT`
- `SCRIPTS_ROOT_PATH`
- `UPLOAD_PATH`
- `KNOWN_CHAT_IDS_PATH`

命令安全基础配置也在这里：

- `CMD_BLACK_LIST = {"rm"}`
- `CMD_BLACK_CHARS = {";", "\n", "&"}`

### `app/benbot/constants.py`

负责：

- `BOT_VERSION`
- 容器名
- 默认 Telegram token 选择
- 角色用户名
- 页面大小和提交数等常量

注意：源码里可能存在历史 token 字符串。写文档和回复用户时不要复制真实 token。

### `app/benbot/plugin_registry.py`

负责扫描 `data/scripts`：

- 读取目录 `.benbot.json`
- 读取脚本旁边的 `<script>.benbot.json`
- 生成 `MenuNode`
- 顶层隐藏 `备份`
- `type = "script"` 的目录会作为一个脚本节点，而不是普通目录
- `plugin_file = "benbot_plugin.py"` 会被加载为目录插件

重要字段：

- `label`
- `order`
- `columns`
- `layout_section`
- `layout_group`
- `entry_script`
- `usage`
- `example`
- `action`
- `placeholder_text`
- `plugin_file`
- `links`

### `app/benbot/home.py`

负责 `/start` 首页文案和按钮布局。

按钮布局规则：

- release 节点先展示
- workbench 节点通过“展开工作台功能”折叠
- 普通 category 和 duty 节点随后展示
- 最后一行是帮助菜单和联系 Ben_Bird

### `app/benbot/menu.py`

负责：

- 目录页面渲染
- 脚本详情页渲染
- 查看用法 / 立即执行示例按钮
- placeholder 页面
- link 页面
- MarkdownV2 输出

如果 Telegram 报 `BadRequest: can't parse entities`，优先检查这里和调用处是否正确转义。

### `app/benbot/handlers/callbacks.py`

所有按钮点击主要经过 `shortcut_cb()`：

- `home:*`：回首页
- `help:*`：打开帮助中心
- `menu:<node_id>`：打开目录或功能
- `usage:<node_id>`：显示用法
- `run:<node_id>`：执行示例
- `plugin:<node_id>:<action>:...`：交给目录插件处理
- `busy:*`：忙碌态按钮

目录插件约定：

- `handle_open(update, context, node=None)`：点击功能入口时执行
- `show_menu(message, user=None, edit=False, node=None)`：展示插件菜单
- `handle_callback(action, payload, update, context, node=None)`：处理插件自定义按钮
- `run_example(update, context, node=None)`：覆盖“立即执行示例”

### `app/benbot/executor.py`

负责实际执行：

- `/script`
- `/sh`
- 实时进度框
- 输出切片
- 日志附件
- 发布进度识别

H5 发布会通过环境变量启用 live output：

- `BEN_BOT_LIVE_OUTPUT=1`
- `BEN_BOT_PROGRESS_KIND=youdianse_h5`
- `BEN_BOT_LIVE_TITLE`
- `BEN_BOT_SEND_LOG_DOCUMENT=1`
- `BEN_BOT_PRIMARY_URL`
- `BEN_BOT_VERSION_TXT_URL`
- `BEN_BOT_VERSION_JSON_URL`

`do_exec()` 的命令如果是脚本，会按 `data/scripts` 相对路径查找，并且先过 `can_access_script_path()` 权限。

### `app/benbot/handlers/files.py`

负责上传和下载。只有运维能用。

### `app/benbot/handlers/shell.py`

负责 `/sh`。只有运维能用。

## 6. data/scripts 菜单系统

`data/scripts` 是机器人功能仓库。新增按钮优先在这里建目录。

### 普通目录

```text
data/scripts/某目录/
├── .benbot.json
└── 子功能/
```

`.benbot.json` 示例：

```json
{
  "label": "📚 文档与联系人",
  "order": 50,
  "columns": 2
}
```

### 目录脚本节点

```text
data/scripts/某功能/
├── .benbot.json
└── main.py
```

`.benbot.json` 示例：

```json
{
  "type": "script",
  "label": "功能按钮",
  "order": 100,
  "entry_script": "main.py",
  "usage": "/script 某功能/main.py run",
  "example": "/script 某功能/main.py run"
}
```

### 目录插件

```text
data/scripts/某功能/
├── .benbot.json
├── benbot_plugin.py
└── main.py
```

`.benbot.json` 必须设置：

```json
{
  "type": "script",
  "plugin_file": "benbot_plugin.py",
  "entry_script": "main.py"
}
```

适合：

- 最近提交分页
- 多按钮选择
- 自定义 callback payload
- 点击入口不直接执行脚本，而先展示菜单

## 7. 当前重点功能

### 测试环境-游点涩-h5-发版

目录：

```text
data/scripts/测试环境-游点涩-h5-发版
```

特点：

- 首页顶部根按钮
- `layout_section = "release"`
- `layout_group = "frontend_release"`
- 拉取 `youdianse-h5` 的 `test` 分支最近提交
- 用户选择 git id 后远程部署
- 任何人当前都可执行测试 H5 发布
- 发布过程使用实时进度框和完整日志附件
- 入口插件：`benbot_plugin.py`
- 主脚本：`youdianse_test_18game_h5_client.py`
- 远程脚本模块：`remote_youdianse_h5_*.py`
- 配置：`server_config.py`

常用命令：

```bash
/script 测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py list
/script 测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py run <git_id>
```

### 线上环境-游点涩-h5-发版

目录：

```text
data/scripts/线上环境-游点涩-h5-发版
```

特点：

- 首页顶部根按钮
- `layout_section = "release"`
- `layout_group = "frontend_release"`
- 拉取 `youdianse-h5` 的 `main` 分支最近提交
- 用户选择 git id 后远程部署
- 同步 Nuxt 静态资源到对象存储/CDN
- 只有运维角色可执行
- 发布过程使用实时进度框和完整日志附件
- 入口插件：`benbot_plugin.py`
- 主脚本：`youdianse_test_18game_h5_client.py`
- 配置：`server_config.py`

常用命令：

```bash
/script 线上环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py list
/script 线上环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py run <git_id>
```

注意：

- 这两个 H5 发版目录曾经在 `data/scripts/前端发布/` 下，现在已经上移到 `data/scripts/` 根目录。
- 任何引用旧路径 `前端发布/测试环境-游点涩-h5-发版` 或 `前端发布/线上环境-游点涩-h5-发版` 的代码都应修正。

### 脱敏配置查看

目录：

```text
data/scripts/脱敏配置查看
```

子功能：

- `线上配置查看/view_env.py`
- `测试配置查看/view_env.py`

共享逻辑：

```text
data/scripts/脱敏配置查看/.shared/sanitized_env_viewer.py
```

能力：

- SSH 到目标服务器
- 优先进入后台容器查找 `.env`
- 读取配置后脱敏
- 在当前飞机群发送 txt 附件
- 输出摘要不包含原始密钥

当前默认目标：

- 测试：`38.92.8.34`，默认用户 `root`
- 线上：`16.209.16.108`，默认用户 `ubuntu`，默认使用 sudo docker

凭证优先级：

1. `CONFIG_VIEW_*_SSH_PRIVATE_KEY`
2. `CONFIG_VIEW_*_SSH_KEY_PATH`
3. `CONFIG_VIEW_*_SSH_PASSWORD`
4. fallback 到对应 H5 发版目录的 `server_config.py`

可配置环境变量：

```text
CONFIG_VIEW_TEST_SSH_HOST
CONFIG_VIEW_TEST_SSH_PORT
CONFIG_VIEW_TEST_SSH_USER
CONFIG_VIEW_TEST_SSH_PRIVATE_KEY
CONFIG_VIEW_TEST_SSH_KEY_PATH
CONFIG_VIEW_TEST_SSH_PASSWORD
CONFIG_VIEW_TEST_SUDO_PASSWORD
CONFIG_VIEW_TEST_USE_SUDO
CONFIG_VIEW_TEST_CONTAINER
CONFIG_VIEW_TEST_ENV_PATH

CONFIG_VIEW_PROD_SSH_HOST
CONFIG_VIEW_PROD_SSH_PORT
CONFIG_VIEW_PROD_SSH_USER
CONFIG_VIEW_PROD_SSH_PRIVATE_KEY
CONFIG_VIEW_PROD_SSH_KEY_PATH
CONFIG_VIEW_PROD_SSH_PASSWORD
CONFIG_VIEW_PROD_SUDO_PASSWORD
CONFIG_VIEW_PROD_USE_SUDO
CONFIG_VIEW_PROD_CONTAINER
CONFIG_VIEW_PROD_ENV_PATH
```

调试命令：

```bash
python3 data/scripts/脱敏配置查看/线上配置查看/view_env.py dry-run
CONFIG_VIEW_SEND_DOCUMENT=0 python3 data/scripts/脱敏配置查看/线上配置查看/view_env.py run
```

在容器里调试：

```bash
sudo docker exec -e CONFIG_VIEW_SEND_DOCUMENT=0 ben-bot \
  python3 /app/data/scripts/脱敏配置查看/线上配置查看/view_env.py run
```

注意：

- 调试时建议设置 `CONFIG_VIEW_SEND_DOCUMENT=0`，避免重复往群里发附件。
- 不要把读取到的原始 `.env` 内容复制到聊天、issue、文档或 commit message。

### 运维值班表

目录：

```text
data/scripts/运维值班表
```

特点：

- `layout_section = "duty"`
- 首页底部按钮
- 公共功能，任何人可点
- 使用目录插件 `benbot_plugin.py`
- 主脚本 `duty_schedule.py` 支持 JSON 输出

## 8. 部署与运行

本地或服务器进入：

```bash
cd devops/python/ben-bot
sh build_and_run_ben_bot.sh
```

脚本会：

1. 读取 `.env`，如果存在
2. 判断宿主机系统
3. 本地 macOS 默认使用本地测试机器人 token
4. Linux/Ubuntu 默认使用线上机器人 token
5. 写入 `data/upload/last_update_notice.txt`
6. `docker compose up -d --build`
7. 输出构建日志到 `data/package`

发送启动说明：

```bash
BEN_BOT_UPDATE_NOTES="- 本次变更说明" sh build_and_run_ben_bot.sh
```

线上机器人部署常用流程：

```bash
ssh -i devops/python/ben-bot/data/scripts/备份/测试环境-后端-发版/id_rsa ubuntu@52.79.252.255
cd /opt/telegram/18game_devops
sudo git fetch origin main
sudo git pull --ff-only origin main
cd devops/python/ben-bot
sudo env BEN_BOT_UPDATE_NOTES="- 更新说明" sh ./build_and_run_ben_bot.sh
```

部署后验证：

```bash
sudo docker ps --filter name=ben-bot --format '{{.Names}} | {{.Image}} | {{.Status}}'
sudo docker logs --tail 120 ben-bot
sudo docker exec -i ben-bot python3 - <<'PY'
from types import SimpleNamespace
from app.benbot.permissions import can_access_script_path
u = SimpleNamespace(username='random_guest')
print(can_access_script_path(u, '脱敏配置查看/线上配置查看/view_env.py'))
print(can_access_script_path(u, '线上环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py'))
PY
```

## 9. 本地验证建议

语法检查：

```bash
python3 -m py_compile app/benbot/permissions.py app/benbot/home.py app/benbot/help_center.py
python3 -m py_compile data/scripts/脱敏配置查看/.shared/sanitized_env_viewer.py
```

注册表检查：

```bash
python3 - <<'PY'
import sys
sys.path.insert(0, 'app')
from benbot.plugin_registry import load_registry
registry = load_registry()
root = registry.get('root')
for child_id in root.children:
    node = registry.get(child_id)
    print(node.label, node.rel_path, node.script_path, node.layout_section, node.layout_group)
PY
```

注意：

- 本地 macOS 的 `python3` 可能是 3.9，而项目代码部分模块使用 `str | None` 这类 Python 3.10+ 注解。
- 容器运行时是 Python 3.11，最终以容器内结果为准。
- 如果本地 import 报类型注解错误，不一定代表线上容器会失败；但可以优先用 Python 3.11 或容器复核。

## 10. 新增功能的推荐步骤

新增一个普通功能：

1. 在 `data/scripts` 下建目录。
2. 写 `.benbot.json`。
3. 写 Python 或 Shell 脚本。
4. 无参数时输出用法。
5. 在 `permissions.py` 决定是否公共、角色专属或仅运维。
6. 用 `/script` 和按钮都走一遍。
7. 同步 README、帮助中心或本 prompt。

新增一个复杂按钮：

1. 建目录。
2. `.benbot.json` 设置 `type = "script"`、`entry_script`、`plugin_file`。
3. 写 `benbot_plugin.py`。
4. 在插件里实现 `handle_open` 和 `handle_callback`。
5. callback_data 用 `plugin:<node_id>:<action>:<payload...>`。
6. 长任务用 `do_exec(..., live_output=True, extra_env=...)`。
7. 需要防重复点击时使用 `busy_state.set_message_busy()`。

新增公共功能：

1. 把顶层路径加入 `PUBLIC_ALLOWED_PATHS`。
2. 更新角色能力说明。
3. 验证 guest 的 `can_access_script_path()`。

新增运维专属功能：

1. 不加入 `PUBLIC_ALLOWED_PATHS`。
2. 不加入普通角色的 `ROLE_ALLOWED_PATHS`。
3. 运维自动拥有全部权限。

## 11. 常见问题和坑

### 按钮看得到但点不了

原因通常是：

- `can_view_menu_path()` 放开了可见性
- 但 `can_access_script_path()` 没放开执行权限

检查：

```python
can_access_script_path(user, "目录/脚本.py")
```

### 目录移动后功能报缺凭证或找不到脚本

检查所有硬编码路径：

```bash
rg -n "旧目录名|旧路径" devops/python/ben-bot
```

H5 发版目录已经从 `前端发布/` 上移到根目录，旧路径应清理。

### Telegram Markdown 报错

优先检查：

- 是否用 `escape_markdown_v2()`
- 是否用 `md_inline_code()` / `md_bash_block()`
- 动态文本里是否有 `_ * [ ] ( ) ~ ` > # + - = | { } . !`

### 长输出刷屏

优先使用：

- 实时进度框
- 输出摘要
- 完整日志 txt 附件

不要把长日志直接分很多条刷群。

### 远程 SSH 失败

检查：

- 容器内是否有 `ssh` 和 `sshpass`
- docker compose 是否传入对应环境变量
- H5 发版目录下 fallback key 是否存在
- 目标服务器用户、端口、sudo docker 权限

### 配置查看发送附件失败

检查：

- `TELEGRAM_API_TOKEN`
- `BEN_BOT_CHAT_ID`
- 当前脚本是否通过机器人上下文执行
- 调试时是否设置了 `CONFIG_VIEW_SEND_DOCUMENT=0`

## 12. 安全边界

这个项目触达发布、SSH、服务器配置和 Telegram 群。任何 AI 二次开发时必须遵守：

- 不在回复中输出真实 token、私钥、密码、原始 `.env`。
- 不把运行中读取到的 `.env` 原文写入仓库。
- 不把私钥内容复制到 prompt 或文档。
- 不随意扩大线上发布权限。
- 不执行破坏性命令，例如 `git reset --hard`、删除数据、清空容器卷，除非用户明确要求。
- 不把 `data/upload` 里的运行期附件当作源代码随意提交。
- 提交前用 `git status --short` 检查是否混入用户未跟踪文件。

## 13. 当前已知工作区习惯

- 仓库根目录通常是 `18game_devops`。
- 用户 IDE 可能打开的是 `devops/python/ben-bot/...`，但终端 cwd 不一定在仓库根。
- 操作时显式指定 workdir。
- 这个仓库里可能长期存在未跟踪的周报草稿，例如 `work-运维部工作进度-周报/2.txt` 和 `2-en.txt`。除非用户明确要求，不要提交它们。

## 14. 面向 AI 的首要执行流程

当用户要求你改 ben-bot 时，按这个顺序：

1. `git status --short --branch`
2. 读取相关模块和 `.benbot.json`
3. 判断是菜单问题、权限问题、脚本问题、插件问题、部署问题还是远程目标问题
4. 小范围修改
5. `py_compile`
6. 权限或注册表小脚本验证
7. 如果用户要求上线或问题发生在线上，提交、推送、服务器拉取、重建容器
8. 看 `docker logs --tail 120 ben-bot`
9. 容器内再验证一次核心行为
10. 最终回复只说结果、提交号、验证结果和未处理事项

## 15. 当前最重要的事实快照

- H5 测试发布和线上发布是根按钮，不在 `前端发布/` 目录下。
- H5 测试发布当前任何人可执行。
- H5 线上发布当前只有运维可执行。
- 脱敏配置查看当前任何人可执行。
- 运维值班表当前任何人可执行。
- `/sh`、上传、下载只有运维可用。
- 菜单由 `data/scripts` 扫描生成，`备份` 顶层隐藏。
- 目录插件是当前复杂交互的标准做法。
- 配置查看共享逻辑会从 H5 发版目录的 `server_config.py` fallback SSH 凭证。
- 部署脚本会发送启动更新通知。

如果你是后续接手的 AI，请把这份文件当作项目事实入口，但仍然以源码为准；发现文档和源码冲突时，先读源码，再更新文档。
