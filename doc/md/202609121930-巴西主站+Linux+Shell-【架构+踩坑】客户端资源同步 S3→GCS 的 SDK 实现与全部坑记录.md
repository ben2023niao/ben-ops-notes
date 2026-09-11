---
id: "doc-9017233d6393"
title: "【架构+踩坑】客户端资源同步 S3→GCS 的 SDK 实现与全部坑记录"
date: "2026-09-12T19:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Docker", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-12-1930-%E3%80%90%E6%9E%B6%E6%9E%84%2B%E8%B8%A9%E5%9D%91%E3%80%91%E5%AE%A2%E6%88%B7%E7%AB%AF%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5S3%E5%88%B0GCS%E7%9A%84SDK%E5%AE%9E%E7%8E%B0%E4%B8%8E%E5%85%A8%E9%83%A8%E5%9D%91%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-12-1930-【架构+踩坑】客户端资源同步S3到GCS的SDK实现与全部坑记录.md"
sourceSha256: "5f7c2292d3c3aca876574ebedca36553e66d1d08494b65ec4dee2893eb719aed"
sourceSystem: "project-doc"
---

# 【架构+踩坑】客户端资源同步 S3→GCS 的 SDK 实现与全部坑记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-12-1930-【架构+踩坑】客户端资源同步S3到GCS的SDK实现与全部坑记录.md`

> 整理日期：2026-09-12 19:30｜日期依据：文件名日期

时间：2026-09-12 19:30（Asia/Manila）
状态：✅ 线上生效并验证（4 个桶 缺失 0 / 大小不符 0 / 内容不符 0）
适用对象：所有要动「前端/客户端资源同步」的人或 AI

> **先读这一句**：客户端资源同步的**唯一正确实现**是
> `docker/scripts/s3_gcs_sdk_sync.py`（boto3 ↔ google-cloud-storage SDK 直连），
> 跑在**后端 03 的容器** `dbqp-resource-sync` 里。
> 本文档列出的都是**已经踩过的坑**，照抄旧写法会重犯。

## 一、当前架构（2026-09-12 起）

```text
前端开发 --上传--> s3://dbqp-s3-<prefix>/（AWS 大阪 ap-northeast-3，私有+版本控制）
                        |
                        |  运维/机器人触发同步（后端 03 的容器，SDK 直连）
                        v
   gs://newgg2-dbqp-gcs-<prefix>-sa/  （项目 newgg2-0520，巴西）
   gs://newgg2-dbqp-gcs-<prefix>/     （项目 newgg2-0520，香港镜像）
                        |
                        v
   Cloudflare Worker summer-wave-c94f（静态代理）→ 静态域名 CDN → 玩家
```

关键事实（与旧文档不同的地方）：

| 项目 | 现状 |
| --- | --- |
| 桶名前缀 | **`newgg2-`**（资源 09-11 迁到 newgg2-0520；旧的 `dbqp-gcs-*` 桶已删除） |
| 执行机 | **后端 03**（203.0.113.1，8C31G）；**宝塔只做管理，不再中转同步** |
| 执行形态 | **容器** `dbqp-resource-sync`（不污染宿主机环境，便于迁移） |
| 同步引擎 | **SDK 直连**（boto3 + google-cloud-storage），不是 aws/gsutil 命令行 |
| 校验方式 | **两边元数据接口比对**（零数据搬运） |
| 触发入口 | 机器人主页「静态资源同步S3到GCS」按钮，仅 @benb6879 / @Ben_Bird 可执行 |

## 二、工具清单（只用这些）

```text
docker/scripts/s3_gcs_sdk_sync.py        ★ 同步主引擎（SDK 直连）
    --prefix tada-statics4,tada-statics5 --apply --jobs 32   # 执行
    --prefix X --verify-only                                 # 只校验（零数据搬运）
    --prefix X --cdn-only                                    # 只做 health.json + CDN 收尾
docker/scripts/s3_to_gcs_client_sync.py  旧 CLI 版（aws+gsutil）——慢，仅作兜底
docker/scripts/gcs_health_json_ensure.py health.json 自动补齐（17 桶，幂等）
docker/resource-sync/                    同步容器（Dockerfile / entrypoint.sh / run.sh）
docker/scripts/s3_sync_request_worker.py 宿主机 worker（旧回退路径）
docker/scripts/s3_to_gcs_static_sync.sh  旧入口，现已改为薄封装（内部走 SDK/CLI 脚本）
```

## 三、踩过的坑（★ 每条都有线上代价）

### ★1 SDK 上传 400：`upload_from_string` 没带 content_type（本次线上事故根因）

