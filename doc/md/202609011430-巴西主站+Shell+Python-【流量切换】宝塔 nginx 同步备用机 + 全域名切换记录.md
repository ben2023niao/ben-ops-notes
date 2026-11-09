---
id: "doc-50fafabff335"
title: "【流量切换】宝塔 nginx 同步备用机 + 全域名切换记录"
date: "2026-09-01T14:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化", "CDN"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-01-1430-%E3%80%90%E6%B5%81%E9%87%8F%E5%88%87%E6%8D%A2%E3%80%91%E5%AE%9D%E5%A1%94nginx%E5%90%8C%E6%AD%A5%E5%A4%87%E7%94%A8%E6%9C%BA%E4%B8%8E%E5%85%A8%E5%9F%9F%E5%90%8D%E5%88%87%E6%8D%A2%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-01-1430-【流量切换】宝塔nginx同步备用机与全域名切换记录.md"
sourceSha256: "99ceffb17e4d44308246e37fda0d1ba92a7febcc9f86bbcf265b04789b88483b"
sourceSystem: "project-doc"
---

# 【流量切换】宝塔 nginx 同步备用机 + 全域名切换记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-01-1430-【流量切换】宝塔nginx同步备用机与全域名切换记录.md`

> 整理日期：2026-09-01 14:30｜日期依据：文件名日期

时间：2026-09-01 14:30（Asia/Manila）
项目：某业务公司 / PGServer master
执行人：Codex（本地 + 宝塔 192.0.2.8 + 备用机 192.0.2.13 + Cloudflare API）

## 一、任务

```text
1. 宝塔 nginx 全量同步到备用机（bizops-saopaulo-nginx-standby-01, 192.0.2.13）
2. 全部域名 A 记录切换到备用机
3. 全厂家全游戏测试
4. 留下流量切换笔记与脚本
```

## 二、勘察结果

```text
宝塔 nginx 1.28.0：52 个站点 conf、78 证书目录
备用机 nginx 1.30.4：25 个 conf（active），磁盘 153G 空闲
差异：25 个共享站点配置中 10 个不同
  - 静态 conf（pg/pg3/pg5/vendor_a-statics/1/2/pp/ppk/vendor_c/vendor_d）：CORS 头位置
  - g759-games：备用机有「根路径 200 线路探测」，宝塔被每日生成脚本覆盖丢失
include 目录（common/extension/well-known/tcp/rewrite）：已同步
证书 78 目录：大小一致
```

## 三、同步执行

```text
1. 配置：25 个共享 conf（排除 btwaf/php/ssl.*/waf）scp -> 备用机 /etc/nginx/conf.d/
2. 证书：/www/server/panel/vhost/cert -> 备用机同路径
3. 静态目录：rsync -a --exclude game_results_data /www/wwwroot/ -> 备用机
   （13 静态目录约 29GB，完成后 dry-run 0 差异）
4. nginx -t + reload 两台均通过
```

## 四、g759 根路径修复（发现并持久化）

```text
现象：备用机根路径 200，宝塔 404
根因：2026-08-26 手工修复被每日 01:40 生成脚本（all_game_domain_sync）覆盖，
      生成模板不含该修复
修复：
  1. 生成脚本 sync_all_game_domains_to_baota.py 的 game_server_conf 增加：
     key=="g759" 时注入 location = / { return 200 "ok"; }
  2. 宝塔重跑 cron wrapper 重新生成 + reload（宝塔/备用机根路径均 200）
  3. 仓库同步该模板（docker/线上服务器信息/baota/scheduled-tasks/sanitized/）
```

## 五、DNS 切换（199 条）

```text
范围：全部 proxied A 记录 content=192.0.2.8 -> 192.0.2.13
  （api.<22 zone>、6 厂商 games.<22 zone>、通配符 *.<zone>、www、根域、
   socket.shanghu01/02/03.cc、verify/api.pgofficialbx.com）
工具：docker/scripts/dns_cutover.py
  --to-standby 切换；--to-baota 回滚；--list 查看
执行：199/199 成功，0 失败
回滚快照：/tmp/dns_cutover_35_247_205_6_snapshot.json（含 zone/id/name/content）
```

