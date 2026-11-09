---
id: "doc-b9637f02d464"
title: "香港静态域名上 CDN 操作手册（运维 + 后端手动）"
date: "2026-09-24T12:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Shell", "Python", "Docker", "自动化", "CDN", "DNS", "故障排查"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-09-24-1245-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E9%A6%99%E6%B8%AF%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8D%E4%B8%8ACDN%E6%93%8D%E4%BD%9C%E6%89%8B%E5%86%8C%EF%BC%88%E8%BF%90%E7%BB%B4%2B%E5%90%8E%E7%AB%AF%E6%89%8B%E5%8A%A8%EF%BC%89.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-09-24-1245-【运维记录】香港静态域名上CDN操作手册（运维+后端手动）.md"
sourceSha256: "9d9b84381c519fb42e23b2ed660b0b1ae6c6bad56e55e9ed7a83555fbe0d8744"
sourceSystem: "project-doc"
---

# 香港静态域名上 CDN 操作手册（运维 + 后端手动）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609241245-%E9%A6%99%E6%B8%AF%20CN%2BShell%2BPython-%E9%A6%99%E6%B8%AF%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8D%E4%B8%8A%20CDN%20%E6%93%8D%E4%BD%9C%E6%89%8B%E5%86%8C%EF%BC%88%E8%BF%90%E7%BB%B4%20%2B%20%E5%90%8E%E7%AB%AF%E6%89%8B%E5%8A%A8%EF%BC%89.md)

> 整理日期：2026-09-24 12:45｜日期依据：文件名日期

目标：把 70 个静态域名从「灰云 → CloudFront → 香港 S3」切成「橙云 → Cloudflare Worker → 香港 S3（带边缘缓存）」，与巴西口径一致。

范围：只动 **14 个静态前缀 × 5 个 zone**；`*-games`、`api.hkcloudplay0X.com`、`hkplaycore.com` 一律不动。

本文是**给人照着做的手册**，本轮没有执行任何生产变更。

---

## 一页速查

| 谁 | 做什么 | 生效时机 |
| --- | --- | --- |
| 运维 | ① 部署 Worker ② 建 Worker 路由 ③ 建 Cache Rules | 都不影响现网（灰云不走 Cloudflare） |
| 运维 | ④ 静态 DNS 记录改「已代理」 | **这一步才生效** |
| 后端 | ⑤ platform-api `static_hosts` 改成 CF 域名 | 玩家开始走 Worker |
| 运维 | ⑥ 发布后清缓存（改 `CACHE_SALT` 重部署） | — |

回滚顺序相反：后端改回 S3 → DNS 改回灰云。**先做①~③再做④**，任何一步都可回滚。

---

## A. 运维操作（Cloudflare 侧）

在**香港入口机**（192.0.2.14）执行，工作目录是 cn 仓库。

前置：

```bash
export CF_ACCOUNT_ID=eaf1a5f4eb53c8cd384ce9088181b97c   # 香港与巴西同一个 Cloudflare 账号
T=/root/.config/cloudflare/workers-token                # 需要 Workers Scripts:Edit、Workers Routes:Edit、Cache Rules:Edit
Z=hkcloudplay01.com,hkcloudplay02.com,hkcloudplay03.com,hkcloudplay04.com,hkcloudplay05.com
```

### A1. 部署 Worker（不影响现网）

⚠️ `--account` / `--token-file` / `--zones` 是**顶层参数，必须写在子命令前面**（写成 `deploy --account ...` 会报 unrecognized arguments）。

```bash
python3 docker/deploy/hongkong/deploy_static_worker.py \
    --account "$CF_ACCOUNT_ID" --token-file $T --zones "$Z" \
    deploy --backup-dir /root/bizops-hk-worker-backup/$(date +%Y%m%d-%H%M)
```

期望输出：`deploy: http=200 success=True` → `deployed ok`。

说明：只上传脚本，没有路由就不会对任何域名生效；旧脚本会自动备份到 `--backup-dir`。

### A2. 建 Worker 路由（不影响现网）

```bash
python3 docker/deploy/hongkong/deploy_static_worker.py --token-file $T --zones "$Z" routes --dry-run   # 先看要建哪些
python3 docker/deploy/hongkong/deploy_static_worker.py --token-file $T --zones "$Z" routes --apply      # 建 14 x 5 = 70 条
```

期望输出：每条 `create route <域名>/*: success=True`。

### A3. 建 Cache Rules（面板操作，不影响现网）

