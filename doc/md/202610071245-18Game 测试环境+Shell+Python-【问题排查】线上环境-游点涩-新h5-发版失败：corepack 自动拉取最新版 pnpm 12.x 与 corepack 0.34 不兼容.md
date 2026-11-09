---
id: "doc-a5c08425363a"
title: "【问题排查】线上环境-游点涩-新h5-发版失败：corepack 自动拉取最新版 pnpm 12.x 与 corepack 0.34 不兼容"
date: "2026-10-07T12:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "自动化", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-07_1245-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E6%96%B0h5%E5%8F%91%E7%89%88%E5%A4%B1%E8%B4%A5-pnpm12%E4%B8%8Ecorepack0.34%E4%B8%8D%E5%85%BC%E5%AE%B9.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-07_1245-【问题排查】线上环境新h5发版失败-pnpm12与corepack0.34不兼容.md"
sourceSha256: "ee9dc1f416b7c1b36184bb7993a21595c77fdb74a2a212b2da0011b7394368d9"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境-游点涩-新h5-发版失败：corepack 自动拉取最新版 pnpm 12.x 与 corepack 0.34 不兼容

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610071245-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83-%E6%B8%B8%E7%82%B9%E6%B6%A9-%E6%96%B0h5-%E5%8F%91%E7%89%88%E5%A4%B1%E8%B4%A5%EF%BC%9Acorepack%20%E8%87%AA%E5%8A%A8%E6%8B%89%E5%8F%96%E6%9C%80%E6%96%B0%E7%89%88%20pnpm%2012.x%20%E4%B8%8E%20corepack%200.34%20%E4%B8%8D%E5%85%BC%E5%AE%B9.md)

> 整理日期：2026-10-07 12:45｜日期依据：文件名日期

- 日期：2026-10-07 12:45（北京）
- 环境：游点涩线上（新 h5 / 16.208.38.88）
- 分类：问题排查 + 构建链路修复（P2）
- 提交：涉及 `18game_devops` 构建模板
- 标签：新h5发版、Docker build、corepack、pnpm、构建缓存、16.208.38.88

## 一、现象

```text
· 「线上环境-游点涩-新h5-发版」连续 3 次失败（48.4s / 51.3s / 38.0s）
· 同一个 git 提交 13f43ca，老的「线上环境-游点涩-h5-发版」两次发布都成功（202.9s / exit 0）
· 即"同一个提交、一个成一个败"，指向构建环境差异而不是代码
```

## 二、关键报错

```text
#10 [build 3/8] RUN ... corepack enable; pnpm -v
#10 4.144 ! Corepack is about to download https://registry.npmjs.org/pnpm/-/pnpm-12.9.1.tgz
#10 4.379 Error: Cannot find module '/root/.cache/node/corepack/v1/pnpm/12.9.1/bin/pnpm.cjs'
ERROR: failed to build: ... did not complete successfully: exit code: 1
```

## 三、根因（已实测复现）

1. **构建脚本把 `corepack enable; pnpm -v` 放在 `COPY package.json` 之前**，
   此时 corepack 读不到 package.json 里的 `"packageManager": "pnpm@10.33.2"` 约束，
   于是去下载**当前最新版** pnpm —— 2026-10-07 时为 `12.9.1`。
2. **node:22.19.0-alpine 自带的 corepack 是 0.34，与 pnpm 12.x 不兼容**。实测两个版本包结构：

   | 版本 | 包内 bin 文件 | 结果 |
   | --- | --- | --- |
   | pnpm@12.9.1（最新） | 无 `bin/pnpm.cjs`（只有 `dist/...`） | corepack 0.34 生成的 shim 找不到入口 → MODULE_NOT_FOUND |
   | pnpm@10.33.2（前端仓库声明） | 有 `bin/pnpm.cjs` | 正常，`pnpm -v` 输出 10.33.2 |

3. **为什么老 h5 还能发成功**：它台机器的 BuildKit 缓存里「工具链那一层」还在，
   构建直接复用缓存层，这条命令根本没重新执行；而新 h5 这台（16.208.38.88）的构建缓存
   在 2026-09-30 因磁盘治理被清理过，必须真跑这条命令 → 隐藏问题被暴露。
   所以本质是「缓存掩盖了缺陷」，不是新老代码差异。