## 六、验证结果

```text
切换前直连 IP 对比（宝塔 vs 备用机）：pg-games 200/200、api 200/200、
  vendor_a 403/403、g759 200/200、verify 200/200、socket 行为一致
切换后（公网）：
  动态 /health 157 项：153 正常 rcode=0；4 个 410 为已知未启用 zone
    （api/pg-games 的 t6qv8m.icu 与 6qv8m.icu，切换前后一致）
  全厂家入口 /health：PG/vendor_a/PP/PPK/vendor_c/PANDA/G759 全部 200
  静态 health.json：pg4/vendor_a/vendor_c/vendor_d 抽检全部 200
  备用机 nginx 日志：已见真实游戏流量（HeadlessChrome POST /web-api/... 200）
```

## 七、回滚方案

```text
export [敏感内容已脱敏]
python3 docker/scripts/dns_cutover.py --to-baota   # 192.0.2.13 -> 192.0.2.8
备用机 nginx 保持运行即可，宝塔配置未被改动（仅生成脚本模板更新）。
```

## 八、遗留事项

```text
1. ✅ 证书同步 cron 已上线（2026-09-01 14:45）：
   docker/scripts/sync_certs_to_standby.sh（rsync --checksum 检测内容变更 →
   同步备用机 → nginx -t + reload，无变更跳过）
   宝塔 cron：40 4,10,16,22 * * *（紧跟 acme 续签 03 分后）
   已实测：测试文件触发同步+reload OK
2. 生成器模板已补丁，后续 all_game_domain_sync 不会再覆盖 g759 根路径修复
3. 静态目录同步为一次性；如本地静态目录继续作为回退源，建议接 gcs_static_sync 或定时 rsync
4. 监控：entry_health_monitor/container_health_monitor 仍指向公网域名，自动覆盖新入口
```

## 九、全量域名检查与 410 修复（2026-09-01 15:21）

```text
背景：用户报 pg-games.6qv8m.icu/health 不通，要求全部厂家全部域名检查。

检查结果：
  动态 /health 全量 181 个域名：177 正常；4 个 410
    - api.t6qv8m.icu / pg-games.t6qv8m.icu / api.6qv8m.icu / pg-games.6qv8m.icu
  静态 CNAME 监控：242/242 OK

根因：nginx all-games-proxy.conf 存在两条故意访问策略验证规则：
  location = /api/report/timing 与 location ^~ / 内：
  if ($host ~* "^(pg-games|api)\.(t6qv8m|6qv8m)\.icu$") { return 410; }
  （覆盖所有路径含 /health，宝塔/备用机一致）

修复：
  1. 移除两条访问策略验证 if 块（备份 /root/all-games-proxy.conf.bak-20260901-410block）
  2. 同步备用机 + nginx -t/reload（两台）
  3. 复检：动态 181/181 全部 rcode=0；pg-games.6qv8m.icu/health 200

待确认：
  - 若 launcher 也要使用 t6qv8m/6qv8m 两个 zone，需把这两个 zone
    加回 platform-api/conf/domains/pg.json 的 game_hosts（当前线上 20 个）
    —— 需要时可改并发布
  - 如这两个 zone 原本要下线，可恢复备份中的 410 规则
```

## 十、m. 前缀 bug 域名下掉 + api_hosts 接入（2026-09-01 15:30）