```text
现象：上传全部失败，但脚本汇总里看起来"完成"；GCS 里资源仍是旧版本 → 玩家进不去。
报错：400 POST .../uploadType=multipart
  "Content-Type specified in the upload (text/plain) does not match
   Content-Type specified in metadata (image/jpeg)"
原因：blob.upload_from_string(data) 默认以上传头 text/plain 走 multipart，
      与我们在 metadata 里写的 image/jpeg 冲突 → GCS 直接拒绝。
正确：显式传 content_type
      blob.upload_from_string(data, content_type=ctype)
      blob.upload_from_file(fh, rewind=True, content_type=ctype)
教训：同步完必须用 --verify-only 复核，不能只看脚本自报成功。
```

### ★2 每个对象起 3 个进程 = CPU 杀手（本次"机器卡住"的直接原因）

```text
旧实现：每对象 aws s3 cp（下载）+ 2×gsutil cp（巴西、香港各一次）。
gsutil 每次启动要加载整套 Python 运行时：约 0.5-1s CPU、约 200MB 内存。
4000+ 对象 ≈ 1.2 万次进程启动 → CPU 全耗在"启动"，不是传输；
小文件多只会把这个开销放大（大文件能被传输时间摊薄）。
现场证据：一台机同时 130 个 aws/gsutil 进程，单个 aws 进程 90% CPU。
新实现：一个进程 + 线程池，对象在内存/临时文件里直接搬运。
实测：tada-statics5 待传 2767 个对象，260s 完成（CLI 版按 0.5 对象/s 需 1 小时+）。
```

### ★3 GCS 写权限是 VM scopes 决定的，不是 IAM

```text
现象：03/01/02 上 gsutil 写 GCS 报
  403 "Provided scope(s) are not authorized"
原因：这些 VM 的默认服务账号 scope 只读；同一个服务账号在宝塔那台机器上却能写，
      说明差别在 VM scopes（不是 IAM 角色）。
修复（必须 beta/alpha 通道，默认 release track 没有该子命令）：
  gcloud beta compute instances stop  <INSTANCE> --zone=southamerica-east1-a
  gcloud beta compute instances set-scopes <INSTANCE> \
      --zone=southamerica-east1-a --scopes=cloud-platform
  gcloud beta compute instances start <INSTANCE> --zone=southamerica-east1-a
注意：缩短命令用 --scopes=cloud-platform 短别名；Cloud Shell 会把长 URL 自动加链接截断。
```

### ★4 改完 scopes 仍然 403：gsutil 缓存了旧 token

```text
gsutil 把 access token 缓存在 /root/.gsutil/credstore2，旧 token 未过期前一直复用。
修复：rm -f /root/.gsutil/credstore2 /root/.config/gcloud/access_tokens.db
      gcloud auth application-default print-access-token >/dev/null   # 重新取
```

### ★5 Cloudflare token 有 IP 白名单

```text
现象：同一个 token，在宝塔上调 CF API 正常；在 03 上调 /zones、purge_cache 全部 403
      （Authentication error / HTTP 403 Forbidden）。
原因：CF token 设了 Client IP Address Filtering，只放行了宝塔出口 IP。
影响：目前 CDN purge 只能由宝塔执行（几个 API 调用，几乎无负载；不是同步压力）。
要迁到 03：在 Cloudflare 控制台给该 token 的 Client IP Filtering 加上 03 出口 IP。
```

### ★6 CDN `cacheEverything` 会缓存 404 和旧内容（7 天），且状态头会误导

```text
worker（summer-wave-c94f）用 cf.cacheEverything + cacheTtl=604800：
  · 资源不存在时请求过的 URL 会把 404 缓存 7 天；
  · 客户端看到的 cf-cache-status=MISS 是"zone 层"状态，
    不代表 worker 子请求没命中缓存 → 看起来"已是最新"，实际还在发旧内容。
正确做法：内容更新后换 CACHE_KEY_PREFIX（当前 v11-20260912-resync）并重新部署 worker，
          让所有边缘缓存键一次性失效；只 purge 具体 URL 不够（且 30 URL/次限制）。
部署：python3 docker/scripts/cf_worker_deploy.py --script summer-wave-c94f --file <worker.js>
```

### ★7 小机器高并发会压死管理面（宝塔 sshd 被饿死）

```text
现象：宝塔（2 vCPU）跑 32 并发 aws+gsutil → load 34、CPU 80%，
      sshd 端口在监听但 SSH 握手超时（连内网也一样），只能到 GCP 控制台 reset 才恢复。
教训：① 同步不要跑在流量入口/管理机上；② 并发 ≤ 2×CPU 核数；
      ③ 用 nice 降低优先级；④ 4C 以下机器建议 jobs ≤ 8。
```

