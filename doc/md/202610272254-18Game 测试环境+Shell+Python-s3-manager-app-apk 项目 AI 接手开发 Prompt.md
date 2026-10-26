---
id: "doc-a5f5af2ab498"
title: "s3-manager-app-apk 项目 AI 接手开发 Prompt"
date: "2026-10-27T22:54:15+08:00"
dateSource: "文件创建/修改时间"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "CDN", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/s3-manager-app-apk/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/python/s3-manager-app-apk/doc/prompt.md"
sourceSha256: "10d4d8014fc20d960eef16c5d0120310cedf19ec6f53f574bee74522518aded7"
sourceSystem: "project-doc"
---

# s3-manager-app-apk 项目 AI 接手开发 Prompt

> 来源文件：`~/Desktop/18game_devops/devops/python/s3-manager-app-apk/doc/prompt.md`

> 整理日期：2026-10-27 22:54｜日期依据：文件创建/修改时间

你正在接手 `devops/python/s3-manager-app-apk` 项目。这个目录下是一组相似的 S3 文件管理 Web 小工具，用于管理不同项目/环境的 APP 安装包、IPA、APK 或静态文件。每个子目录基本是一套独立 FastAPI 服务，共用类似代码结构。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- Python 项目总索引：`devops/python/doc/prompt.md`
- 服务器上下文：`devops/ai_context/doc/prompt.md`
- 运维导航站入口：`devops/work.youdianse.com/doc/prompt.md`
- 周报生成：`work-运维部工作进度-周报/doc/prompt.md`

这个项目和 H5 静态资源、S3/CloudFront、Telegram 通知的边界容易混淆。涉及线上 bucket、CloudFront 域名、删除备份和通知时，先确认具体子项目和环境，再同步检查服务器上下文与导航入口。

## 1. 项目定位

- 项目目录：`devops/python/s3-manager-app-apk`
- 服务类型：FastAPI Web 管理后台
- 云服务：AWS S3 + CloudFront
- 通知渠道：Telegram Bot API
- 主要功能：列 S3 目录、上传文件、删除文件、删除前发送 Telegram 备份、生成访问链接
- 部署方式：每个子项目独立 Docker 构建和 `deploy.sh`

## 2. 子项目列表

当前包含三个子项目：

```text
s3-manager-app-apk/
├── s3-manager-18gane-prod/
├── s3-manager-18gane-test/
└── s3-manager-xcp-prod/
```

每个子项目结构大致相同：

```text
子项目/
├── Dockerfile
├── README.txt
├── app.py
├── deploy.sh
├── requirements.txt
├── photo_*.jpg
└── s3信息/
```

注意：`s3信息` 目录和历史 README/deploy 里可能包含云凭证或敏感资料。不要在文档、回复或提交说明中复制这些值。

## 3. 当前子项目差异

### `s3-manager-18gane-prod`

- 容器名：`s3-manager-18gane-prod`
- 镜像名：`s3-manager-18gane-prod`
- 端口：`8222`
- S3 bucket：`18game-prod`
- AWS region：`ap-northeast-3`
- CloudFront URL：由代码常量配置

### `s3-manager-18gane-test`

- 容器名：`s3-manager-18gane-test`
- 镜像名：`s3-manager-18gane-test`
- 端口：`8333`
- S3 bucket：代码常量配置
- AWS region：`ap-southeast-1`
- CloudFront URL：由代码常量配置

### `s3-manager-xcp-prod`

- 容器名：`s3-manager-xcp-prod`
- 镜像名：`s3-manager-xcp-prod`
- 端口：`8111`
- S3 bucket：代码常量配置
- AWS region：`ap-southeast-1`
- CloudFront URL：由代码常量配置

## 4. 核心代码地图

每个子项目的 `app.py` 基本一致。

关键常量：

- `TG_BOT_TOKEN`
- `TG_CHAT_ID`
- `HANDLERS`
- `BUCKET`
- `CLOUDFRONT_URL`
- `TG_FILE_LIMIT`
- `UPLOAD_CHUNK_SIZE`

关键对象：

- `app = FastAPI()`
- `s3 = boto3.client(...)`
- `delete_progress = {}`

关键函数：

- `human_size(size)`：格式化文件大小。
- `send_telegram_chunked(key, file_path, progress_id)`：删除前把文件分片发送到 Telegram。
- `send_telegram_alert(action, key, size=None, md5=None)`：上传/删除通知。
- `home()`：返回内嵌 HTML 页面。
- `list_files(prefix="")`：列出 S3 当前前缀下的目录和文件。
- `upload(file, prefix="")`：上传文件到 S3。
- `delete(filename)`：删除文件，并触发 Telegram 备份/进度。
- `get_progress(progress_id)`：前端轮询删除备份进度。
- `link(filename)`：生成 CloudFront 访问链接。

## 5. 当前页面行为

页面是 `app.py` 里内嵌的 HTML/CSS/JS。

前端功能：

