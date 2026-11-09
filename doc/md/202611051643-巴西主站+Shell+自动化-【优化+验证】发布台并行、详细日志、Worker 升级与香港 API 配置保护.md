---
id: "doc-4fe8b407a86a"
title: "【优化+验证】发布台并行、详细日志、Worker 升级与香港 API 配置保护"
date: "2026-11-05T16:43:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "自动化", "CDN", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-11-05-1643-%E3%80%90%E4%BC%98%E5%8C%96%2B%E9%AA%8C%E8%AF%81%E3%80%91%E5%8F%91%E5%B8%83%E5%8F%B0%E5%B9%B6%E8%A1%8C%E6%97%A5%E5%BF%97Worker%E5%8D%87%E7%BA%A7%E4%B8%8E%E9%A6%99%E6%B8%AFAPI%E9%85%8D%E7%BD%AE%E4%BF%9D%E6%8A%A4.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-11-05-1643-【优化+验证】发布台并行日志Worker升级与香港API配置保护.md"
sourceSha256: "dbaf227a2767870051001eb3e6d53822110d682b9e316c495d1a9e582a5aae7b"
sourceSystem: "project-doc"
---

# 【优化+验证】发布台并行、详细日志、Worker 升级与香港 API 配置保护

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202611051643-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2B%E8%87%AA%E5%8A%A8%E5%8C%96-%E3%80%90%E4%BC%98%E5%8C%96%2B%E9%AA%8C%E8%AF%81%E3%80%91%E5%8F%91%E5%B8%83%E5%8F%B0%E5%B9%B6%E8%A1%8C%E3%80%81%E8%AF%A6%E7%BB%86%E6%97%A5%E5%BF%97%E3%80%81Worker%20%E5%8D%87%E7%BA%A7%E4%B8%8E%E9%A6%99%E6%B8%AF%20API%20%E9%85%8D%E7%BD%AE%E4%BF%9D%E6%8A%A4.md)

> 整理日期：2026-11-05 16:43｜日期依据：文件名日期

更新时间：2026-11-05 16:43（Asia/Manila）

执行范围：`bizops-ops-console`、Cloudflare Worker `summer-wave-c94f`、香港
01/02 配置保护、03 打包源。

## 一、结论

本轮需求已全部实现并验证：

- 巴西与香港一键发布可并行，同区域和全局准备任务仍互斥；
- 业务节点必须全停且 `game-service*` 为 0，才能同步结果集；
- 一键准备自动执行 03 的 `sync_results.sh all`；
- 版本号默认北京时间 `YYYYMMDDHH-ben`；
- 香港 `configs-api.py` 有独立来源保护和哈希门禁；
- 一键发布成功后由服务端自动发送指定测试通知；
- Worker 线上代码已备份，17 个静态前缀版本全部提升；
- 页面可展开查看最新 Worker 和历史 Worker，任务可导出完整 JSON 日志。

## 二、开始前基线

```text
本地 master：ccd6b74f
origin/master：a72f41fb
本地状态：干净，领先远端 8 个提交
origin/ben：e1af715a
03 HEAD：e1af715a
03 工作区：干净
```

## 三、需求逐项核验

| 需求 | 状态 | 证据 |
| --- | --- | --- |
| 巴西/香港厂家差异 | PASS | 巴西 9 个业务容器，香港 10 个业务容器；香港额外包含 vendor_a HTTP 9096 |
| 03 巴西/香港 start.sh、stop.sh 独立 | PASS | 巴西与香港发布分别使用 `/data/server-runtime` 和 `/data/server-runtime-hk`；香港 01/02 已补 vendor_a |
| 业务节点全停后才同步结果集 | PASS | 香港两次任务在 vendor_a 残留时中止，均为 `running=1`；修复后先输出 `BUSINESS_CONTAINERS_STOPPED=0` 才 rsync |
| 03 最新结果集同步到巴西/香港 | PASS | 巴西 4 台、香港 2 台均完成同步；香港两台各 xfr#27 / 2,146,760,704 bytes |
| 一键准备更新 03 结果集 | PASS | 一键准备已包含 `sh sync_results.sh all` 和 `RESULT_SET_SYNC_OK` 检查 |
| share.so 巴西/香港统一 | PASS | 两地均为 `2a325437638df875c6cb316cff3c72af` |
| 巴西 version-bx 独立同步 | PASS | `/data/pgserver/version-bx/{server_configs,version.json}` → 巴西 runtime |
| 香港 version-zh 独立同步 | PASS | `/data/pgserver/version-zh/{server_configs,version.json}` → 香港 runtime |
| 香港 configs-api.py 不被覆盖 | PASS | 构建合并跳过；香港发布只从香港专源同步，并做源前/源后/目标三方哈希门禁 |
| 一键发布成功通知 | PASS | 服务端任务完成逻辑触发指定模板；容器内模拟发送验证巴西/香港各 1 条，无外部群副作用 |
| 巴西/香港并行 | PASS | 测试任务 `dbf85d00e00641c8` 与 `a327e5b3d1714ffa` 同时 running；同区域第二个任务返回 409 |
| 默认小时版本号 | PASS | 页面当前默认 `2026110516-ben`；日期改为 11-04 后自动变为 `2026110416-ben` |
| 每次操作详细日志 | PASS | 审计保存点击、输入、命令、前后快照；任务导出包含 job、全部 SSE 事件和前后 60 秒审计 |
| Worker 线上备份 | PASS | `/root/bizops-cf-backups/20261105-081252-summer-wave-c94f` |
| Worker 最新/历史查看 | PASS | 页面展开后加载 1 个最新版本和 16 个历史版本；API 内容 SHA256 与线上一致 |