```text
背景：用户确认 t6qv8m.icu/6qv8m.icu（m.icu 结尾，前端 "m."->"api." 替换 bug
      历史 2026-07-06）应下掉；410 访问策略验证规则加回宝塔/备用机。

执行：
1. nginx：all-games-proxy.conf 恢复两条 410 访问策略验证
   （(pg-games|api).(t6qv8m|6qv8m).icu，备份 .bak-20260901-410block 已存在）
   宝塔+备用机 reload；验证 4 域名 410（cache-buster/直连源站均 410）
2. platform-api 配置：6 厂商移除 t6qv8m.icu/6qv8m.icu（game+static hosts）
3. api_hosts：pg.json default 新增 api_hosts=20 条 api.<zone>
   （含 3 条 Argo：api.xqv9m8 / api.vendor_a-cdn-2026 / api.cdn-tokyo-bizops）
4. launcher 代码：game_launcher.py 注入 params_dict["api_hosts"]
   （conf/domains/<provider>.json -> default.api_hosts，增量不破坏现有逻辑）
5. 发布：3 台后端容器 docker cp 更新 json+py 并 docker restart；
   容器内校验 api_hosts=20、无 t6qv8m/6qv8m
6. 验证：api.xqv9m8/vendor_a-cdn-2026/cdn-tokyo-bizops 200、其他 api 200、
   api.t6qv8m/6qv8m 410、游戏域名 200

备注：容器为热更新（docker cp + restart）；下次镜像重建需以 master 为准，
      已同步 master 仓库与宝塔/后端 /opt/pgserver 副本。
```

## 十一、厂商配置清理：删除 fc/vendor_b/jdb + g759 线上化（2026-09-01 17:00）

```text
用户要求：删除测试环境厂商配置 fc.json / vendor_b.json / jdb.json；
          g759.json 由测试配置改为线上配置（参考其他厂商）。

执行：
1. 删除 platform-api/conf/domains/ 的 fc.json / vendor_b.json / jdb.json（master）
   - 同时删除宝塔 /opt/pgserver 与 3 台后端主机副本 + 运行容器内文件
   - 容器内最终 7 个厂商文件：g759/vendor_d/pg/vendor_c/popok/pp/vendor_a
2. g759.json 重写为线上配置（镜像 vendor_d 结构，排除 t6qv8m/6qv8m）：
   - static_hosts 20 条 g759-static.<zone>（含 xqv9m8/vendor_a-cdn-2026/cdn-tokyo-bizops）
   - game_hosts 20 条 g759-games.<zone>
   - special_games: []
3. 发布：3 台后端容器 docker cp 更新 + 删除测试文件（按请求读配置，无需重启）
4. 验证：
   - 容器内 g759 static=20/game=20、无 fc/vendor_b/jdb
   - g759-games.xqv9m8/vendor_a-cdn-2026/cdn-tokyo-bizops /health 200
   - g759-static 游戏页 load.html 200、health.json 200（games/<game>/health.json）

备注：agent_apis.py 仍 import game_plat_vendor_b/game_plat_jdb（模块保留）；
      删除的是域名配置，未删除 python 模块（如需彻底下线厂商再单独处理）。
```

## 十二、静态 health 文件全量统一替换（2026-09-01 17:30）

```text
用户提供统一 health.json 模板：
  {"rcode":0,"data":"k9#mP8$vX2!zL5qW","msg":"succ"}
模板存档：docker/scripts/static_health.json

执行：
1. 12 桶根目录 health.json 全部替换为新模板
2. 游戏目录 health.json 全量补齐+替换：
   - 原 304 个（发现入口目录）+ 360 个（全量 top-level 目录补齐）= 707 个对象
   - 用 gcloud storage cp 逐文件显式上传（cp -r 不覆盖已存在对象，已规避）
3. Worker 缓存：health.json 缓存键加版本盐 v2->v3（Workers Cache API 不受
   zone purge 清除，版本盐强制全边缘失效），部署后全量新内容
4. 验证：桶直出 200、CF 抽样 15/15 新内容、cache-buster 全 200
5. 覆盖度：gcloud storage ls 统计 707 个 health.json 对象（12 桶）

备注：CF 抽样个别旧内容为边缘缓存残留，v3 版本盐已强制刷新；
      后续再改 health 内容时，同步改 Worker 版本盐即可。
```