### 顺带排除的怀疑

```text
有人怀疑"打包后提交有污染"（工作区里出现 M nuxt.config.ts / M ecosystem.config.cjs /
?? Dockerfile / env.txt / public/version.*）。经核对：那些是发布脚本自己写入的
（注入 env、版本号文件、按模板生成 Dockerfile），属正常产物；
且失败发生在 build 3/8 阶段（在 COPY 代码之前），与工作区文件内容无关。
```

## 四、修复

文件（两套模板都改，新 h5 走「测试环境」那套）：

- `devops/python/ben-bot/data/scripts/线上环境-游点涩-h5-发版/remote_youdianse_h5_templates.py`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_templates.py`

```diff
+Pnpm版本 = os.environ.get("H5_PNPM_VERSION", "10.33.2").strip() or "10.33.2"

 RUN set -eux; \
     ...
     corepack --version; \
     corepack enable; \
+    corepack prepare pnpm@{Pnpm版本} --activate; \
     pnpm -v
```

- 默认固定为前端仓库 `package.json` 声明的 **10.33.2**，可用环境变量 `H5_PNPM_VERSION` 覆盖，
  以后前端升 pnpm 只需改一处
- 不再依赖「registry 上的最新版」，从根上避免同类问题（corepack 版本升级前一直有效）

## 五、部署

```text
· ben-bot 宿主机脚本目录是挂载进容器的（/opt/telegram/18game_devops/.../data/scripts → /app/data/scripts），
  改宿主机文件即生效，无需重建机器人
· 备份：~/tpl-backup/tpl-prod-20261007-124534.py、tpl-test-20261007-124534.py
· 校验：宿主机两处 + 容器内均包含修复；Python 语法校验通过
```

## 六、验证（真实构建，只构建不发布）

```text
机器/目录：16.208.38.88 上失败现场原目录（未换代码）
        /18game_h5_client/youdianse_prod_h5_main_13f43ca_18game_h5_client_3003
命令：docker build --target build --build-arg BRANCH=main --build-arg SHORT_ID=13f43ca
      --build-arg SYNC_STATIC_TO_S3=0 --build-arg SYNC_STATIC_TO_COS=0
（只把修复行注入该目录 Dockerfile，注入前备份 Dockerfile.bak.<时间戳>；不动线上容器）

结果：exit 0，全流程通过
  · build 3/8（原失败点）：Preparing pnpm@10.33.2 for immediate activation... → pnpm -v = 10.33.2 ✅
  · build 5/8：packageManager=pnpm@10.33.2，pnpm install --no-frozen-lockfile 完成 ✅
  · build 6/8：pnpm build 完成（135.7s），.output 正常生成 ✅
  · build 8/8：按预期输出「跳过 S3 静态资源同步」「跳过腾讯 COS…」（验证时同步开关关掉了）
  · 日志中 2 处 "ERROR" 只是 Nuxt 产物文件名 error-500.mjs，非真实错误
· 验证用镜像已删除；构建机根盘 14G/49G（28%）
```

## 七、回滚

```text
· 模板：还原 ~/tpl-backup/tpl-prod-<ts>.py / tpl-test-<ts>.py 到对应脚本目录
· 失败现场 Dockerfile：目录内 Dockerfile.bak.<时间戳>（下次发布会按模板重新生成）
```

## 八、后续建议

1. **构建工具链要么固定版本，要么固定镜像**：本次教训是「工具链版本随上游漂移」，
   建议后续把 node 镜像 + pnpm 版本一起固化（必要时引入锁文件 `corepack` 版本）
2. **构建缓存清理会暴露隐藏问题**：缓存清理属于常规运维动作，
   今后清理前后建议各跑一次「只构建不发布」的冒烟验证
3. **新老两套 h5 发布链路建议统一**：目前老 h5 依赖缓存侥幸成功，
   本次修复已同时覆盖两套模板
