---
id: "doc-9a2f2fd798f5"
title: "2026-09-25 香港后端按巴西流程启动（version-zh / start.sh / 最新镜像）+ 静态资源同步"
date: "2026-09-25T12:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Shell", "Python", "Docker", "Nginx", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-09-25-1230-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AF%E5%90%8E%E7%AB%AF%E6%8C%89%E5%B7%B4%E8%A5%BF%E6%B5%81%E7%A8%8B%E5%90%AF%E5%8A%A8%E4%B8%8E%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-09-25-1230-【架构改造】香港后端按巴西流程启动与静态资源同步记录.md"
sourceSha256: "35abfa0a3df58dde9334f0781dafb6a5ae78ba9ecae2775741f668d2c7f83cd5"
sourceSystem: "project-doc"
---

# 2026-09-25 香港后端按巴西流程启动（version-zh / start.sh / 最新镜像）+ 静态资源同步

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/cn/docker/doc/2026-09-25-1230-【架构改造】香港后端按巴西流程启动与静态资源同步记录.md`

> 整理日期：2026-09-25 12:30｜日期依据：文件名日期

## 一、用户给出的 9 步流程与执行结果

| # | 要求 | 状态 | 说明 |
| ---: | --- | --- | --- |
| 1 | 静态资源采用 AWS S3，同步到最新 | 🔄 执行中 | 香港 S3 `bizops-h5-hk-517506432530` 已是静态源；本轮修正同步工具的过期桶名后重新增量同步（见第四节） |
| 2 | 域名参考巴西，静态域名挂 S3，复刻巴西 Worker/规则（hkcloudplay06/07） | ✅ 已完成 | 2026-09-24/25 已做：14 前缀 × 2 zone 橙云 A + Worker `bizops-hk-static-proxy` + `statics` Cache Rules |
| 3 | 动态域名走 nginx，nginx 复刻巴西配置 | ✅ 已完成 | standby 入口（192.0.2.37）8 个 upstream 复刻巴西 `socket_backend` 口径，只反代自建后端内网 IP |
| 4 | 首次 sync 同步 | ✅ 已完成 | 152.1 GiB：prod-03 → prod-01 → prod-02，CHECK 差异条目 0/0 |
| 5 | `/data/server-runtime/` 执行 `cp version-zh/* ./` | ✅ 已完成 | 两台执行；`config_version` 由 `bx.2026.09.09` → **`zh.2026.09.09`**（中文版 server_configs + version.json），原文件备份 `*.bx-bak-*` |
| 6 | 修改 `start.sh` 的 `REGISTRY="192.0.2.20:5000"` | ✅ 已完成 | 两台已改（原 `192.0.2.1:5000`），备份 `start.sh.bak-*` |
| 7 | `/data/server-runtime/conf/domains` 改域名配置 | ✅ 已完成 | 10 个 JSON 香港化（hkcloudplay06/07 + `socket.hk-socket.com`，vendor_b 前缀映射），原配置备份 `conf/domains.br-backup-*` |
| 8 | 后续 sync 只同步 share.so | ✅ 已完成 | `/root/hk-runtime-sync.sh` 已收窄为只同步 share.so |
| 9 | 找到线上各厂商最新版本并启动 docker | ✅ 已完成 | 由 registry 取各厂商最新日期 tag，用 `start.sh` 启动 8 个厂商（见第三节） |

## 二、start.sh 结构核对（香港可直接用）

```text
用法：./start.sh <vendor> <VERSION_TAG>
镜像：${REGISTRY}/game-service-<vendor>:<TAG>
容器：game-service-<vendor>-prod，端口按内置映射（api 9090 / pg 9091 / vendor_b 9093 /
      ppk 9098 / pp 9099 / vendor_d 9018 / g759 9019 / vendor_c 9020 / vendor_a 9096 / vendor_a_ws 8765）
挂载：share.so / server_configs / version.json / xxxxxx.mmdb / conf/domains /
      game_result_datas/<vendor> / logs
vendor_b：脚本内置 `docker run ... python /app/vendor_a/vendor_b.py`（与镜像自带
      CURRENT_VENDOR=vendor_a + MAIN_ENTRY=vendor_b.py 一致）
容器用户：脚本未写 --user，但镜像 Config.User=appuser，仍以 appuser 运行（与巴西一致）
```

各镜像自带 env 已核对（可省去手工传 env）：api=platform-api/main.py、pg=pg/server.py、
pp=pp/pp.py、ppk=ppk/ppk.py、vendor_d=vendor_d/vendor_d.py、g759=g759/g759.py、
vendor_c=vendor_c/vendor_c.py、vendor_b=**vendor_a/vendor_b.py**。

## 三、步骤 9：各厂商最新版本与启动

从 registry（`192.0.2.20:5000`）按日期取最新 tag：

| 厂商 | 最新 tag |
| --- | --- |
| api | `20260923-ben` |
| pg | `20260921-ben` |
| pp | `20260923-ben` |
| vendor_d | `20260919-ben` |
| vendor_b / ppk / g759 / vendor_c | `20260916-ben-cb8f2c55` |

两台分别执行：

```bash
cd /data/server-runtime
./start.sh api     20260923-ben
./start.sh pg      20260921-ben
./start.sh vendor_b    20260916-ben-cb8f2c55
./start.sh ppk     20260916-ben-cb8f2c55
./start.sh pp      20260923-ben
./start.sh vendor_d   20260919-ben
./start.sh g759    20260916-ben-cb8f2c55
./start.sh vendor_c 20260916-ben-cb8f2c55
```

启动后状态（`docker ps`）：8 个容器都起来了；Sanic 日志显示
`Goin' Fast @ http://192.0.2.3:<port>`、`mode: production, w/ 4 workers`。

```text
api 容器 restarts=0（platform-api 正常，socket.hk-socket.com/ 返回 404 形态、/healthz 200）；
其余厂商容器 restarts 逐步增加（重启循环）——与用户说明的「数据库没开权限」一致，
属预期；DB 权限开通后应稳定。
```

（vendor_a / vendor_a-WS 不在 cn 范围，未用 start.sh 启动；prod-02 上另有用户手工起的
`game-service-vendor_a-prod` / `game-service-vendor_a_ws-prod`，未干预。）

## 四、步骤 1：静态资源同步（含工具修复）

发现问题：`/usr/local/bin/bizops-sync-gcs-to-s3` 的桶映射仍是旧桶名
`bizops-gcs-*`，实测报 `directory not found`（旧桶已在 2026-09-11 迁移中删除），
现役桶是 `newgg2-bizops-gcs-*`（公网抽查 200）。

处理：

```text
1) 备份 /opt/bizops-hk-ops/sync_gcs_to_s3.py -> *.bak-YYYYMMDD-HHMM
2) 映射统一改为 newgg2-bizops-gcs-<前缀>（含 vendor_a-statics/1/2）
3) 重新执行增量同步（后台）：/root/sync-statics.sh -> /root/sync-statics.log
   前缀：pg-static / pg3 / pg4 / pg5 / pp-static / ppk-static / vendor_d-static /
        vendor_c-static / vendor_b-static / vendor_b-static1 / vendor_b-static2
```

待补：pg6-static / pg7-static / g759-static 的源是 gitlab client 仓库（非 GCS），
需按 2026-09-02 的 git→S3 流程单独同步（不在本次脚本范围内）。

## 五、踩坑记录

```text
1) GCS 桶名过期：同步工具写死旧桶 bizops-gcs-*，实际已迁移到 newgg2-bizops-gcs-*，
   不改会一直 directory not found。
2) pkill -f 自匹配（第二次踩）：命令行里包含同一模式串时会把自己所在 shell 杀掉，
   表现为命令无输出/后续步骤不执行；应使用 pgrep -x（精确进程名）或按 PID kill。
3) vendor_b 入口：必须 CURRENT_VENDOR=vendor_a + MAIN_ENTRY=vendor_b.py（镜像代码在 /app/vendor_a），
   用 vendor=vendor_b 会 can't open file '/app/vendor_b/vendor_b.py' 无限重启；start.sh 已内置正确写法。
4) /data/server-runtime/server_configs 是文件不是目录。
```

## 六、待办

```text
1. 数据库权限开通后复测各厂商（当前除 api 外仍在重启循环）；
2. pg6/pg7/g759 静态资源（git 源）按 git→S3 流程同步；
3. share.so 更新：跑 /root/hk-runtime-sync.sh（只同步 share.so）+ 重启容器；
4. 老入口机上游仍为外部双后端（老域名现网），如需收口另行授权。
```

## 七、范围变更（2026-09-25 12:45，用户指示）

```text
用户：「不需要同步前端资源了，开发操作了」
=> 前端/静态资源（S3 上的 static 前缀）同步**改由开发侧操作**，cn 运维不再执行该类同步。

本轮处理：
1. 已停止后台静态同步任务（/root/sync-statics.sh 与 rclone 进程全部停止，无残留）；
   停止前进度：pg-static 校验进行中（chk#25460/35584），S3 对象数 39264 -> 39326（+62）。
2. 同步工具的桶名修正**保留**（旧桶 bizops-gcs-* 已删除，现役 newgg2-bizops-gcs-*；
   原文件备份 /opt/bizops-hk-ops/sync_gcs_to_s3.py.bak-*）——以后若开发侧需要该工具可直接用。
3. 本节之后，文档第一节表格中「步骤 1 静态同步」与 TASK-20260925-HK-STATIC-* 相关
   待办均移交开发侧，不再由 cn 跟进。
```

## 八、关联

```text
docker/deploy/hongkong/start_hk_backends.py      容器启停/状态/日志工具（备用，与 start.sh 等效）
docker/deploy/hongkong/render_hk_domains.py      conf/domains 香港化渲染
docker/doc/2026-09-25-1130-【架构改造】香港后端conf-domains香港化与业务容器启动记录.md
docker/doc/2026-09-25-1030-【架构改造】香港standby入口上游收口为自建后端内网IP记录.md
```
