---
id: "doc-536c2ca61e43"
title: "2026-09-25 香港 JILI 静态资源独立桶接入 + Worker 跨桶改造记录"
date: "2026-09-25T14:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Shell", "Python", "Docker", "Nginx", "CDN", "安全运维", "数据库恢复"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-09-25-1420-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AFJILI%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E7%8B%AC%E7%AB%8B%E6%A1%B6%E6%8E%A5%E5%85%A5%E4%B8%8EWorker%E8%B7%A8%E6%A1%B6%E6%94%B9%E9%80%A0%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-09-25-1420-【架构改造】香港JILI静态资源独立桶接入与Worker跨桶改造记录.md"
sourceSha256: "ffad2dcfbc951ae562602dcb08f7b1e2ba4adbc7ba1ddde14e26c8e2cc65d399"
sourceSystem: "project-doc"
---

# 2026-09-25 香港 JILI 静态资源独立桶接入 + Worker 跨桶改造记录

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-09-25-1420-【架构改造】香港JILI静态资源独立桶接入与Worker跨桶改造记录.md`

> 整理日期：2026-09-25 14:20｜日期依据：文件名日期

## 一、需求

```text
用户：香港的 Worker 代码修改一下（附件给出 jili-static -> tada-statics 的映射），
     AWS 创建 dbqp-s3-jili-static / dbqp-s3-jili-static1，与其他桶同权限、对外；
     JILI 不再复用 TADA 共享资源。
```

## 二、桶与资源链路

```text
AWS S3（大阪 ap-northeast-3，开发侧上传，与其他 dbqp-s3-* 桶同权限/公开读）：
  dbqp-s3-jili-static    2026-09-25 11:39 由用户手动创建（21 个桶）
  dbqp-s3-jili-static1   2026-09-25 11:39 同上
GCS（巴西，后端 SDK 同步的目标，用户已创建）：
  newgg2-dbqp-gcs-jili-static / newgg2-dbqp-gcs-jili-static1
香港 Worker 回源：直接回 AWS S3 新桶（与其它前缀「香港用 S3」口径一致）
对象 key 约定：直接放桶根（master 文档：前端上传 s3://dbqp-s3-<prefix>/<路径>），
  因此 Worker 拼 `https://<新桶>.s3.ap-northeast-3.amazonaws.com<pathname>`。
```

验证：`curl -I https://dbqp-s3-jili-static.s3.ap-northeast-3.amazonaws.com/` = 403，
与现役 `dbqp-s3-pp-static` 行为一致（桶存在、未开放列目录）。

## 三、Worker 改造（hk_static_worker.js，保持老写法）

**只动 3 处、共 11 增 7 删**（用户要求「按照老写法来」「砍掉 jili-static2」）：

```js
// ① PREFIX_MAP 仍是「前缀 -> 值」的字符串写法（未改成对象结构）
const PREFIX_MAP = new Map([
    ["pg-static", "pg-static"],
    ...（pg3-pg7 / pp / ppk / panda / playson / g759 原样不动）
    // JILI 独立桶（2026-09-25 起，大阪 ap-northeast-3）：值写完整回源地址
    ["jili-static",  "https://dbqp-s3-jili-static.s3.ap-northeast-3.amazonaws.com"],
    ["jili-static1", "https://dbqp-s3-jili-static1.s3.ap-northeast-3.amazonaws.com"],
]);
// ② 回源拼接：值是完整 URL 就直接拼；否则仍是「香港主桶 / 目录前缀」
const target = s3Prefix.startsWith("http")
    ? `${s3Prefix}${url.pathname}${url.search}`
    : `${S3_ENDPOINT}/${s3Prefix}${url.pathname}${url.search}`;
// ③ jili-static2 已按要求从映射表移除（不再由 Worker 代理，请求原样放行到源站）
```

```text
缓存盐同步升级：CACHE_SALT v1-20260924 -> v2-20260925、HEALTH_CACHE_SALT h1 -> h2，
  原因：JILI 前缀名没变，不换盐会命中旧的 tada-statics 缓存内容。
```

配套工具同步升级（避免解析不到新结构）：

```text
docker/ci/check.py                       按 { endpoint, prefix } 解析并校验 JILI 三前缀映射
docker/ci/test_hk_static_worker.mjs      新增 jili-static/-static1 独立桶与 jili-static2 复用断言（31 项全通过）
docker/deploy/hongkong/deploy_static_worker.py  parse_prefix_map 兼容新结构（旧字符串格式仍兼容）
```

