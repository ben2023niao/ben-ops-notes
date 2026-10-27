---
id: "doc-d9134f9fdb0f"
title: "【优化+文档】发布页打包后同步香港 configs 与新 Mac sshpass 修复记录"
date: "2026-10-28T15:42:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Docker", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-28-1542-%E3%80%90%E4%BC%98%E5%8C%96%2B%E6%96%87%E6%A1%A3%E3%80%91%E5%8F%91%E5%B8%83%E9%A1%B5%E6%89%93%E5%8C%85%E5%90%8E%E5%90%8C%E6%AD%A5%E9%A6%99%E6%B8%AFconfigs%E4%B8%8E%E6%96%B0Macsshpass%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-28-1542-【优化+文档】发布页打包后同步香港configs与新Macsshpass修复记录.md"
sourceSha256: "f96841f7304b3918585298ce1ce3e40dfc94ebb9a26ce67b2b8e3e6a43b6c736"
sourceSystem: "project-doc"
---

# 【优化+文档】发布页打包后同步香港 configs 与新 Mac sshpass 修复记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-28-1542-【优化+文档】发布页打包后同步香港configs与新Macsshpass修复记录.md`

> 整理日期：2026-10-28 15:42｜日期依据：文件名日期

更新时间：2026-10-28 15:52（Asia/Manila）

状态：发布页与文档改造完成并验证；实际全厂家镜像构建仍等待开发推送更新后的 `share.so`。

## 一、需求

1. “03 拉代码（ben 分支）”步骤在拉取后输出 `share.so` MD5。
2. 老 Mac 没有 `sshpass`，需要安装并保证发布页命令可执行。
3. 每次镜像打包成功后，将：

   ```bash
   /data/server-runtime/conf/configs-*.py
   ```

   同步到：

   ```bash
   /data/server-runtime-hk/conf/
   ```

4. 按标准流程先写汇总文档并发群，再提交本地 Git，最后回报提交结果。

## 二、开始前基线

```text
本地 ops master：b4042b02
本地 origin/master 缓存：8fcefd60
远端 master：8fcefd60
远端 ben：f8e49c4b（2026-10-28 15:25，“开放新游戏”）
03 HEAD：f8e49c4b
03 share.so：fc5a5f137db8de5cc91af052499215c7
运行目录 share.so：fc5a5f137db8de5cc91af052499215c7
```

本地工作区开始前只有本轮预期修改：`workbench/CURRENT_TASK.md` 和
`运维发布页.html`。03 上有 7 个线上域名配置修改及一个历史备份目录，已在拉取前暂存并在快进后逐字节恢复。

## 三、发布页改动

### 3.1 拉代码与 MD5

- 使用 `git pull --ff-only`，避免隐式合并。
- 拉取后显示最新提交和 `share.so` MD5。
- 确认条件改为“HEAD 正确，share.so MD5 已核对”。
- 增加本地域名配置挡拉取时的备份与差异核对提示。

### 3.2 新 Mac 发布环境

- 源码编译安装 `sshpass 1.10` 到 `/Users/ben/.local/bin/sshpass`。
- `~/.local/bin` 已写入 `~/.zshrc`。
- 发布页 9 条 SSH 命令和 3 条 rsync 命令统一增加：

  ```text
  StrictHostKeyChecking=accept-new
  ConnectTimeout=15
  ```

- 03 首次连接已验证可记录主机密钥，后续密钥变化仍会被拒绝。

### 3.3 打包后同步香港配置

普通模式和精简模式的打包命令都已按以下顺序执行：

```text
8 个厂家镜像构建
→ cp /data/server-runtime/conf/configs-*.py /data/server-runtime-hk/conf/
→ 对每个 configs-*.py 执行源/目标 cmp
→ 输出 CONFIG_SYNC=OK
→ 输出两目录 MD5
```

打包命令启用 `set -e`；精简模式增加 `set -o pipefail`。任一镜像构建、复制或逐文件比对失败都会中止，不再把失败状态当作打包完成。

检查步骤也再次执行逐文件 `cmp`，自动检查输出必须同时满足：

```text
8/8 镜像 tag 正确
share.so MD5 与开发值一致
CONFIG_SYNC=OK
g759 单域名配置正确
version.json 含 config_version
```

## 四、验证

```text
HTML 解析：OK（48,542 bytes）
Python compileall：通过
servers.json：通过
git diff --check：通过
sshpass：1.10，命令可在新写入的 zsh PATH 中找到
03 原拉代码命令：通过；Already up to date；HEAD f8e49c4b
Chrome 实际渲染：通过
自动检查样例：镜像 8/8、MD5、香港 configs、g759 域名、version.json 全部通过
```

## 五、未完成与阻塞

开发反馈 `share` 有更新，但远端 `ben` 中 `share.so` 最后变更仍为：

```text
90512a47 2026-10-14 16:34:31 +08:00 修复字段类型问题
```

拉取后 MD5 仍与运行目录相同，说明最新远端没有新二进制。由于 Dockerfile 会把
`share.so` 打入全部镜像，本次未执行 8 个厂家构建，避免生成带旧 share 的镜像。

下一步：开发推送新 `share.so` 到 `ben` 后重新拉取，MD5 变化并核对通过，再执行全量打包。

## 六、通知

```text
任务开始：message_id=541
share.so 未变化、暂停打包：message_id=542
新 Mac sshpass/首连策略修复：message_id=544
```

## 七、修改文件

```text
运维发布页.html
workbench/CURRENT_TASK.md
workbench/CURRENT_STATE.md
workbench/ACTIVE_TASKS.md
docs/history/2026-10-28-1542-【优化+文档】发布页打包后同步香港configs与新Macsshpass修复记录.md
```
