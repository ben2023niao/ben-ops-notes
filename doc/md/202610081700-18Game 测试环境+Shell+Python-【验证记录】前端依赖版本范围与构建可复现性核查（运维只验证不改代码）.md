---
id: "doc-32cccf573e7e"
title: "【验证记录】前端依赖版本范围与构建可复现性核查（运维只验证不改代码）"
date: "2026-10-08T17:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "监控告警", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-08_1700-%E3%80%90%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91%E5%89%8D%E7%AB%AF%E4%BE%9D%E8%B5%96%E7%89%88%E6%9C%AC%E8%8C%83%E5%9B%B4%E4%B8%8E%E6%9E%84%E5%BB%BA%E5%8F%AF%E5%A4%8D%E7%8E%B0%E6%80%A7%E6%A0%B8%E6%9F%A5.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-08_1700-【验证记录】前端依赖版本范围与构建可复现性核查.md"
sourceSha256: "5e1ad528df4b804021b38e40bfef0bf5b315a61029d75d121ebc322318e73967"
sourceSystem: "project-doc"
---

# 【验证记录】前端依赖版本范围与构建可复现性核查（运维只验证不改代码）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610081700-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E3%80%90%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91%E5%89%8D%E7%AB%AF%E4%BE%9D%E8%B5%96%E7%89%88%E6%9C%AC%E8%8C%83%E5%9B%B4%E4%B8%8E%E6%9E%84%E5%BB%BA%E5%8F%AF%E5%A4%8D%E7%8E%B0%E6%80%A7%E6%A0%B8%E6%9F%A5%EF%BC%88%E8%BF%90%E7%BB%B4%E5%8F%AA%E9%AA%8C%E8%AF%81%E4%B8%8D%E6%94%B9%E4%BB%A3%E7%A0%81%EF%BC%89.md)

> 整理日期：2026-10-08 17:00｜日期依据：文件名日期

- 日期：2026-10-08 17:00（北京）
- 范围：线上 H5 / PC 前端构建（构建机 16.208.38.88 + ben-bot 发布链路）
- 诉求（Ben）：各个组件依赖尽量固定版本、不要写范围；否则同样代码每次打包出来的容器里组件版本可能不一样
- **本次运维未修改任何代码/配置**，只做只读核查与沙箱对照实验（沙箱在 /tmp，仓库与线上构建目录未改动）

## 一、结论

1. **现状确实存在"范围版本"问题**：H5 与 PC 的 `package.json` 共 **46 个依赖使用范围写法**
   （`~` 波浪 44 个 + `^` 脱字符 2 个），没有一个是精确版本。
2. **当前这批构建是可复现的**：仓库提交的 `pnpm-lock.yaml` 与 `package.json` 一致
   （实测 `--frozen-lockfile` 校验 exit=0），同一份输入重新解析，版本与锁文件完全一致。
3. **但风险是真实的，而且是"静默"的**：构建命令写死 `pnpm install --no-frozen-lockfile`，
   一旦锁文件与 `package.json` 不同步（改依赖没重新生成/提交锁、或锁缺失），
   构建会在构建机上**现场重新解析**而不是报错；此时同一提交在不同日期构建，
   产出的组件版本就会不同 —— 漂移幅度见第三节实验 B。
4. 一句话：**现在没漂，但机制上很容易漂，且漂了不会有人知道。**

## 二、证据一：依赖写法（线上构建目录实测）

```text
H5  /18game_h5_client/youdianse_prod_h5_main_13f43ca_.../package.json
    ~ 波浪 44 个 | ^ 脱字符 2 个 | 精确版本 0 个
    例：nuxt@~3.16.2、element-plus@~2.9.9、hls.js@~1.6.3、dayjs@~1.11.13、
        @nuxtjs/i18n@~9.5.3、@nuxt/image@~1.10.0、pinia@~3.0.2、crypto-js@~4.2.0 …
    ^ 例：@vue/typescript-plugin@^3.2.7、terser@^5.46.2

PC  /18game_pc_client/youdianse_prod_pc_dev_cbaacc2_.../package.json
    ~ 波浪 45 个 | ^ 脱字符 2 个

含义：~3.16.2 = ">=3.16.2 且 <3.17.0"（允许补丁位自动升级）；
      ^3.2.7  = ">=3.2.7 且 <4.0.0"（允许次版本自动升级）
```

## 三、证据二：对照实验（同一份代码，两种前提）

实验环境：构建机 16.208.38.88，沙箱目录 `/tmp/h5lockexp`、`/tmp/h5exp2`，
容器 `node:22.19.0-alpine` + 固定 pnpm 10.33.2，
命令 `pnpm install --lockfile-only --no-frozen-lockfile`（只解析、不装包、不动仓库）。

### 实验 A：带上仓库提交的 lock → 结果完全一致（说明锁有效）

