---
id: "doc-2680105d6046"
title: "【运维】巴西 PP 静态资源缓存清理与 Worker 回源缓存修复"
date: "2026-10-24T16:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Docker", "监控告警", "自动化", "CDN", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-10-24-1645-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91%E5%B7%B4%E8%A5%BFPP%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E7%BC%93%E5%AD%98%E6%B8%85%E7%90%86%E4%B8%8EWorker%E5%9B%9E%E6%BA%90%E7%BC%93%E5%AD%98%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-10-24-1645-【运维】巴西PP静态资源缓存清理与Worker回源缓存修复.md"
sourceSha256: "31b6091977536a6511a69fb54b858feef6a69a957f1295595beda5b378823f25"
sourceSystem: "project-doc"
---

# 【运维】巴西 PP 静态资源缓存清理与 Worker 回源缓存修复

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610241645-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BShell-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91%E5%B7%B4%E8%A5%BF%20PP%20%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E7%BC%93%E5%AD%98%E6%B8%85%E7%90%86%E4%B8%8E%20Worker%20%E5%9B%9E%E6%BA%90%E7%BC%93%E5%AD%98%E4%BF%AE%E5%A4%8D.md)

> 整理日期：2026-10-24 16:45｜日期依据：文件名日期

时间：北京 2026-10-24 16:45 ｜ 巴西圣保罗 2026-10-24 05:45

需求：清理巴西 PP 静态资源缓存，提供可核对证据并发送监控报警群；补充可直接执行的
命令行验证文件；整理缓存清理 HTML 笔记；清理不再使用的根目录旧发布入口。

## 一、处理范围

```text
项目：巴西
厂家：PP
公网主机名：pp-static.xqv9m8.icu
GCS 桶：newgg2-bizops-gcs-pp-static
Cloudflare Worker：summer-wave-c94f
Worker 缓存版本：运维清理时 pp-static v3 -> v6；随后开发在 09:42 UTC
手工改为 `FACTORY_CONFIG`，线上最终以开发手工版为准。
```

没有清理其它厂家的缓存。`v4` 是中间排查版本；发现只修改 Worker 缓存键仍返回
`cf-cache-status: HIT` 后，继续将厂家版本写入 GCS 回源 URL，运维侧最终使用 `v6`
完成当时验证。之后开发手工把 Worker 改成 `FACTORY_CONFIG` 结构，不能把本仓库旧
`v6` 文件直接再部署回线上。

## 二、实际根因

原 Worker 虽然把版本写进了 `fetch()` 的 `cacheKey`，但 CDN 对 GCS 子请求仍按真实回源
URL 缓存。因此只做以下动作时仍会命中旧对象：

```text
改 CACHE_VERSION
按 pp-static.xqv9m8.icu 清主机名
```

最终修复是在 Worker 回源地址中追加：

```text
__bizops_cache_version=v6
```

GCS 会忽略这个未知查询参数，但 Cloudflare 会把它算进子请求缓存键，从而真正强制回源。

## 三、验证证据

验证必须在巴西宝塔或巴西网络执行，否则 PP 的国家白名单可能返回 403。

```text
出口：bizops-saopaulo-game-results-data-bt / 192.0.2.8
对象：/gs2c/common/game-history-client/0.28720e9b.min.js
```

清理前：

```text
第1次：HTTP 200 / cf-cache-status: MISS
第2次：HTTP 200 / cf-cache-status: HIT
```

最终清理后：

```text
第1次：HTTP 200 / cf-cache-status: MISS
第2次：HTTP 200 / cf-cache-status: HIT
Cache-Control: public, max-age=31536000, immutable
content-length: 13311
last-modified: Thu, 17 Sep 2026 08:25:16 GMT
```

HTML 抽查：

```text
https://pp-static.xqv9m8.icu/gs2c/announcements/unread/index.html
HTTP 200 / cf-cache-status: MISS
```

最终独立对象复核：

```text
https://pp-static.xqv9m8.icu/favicon.ico
第1次：HTTP 200 / cf-cache-status: MISS
第2次：HTTP 200 / cf-cache-status: HIT
Cache-Control: public, max-age=300, must-revalidate
content-length: 15086
```

GCS 源站直连：

```text
https://storage.googleapis.com/newgg2-bizops-gcs-pp-static/gs2c/common/game-history-client/0.28720e9b.min.js
HTTP 200 / content-length: 13311
```

证据已发送监控报警群：`message_id=510`。
`vswayssw` 声音/公告复查证据：`message_id=511`。

开发手工版本备份：