对 `hkcloudplay01.com` ~ `hkcloudplay05.com` **每个 zone 各建 1 条**：

```text
位置：Cloudflare 面板 -> 该 zone -> 缓存 -> Cache Rules -> 创建规则
名称：statics
匹配：自定义表达式（把下面表达式里的 02 换成对应 zone 编号）
操作：符合缓存条件（Eligible）+ 边缘 TTL：覆写源站 604800 秒
状态：活动
```

表达式（每个 zone 一条，`02` 换成 `01`~`05`）：

```text
(ends_with(http.host, "-static.hkcloudplay02.com"))
or (ends_with(http.host, "-static1.hkcloudplay02.com"))
or (ends_with(http.host, "-static2.hkcloudplay02.com"))
```

注意：香港 vendor_b 对外是 `vendor_b-static`/`vendor_b-static1`/`vendor_b-static2`，所以必须像上面这样写三段；**不要照抄巴西的 `starts_with("vendor_a-statics...")`**。

### A4. 切 DNS（这一步才生效，建议先灰度 1 个域名）

灰度（面板操作）：

```text
位置：面板 -> 该 zone -> DNS -> pg-static.hkcloudplay02.com
操作：编辑 -> 代理状态改为「已代理」-> 保存
```

验证灰度域名（在任意能上网的机器执行）：

```bash
# 1) 第一次请求：期望 200，并且带 x-bizops-worker 头
curl -s -D - -o /dev/null "https://pg-static.hkcloudplay02.com/85/c445ebb91e.cadb1.json" | head -20

# 2) 第二次请求：期望 cf-cache-status: HIT
curl -s -D - -o /dev/null "https://pg-static.hkcloudplay02.com/85/c445ebb91e.cadb1.json" | grep -i cf-cache-status

# 3) 目录请求：期望 302 到 index.html
curl -s -D - -o /dev/null "https://pg6-static.hkcloudplay02.com/1834850/" | head -3

# 4) OPTIONS 预检：期望 204
curl -s -o /dev/null -w '%{http_code}\n' -X OPTIONS \
    -H 'Origin: https://pg-static.hkcloudplay02.com' \
    -H 'Access-Control-Request-Method: GET' \
    "https://pg-static.hkcloudplay02.com/85/c445ebb91e.cadb1.json"
```

灰度通过后全量切换（70 条一起）：

```bash
python3 docker/deploy/hongkong/deploy_static_worker.py dns-proxy --enable --dry-run   # 先看计划
python3 docker/deploy/hongkong/deploy_static_worker.py dns-proxy --enable --yes        # 执行，自动备份到 /root/bizops-hk-worker-backup/
```

### A5. 全量验证

```bash
python3 docker/deploy/hongkong/deploy_static_worker.py verify
```

期望：`worker verify summary passed=70 failed=0`（每个域名 200 + CORS 正确 + Worker 标记 + 缓存命中）。

---

## B. 后端手动操作（platform-api）

不做这一步，玩家不会走 Worker（现网 `static_hosts` 直指 S3 公开地址）。

### B1. 改配置

把 platform-api 的 domains 配置里静态前缀的 `static_hosts` 从 S3 地址改成 CF 域名：

```text
改前：https://bizops-h5-hk-517506432530.s3.ap-east-1.amazonaws.com/pg-static
改后：https://pg-static.hkcloudplay02.com
```

对应关系（每个前缀换成同名域名即可）：

```text
pg-static / pg3-static / pg4-static / pg5-static / pg6-static / pg7-static
pp-static / ppk-static / vendor_d-static / vendor_c-static / g759-static
vendor_b-static / vendor_b-static1 / vendor_b-static2
```

建议顺序：先只配 **1 个 zone** 的域名（例如 `...hkcloudplay02.com`）验证，通过后再补齐到 5 个 zone。

配置来源：cn 仓库 `docker/conf/domains/*.json`（复制到 `platform-api/conf/domains/`，或让 `GAME_DOMAINS_PATH` 指向该目录）。

### B2. 生效与验证

按后端既有流程应用配置（重启或热加载），然后验证：

```bash
# 静态资源请求头应出现 Worker 标记与缓存状态
curl -s -D - -o /dev/null "https://<后端下发的静态域名>/<任一真实资源路径>" | \
    grep -Ei 'HTTP|x-bizops-worker|cf-cache-status|cache-control'
```

期望：`x-bizops-worker: hk-static-proxy`，第二次请求 `cf-cache-status: HIT`。