```text
原始 lock 16230 行 → 重新解析后仍 16230 行；抽样 9 个包逐一对齐：
nuxt 3.16.2 / element-plus 2.9.11 / hls.js 1.6.5 / dayjs 1.11.13 /
ofetch 1.4.1 / dexie 4.0.11 / pinia 3.0.3 / artplayer 5.2.3  → 全部“相同”
```

### 实验 B：不带 lock（模拟"锁缺失/与 package.json 不同步"）→ 版本漂移

| 依赖 | 声明范围 | 提交的 lock | 今天无 lock 解析 | 差异 |
| --- | --- | --- | --- | --- |
| hls.js | ~1.6.3 | 1.6.5 | **1.6.19** | 补丁位 +14 |
| dayjs | ~1.11.13 | 1.11.13 | **1.11.23** | 补丁位 +10 |
| pinia | ~3.0.2 | 3.0.3 | **3.0.4** | 补丁位 +1 |
| element-plus | ~2.9.9 | 2.9.11 | 2.9.11 | 相同 |
| nuxt | ~3.16.2 | 3.16.2 | 3.16.2 | 相同 |
| ofetch | ~1.4.1 | 1.4.1 | 1.4.1 | 相同 |
| dexie | ~4.0.11 | 4.0.11 | 4.0.11 | 相同 |

即：**同一份 package.json，只要锁不同步，今天构建就会装到
hls.js 1.6.19 / dayjs 1.11.23 / pinia 3.0.4** —— 这就是"同样代码、不同时间打包，
容器里组件版本不一样"的来源。

## 四、证据三：构建命令不校验锁（关键放大器）

```text
devops/python/ben-bot/data/scripts/线上环境-游点涩-h5-发版/remote_youdianse_h5_config.py:37
  Pnpm安装参数 = os.getenv("H5_PNPM_INSTALL_FLAGS", "--no-frozen-lockfile") …
devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_config.py:38   同上
devops/python/ben-bot/data/scripts/线上环境-游点涩-h5-发版/server_config.py:84              同上
→ 生成的 Dockerfile 里落地为： pnpm install --no-frozen-lockfile
```

`--no-frozen-lockfile` 的语义是"锁与 package.json 不一致时自动更新锁（而不是报错）"，
所以实验 B 的漂移会在构建时静默发生，没有任何告警。

## 五、证据四：当前锁是新的（所以今天是可复现的）

```text
对两个提交分别做 pnpm install --lockfile-only --frozen-lockfile 校验：
  13f43ca → exit 0     2108ac9 → exit 0
说明这两个提交的 pnpm-lock.yaml 与 package.json 是一致的。
另：两个提交的依赖声明指纹相同（c9ec9607245c），lock 解析版本也一致
（hls.js 1.6.5 / dayjs 1.11.13 / element-plus 2.9.11 / ofetch 1.4.1 / dexie 4.0.11 / pinia 3.0.3）。
```

## 六、给前端的优化建议（代码由前端改，运维配合）

1. **依赖写精确版本**（Ben 的要求）：`~3.16.2`、`^3.2.7` 这类改成 `3.16.2`、`3.2.7`。
   即使锁文件缺失/过期，构建也只能装到指定版本，从根上杜绝漂移。
2. **若保留范围版本，至少要"锁同步 + 构建强校验"**：
   `pnpm-lock.yaml` 必须与 `package.json` 一起提交；发布构建参数由
   `--no-frozen-lockfile` 换成 `--frozen-lockfile`（不一致时直接失败，而不是静默重解析）
   —— 这条在运维发布脚本里，前端确认后我们配合改。
3. **加 CI/提交前校验**：`pnpm install --frozen-lockfile`，避免"改了 package.json 忘记更新锁"。
4. （可选）构建时把 `pnpm list --depth 0` 输出到构建日志/产物，便于事后比对
   "这次构建到底装了哪些版本"。

## 七、复现命令（供前端自查）

```bash
# 1) 统计范围版本
python3 - <<'PY'
import json,collections
p=json.load(open("package.json")); c=collections.Counter()
for s in ("dependencies","devDependencies"):
    for k,v in (p.get(s) or {}).items():
        c["~" if v.startswith("~") else "^" if v.startswith("^") else "exact/other"] += 1
print(c)
PY

# 2) 校验锁与 package.json 是否一致（不一致会报错）
pnpm install --lockfile-only --frozen-lockfile

# 3) 对比"有锁 / 无锁"解析出的版本差异
mkdir -p /tmp/exp && cp package.json /tmp/exp/ && cd /tmp/exp \
  && pnpm install --lockfile-only --no-frozen-lockfile \
  && grep -E '^  (hls\.js|dayjs|pinia)@' pnpm-lock.yaml | head
```

## 八、本次操作边界

- 未修改任何代码、未修改任何构建参数、未重启任何服务；
- 仅在构建机 `/tmp` 下创建沙箱目录做依赖解析对照，仓库与线上构建目录 `/18game_h5_client` 保持原样；
- 沙箱目录确认后可清理：`/tmp/h5lockexp`、`/tmp/h5exp2`、`/tmp/frz-13f43ca`、`/tmp/frz-2108ac9`。