- 使用 `localStorage` 做简单口令提示。
- 显示 S3 当前目录。
- 支持进入文件夹。
- 支持返回上一级。
- 支持上传文件，显示上传进度。
- 支持删除文件，删除前确认。
- 删除时弹出进度框，轮询 `/progress/{progress_id}`。
- 文件链接通过 `/link/{filename}` 打开。

注意：当前口令机制只是前端提示，不是安全鉴权。真正生产化应改成服务端鉴权。

## 6. 部署方式

进入对应子项目执行：

```bash
cd devops/python/s3-manager-app-apk/s3-manager-18gane-prod
bash deploy.sh
```

脚本会：

1. 停止旧容器。
2. 删除旧容器。
3. 删除旧镜像。
4. 重新构建镜像。
5. 启动新容器。
6. 输出公网访问地址。

每个子项目端口不同，不要混用。

## 7. 依赖

每个子项目 `requirements.txt` 当前类似：

```text
fastapi
uvicorn[standard]
boto3
jinja2
python-multipart
requests
```

`jinja2` 当前可能是历史遗留，因为页面是直接返回 HTML 字符串。

## 8. 重要安全债

这个项目存在明显历史安全债：

- 部分代码或脚本中可能硬编码 Telegram token。
- 部分 `deploy.sh` 中可能硬编码 AWS 凭证。
- `s3信息` 目录可能保存凭证 CSV。
- 前端 localStorage 口令不是真正后端认证。

后续 AI 维护时必须：

- 不复制任何真实 token、key、secret 到回复和文档。
- 不把凭证文件内容读出来贴给用户。
- 优先建议迁移到环境变量或密钥管理。
- 如果修改部署脚本，应把 AWS 凭证改为从外部环境变量传入。
- 如果要提交，确认没有新增凭证明文。

推荐的长期修复方向：

```bash
docker run -d \
  -p "$PORT:$PORT" \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e TG_BOT_TOKEN \
  -e TG_CHAT_ID \
  --restart=always \
  --name "$APP_NAME" \
  "$IMAGE_NAME"
```

并在 `app.py` 中改为：

```python
[敏感内容已脱敏], "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")
```

## 9. 二次开发建议

### 修改 bucket 或 CloudFront

改对应子项目 `app.py` 的：

- `BUCKET`
- `CLOUDFRONT_URL`
- AWS region

不要跨环境误改。

### 修改端口

改对应子项目 `deploy.sh` 的 `PORT`，并确认 Dockerfile/uvicorn 监听端口是否一致。

### 增加服务端鉴权

建议增加中间件或依赖：

- Basic Auth
- 简单 token header
- 登录 cookie/session

不要只依赖前端 prompt。

### 上传后自动通知

看 `send_telegram_alert("上传", ...)` 是否在上传流程中调用。如果要调整通知内容，确保 HTML parse_mode 转义文件名。

### 删除前备份

删除流程涉及：

1. 下载 S3 文件到本地临时文件。
2. 按 Telegram 限制分片发送。
3. 删除 S3 对象。
4. 前端轮询进度。

如果文件较大，注意本地磁盘空间和 Telegram 发送限制。

## 10. 常见坑

### 删除时 Telegram 备份失败

检查：

- Telegram token/chat id 是否可用。
- 文件是否超过分片限制。
- 临时文件是否可写。
- 群是否允许机器人发送文件。

### 上传成功但链接打不开

检查：

- CloudFront 是否指向对应 bucket。
- 文件 key 是否包含空格或中文，URL 编码是否正确。
- S3 对象权限或 CloudFront policy。

### 列目录为空

检查：

- AWS 凭证是否属于对应账号。
- bucket 名是否正确。
- region 是否正确。
- prefix 是否正确。

### 容器启动后页面 404 或端口不通

检查：

```bash
docker ps | grep s3-manager
docker logs --tail 100 <container>
```

## 11. 验证清单

语法：

```bash
python3 -m py_compile devops/python/s3-manager-app-apk/s3-manager-18gane-prod/app.py
python3 -m py_compile devops/python/s3-manager-app-apk/s3-manager-18gane-test/app.py
python3 -m py_compile devops/python/s3-manager-app-apk/s3-manager-xcp-prod/app.py
```

部署脚本语法：

```bash
bash -n devops/python/s3-manager-app-apk/s3-manager-18gane-prod/deploy.sh
bash -n devops/python/s3-manager-app-apk/s3-manager-18gane-test/deploy.sh
bash -n devops/python/s3-manager-app-apk/s3-manager-xcp-prod/deploy.sh
```

运行验证：

- 打开首页。
- 输入口令。
- 列出文件。
- 小文件上传。
- 生成链接。
- 删除测试文件并确认 Telegram 备份。

不要用生产重要文件做删除测试。

## 12. AI 接手流程

1. 先确认用户要改哪个子项目。
2. 只读对应子项目代码，避免误改其他环境。
3. 不读取或展示凭证 CSV 内容。
4. 修改前记录 bucket、region、端口、容器名。
5. 改完跑 `py_compile` 和 `bash -n`。
6. 如需部署，只部署对应子项目。
7. 最终回复说明影响的子项目、端口、容器名和验证结果。