## 四、部署与验证

```bash
# 香港入口机
python3 /root/dbqp-hk-worker/docker/deploy/hongkong/deploy_static_worker.py \
    --account eaf1a5f4eb53c8cd384ce9088181b97c \
    --token-file /root/.config/cloudflare/workers-token \
    --zones hkcloudplay06.com,hkcloudplay07.com \
    deploy --backup-dir /root/dbqp-hk-worker-backup/20260925-jili
# -> deploy: http=200 success=True；旧版本已备份
```

线上源码复核（从 CF 拉取，只列 JILI 相关行）：

```text
["jili-static",  "https://dbqp-s3-jili-static.s3.ap-northeast-3.amazonaws.com"]
["jili-static1", "https://dbqp-s3-jili-static1.s3.ap-northeast-3.amazonaws.com"]
（无 jili-static2）
```

端到端验证：

| 域名 | 结果 | 说明 |
| --- | --- | --- |
| `pg-static.hkcloudplay06.com/100/001aacae6a.117d6.json` | 200 | 改造未影响既有前缀 |
| `pg6-static...`、`pp-static...`、`panda-static...`、`g759-static...` | 200 | 同上 |
| `jili-static.hkcloudplay06.com/...` | 403 | 新桶尚无对象（等开发上传），Worker 已生效 |
| `jili-static1.hkcloudplay06.com/...` | 403 | 同上 |
| `jili-static2.hkcloudplay06.com/...` | 403 | 已移出 Worker，原样放行到源站（standby nginx 兜底） |

（响应头 `x-dbqp-worker: hk-static-proxy` 确认请求经过本 Worker。）

## 五、待办

```text
1. 开发上传前端代码到 dbqp-s3-jili-static / dbqp-s3-jili-static1 后，复测：
   https://jili-static.hkcloudplay06.com/<真实路径> 应为 200（两个桶各抽一个文件）；
2. jili-static2 已按要求移出 Worker（不再代理）。如需它也有源，再单独确认（建独立桶后加回一行映射即可）；
3. 备份：本轮改了 Worker 与 CACHE_SALT，需要重跑 backup_cdn_config.py 更新 cdn-backup/。
```

## 六、追加：巴西 GCS 侧两个桶补建（2026-09-25 15:10）

用户先以为 GCS 侧已建，核对控制台后发现**并不存在**（GCS 列表 17 个桶里只有 panda/pg/pg3-pg7/
playson/pp/ppk/tada-statics1-5/g759，没有 jili）。香港链路不依赖 GCS（Worker 直接回源 AWS S3），
但巴西侧要读 JILI 前端资源就需要，因此补建：

```bash
# ⚠️ 必须指定 --project=newgg2-0520（其它 newgg2-* 桶都属于这个项目）
gcloud storage buckets create gs://newgg2-dbqp-gcs-jili-static \
    --project=newgg2-0520 --location=southamerica-east1 --default-storage-class=STANDARD
gcloud storage buckets create gs://newgg2-dbqp-gcs-jili-static1 \
    --project=newgg2-0520 --location=southamerica-east1 --default-storage-class=STANDARD
gcloud storage buckets add-iam-policy-binding gs://newgg2-dbqp-gcs-jili-static \
    --member=allUsers --role=roles/storage.objectViewer
gcloud storage buckets add-iam-policy-binding gs://newgg2-dbqp-gcs-jili-static1 \
    --member=allUsers --role=roles/storage.objectViewer
```

过程中的一次返工（记录备查）：

```text
第一次建桶时没带 --project，落到香港入口机 gcloud 的默认项目 infra-alc-20260511，
用户指出应为 newgg2-0520。处理：
  1) 确认两桶为空（gcloud storage ls -r 只有标题行）；
  2) 删除错项目下的两个空桶；
  3) 带 --project=newgg2-0520 重建 + 重新配公开读；
  4) 复核 infra-alc-20260511 下已无 jili 桶。
```

最终验证（实测）：

| 检查 | newgg2-dbqp-gcs-jili-static | newgg2-dbqp-gcs-jili-static1 | 现有桶对照（pg-static） |
| --- | --- | --- | --- |
| 所属项目 | newgg2-0520 | newgg2-0520 | newgg2-0520 |
| 区域 / 类别 | SOUTHAMERICA-EAST1 / STANDARD | 同 | 同 |
| 公开绑定 | `roles/storage.objectViewer` → `allUsers` | 同 | `roles/storage.objectViewer` → `allUsers` |
| 公网根路径 | 200 | 200 | 200 |

