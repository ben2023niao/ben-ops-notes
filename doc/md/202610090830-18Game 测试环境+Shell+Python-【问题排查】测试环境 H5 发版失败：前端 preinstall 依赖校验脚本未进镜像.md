---
id: "doc-2b379e5fa13f"
title: "【问题排查】测试环境 H5 发版失败：前端 preinstall 依赖校验脚本未进镜像"
date: "2026-10-09T08:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-09_0830-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83h5%E5%8F%91%E7%89%88%E5%A4%B1%E8%B4%A5-preinstall%E4%BE%9D%E8%B5%96%E6%A0%A1%E9%AA%8C%E8%84%9A%E6%9C%AC%E6%9C%AA%E8%BF%9B%E9%95%9C%E5%83%8F.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-09_0830-【问题排查】测试环境h5发版失败-preinstall依赖校验脚本未进镜像.md"
sourceSha256: "4f5dfa65075720e44feb481258f3314a1420180b6877b3eae51b6eef02a743bc"
sourceSystem: "project-doc"
---

# 【问题排查】测试环境 H5 发版失败：前端 preinstall 依赖校验脚本未进镜像

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610090830-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20H5%20%E5%8F%91%E7%89%88%E5%A4%B1%E8%B4%A5%EF%BC%9A%E5%89%8D%E7%AB%AF%20preinstall%20%E4%BE%9D%E8%B5%96%E6%A0%A1%E9%AA%8C%E8%84%9A%E6%9C%AC%E6%9C%AA%E8%BF%9B%E9%95%9C%E5%83%8F.md)

> 整理日期：2026-10-09 08:30｜日期依据：文件名日期

- 日期：2026-10-09 08:30（北京）
- 环境：测试环境 H5（构建机 15.152.247.196）+ ben-bot 发布链路
- 分类：问题排查（构建镜像缺文件 / 与前端新增 preinstall 钩子冲突）
- 触发：`测试环境-游点涩-h5-发版失败，退出码 1，耗时 63.5s`（前端 方林 反馈）
- 关联：`2026-10-07_1245`（固定 pnpm 版本）、`2026-10-08_1700`（依赖版本范围核查——本次前端就是按那份建议做的改造）

## 一、现象

```text
· 10-08 16:36 提交 c1efd22、10-09 08:05 提交 68332c4 两次测试 H5 发布均失败（exit 1）
· 失败发生在 Docker build 的 pnpm install 阶段（不是编译阶段）：
    #11 > youdianse-h5@ preinstall /app
    #11 > node scripts/check-dependency-policy.mjs
    #11 Error: Cannot find module '/app/scripts/check-dependency-policy.mjs'  (MODULE_NOT_FOUND)
    #11  ELIFECYCLE  Command failed with exit code 1.
```

## 二、根因

1. 前端按运维 10-08 的建议做了依赖治理，并在 `package.json` 里加了安装期钩子：

```json
"preinstall":  "node scripts/check-dependency-policy.mjs",
"check:deps":  "node scripts/check-dependency-policy.mjs && pnpm install --frozen-lockfile",
"build:ci":    "pnpm run check:deps && pnpm list --depth 0 && pnpm run build"
```

2. 而我们的 Dockerfile 为了复用 pnpm 安装层缓存，在 install 前**只拷贝了两个文件**：

```dockerfile
COPY package.json pnpm-lock.yaml ./
RUN ... pnpm install --no-frozen-lockfile     # ← 此时镜像里没有 scripts/ 目录
COPY . .                                      # ← 源码在这之后才进来（太晚）
```

3. `preinstall` 由 pnpm 在安装前执行，此时 `scripts/` 还不存在 → 模块找不到 → 安装失败 → 构建失败。

**结论：不是前端代码问题，是我们的构建镜像没有把"安装期钩子需要用的仓库文件"带进去。**

## 三、修复（本次已改、已部署）

两套模板都把源码拷贝提前到 install 之前（`.dockerignore` 已排除 `.git`/`node_modules`/`.output` 等）：

```diff
-COPY package.json pnpm-lock.yaml ./
+# 依赖安装期的钩子（preinstall/postinstall/prepare）需要仓库内的脚本文件，故先 COPY 全量源码
+COPY . .
 RUN set -eux; ... pnpm install {Pnpm安装参数}
-
-COPY . .
```