### B3. 后端回滚

把 `static_hosts` 改回原 S3 地址并重新应用配置即可，不需要动 Cloudflare。

---

## C. 发布后清缓存（运维）

```text
1) Worker/边缘缓存：改 docker/deploy/hongkong/hk_static_worker.js 里的 CACHE_SALT，重新执行 A1 部署。
   （Cache API 按 zone 隔离，Cloudflare 面板「清除缓存」清不掉它。）
2) 浏览器缓存：改完 salt 后，配合静态域名 URL 版本变化自然失效。
3) 回滚期：如需回到 CloudFront，先执行回滚，再用 CloudFront invalidation 兜底。
```

发布后建议预热（巴西是逐 20 zone，香港是 5 zone）：把变更文件在 5 个 zone 各请求一次，确认 `cf-cache-status: HIT`。

---

## D. 回滚（3 步，任一步独立可用）

```bash
# 1) DNS 改回灰云（立即回到 CloudFront -> S3，原有链路完全不变）
python3 docker/deploy/hongkong/deploy_static_worker.py dns-proxy --disable --yes

# 2) 后端 static_hosts 改回 S3 地址（B3）

# 3) 可选：删 Worker 路由 / 停用 Cache Rules（面板操作）
```

---

## E. 常用命令速查（香港入口机）

```bash
cd <cn 仓库目录>
W="python3 docker/deploy/hongkong/deploy_static_worker.py"

A=eaf1a5f4eb53c8cd384ce9088181b97c
T=/root/.config/cloudflare/workers-token
Z=<目标 zone，逗号分隔，如 hkcloudplay06.com,hkcloudplay07.com>

# 注意：--account / --token-file / --zones 必须写在子命令前面
$W --zones "$Z" plan                                            # 打印前缀与路由计划（不联网）
$W --account $A --token-file $T --zones "$Z" deploy             # 部署 Worker
$W --token-file $T --zones "$Z" routes --dry-run                # 查看要建的路由
$W --token-file $T --zones "$Z" routes --apply                  # 建路由
$W --token-file $T --zones "$Z" dns-proxy --enable --dry-run    # 查看要改的 DNS
$W --token-file $T --zones "$Z" dns-proxy --enable --yes        # 切橙云
$W --token-file $T --zones "$Z" dns-proxy --disable --yes       # 回滚成灰云
$W --zones "$Z" verify                                          # 全量验证

# Cache Rules（巴西口径 statics 规则；默认只打印，加 --apply 才落库）
python3 docker/deploy/hongkong/static_cdn_config.py \
    apply-cache-rules --zones "$Z" --token-file $T --apply
```

---

## F. 不要照抄巴西的 5 个地方

```text
1. 源站：巴西是 GCS newgg2-bizops-gcs-*；香港是私有 S3 bizops-h5-hk-517506432530（前缀公开读）。
2. 前缀名：巴西对外 vendor_a-statics*；香港对外 vendor_b-static*（内部才映射 vendor_a-statics*）。
3. Cache Rules 表达式：香港要匹配 -static. / -static1. / -static2. 三种结尾。
4. zone 数量：巴西 20 个，香港 5 个。
5. 地区白名单：巴西 BR/SG/HK/AE；香港面向国内，是否限制需单独确认（当前 Worker 默认不限制）。
```

---

## G. 需要拍板的 5 件事（拍完再开工）

```text
1. CORS：巴西口径一律 *，还是保留香港现网「平台域精确回显 + 其它 *」？
   （Worker 里 CORS_MODE 开关：wildcard / echo-platform，默认 echo-platform）
2. 是否加地区白名单（Worker 里 ALLOWED_COUNTRIES，默认空 = 不限制）。
3. 是否切 platform-api 的 static_hosts（不切则改造空转）。
4. 路由粒度：70 条精确（当前工具做法）还是 5 条通配 *.hkcloudplay0N.com/*。
5. 灰度顺序（建议先 pg-static.hkcloudplay02.com）。
```

---

## 附：涉及文件

```text
Worker 源码（未部署）  docker/deploy/hongkong/hk_static_worker.js
部署/路由/DNS/验证工具 docker/deploy/hongkong/deploy_static_worker.py
本地逻辑自检          docker/ci/test_hk_static_worker.mjs
差异清单（分析）      docker/doc/2026-09-24-1230-【问题排查+架构改造】香港CN静态域名CDN与巴西口径差异清单.md
```