## 七、改造：全部前缀改为「一个厂家一个 S3 桶」（2026-09-25 15:40）

用户要求：Worker 映射统一改成「一个厂家一个 S3 地址」——所有静态前缀不再走香港主桶
`dbqp-h5-hk-517506432530`，而是各自回源 AWS 大阪（ap-northeast-3）的同名桶。

```js
// hk_static_worker.js（老写法：值直接写完整回源地址）
const PREFIX_MAP = new Map([
    ["pg-static",      "https://dbqp-s3-pg-static.s3.ap-northeast-3.amazonaws.com"],
    ["pg3-static",     "https://dbqp-s3-pg3-static.s3.ap-northeast-3.amazonaws.com"],
    ["pg4-static",     "https://dbqp-s3-pg4-static.s3.ap-northeast-3.amazonaws.com"],
    ["pg5-static",     "https://dbqp-s3-pg5-static.s3.ap-northeast-3.amazonaws.com"],
    ["pg6-static",     "https://dbqp-s3-pg6-static.s3.ap-northeast-3.amazonaws.com"],
    ["pg7-static",     "https://dbqp-s3-pg7-static.s3.ap-northeast-3.amazonaws.com"],
    ["pp-static",      "https://dbqp-s3-pp-static.s3.ap-northeast-3.amazonaws.com"],
    ["ppk-static",     "https://dbqp-s3-ppk-static.s3.ap-northeast-3.amazonaws.com"],
    ["panda-static",   "https://dbqp-s3-panda-static.s3.ap-northeast-3.amazonaws.com"],
    ["playson-static", "https://dbqp-s3-playson-static.s3.ap-northeast-3.amazonaws.com"],
    ["g759-static",    "https://dbqp-s3-g759-static.s3.ap-northeast-3.amazonaws.com"],
    ["jili-static",    "https://dbqp-s3-jili-static.s3.ap-northeast-3.amazonaws.com"],
    ["jili-static1",   "https://dbqp-s3-jili-static1.s3.ap-northeast-3.amazonaws.com"],
]);
```

`check.py` 已同步为「逐前缀校验必须等于 `https://dbqp-s3-<前缀>.s3.ap-northeast-3.amazonaws.com`」，
本地自检 31 项通过。

### 7.1 ⛔ 部署阻塞：这些 S3 桶目前是私有的

**未部署**（避免线上静态资源全量 403）。实测对照：

| 探测 | S3（dbqp-s3-pg-static） | GCS（newgg2-dbqp-gcs-pg-static） |
| --- | --- | --- |
| `100/001aacae6a.117d6.json` | **403** | **200** |
| 桶根 | 403 | 200 |
| pg6 / pp 同路径 | 403 | 200 |

结论：**对象存在且路径结构与香港一致**（GCS 侧同为桶根 key，如 `100/xxx.json`），
S3 侧 403 的原因是这些桶**没有配公开读**（私有桶对匿名请求返回 403）。

因此切换前必须先给桶开公开读（与香港桶的 PublicRead 口径一致），两种方式：

```text
方式一：控制台逐桶配置（13 个桶）
  1) 权限 -> 阻止公共访问：关闭「阻止通过任何公有存储桶策略…」
  2) 权限 -> 存储桶策略 -> 编辑，粘贴（Resource 换成对应桶名）：
     {
       "Version": "2012-10-17",
       "Statement": [{
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::dbqp-s3-pg-static/*"
       }]
     }
方式二：有 AK/SK 时批量执行（每个桶一条）：
  aws s3api put-public-access-block --bucket <桶> \
    --public-access-block-configuration \
    BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
  aws s3api put-bucket-policy --bucket <桶> --policy file://public-read.json
```

桶公开后我会：部署新 Worker → 逐前缀用真实文件复验（期望 200 + `x-dbqp-worker` + 二次 HIT）。

## 八、关联

```text
docker/deploy/hongkong/hk_static_worker.js                         Worker 源码（本次改造）
docker/deploy/hongkong/deploy_static_worker.py                     部署/备份工具
docker/ci/check.py + docker/ci/test_hk_static_worker.mjs           静态校验（31 项通过）
docker/deploy/hongkong/cdn-backup/                                 CDN 配置与 Worker 备份
docker/doc/2026-09-25-1000-【架构改造】香港商户socket域名hk-socket.com接入记录.md
```
