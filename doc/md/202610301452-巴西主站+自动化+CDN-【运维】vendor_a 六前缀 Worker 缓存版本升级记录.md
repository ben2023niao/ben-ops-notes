---
id: "doc-8e0dd04340b8"
title: "【运维】vendor_a 六前缀 Worker 缓存版本升级记录"
date: "2026-10-30T14:52:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "自动化", "CDN", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-10-30-1452-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_a%E5%85%AD%E5%89%8D%E7%BC%80Worker%E7%BC%93%E5%AD%98%E7%89%88%E6%9C%AC%E5%8D%87%E7%BA%A7%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-10-30-1452-【运维】vendor_a六前缀Worker缓存版本升级记录.md"
sourceSha256: "3c52201b180fbb1c4f1425a722ad7b47ea1ec400eef51a90171e88b486dc932d"
sourceSystem: "project-doc"
---

# 【运维】vendor_a 六前缀 Worker 缓存版本升级记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-10-30-1452-【运维】vendor_a六前缀Worker缓存版本升级记录.md`

> 整理日期：2026-10-30 14:52｜日期依据：文件名日期

时间：北京 2026-10-30 14:52 ｜ UTC 2026-10-30 06:52

状态：✅ 线上 Worker 已备份并部署；vendor_a 六个静态前缀缓存版本升级与回读验证通过。

## 一、开始前基线

```text
仓库：/Users/operator/Projects/ops/private-notes/master
本地分支：master
本地 HEAD：04c4b527
远端 origin/master：b1d35aa3
本地状态：领先 origin/master 9 个提交
未提交修改：无
```

远端 master 是本地 HEAD 的祖先。本轮基于本地最新提交继续操作。

## 二、反馈与目标

产品反馈：

```text
vendor_a Jackpot Joker：网页端可进入，安卓 PWA 和 Chrome 仍卡在 50%。
vendor_a Lucky Macaw：网页端和安卓 PWA 进度到 100% 后弹出登录问题。
```

开发要求清理 vendor_a 缓存，并确认 Worker 是否需要提升 vendor_a 版本号。

本轮目标：

1. 操作前读取 Worker 与 vendor_a 缓存历史记录；
2. 从 Cloudflare API 拉取并备份当前线上 Worker；
3. 只提升 vendor_a 六个静态前缀的缓存版本；
4. 回读线上 Worker，并从巴西出口验证缓存失效与重建；
5. 不影响 PP、G759 及其他厂家。

## 三、读取的历史依据

```text
scripts/worker-js-cdn-代码备份/README.md
scripts/worker-js-cdn-代码备份/history/README.md
docs/history/2026-10-24-1645-【运维】巴西PP静态资源缓存清理与Worker回源缓存修复.md
docs/history/2026-10-20-1358-【运维】g759静态资源CDN缓存清理记录.md
docs/history/2026-10-17-1420-【问题排查+架构改造】巴西静态资源前端缓存问题根治(Worker缓存策略+zone规则覆盖).md
docs/history/2026-09-10-0949-【运维】vendor_a-statics3-5 CDN缓存清理与Worker缓存盐记录.md
```

历史规范确认：

- 开发可能直接修改线上 Worker，不能直接用仓库旧文件覆盖；
- 操作前必须从 Cloudflare API 拉取线上源码并备份；
- 单个厂家需要一起提升其全部相关静态前缀；
- `version` 负责绕过边缘旧缓存；
- `forceNoCache` 用于更新窗口内让浏览器重新协商，避免继续使用本地旧资源。

## 四、Worker 备份

操作前线上源码：

```text
SHA256：22c5e0185e3b9b2856a417eb8144826e2ad0b2939a09e44182360c4b51bef048
采集时间：2026-10-30 06:48:28 UTC
宝塔备份：/root/bizops-cf-backups/20261030-064828-summer-wave-c94f
```

部署前再次从 API 拉取确认，线上 SHA256 仍为
`22c5e018…`，说明没有开发并发修改：

```text
复核备份：/root/bizops-cf-backups/20261030-065019-summer-wave-c94f
```

备份包含：

```text
summer-wave-c94f.api-response
summer-wave-c94f.js
SHA256SUMS
mevendor_ata.json
```

## 五、配置变更

只修改以下 6 个前缀：

```text
vendor_a-statics
vendor_a-statics1
vendor_a-statics2
vendor_a-statics3
vendor_a-statics4
vendor_a-statics5
```

每个前缀均从：

```text
version: ""
forceNoCache: false
```

提升为：

```text
version: "v1"
forceNoCache: true
```

配置对比确认：

