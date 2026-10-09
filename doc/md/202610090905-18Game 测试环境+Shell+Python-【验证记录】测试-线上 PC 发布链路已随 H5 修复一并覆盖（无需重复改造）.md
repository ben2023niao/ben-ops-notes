---
id: "doc-59221326eb3f"
title: "【验证记录】测试/线上 PC 发布链路已随 H5 修复一并覆盖（无需重复改造）"
date: "2026-10-09T09:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-09_0905-%E3%80%90%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91PC%E5%8F%91%E5%B8%83%E9%93%BE%E8%B7%AF%E4%B8%8EH5%E5%85%B1%E7%94%A8%E5%90%8C%E4%B8%80%E5%A5%97%E6%9E%84%E5%BB%BA%E6%A8%A1%E6%9D%BF%EF%BC%88%E6%97%A0%E9%9C%80%E9%87%8D%E5%A4%8D%E6%94%B9%E9%80%A0%EF%BC%89.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-09_0905-【验证记录】PC发布链路与H5共用同一套构建模板（无需重复改造）.md"
sourceSha256: "bef38502cb0e054dfbc1e612d859ddc62702f9c3057b5a09ef8ad8533a32f345"
sourceSystem: "project-doc"
---

# 【验证记录】测试/线上 PC 发布链路已随 H5 修复一并覆盖（无需重复改造）

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-09_0905-【验证记录】PC发布链路与H5共用同一套构建模板（无需重复改造）.md`

> 整理日期：2026-10-09 09:05｜日期依据：文件名日期

- 日期：2026-10-09 09:05（北京）
- 背景：Ben 要求「同样方式改造一下测试、线上 PC 发布」（即把 10-09 08:29 对 H5 的
  「先 COPY 全量源码再 pnpm install」修复也应用到 PC）
- 结论：**PC（测试 + 线上）复用 H5 的同一套发布引擎与 Dockerfile 模板，已随 H5 修复自动覆盖，无需再改脚本**
- 关联：`2026-10-09_0830`（测试 H5 发版失败：preinstall 脚本未进镜像）

## 一、结论与依据

PC 的发布入口只做「换配置 + 转发」，真正的构建引擎与 Dockerfile 模板与 H5 是同一份文件：

```text
线上环境-游点涩-新pc-发版/youdianse_prod_18game_pc_client.py
   └─ os.execve → 测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py
        ├─ H5_RELEASE_DIR = ../测试环境-游点涩-h5-发版
        ├─ 读该目录的 server_config.py 作为配置源
        └─ 执行该目录的 youdianse_test_18game_h5_client.py（共用前端发布引擎）
             └─ remote_youdianse_h5_templates.py（Dockerfile 模板，本次修复的文件）
```

即：**改一次 H5 模板 = 同时改到测试 PC、线上 PC、测试 H5、线上 H5**。
本次 08:29 已经改过两套模板（线上环境-游点涩-h5-发版 / 测试环境-游点涩-h5-发版），所以 PC 无需再动。

## 二、验证证据

### 2.1 测试 PC：真实发布已成功（含新的依赖校验）

```text
2026-10-09 08:43:26  #10 [build 4/7] COPY . .                          ← 新模板生效
2026-10-09 08:43:53  #11 youdianse-pc@ preinstall /app
2026-10-09 08:43:53  #11 [依赖校验通过] pnpm@10.33.2，直接依赖均为精确版本。  ← 前端策略校验通过
2026-10-09 08:47:59  游点涩pc 测试环境-游点涩-pc-发版 镜像打包脚本运行结束: 成功
```

（该次发布发生在模板修复部署 08:29 之后，属"修复后真实验证"，非人工构造。）

### 2.2 线上 PC：用新模板做回归构建，通过

```text
机器/目录：16.208.38.88 /18game_pc_client/youdianse_prod_pc_main_7ebc1e3_18game_pc_client_3004
        （现场目录原样，只把 Dockerfile 按新模板调整，原文件备份 Dockerfile.bak.20261009-085019）
命令：docker build --progress=plain --build-arg BRANCH=main --build-arg SHORT_ID=7ebc1e3
      --build-arg SYNC_STATIC_TO_S3=0 --build-arg SYNC_STATIC_TO_COS=0 …（关闭静态同步，不发布）
结果：exit 0
  #11 Done in 14.8s using pnpm v10.33.2   ← 依赖安装正常
  #12 DONE 155.2s                          ← 前端构建完成
  #18 DONE 5.1s                            ← 镜像导出完成
· 验证镜像已删除，构建机无残留
```

说明：线上 PC 当前分支**还没有**前端的 preinstall 策略脚本（现场仍是 `npx only-allow pnpm`），
所以本次线上是"回归验证"（证明新模板对 PC 无副作用）；
等前端把依赖治理合并到线上分支后，同一套模板会自动带上 `COPY . .`，不会再出现 H5 那种失败。

## 三、两侧代码现状（核对结果）

| 项目 | 分支代码状态 | 说明 |
| --- | --- | --- |
| 测试 H5 | 已合并（精确版本 + preinstall） | 08:43 发布成功 |
| 测试 PC | 已合并：`packageManager=pnpm@10.33.2`、46 个依赖**全部精确**、`preinstall/check:deps/build:ci` 齐全 | 08:47 发布成功 |
| 线上 H5 | 已合并 | 修复已部署，待下次发布验证 |
| 线上 PC | **未合并**（现场仍是 `preinstall="npx only-allow pnpm"`） | 等前端合并；模板已就绪 |

## 四、给前端的对齐点（与 H5 相同）

1. 线上 PC 合并依赖治理后，发布命令是否切换为 `pnpm run build:ci`（含 `check:deps` +
   `pnpm install --frozen-lockfile` + `pnpm list --depth 0`），由 Ben/前端确认；
   当前 PC 配置的构建命令是 `pnpm build:prod`（PC 仓库没有该脚本 → 运行时自动回退 `pnpm build`）。
   安全前提：脚本名解析通用，缺 `build:ci` 的仓库/老提交会自动回退，不会卡死老发布。
2. 合并后建议先发一次测试 PC（失败也能立刻看到依赖校验原因），再发线上 PC。

## 五、操作边界

- **本次未修改任何代码**（PC 复用 H5 模板，无需改造）；
- 仅做只读核查 + 线上 PC 现场一次"只构建不发布"的回归构建（同步开关关闭）；
- 验证前备份现场 Dockerfile，验证后删除验证镜像。

## 六、回滚

```text
· 现场 Dockerfile：/18game_pc_client/youdianse_prod_pc_main_7ebc1e3_18game_pc_client_3004/Dockerfile.bak.20261009-085019
  （下次发布也会按模板自动重新生成，不影响后续）
· 模板层如需回滚：~/tpl-backup/tpl-{prod,test}-20261009-082928.py（ben-bot 宿主机）