文件：

- `devops/python/ben-bot/data/scripts/线上环境-游点涩-h5-发版/remote_youdianse_h5_templates.py`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_templates.py`

部署：ben-bot 宿主机脚本目录是挂载进容器的，替换即生效；
备份 `~/tpl-backup/tpl-prod-20261009-082928.py`、`tpl-test-20261009-082928.py`；
校验：两处模板 `COPY . .` 各 1 次、Python 语法 OK。

代价说明：源码先于 install 拷贝后，pnpm 安装层不再跨提交复用，每次构建多约 30 秒安装时间
（实测 install 34.3s），换来的是"任何安装期钩子都不缺文件"。

## 四、验证（真实构建，只构建不发布）

```text
机器/目录：15.152.247.196 的失败现场 /www/wwwroot/18game_h5_client/youdianse_test_68332c4_18game_h5_client_3003
        （未换代码；只把该目录 Dockerfile 按新模板调整，原文件备份 Dockerfile.bak.<时间戳>）
命令：docker build --progress=plain --build-arg BRANCH=test --build-arg SHORT_ID=68332c4
      --build-arg SYNC_STATIC_TO_S3=0 …（验证时关闭静态资源同步，不产生任何发布副作用）

结果：exit 0，全流程通过
  #11 . preinstall$ node scripts/check-dependency-policy.mjs
  #11 . preinstall: [依赖校验通过] pnpm@10.33.2，直接依赖均为精确版本。   ← 前端策略校验通过
  #11 Done in 34.3s using pnpm v10.33.2                                ← 依赖安装完成
  #12 pnpm build 完成、#18 镜像导出成功
· 验证用镜像已删除，构建机无残留
```

## 五、影响面（重要）

线上 H5 与测试 H5 **是同一个前端仓库**（`youdianse-h5`，分支不同），
同样的 `preinstall` 在线上构建时也会触发 —— 也就是说**不修的话线上 H5 下次发布同样会失败**。
本次两套模板一起修，测试与线上都已覆盖。

## 六、前端侧状态（本次顺带核实）

```text
· packageManager = pnpm@10.33.2（精确）
· dependencies + devDependencies 共 46 个，全部为精确版本（0 个 ~ / ^）—— 10-08 建议已落实
· scripts 新增 check-dependency-policy.mjs / check:deps / build:ci，
  其中 build:ci = 依赖策略校验 + pnpm install --frozen-lockfile + pnpm list --depth 0 + build
```

## 七、建议（需 Ben/前端确认，属发布配置项）

发布构建命令目前是 `pnpm build:prod`，而前端 `package.json` 没有 `build:prod`，
运行时**自动回退成 `pnpm build`**（日志里可见「package.json 缺少 scripts.build:prod，自动改用: pnpm build」）。
也就是说：发布过程中**没有**跑前端的 `check:deps`（含 `--frozen-lockfile`）与依赖清单打印。

若希望发布也强约束依赖（与 10-08 的建议一致），把构建命令改成 `pnpm run build:ci` 即可：

```text
测试：H5_BUILD_COMMAND / YOUDIANSE_H5_TEST_BUILD_COMMAND=pnpm run build:ci
线上：YOUDIANSE_H5_PROD_BUILD_COMMAND=pnpm run build:ci
```

安全性：脚本名解析是通用的（`获取实际构建命令`），若某个提交/仓库没有 `build:ci`，
会自动回退到 `pnpm build`，不会因为这条配置把老提交卡死。

## 八、回滚

```text
· 模板：还原 ~/tpl-backup/tpl-prod-20261009-082928.py / tpl-test-20261009-082928.py 到对应脚本目录
· 失败现场 Dockerfile：目录内 Dockerfile.bak.<时间戳>（下次发布会按模板重新生成）
```

## 九、操作边界

- 仅修改构建模板（两套），未改前端代码、未改业务服务、未重启容器；
- 测试机验证只做 `docker build`（关闭 S3/COS 同步），未执行发布动作；
- 验证前备份现场 Dockerfile，验证后删除验证镜像。