```text
变更前结构：17 个厂家/前缀
变更后结构：17 个厂家/前缀
实际变化：仅 vendor_a 6 个前缀
PP、G759、PG、PPK、vendor_c、PANDA：配置未变化
```

## 六、部署与线上回读

部署：

```text
Cloudflare Worker：summer-wave-c94f
部署结果：HTTP 200 / success=True
部署方式：ES Module multipart
compatibility_date：2026-09-01
```

部署后重新从 Cloudflare API 拉取：

```text
线上 SHA256：4aa0c2e32efbaae0dec53d6f1c3ebe63083aeacbd2d78a255632105f44bfbe66
与本地候选文件：一致
线上备份：/root/bizops-cf-backups/20261030-065044-summer-wave-c94f
```

仓库留档：

```text
scripts/worker-js-cdn-代码备份/【线上在用】worker.js
scripts/worker-js-cdn-代码备份/history/cloudflare/2026-10-30-064828-变更前.js
scripts/worker-js-cdn-代码备份/history/cloudflare/2026-10-30-065044-线上vendor_a-v1.js
```

## 七、缓存验证

从巴西宝塔出口 `192.0.2.8` 使用移动端浏览器 UA 请求。

六个 `health.json`：

| 前缀 | 第一次 | 第二次 |
| --- | --- | --- |
| vendor_a-statics | HTTP 200 / MISS | HTTP 200 / HIT |
| vendor_a-statics1 | HTTP 200 / MISS | HTTP 200 / HIT |
| vendor_a-statics2 | HTTP 200 / MISS | HTTP 200 / HIT |
| vendor_a-statics3 | HTTP 200 / MISS | HTTP 200 / HIT |
| vendor_a-statics4 | HTTP 200 / MISS | HTTP 200 / HIT |
| vendor_a-statics5 | HTTP 200 / MISS | HTTP 200 / HIT |

问题游戏对应静态入口：

```text
Jackpot Joker / jpj/index.html
  vendor_a-statics3：第一次 HTTP 200 / MISS，第二次 HTTP 200 / HIT
  Cache-Control：no-cache, must-revalidate

Lucky Macaw / lm/index.html
  vendor_a-statics2：HTTP 200 / HIT
  vendor_a-statics3：第一次 HTTP 200 / MISS，第二次 HTTP 200 / HIT
  Cache-Control：no-cache, must-revalidate

补充旧样例 dad/index.html
  vendor_a-statics4：第一次 HTTP 200 / MISS，第二次 HTTP 200 / HIT
  Cache-Control：no-cache, must-revalidate
```

`vendor_a-statics2/lm/index.html` 在专项测试前已经被同一轮健康检查后的第一次页面请求重建进新
版本缓存，因此专项测试看到 `HIT`，不是旧版本缓存。

## 八、效果边界

本次已让 Worker 边缘缓存使用全新的 vendor_a `v1` 缓存键，并对页面/动态资源下发
`no-cache, must-revalidate`。

已经保存在用户手机浏览器本地的旧资源，发布端无法直接远程删除。仍保留旧本地缓存的设备
需要强制刷新、清除站点缓存或用无痕窗口打开一次。之后会进入新的缓存策略。

本次验证覆盖静态页面、缓存键、缓存重建和响应头。如果强制刷新后游戏仍卡在 50% 或 100%
后登录异常，需要继续按具体游戏收集浏览器 Network、Console 与 vendor_a `/req` 请求日志，
不能仅归因于 CDN。

## 九、回滚

回滚文件：

```text
/root/bizops-cf-backups/20261030-064828-summer-wave-c94f/summer-wave-c94f.js
```

回滚前必须再次拉取线上当前源码，确认期间没有开发手工修改，再通过
`cf_worker_deploy.py` 部署上述回滚文件。

## 十、群通知

```text
Worker 备份完成：671
开始升级 vendor_a 版本：672
完成汇总：673
完整事件文档：674
```

## 十一、修改文件

```text
scripts/worker-js-cdn-代码备份/【线上在用】worker.js
scripts/worker-js-cdn-代码备份/【线上在用】worker.sha256
scripts/worker-js-cdn-代码备份/README.md
scripts/worker-js-cdn-代码备份/history/cloudflare/2026-10-30-064828-变更前.js
scripts/worker-js-cdn-代码备份/history/cloudflare/2026-10-30-065044-线上vendor_a-v1.js
workbench/CURRENT_TASK.md
workbench/CURRENT_STATE.md
workbench/ACTIVE_TASKS.md
docs/history/2026-10-30-1452-【运维】vendor_a六前缀Worker缓存版本升级记录.md
```