## 四、香港 configs-api.py 保护

### 4.1 现状核对

```text
03 香港专源：
/data/server-runtime-hk/conf/configs-api.py
MD5：3b576ac97f6bb4c5aa7e6772354af0b0
SHA256：5adf1dbd46b167310b002605e37d6213d104401b4674e22cf9c9e2f5566d3cca

HK01 当前：
MD5/SHA256 以本机备份为准
/data/server-runtime/conf/configs-api.py.bak-YYYYMMDD-HHMMSS

HK02 当前：
MD5/SHA256 以本机备份为准
/data/server-runtime/conf/configs-api.py.bak-YYYYMMDD-HHMMSS
```

### 4.2 固化规则

1. 03 打包构建不得把 `configs-api.py` 写入
   `/data/server-runtime-hk/conf/`；
2. `/api/build-info` 返回香港专源 MD5，页面显示绝对路径；
3. 一键准备在构建前再次校验该 MD5，源文件变化则拒绝继续；
4. 香港发布以 `/data/server-runtime-hk/conf/configs-api.py` 为唯一来源；
5. 同步前备份每个香港节点的旧文件；
6. 同步后要求“源文件同步前 SHA256 = 源文件同步后 SHA256 = 目标文件 SHA256”。

## 五、云 Worker 缓存刷新

### 5.1 备份与版本

```text
变更前 SHA256：099c91659b38e78b7f9f157bf989f56d364382ae1c48da6efc7df0191558188d
变更后 SHA256：98ac274182cbd8e5086e24316cf220d5f47a6b554c3f952c73ded671681ea1ea
```

17 个静态前缀：

```text
pg-static / pg3-static / pg4-static / pg5-static / pg6-static / pg7-static：v1
vendor_a-statics / 1 / 2 / 3 / 4 / 5：v2
pp-static：v10
ppk-static / vendor_c-static / vendor_d-static：v1
g759-static：v3
```

`forceNoCache` 保持原值，其它 Worker 逻辑未修改。

### 5.2 缓存验证

从巴西宝塔出口逐前缀请求 `health.json`：

```text
pg-static / pg3 / pg4 / pg5：200 MISS → 200 HIT
pg6 / pg7：200 HIT（此前已有新键预热）；唯一查询参数复测均为 MISS → HIT
vendor_a-statics / 1 / 2 / 3 / 4 / 5：200 MISS → 200 HIT
pp-static / ppk-static / vendor_c-static / vendor_d-static / g759-static：200 MISS → 200 HIT
```

### 5.3 页面查看

- 最新代码：`latest/worker.js`
- 历史代码：`history/cloudflare/*.js`，共 16 个
- 页面外层展开后加载索引，点击具体条目再读取代码；
- 只读接口：`GET /api/worker-files`、`GET /api/worker-file?key=...`
- 路径白名单限制在 `/app/worker-backups`，不能读取任意服务器文件。

## 六、并行发布与日志

服务端锁：

```text
br：巴西手动步骤与 cmdFlowBr
hk：香港手动步骤与 cmdFlowHk
global：拉代码、打包、配置准备等互斥任务
```

实测：

```text
cmdFlowBr job dbf85d00e00641c8：running 08:38:42
cmdFlowHk job a327e5b3d1714ffa：running 08:38:42
两者同时执行，随后分别因测试命令返回 1 结束，不发送成功通知
同区域第二个 cmdFlowBr：HTTP 409
```

任务日志：

```text
GET /api/jobs/{job_id}/export
```

导出内容包括：

- job 元数据、命令、开始/结束时间、耗时、状态、退出码；
- 全部 SSE 事件及序号、时间戳、stdout/stderr；
- 任务开始前 60 秒到结束后 60 秒的审计记录；
- 页面点击、输入、快照和通知记录。

## 七、控制台部署验证

```text
镜像：bizops-ops-console:20261105-r5
镜像 ID：sha256:f3ea28d50b165feb3e089b6e73617510e9c166fae1a8e4c35c59d8439ab80c1f
状态：running / healthy
入口：http://192.0.2.8:8787
```

生产 API：

```text
/api/build-info：200，返回 6 个源文件（含香港 configs-api.py）
/api/worker-files：200，latest + 16 history
/api/worker-file?key=latest/worker.js：200，SHA256 与线上 Worker 一致
/api/jobs/{id}/export：200，包含 job + events + audit_events
```

页面：

```text
手机视口 Chromium：0 个 JS 异常
默认 tag：2026110516-ben
日期改为 11-04：自动变为 2026110416-ben
香港 configs-api 保护门禁：可见且生成命令通过 bash -n
Worker 最新/历史展开：通过
最近任务完整日志入口：通过
```

## 八、运行态

```text
巴西 01/02/04/05：各 9 个业务容器
香港 01/02：各 10 个业务容器
控制台：无运行中的发布任务
```

HK01 vendor_a 首启仍有 1 次历史 Sanic worker 启动超时，当前稳定；后续可单独
评估 `SANIC_WORKER_ACK_TIMEOUT=120`。

## 九、群通知

```text
823：巴西更新好了
826：香港更新好了
827/828：上一轮发布全过程汇总/文档
829：上一轮提交结果
830：Worker 全厂家缓存刷新开始
831：发布台 r5、Worker 升级和逐项核验汇总
832：完整事件文档
```

本轮提交 SHA 和提交结果在完成后补记。

## 十、后续修复

后续一键准备暴露 `sync_results.sh` 可执行位误判，并发现内部验证任务污染服务器
状态。已升级到 r6 修复，详见：

`docs/history/2026-11-05-1651-【修复】一键准备结果集脚本权限误判与服务器状态污染修复记录.md`