```text
线上 SHA256：
d3c90b51d3cde911d7c9ac7c1c17b745a0ad84375725092abc88a1986cd4f265

宝塔：
/root/bizops-cf-backups/20261024-094228-worker-manual/

仓库：
scripts/worker-js-cdn-代码备份/【线上在用】worker.js
scripts/worker-js-cdn-代码备份/history/cloudflare/【历史备份】2026-10-24-094228-开发手工变更-FACTORY_CONFIG.js
```

`vswayssw` 游戏复查：

```text
/gs2c/announcements/unread/?symbol=vswayssw&mackey=ey/
  -> 302 到 index.html -> HTTP 200

mobile/game/sounds.mp3.json             HTTP 200 / 6580205 bytes
mobile/game/sounds.ogg.json             HTTP 200 / 6216577 bytes
mobile/game/GUI_sounds.mp3.json         HTTP 200 / 533721 bytes
mobile/game/MDL_Jackpot_sounds.mp3.json HTTP 200 / 1036461 bytes

声音 JSON 首次 MISS，第二次 HIT。
```

该游戏 GCS 目录共 261 个对象，声音以 Base64 数据打包在 `*.sounds.mp3.json` /
`*.sounds.ogg.json` 内，不存在单独的 `.mp3` / `.ogg` 音频对象。因此排查时不能只找
独立音频后缀，还要验证这些声音 JSON 文件和公告接口。

## 四、可直接复制执行的验证命令

```bash
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X)'
TEST_URL='https://pp-static.xqv9m8.icu/gs2c/common/game-history-client/0.28720e9b.min.js'

curl -sS -o /dev/null -D - -A "$UA" "$TEST_URL" \
  | grep -iE 'HTTP/|cf-cache-status|cache-control|content-length|last-modified'

curl -sS -o /dev/null -D - -A "$UA" "$TEST_URL" \
  | grep -iE 'HTTP/|cf-cache-status'
```

预期清理后第一次为 `HTTP 200 / MISS`，第二次为 `HTTP 200 / HIT`。

## 五、备份与回滚

```text
最终上线前备份：
/root/bizops-cf-backups/20261024-091537-pp-v6/summer-wave-c94f.js

中间版本备份：
/root/bizops-cf-backups/20261024-083528-pp-v4/summer-wave-c94f.js
/root/bizops-cf-backups/20261024-083724-pp-v5/summer-wave-c94f.js
```

回滚或再次部署时必须先从 Cloudflare API 拉取最新线上源码。开发会直接改 Worker，
仓库文件只能作为备份，不能直接覆盖。当前开发版本使用 `FACTORY_CONFIG`，其中 PP 为
`version=v9`、`forceNoCache=true`；每个厂家/前缀已有独立版本字段。

## 六、后续标准操作

1. 先确认新文件已经上传到巴西 GCS。
2. 在 Worker 的 `CACHE_VERSION` 中只把目标厂家版本号加一。
3. 重新部署 `summer-wave-c94f`，部署前自动备份。
4. 在巴西出口请求同一稳定 URL。
5. 第一次必须是 `MISS`，第二次变为 `HIT`。
6. 浏览器端已有旧缓存时，仍可能需要用户刷新一次；服务端无法清理用户手机本地缓存。

`静态资源缓存清理笔记.html` 已同步加入真实测试文件、本次证据、GCS 回源版本说明和
国家白名单 403 注意事项。

## 七、旧发布入口与机器人清理

线上已经使用 `/data` 下的 `build.sh`、`stop.sh`、`start.sh` 完整 shell 流程。本轮从
`master` 删除以下冗余入口和组件：

```text
deploy-自动化部署最新版本.py
update_pgserver.sh
scripts/
docker/ben-bot/
docker/browser-test/
docker/ci/
docker/deploy/
docker/resource-sync/
docker/services/
```

机器人几个月未使用，已同时移除：

```text
宝塔：bizops-ben-bot、旧 ben-bot 容器及两个机器人镜像
备用入口机：bizops-ben-bot-standby 容器及机器人镜像
巴西 03：bizops-resource-sync 停止容器及 1.72GB 镜像
```

Telegram 通知没有随机器人一起下线：`docker/scripts/bizops_notify.py` 改为通过 SSH 在
宝塔宿主机读取 `/opt/benbot-runtime.env`，直接调用 Telegram API。机器人容器删除后，
宿主机通知凭据和目标群 `监控报警群` 校验均通过。

删除后复核：宝塔与备用机均无机器人/资源同步进程、无机器人容器和镜像；
之前的 Chromium 僵尸进程也已随机器人容器一起消失。

人工发布统一使用 `运维发布页.html`；`master` 现在只保留 `scripts/`、`doc/`、
`workbench/`、`线上服务器信息/` 和 HTML 运维页面。