### ★8 Ubuntu 26 + Python 3.14 的 apt 版 awscli 不可用

```text
现象：aws 任何子命令都报 "badly formed help string"。
原因：发行版 awscli 与 Python 3.14 的 argparse 兼容问题。
修复：用官方安装包（自带运行时）：
  curl -sSL -o /tmp/awscliv2.zip https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip
  unzip -q /tmp/awscliv2.zip -d /tmp && /tmp/aws/install --update
```

### ★9 S3 分片上传的 ETag 不是 MD5

```text
单段上传：ETag = 内容 MD5，可直接与 GCS 的 md5Hash 比对。
分片上传：ETag 形如 <md5>-N（如 abc...-7），**不是**内容 MD5，
          不能用它判内容一致；只能比大小或抽样下载（对应 GCS 侧 composite 对象）。
本次 statics4/5 各只有 1 个对象属于这种情况。
```

### ★10 单文件 bind mount 的 inode 陷阱（容器里看到的还是旧文件）

```text
场景：容器用「单文件 bind mount」挂了宿主机的 version.json / server_configs /
      permissions.py / 00.vendor-upstreams.conf 等。
现象：宿主机文件已更新（md5 变了），容器内还是旧内容；
      docker cp 覆盖会被挡：unlinkat ...: device or resource busy。
原因：git checkout / scp 换文件是替换 inode，运行中的容器仍绑旧 inode。
修复：重启容器重新解析挂载，或 docker cp 到容器内路径（不要覆盖挂载点）。
注意：目录挂载没有这个问题（如 /opt/pgserver/docker/ben-bot/data/scripts）。
```

### ★11 health.json 不是每个桶都有

```text
health.json 是运维探针探活用的固定返回值；前端同步后偶尔缺，
会让探针/污染排查清单误报。
解决：gcs_health_json_ensure.py 幂等补齐（17 个桶），已挂宝塔 cron */15。
```

## 四、标准操作流程（SOP）

```text
1) 同步（后端 03，容器内）
   docker run -d --name dbqp-resource-sync --network host \
     -v /root/dbqp-h5-download.env:/creds/aws.env:ro \
     -v /root/dbqp-notify.env:/creds/notify.env:ro \
     dbqp-resource-sync:latest \
     --prefix tada-statics4,tada-statics5 --apply --jobs 32 --interval 60

2) 必须复核（零数据搬运，45-62s）
   ... dbqp-resource-sync:latest --prefix <同上> --verify-only
   判定标准：缺失 0 / 大小不符 0 / 内容不符 0（分片 ETag 例外单独看）

3) 收尾
   health.json：脚本内自动执行（17 桶）
   CDN：worker 缓存键换版本重新部署（内容有更新时）＋按需 purge
        （purge 目前只能从宝塔执行，原因见坑 ★5）

4) 有更新就播报进度到飞机群（脚本自动，含北京/巴西圣保罗双时区）
```

## 五、历史文档更正索引（避免被旧内容误导）

| 文档 | 已过时/错误的内容 | 现状 |
| --- | --- | --- |
| `docker/线上服务器信息/frontend-reflow-s3-to-gcs.md` | 「在宝塔上中转」「gsutil 只认 GCS/aws 只认 S3，所以必须中转」「桶名 dbqp-gcs-*」 | 已加更正横幅：执行机=03 容器、SDK 直连、桶名 newgg2-* |
| `docker/workbench/PROJECT_RUNTIME_CHAINS.md` | 「静态更新源 = client.git → GCS 双区」 | 已更正：git 同步已停用，现为 S3 → GCS |
| `docker/scripts/s3_to_gcs_static_sync.sh` | 每个对象下载两次（巴西一次、香港一次） | 已改为薄封装，统一走 SDK/CLI 脚本 |
| 本文档 | — | 以上所有坑的唯一权威记录 |

## 六、飞机群通知 message_id

```text
6329/6341/6362/6376/6383/6391 迁移与容器化过程
6426 答疑（CPU 原因 + 元数据校验）
6454 首次同步汇总（后被证明是误报）
6481 400 根因定位与修复完成（4 桶校验全绿，请复测）
```

## 七、本地提交

```text
f3c348b2 docs(sync): 客户端资源同步（S3→GCS）SDK 实现与全部踩坑记录 + 历史文档更正
aa922391 fix(sync): SDK 上传 400 根因修复 + worker 缓存键 v11
194d2c09 feat(sync): SDK 直连同步引擎 + 容器化落地
master 领先 origin/master（未 Push）
```
